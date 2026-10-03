"""
Pane class which render various markup languages including HTML,
Markdown, and also regular strings.
"""
from __future__ import annotations

import asyncio
import functools
import json
import re
import textwrap
import time
import typing as t

from functools import partial
from html import escape, unescape

import param  # type: ignore

from ..config import config
from ..io.document import unlocked
from ..io.notebook import push
from ..io.resources import CDN_DIST
from ..io.state import state
from ..models.markup import HTML as _BkHTML, JSON as _BkJSON, HTMLStreamEvent
from ..util import HTML_SANITIZER, splice_diff, utf16_offset
from .base import ModelPane

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from bokeh.document import Document
    from bokeh.model import Model
    from markdown_it import MarkdownIt
    from pyviz_comms import Comm  # type: ignore

# Syntax whose rendering depends on other blocks (footnotes, reference
# links, definition lists) or which breaks line offsets (\r).
_NON_LOCAL_SYNTAX = re.compile(r'\[\^|\]:|^ {0,3}[:~][ \t]|\r', re.MULTILINE)

_HEADING_ID = re.compile(r'<h[1-6][^>]*?\sid="([^"]*)"')


class HTMLBasePane(ModelPane):
    """
    Baseclass for Panes which render HTML inside a Bokeh Div.
    See the documentation for Bokeh Div for more detail about
    the supported options like style and sizing_mode.
    """

    enable_streaming = param.Boolean(default=False, doc="""
        Whether to enable streaming of text snippets. This is useful
        when updating a string step by step, e.g. in a chat message.""")

    _bokeh_model: t.ClassVar[type[Model]] = _BkHTML

    _rename: t.ClassVar[Mapping[str, str | None]] = {'object': 'text', 'enable_streaming': None}

    _updates: t.ClassVar[bool] = True

    # Minimum interval (in seconds) between streamed updates sent to a
    # view; updates arriving in between are coalesced into one patch.
    _stream_interval: t.ClassVar[float] = 0.03

    __abstract = True

    def __init__(self, object=None, **params):
        self._raw_html: str | None = None
        # Per view: (escaped text, unescaped text) last sent to the frontend
        self._stream_state: dict[str, tuple[str, str]] = {}
        # Per view: token identifying the scheduled flush, or its due time
        self._stream_pending: dict[str, float] = {}
        self._stream_last: dict[str, float] = {}
        super().__init__(object=object, **params)

    def _escape_html(self, html: str) -> dict[str, t.Any]:
        # Keeping the unescaped HTML saves unescaping it when streaming
        self._raw_html = html
        return dict(object=escape(html))

    def _cleanup(self, root: Model | None = None) -> None:
        if root is not None:
            ref = root.ref['id']
            self._stream_state.pop(ref, None)
            self._stream_pending.pop(ref, None)
            self._stream_last.pop(ref, None)
        super()._cleanup(root)

    def _update_pane(self, *events) -> None:
        if (not self.enable_streaming or not self._stream_interval or
            any(event.name != 'object' for event in events)):
            super()._update_pane(*events)
            return
        for ref in list(self._models):
            if ref not in state._views or ref in state._fake_roots:
                continue
            doc, comm = state._views[ref][2:]
            if comm or not doc.session_context or state._unblocked(doc):
                self._stream_update(ref)
            elif ref not in self._stream_pending:
                # Off the event loop thread the throttle has to be
                # applied on the loop, which picks up the latest object.
                self._stream_pending[ref] = token = time.monotonic()
                doc.add_next_tick_callback(state._handle_exception_wrapper(
                    partial(self._stream_scheduled, ref, token, True), doc
                ))

    def _stream_update(self, ref: str) -> None:
        if ref not in self._models or ref not in state._views:
            return
        doc, comm = state._views[ref][2:]
        now = time.monotonic()
        due = self._stream_pending.get(ref)
        if due is not None and now < due:
            return
        wait = self._stream_last.get(ref, -float('inf')) + self._stream_interval - now
        if due is None and wait > 0 and self._stream_schedule(ref, doc, comm, now + wait):
            return
        self._stream_flush(ref)

    def _stream_schedule(self, ref: str, doc: Document, comm: Comm | None, due: float) -> bool:
        """
        Schedules a trailing flush, returning False if no event loop
        is available to run it.
        """
        callback = state._handle_exception_wrapper(
            partial(self._stream_scheduled, ref, due), doc
        )
        delay = max(due - time.monotonic(), 0)
        if doc.session_context:
            doc.add_timeout_callback(callback, int(delay * 1000))
        elif comm:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return False
            loop.call_later(delay, callback)
        else:
            return False
        self._stream_pending[ref] = due
        return True

    def _stream_scheduled(self, ref: str, token: float, throttle: bool = False) -> None:
        # A blocked event loop may have forced an earlier flush, which
        # superseded this callback.
        if self._stream_pending.get(ref) != token:
            return
        del self._stream_pending[ref]
        if throttle:
            self._stream_update(ref)
        else:
            self._stream_flush(ref)

    def _stream_flush(self, ref: str) -> None:
        self._stream_pending.pop(ref, None)
        if ref not in self._models or ref not in state._views:
            return
        _, root, doc, comm = state._views[ref]
        self._stream_last[ref] = time.monotonic()
        with unlocked():
            self._update_object(ref, doc, root, self._models[ref][1], comm)
        if comm and 'embedded' not in root.tags:
            push(doc, comm)

    def _update(self, ref: str, model: Model) -> None:
        self._raw_html = None
        props = self._get_properties(model.document)
        text = props.get('text')
        if (not self.enable_streaming or text is None or ref not in state._views
            or not isinstance(model, _BkHTML)):
            model.update(**props)
            return
        del props['text']
        html = unescape(text) if self._raw_html is None else self._raw_html
        old_text, old_html = self._stream_state.get(ref, (None, None))
        if old_text is not model.text or old_html is None:
            old_html = unescape(model.text)
        if html != old_html:
            start, end, patch = splice_diff(old_html, html)
            start, end = utf16_offset(old_html, start), utf16_offset(old_html, end)
            version = model.stream_version + 1
            props['run_scripts'] = False
            # Bypass the property setters so no full text update is sent
            model._property_values['text'] = text
            model._property_values['stream_version'] = version
            state._views[ref][2].callbacks.send_event(HTMLStreamEvent(
                model=model, patch=escape(patch), start=start, end=end, version=version
            ))
        self._stream_state[ref] = (model.text, html)
        model.update(**props)


