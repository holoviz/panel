"""
Pane class which render various markup languages including HTML,
Markdown, and also regular strings.
"""
from __future__ import annotations

import functools
import json
import textwrap

from typing import (
    TYPE_CHECKING, Any, ClassVar, Dict, List, Mapping, Type,
)

import param  # type: ignore

from ..io.resources import CDN_DIST
from ..models import HTML as _BkHTML, JSON as _BkJSON
from ..util import HTML_SANITIZER, escape
from ..util.warnings import deprecated
from .base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm  # type: ignore

class HTMLBasePane(ModelPane):
    """
    Baseclass for Panes which render HTML inside a Bokeh Div.
    See the documentation for Bokeh Div for more detail about
    the supported options like style and sizing_mode.
    """

    _bokeh_model: ClassVar[Model] = _BkHTML

    _rename: ClassVar[Mapping[str, str | None]] = {'object': 'text'}

    _updates: ClassVar[bool] = True

    __abstract = True

    def __init__(self, object=None, **params):
        if "style" in params:
            # In Bokeh 3 'style' was changed to 'styles'.
            params["styles"] = params.pop("style")
            deprecated("1.3", "style",  "styles")
        super().__init__(object=object, **params)


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
    priority: ClassVar[float | bool | None] = None

    _rename: ClassVar[Mapping[str, str | None]] = {
        'sanitize_html': None, 'sanitize_hook': None
    }

    _rerender_params: ClassVar[List[str]] = [
        'object', 'sanitize_html', 'sanitize_hook'
    ]

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        module, name = getattr(obj, '__module__', ''), type(obj).__name__
        if ((any(m in module for m in ('pandas', 'dask')) and
            name in ('DataFrame', 'Series')) or hasattr(obj, '_repr_html_')):
            return 0 if isinstance(obj, param.Parameterized) else 0.2
        elif isinstance(obj, str):
            return None
        else:
            return False

    def _transform_object(self, obj: Any) -> Dict[str, Any]:
        text = '' if obj is None else obj
        if hasattr(text, '_repr_html_'):
            text = text._repr_html_()
        if self.sanitize_html:
            text = self.sanitize_hook(text)
        return dict(object=escape(text))