class HTML(HTMLBasePane):
    """
    `HTML` panes renders HTML strings and objects with a `_repr_html_` method.

    The `height` and `width` can optionally be specified, to
    allow room for whatever is being wrapped.

    Reference: https://panel.holoviz.org/reference/panes/HTML.html

    :Example:

    >>> HTML(
    ...     "<h1>This is a HTML pane</h1>",
    ...     styles={'background-color': '#F6F6F6'}
    ... )
    """

    disable_math = param.Boolean(default=True, doc="""
        Whether to disable support for MathJax math rendering for
        strings escaped with $$ delimiters.""")

    sanitize_html = param.Boolean(default=False, doc="""
        Whether to sanitize HTML sent to the frontend.""")

    sanitize_hook = param.Callable(default=HTML_SANITIZER.clean, doc="""
        Sanitization callback to apply if `sanitize_html=True`.""")

    # Priority is dependent on the data type
    priority: t.ClassVar[float | bool | None] = None

    _rename: t.ClassVar[Mapping[str, str | None]] = {
        'sanitize_html': None, 'sanitize_hook': None, 'stream': None
    }

    _rerender_params: t.ClassVar[list[str]] = [
        'object', 'sanitize_html', 'sanitize_hook'
    ]

    @classmethod
    def applies(cls, object: t.Any) -> float | bool | None:
        module, name = getattr(object, '__module__', ''), type(object).__name__
        if ((any(m in module for m in ('pandas', 'dask')) and
            name in ('DataFrame', 'Series')) or hasattr(object, '_repr_html_')):
            return 0 if isinstance(object, param.Parameterized) else 0.2
        elif isinstance(object, str):
            return None
        else:
            return False

    def _transform_object(self, obj: t.Any) -> dict[str, t.Any]:
        text = '' if obj is None else obj
        if hasattr(text, '_repr_html_'):
            text = text._repr_html_()
        if self.sanitize_html:
            text = self.sanitize_hook(text)
        return self._escape_html(text)


class DataFrame(HTML):
    """
    The `DataFrame` pane renders pandas, dask and streamz DataFrame types using
    their custom HTML repr. Other DataFrame-like objects supported by
    Narwhals, e.g. polars and pyarrow, are rendered by converting them to
    pandas first, falling back to rendering the table directly if the
    conversion is not possible, e.g. because pandas or pyarrow are not
    installed.

    In the case of a streamz DataFrame the rendered data will update
    periodically.

    Reference: https://panel.holoviz.org/reference/panes/DataFrame.html

    :Example:

    >>> DataFrame(df, index=False, max_rows=25, width=400)
    """

    bold_rows = param.Boolean(default=True, doc="""
        Make the row labels bold in the output.""")

    border = param.Integer(default=0, doc="""
        A ``border=border`` attribute is included in the opening
        `<table>` tag.""")

    classes = param.List(default=['panel-df'], doc="""
        CSS class(es) to apply to the resulting html table.""")

    col_space = param.ClassSelector(default=None, class_=(str, int, dict), doc="""
        The minimum width of each column in CSS length units. An int
        is assumed to be px units.""")

    decimal = param.String(default='.', doc="""
        Character recognized as decimal separator, e.g. ',' in Europe.""")

    escape = param.Boolean(default=True, doc="""
        Whether or not to escape the dataframe HTML. For security reasons
        the default value is True.""")

    float_format = param.Callable(default=None, doc="""
        Formatter function to apply to columns' elements if they are
        floats. The result of this function must be a unicode string.""")

    formatters = param.ClassSelector(default=None, class_=(dict, list), doc="""
        Formatter functions to apply to columns' elements by position
        or name. The result of each function must be a unicode string.""")

    header = param.Boolean(default=True, doc="""
        Whether to print column labels.""")

    index = param.Boolean(default=True, doc="""
        Whether to print index (row) labels.""")

    index_names = param.Boolean(default=True, doc="""
        Prints the names of the indexes.""")

    justify: t.Literal[
        'left', 'right', 'center', 'justify', 'justify-all', 'start',
        'end', 'inherit', 'match-parent', 'initial', 'unset'
    ] | None = param.Selector(default=None, allow_None=True, objects=[
        'left', 'right', 'center', 'justify', 'justify-all', 'start',
        'end', 'inherit', 'match-parent', 'initial', 'unset'], doc="""
        How to justify the column labels.""")  # type: ignore[assignment, ty:invalid-assignment]

    max_rows = param.Integer(default=None, doc="""
        Maximum number of rows to display.""")

    max_cols = param.Integer(default=None, doc="""
        Maximum number of columns to display.""")

    na_rep = param.String(default='NaN', doc="""
        String representation of NAN to use.""")

    render_links = param.Boolean(default=False, doc="""
        Convert URLs to HTML links.""")

    show_dimensions = param.Boolean(default=False, doc="""
        Display DataFrame dimensions (number of rows by number of
        columns).""")

    sparsify = param.Boolean(default=True, doc="""
        Set to False for a DataFrame with a hierarchical index to
        print every multi-index key at each row.""")

    text_align: t.Literal['start', 'end', 'center'] | None = param.Selector(
        default=None, objects=[
        'start', 'end', 'center'], doc="""
         Alignment of non-header cells.""")  # type: ignore[assignment, ty:invalid-assignment]

    _object: t.Any = param.Parameter(default=None, doc="""Hidden parameter.""")  # type: ignore[assignment, ty:invalid-assignment]

    _dask_params: t.ClassVar[list[str]] = ['max_rows']

    _rerender_params: t.ClassVar[list[str]] = [
        'object', '_object', 'bold_rows', 'border', 'classes',
        'col_space', 'decimal', 'escape', 'float_format', 'formatters',
        'header', 'index', 'index_names', 'justify', 'max_rows',
        'max_cols', 'na_rep', 'render_links', 'show_dimensions',
        'sparsify', 'text_align', 'sizing_mode'
    ]

    _rename: t.ClassVar[Mapping[str, str | None]] = {
        rp: None for rp in _rerender_params[1:-1]
    }

    _stylesheets: t.ClassVar[list[str]] = [
        f'{CDN_DIST}css/dataframe.css'
    ]

    def __init__(self, object=None, **params):
        self._stream = None
        super().__init__(object, **params)

    @classmethod
    def applies(cls, object: t.Any) -> float | bool | None:
        module = getattr(object, '__module__', '')
        name = type(object).__name__
        if (any(m in module for m in ('pandas', 'dask', 'streamz', 'geopandas', 'spatialpandas')) and
            name in ('DataFrame', 'Series', 'Random', 'DataFrames',
                     'Seriess', 'Styler', 'GeoDataFrame', 'GeoSeries')):
            return 0.3
        elif cls._is_narwhals_compatible(object):
            return 0.3
        else:
            return False

    @staticmethod
    def _is_narwhals_compatible(object: t.Any) -> bool:
        import narwhals.stable.v2.dependencies as nwd
        return nwd.is_into_dataframe(object) or nwd.is_into_series(object)

    @staticmethod
    def _to_narwhals_frame(object: t.Any):
        import narwhals.stable.v2 as nw
        obj = nw.from_native(object, allow_series=True)
        if isinstance(obj, nw.Series):
            obj = obj.to_frame()
        if isinstance(obj, nw.LazyFrame):
            obj = obj.collect()
        return obj

    @classmethod
    def _narwhals_to_pandas(cls, object: t.Any):
        return cls._to_narwhals_frame(object).to_pandas()

    def _format_narwhals_value(self, value: t.Any, formatter: t.Callable | None) -> str:
        if value is None or (isinstance(value, float) and value != value):
            return self.na_rep
        if formatter is not None:
            value = formatter(value)
        elif isinstance(value, float) and self.float_format is not None:
            value = self.float_format(value)
        value = str(value)
        return escape(value) if self.escape else value

    def _narwhals_to_html(self, object: t.Any, classes: list[str]) -> str:
        # Conversion to pandas may fail, e.g. because the backend (like
        # polars) requires pyarrow for the conversion and it is not
        # installed. The backends' own HTML reprs ship their own classes
        # and styling, so we render the table ourselves to ensure the
        # Panel dataframe stylesheet still applies.
        import narwhals.stable.v2 as nw

        df = self._to_narwhals_frame(object)
        nrows, ncols = df.shape

        columns = list(df.columns)
        if isinstance(self.formatters, dict):
            formatters = [self.formatters.get(col) for col in columns]
        elif isinstance(self.formatters, list):
            formatters = list(self.formatters) + [None] * (ncols-len(self.formatters))
        else:
            formatters = [None] * ncols

        ellipsis_col = None
        if self.max_cols is not None and ncols > self.max_cols:
            ellipsis_col = self.max_cols // 2 + self.max_cols % 2
            keep = slice(ncols-(self.max_cols-ellipsis_col), None)
            columns = columns[:ellipsis_col] + columns[keep]
            formatters = formatters[:ellipsis_col] + formatters[keep]
            df = df.select(columns)

        ellipsis_row = None
        if self.max_rows is not None and nrows > self.max_rows:
            ellipsis_row = self.max_rows // 2 + self.max_rows % 2
            tail = self.max_rows - ellipsis_row
            df = nw.concat([df.head(ellipsis_row), df.tail(tail)]) if tail else df.head(ellipsis_row)

        def with_ellipsis(cells: list[str]) -> list[str]:
            if ellipsis_col is not None:
                cells = cells[:ellipsis_col] + ['...'] + cells[ellipsis_col:]
            return cells

        thead = ''
        if self.header:
            labels = with_ellipsis([
                escape(str(col)) if self.escape else str(col) for col in columns
            ])
            justify = f' style="text-align: {self.justify};"' if self.justify else ''
            header = ''.join(f'<th>{label}</th>' for label in labels)
            thead = f'<thead>\n<tr{justify}>{header}</tr>\n</thead>\n'

        rows = []
        for i, row in enumerate(df.rows()):
            if i == ellipsis_row:
                rows.append('<tr>' + '<td>...</td>' * len(with_ellipsis(list(columns))) + '</tr>')
            cells = with_ellipsis([
                self._format_narwhals_value(value, formatter)
                for value, formatter in zip(row, formatters, strict=True)
            ])
            rows.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>')
        tbody = '<tbody>\n' + '\n'.join(rows) + '\n</tbody>'

        class_string = ' '.join(classes)
        html = f'<table border="{self.border}" class="{class_string}">\n{thead}{tbody}\n</table>'
        if self.show_dimensions:
            html += f'\n<p>{nrows} rows × {ncols} columns</p>'
        return html

    def _set_object(self, object):
        self._object = object

    @param.depends('object', watch=True, on_init=True)
    def _setup_stream(self):
        if not self._models or not hasattr(self.object, 'stream'):
            return
        elif self._stream:
            self._stream.destroy()
            self._stream = None
        self._stream = self.object.stream.latest().rate_limit(0.5).gather()
        self._stream.sink(self._set_object)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._setup_stream()
        return model

    def _cleanup(self, root: Model | None = None) -> None:
        super()._cleanup(root)
        if not self._models and self._stream:
            self._stream.destroy()
            self._stream = None

    def _transform_object(self, obj: t.Any) -> dict[str, t.Any]:
        if hasattr(obj, 'to_frame'):
            obj = obj.to_frame()

        classes = list(self.classes)
        if self.text_align:
            classes.append(f'{self.text_align}-align')

        narwhals_obj = None
        if not hasattr(obj, 'to_html') and self._is_narwhals_compatible(obj):
            try:
                obj = self._narwhals_to_pandas(obj)
            except Exception:
                narwhals_obj = obj

        module = getattr(obj, '__module__', '')
        if narwhals_obj is not None:
            html = self._narwhals_to_html(narwhals_obj, classes)
        elif hasattr(obj, 'to_html'):
            if 'dask' in module:
                html = obj.to_html(max_rows=self.max_rows).replace('border="1"', '')
            elif 'style' in module:
                class_string = ' '.join(classes)
                html = obj.to_html(table_attributes=f'class="{class_string}"')
            else:
                kwargs = {p: getattr(self, p) for p in self._rerender_params
                          if p not in HTMLBasePane.param and p not in ('_object', 'text_align')}
                kwargs['classes'] = classes
                html = obj.to_html(**kwargs)
        else:
            html = ''
        return self._escape_html(html)

    def _init_params(self) -> dict[str, t.Any]:
        params = HTMLBasePane._init_params(self)

        if self._stream:
            params['object'] = self._object

        return params