class DataFrame(HTML):
    """
    The `DataFrame` pane renders pandas, dask and streamz DataFrame types using
    their custom HTML repr.

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

    justify = param.ObjectSelector(default=None, allow_None=True, objects=[
        'left', 'right', 'center', 'justify', 'justify-all', 'start',
        'end', 'inherit', 'match-parent', 'initial', 'unset'], doc="""
        How to justify the column labels.""")

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

    _object = param.Parameter(default=None, doc="""Hidden parameter.""")

    _dask_params: ClassVar[List[str]] = ['max_rows']

    _rerender_params: ClassVar[List[str]] = [
        'object', '_object', 'bold_rows', 'border', 'classes',
        'col_space', 'decimal', 'escape', 'float_format', 'formatters',
        'header', 'index', 'index_names', 'justify', 'max_rows',
        'max_cols', 'na_rep', 'render_links', 'show_dimensions',
        'sparsify', 'sizing_mode'
    ]

    _rename: ClassVar[Mapping[str, str | None]] = {
        rp: None for rp in _rerender_params[1:-1]
    }

    _stylesheets: ClassVar[List[str]] = [
        f'{CDN_DIST}css/dataframe.css'
    ]

    def __init__(self, object=None, **params):
        self._stream = None
        super().__init__(object, **params)

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        module = getattr(obj, '__module__', '')
        name = type(obj).__name__
        if (any(m in module for m in ('pandas', 'dask', 'streamz')) and
            name in ('DataFrame', 'Series', 'Random', 'DataFrames', 'Seriess', 'Styler')):
            return 0.3
        else:
            return False

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

    def _transform_object(self, obj: Any) -> Dict[str, Any]:
        if hasattr(obj, 'to_frame'):
            obj = obj.to_frame()

        module = getattr(obj, '__module__', '')
        if hasattr(obj, 'to_html'):
            if 'dask' in module:
                html = obj.to_html(max_rows=self.max_rows).replace('border="1"', '')
            elif 'style' in module:
                classes = ' '.join(self.classes)
                html = obj.to_html(table_attributes=f'class="{classes}"')
            else:
                kwargs = {p: getattr(self, p) for p in self._rerender_params
                          if p not in HTMLBasePane.param and p != '_object'}
                html = obj.to_html(**kwargs)
        else:
            html = ''
        return dict(object=escape(html))

    def _init_params(self) -> Dict[str, Any]:
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

    priority: ClassVar[float | bool | None] = 0

    _bokeh_model: ClassVar[Type[Model]] = _BkHTML

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'object': """JSON.stringify(value).replace(/,/g, ", ").replace(/:/g, ": ")"""
    }

    @classmethod
    def applies(cls, obj: Any) -> bool:
        return True

    def _transform_object(self, obj: Any) -> Dict[str, Any]:
        if obj is None or (isinstance(obj, str) and obj == ''):
            text = '<pre> </pre>'
        else:
            text = '<pre>'+str(obj)+'</pre>'
        return dict(object=escape(text))


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

    disable_math = param.Boolean(default=False, doc="""
        Whether to disable support for MathJax math rendering for
        strings escaped with $$ delimiters.""")

    extensions = param.List(default=[
        "extra", "smarty", "codehilite"], doc="""
        Markdown extension to apply when transforming markup.
        Does not apply if renderer is set to 'markdown-it' or 'myst'.""")

    plugins = param.List(default=[], doc="""
        Additional markdown-it-py plugins to use.""")

    renderer = param.Selector(default='markdown-it', objects=[
        'markdown-it', 'myst', 'markdown'], doc="""
        Markdown renderer implementation.""")

    renderer_options = param.Dict(default={}, doc="""
        Options to pass to the markdown renderer.""")

    # Priority depends on the data type
    priority: ClassVar[float | bool | None] = None

    _rename: ClassVar[Mapping[str, str | None]] = {
        'dedent': None, 'disable_math': None, 'extensions': None,
        'plugins': None, 'renderer': None, 'renderer_options': None
    }

    _rerender_params: ClassVar[List[str]] = [
        'object', 'dedent', 'extensions', 'css_classes', 'plugins',
    ]

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'object': None
    }

    _stylesheets: ClassVar[List[str]] = [
        f'{CDN_DIST}css/markdown.css'
    ]

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if hasattr(obj, '_repr_markdown_'):
            return 0.3
        elif isinstance(obj, str):
            return 0.1
        else:
            return False

    @classmethod
    @functools.lru_cache(maxsize=None)
    def _get_parser(cls, renderer, plugins, **renderer_options):
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
            if "breaks" not in renderer_options:
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
            .use(anchors_plugin, permalink=True).use(deflist_plugin).use(footnote_plugin).use(tasklists_plugin)
        )
        for plugin in plugins:
            parser = parser.use(plugin)
        try:
            from mdit_py_emoji import emoji_plugin
            parser = parser.use(emoji_plugin)
        except Exception:
            pass
        parser.options['highlight'] = hilite
        return parser

    def _transform_object(self, obj: Any) -> Dict[str, Any]:
        import markdown
        if obj is None:
            obj = ''
        elif not isinstance(obj, str):
            obj = obj._repr_markdown_()
        if self.dedent:
            obj = textwrap.dedent(obj)

        if self.renderer == 'markdown':
            html = markdown.markdown(
                obj,
                extensions=self.extensions,
                output_format='html5',
                **self.renderer_options
            )
        else:
            html = self._get_parser(
                self.renderer, tuple(self.plugins), **self.renderer_options
            ).render(obj)
        return dict(object=escape(html))

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

    theme = param.ObjectSelector(default="dark", objects=["light", "dark"], doc="""
        Whether the JSON tree view is expanded by default.""")

    priority: ClassVar[float | bool | None] = None

    _applies_kw: ClassVar[bool] = True

    _bokeh_model: ClassVar[Model] = _BkJSON

    _rename: ClassVar[Mapping[str, str | None]] = {
        "object": "text", "encoder": None, "style": "styles"
    }

    _rerender_params: ClassVar[List[str]] = [
        'object', 'depth', 'encoder', 'hover_preview', 'theme'
    ]

    _stylesheets: ClassVar[List[str]] = [
        f'{CDN_DIST}css/json.css'
    ]

    @classmethod
    def applies(cls, obj: Any, **params) -> float | bool | None:
        if isinstance(obj, (list, dict)):
            try:
                json.dumps(obj, cls=params.get('encoder', cls.encoder))
            except Exception:
                return False
            else:
                return 0.1
        elif isinstance(obj, str):
            return 0
        else:
            return None

    def _transform_object(self, obj: Any) -> Dict[str, Any]:
        try:
            data = json.loads(obj)
        except Exception:
            data = obj
        text = json.dumps(data or {}, cls=self.encoder)
        return dict(object=text)

    def _process_property_change(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        properties = super()._process_property_change(properties)
        if 'depth' in properties:
            properties['depth'] = -1 if properties['depth'] is None else properties['depth']
        return properties

    def _process_param_change(self, params: Dict[str, Any]) -> Dict[str, Any] :
        params = super()._process_param_change(params)
        if 'depth' in params:
            params['depth'] = None if params['depth'] < 0 else params['depth']
        return params