class Str(HTMLBasePane):
    """
    The `Str` pane allows rendering arbitrary text and objects in a panel.

    Unlike Markdown and HTML, a `Str` is interpreted as a raw string without
    applying any markup and is displayed in a fixed-width font by default.

    The pane will render any text, and if given an object will display the
    object’s Python `repr`.

    Reference: https://panel.holoviz.org/reference/panes/Str.html

    :Example:

    >>> Str(
    ...    'This raw string will not be formatted, except for the applied style.',
    ...    styles={'font-size': '12pt'}
    ... )
    """

    priority: t.ClassVar[float | bool | None] = 0

    _bokeh_model: t.ClassVar[type[Model]] = _BkHTML

    _target_transforms: t.ClassVar[Mapping[str, str | None]] = {
        'object': """JSON.stringify(value).replace(/,/g, ", ").replace(/:/g, ": ")"""
    }

    @classmethod
    def applies(cls, object: t.Any) -> bool:
        return True

    def _transform_object(self, obj: t.Any) -> dict[str, t.Any]:
        if obj is None or (isinstance(obj, str) and obj == ''):
            text = '<pre> </pre>'
        else:
            text = '<pre>'+str(obj)+'</pre>'
        return self._escape_html(text)


class Markdown(HTMLBasePane):
    """
    The `Markdown` pane allows rendering arbitrary markdown strings in a panel.

    It renders strings containing valid Markdown as well as objects with a
    `_repr_markdown_` method, and may define custom CSS styles.

    Reference: https://panel.holoviz.org/reference/panes/Markdown.html

    :Example:

    >>> Markdown("# This is a header")
    """

    dedent = param.Boolean(default=True, doc="""
        Whether to dedent common whitespace across all lines.""")

    disable_anchors = param.Boolean(default=False, doc="""
        Whether to disable automatically adding anchors to headings.""")

    disable_math = param.Boolean(default=False, doc="""
        Whether to disable support for MathJax math rendering for
        strings escaped with $$ delimiters.""")

    extensions = param.List(default=[
        "extra", "smarty", "codehilite"], nested_refs=True, doc="""
        Markdown extension to apply when transforming markup.
        Does not apply if renderer is set to 'markdown-it' or 'myst'.""")

    hard_line_break = param.Boolean(default=False, doc="""
        Whether simple new lines are rendered as hard line breaks. False by
        default to conform with the original Markdown spec. Not supported by
        the 'myst' renderer.""")

    plugins: list[t.Any] = param.List(default=[], nested_refs=True, doc="""
        Additional markdown-it-py plugins to use.""")  # type: ignore[assignment, ty:invalid-assignment]

    renderer: t.Literal['markdown-it', 'myst', 'markdown'] = param.Selector(
        default='markdown-it', objects=[
        'markdown-it', 'myst', 'markdown'], doc="""
        Markdown renderer implementation.""")  # type: ignore[assignment, ty:invalid-assignment]

    renderer_options = param.Dict(default={}, nested_refs=True, doc="""
        Options to pass to the markdown renderer.""")

    # Priority depends on the data type
    priority: t.ClassVar[float | bool | None] = None

    _rename: t.ClassVar[Mapping[str, str | None]] = {
        'hard_line_break': None, 'disable_anchors': None,
        'dedent': None, 'disable_math': None, 'extensions': None,
        'plugins': None, 'renderer': None, 'renderer_options': None
    }

    _rerender_params: t.ClassVar[list[str]] = [
        'object', 'dedent', 'extensions', 'css_classes', 'plugins', 'disable_anchors'
    ]

    _target_transforms: t.ClassVar[Mapping[str, str | None]] = {
        'object': None
    }

    _stylesheets: t.ClassVar[list[str]] = [
        f'{CDN_DIST}css/markdown.css'
    ]

    @classmethod
    def applies(cls, object: t.Any) -> float | bool | None:
        if hasattr(object, '_repr_markdown_'):
            return 0.3
        elif isinstance(object, str):
            return 0.1
        else:
            return False

    @classmethod
    @functools.cache
    def _get_parser(cls, renderer, plugins, hard_line_break=False, disable_anchors=True, **renderer_options):
        if renderer == 'markdown':
            return None
        from markdown_it import MarkdownIt
        from markdown_it.renderer import RendererHTML
        from mdit_py_plugins.anchors import anchors_plugin
        from mdit_py_plugins.deflist import deflist_plugin
        from mdit_py_plugins.footnote import footnote_plugin
        from mdit_py_plugins.tasklists import tasklists_plugin

        def hilite(token, langname, attrs):
            try:
                from markdown.extensions.codehilite import CodeHilite
                return CodeHilite(src=token, lang=langname).hilite()
            except Exception:
                return token

        if renderer == 'markdown-it':
            if hard_line_break and "breaks" not in renderer_options:
                renderer_options["breaks"] = True

            parser = MarkdownIt(
                'gfm-like',
                renderer_cls=RendererHTML,
                options_update=renderer_options
            )
        elif renderer == 'myst':
            from myst_parser.parsers.mdit import (
                MdParserConfig, create_md_parser,
            )
            config = MdParserConfig(heading_anchors=1, enable_extensions=[
                'colon_fence', 'linkify', 'smartquotes', 'tasklist',
                'attrs_block'
            ], enable_checkboxes=True, **renderer_options)
            parser = create_md_parser(config, RendererHTML)
        parser = (
            parser
            .enable('strikethrough').enable('table')
            .use(deflist_plugin).use(footnote_plugin).use(tasklists_plugin)
        )
        if not disable_anchors:
            parser = parser.use(anchors_plugin, permalink=True)
        for plugin in plugins:
            parser = parser.use(plugin)
        try:
            from mdit_py_emoji import emoji_plugin
            parser = parser.use(emoji_plugin)
        except Exception:
            pass
        parser.options['highlight'] = hilite
        return parser

    def __init__(self, object=None, **params):
        # (parser, source, html, heading slugs) of the leading blocks
        self._block_cache: tuple[MarkdownIt, str, str, frozenset[str]] | None = None
        super().__init__(object=object, **params)

    def _transform_object(self, obj: t.Any) -> dict[str, t.Any]:
        return self._escape_html(self._render_markdown(obj))

    def _render_markdown(self, obj: t.Any) -> str:
        if obj is None:
            obj = ''
        elif not isinstance(obj, str):
            obj = obj._repr_markdown_()
        if self.dedent:
            obj = textwrap.dedent(obj)

        if self.renderer == 'markdown':
            import markdown
            self._block_cache = None
            extensions = self.extensions + ['nl2br'] if self.hard_line_break else self.extensions
            return markdown.markdown(
                obj,
                extensions=extensions,
                output_format='xhtml',
                **self.renderer_options
            )
        parser = self._get_parser(
            self.renderer, tuple(self.plugins), self.hard_line_break, self.disable_anchors, **self.renderer_options
        )
        if self.renderer == 'markdown-it' and not self.plugins and not _NON_LOCAL_SYNTAX.search(obj):
            try:
                return self._render_incremental(parser, obj)
            except IndexError:
                pass
        self._block_cache = None
        try:
            return parser.render(obj)
        except IndexError:
            # Likely markdown-it mdurl parser error
            with parser.reset_rules():
                parser.disable('link')
                return parser.render(obj)

    def _render_incremental(self, parser: MarkdownIt, src: str) -> str:
        """
        Renders markdown reusing the HTML of the leading top-level
        blocks from the previous render if the source was appended to.
        Every block but the last is final once a later block starts, so
        streaming only has to re-parse and re-highlight the last block.
        """
        cache = self._block_cache
        if cache and cache[0] is parser and src.startswith(cache[1]):
            _, prefix_src, prefix_html, slugs = cache
        else:
            prefix_src, prefix_html, slugs = '', '', frozenset()
        tail_src = src[len(prefix_src):]
        env: dict[str, t.Any] = {}
        tokens = parser.parse(tail_src, env)
        split = next((
            i for i in range(len(tokens)-1, 0, -1)
            if tokens[i].level == 0 and tokens[i].map is not None
        ), 0)
        render = parser.renderer.render
        stable_html = render(tokens[:split], parser.options, env) if split else ''
        tail_html = render(tokens[split:], parser.options, env)
        if slugs and not self.disable_anchors:
            # Heading anchors are deduplicated per render
            new_slugs = _HEADING_ID.findall(stable_html + tail_html)
            if not slugs.isdisjoint(new_slugs):
                self._block_cache = None
                return self._render_incremental(parser, src)
        if split:
            line = tokens[split].map[0]
            offset = 0
            for _ in range(line):
                offset = tail_src.index('\n', offset) + 1
            if not self.disable_anchors:
                slugs = slugs.union(_HEADING_ID.findall(stable_html))
            self._block_cache = (
                parser, prefix_src + tail_src[:offset], prefix_html + stable_html, slugs
            )
        else:
            self._block_cache = (parser, prefix_src, prefix_html, slugs)
        return prefix_html + stable_html + tail_html

    def _process_param_change(self, params):
        if 'css_classes' in params:
            params['css_classes'] = ['markdown'] + params['css_classes']
        return super()._process_param_change(params)

class JSON(HTMLBasePane):
    """
    The `JSON` pane allows rendering arbitrary JSON strings, dicts and other
    json serializable objects in a panel.

    Reference: https://panel.holoviz.org/reference/panes/JSON.html

    :Example:

    >>> JSON(json_obj, theme='light', height=300, width=500)
    """

    depth = param.Integer(default=1, bounds=(-1, None), doc="""
        Depth to which the JSON tree will be expanded on initialization.""")

    encoder = param.ClassSelector(class_=json.JSONEncoder, is_instance=False, doc="""
        Custom JSONEncoder class used to serialize objects to JSON string.""")

    hover_preview = param.Boolean(default=False, doc="""
        Whether to display a hover preview for collapsed nodes.""")

    theme: t.Literal["light", "dark"] = param.Selector(
        default="light", objects=["light", "dark"], doc="""
        If no value is provided, it defaults to the current theme
        set by pn.config.theme, as specified in the
        JSON.THEME_CONFIGURATION dictionary. If not defined there, it
        falls back to the default parameter value.""")  # type: ignore[assignment, ty:invalid-assignment]

    priority: t.ClassVar[float | bool | None] = None

    _applies_kw: t.ClassVar[bool] = True

    _bokeh_model: t.ClassVar[type[Model]] = _BkJSON

    _rename: t.ClassVar[Mapping[str, str | None]] = {
        "object": "text", "encoder": None, "style": "styles"
    }

    _rerender_params: t.ClassVar[list[str]] = [
        'object', 'depth', 'encoder', 'hover_preview', 'theme'
    ]

    _stylesheets: t.ClassVar[list[str]] = [
        f'{CDN_DIST}css/json.css'
    ]

    THEME_CONFIGURATION: t.ClassVar[dict[str,str]] = {"default": "light", "dark": "dark"}

    def __init__(self, object=None, **params):
        if "theme" not in params:
            params["theme"]=self._get_theme(config.theme)
        super().__init__(object=object, **params)

    @classmethod
    def applies(cls, object: t.Any, **params) -> float | bool | None:
        if isinstance(object, (list, dict)):
            try:
                json.dumps(object, cls=params.get('encoder', cls.encoder))
            except Exception:
                return False
            else:
                return 0.1
        elif isinstance(object, str):
            return 0
        else:
            return None

    def _transform_object(self, obj: t.Any) -> dict[str, t.Any]:
        try:
            data = json.loads(obj)
        except Exception:
            data = obj
        text = json.dumps(data or {}, cls=self.encoder)
        return dict(object=text)

    def _process_property_change(self, props: dict[str, t.Any]) -> dict[str, t.Any]:
        props = super()._process_property_change(props)
        if 'depth' in props:
            props['depth'] = -1 if props['depth'] is None else props['depth']
        return props

    def _process_param_change(self, params: dict[str, t.Any]) -> dict[str, t.Any] :
        params = super()._process_param_change(params)
        if 'depth' in params:
            params['depth'] = None if params['depth'] < 0 else params['depth']
        return params

    @classmethod
    def _get_theme(cls, config_theme: str)->str:
        return cls.THEME_CONFIGURATION.get(config_theme, cls.param.theme.default)
