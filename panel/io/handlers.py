from __future__ import annotations

import ast
import html
import json
import logging
import os
import pathlib
import re
import sys
import traceback
import urllib.parse as urlparse

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from types import ModuleType
from typing import IO, TYPE_CHECKING, Any

import bokeh.command.util

from bokeh.application.handlers.code import CodeHandler
from bokeh.application.handlers.code_runner import CodeRunner
from bokeh.application.handlers.handler import Handler, handle_exception
from bokeh.core.types import PathLike
from bokeh.document import Document
from bokeh.io.doc import curdoc, patch_curdoc, set_curdoc as bk_set_curdoc
from bokeh.util.dependencies import import_required

from ..config import config
from .mime_render import MIME_RENDERERS
from .profile import profile_ctx
from .reload import record_modules
from .state import state

if TYPE_CHECKING:
    from nbformat import NotebookNode

log = logging.getLogger('panel.io.handlers')

CELL_DISPLAY = []


@contextmanager
def _patch_ipython_display():
    try:
        import IPython
        _orig_display = IPython.display
        IPython.display.display = display
    except Exception:
        pass
    yield
    try:
        IPython.display.display = _orig_display
    except Exception:
        pass

@contextmanager
def _monkeypatch_io(loggers: dict[str, Callable[..., None]]) -> Iterator[None]:
    import bokeh.io as io
    old: dict[str, Any] = {}
    for f in CodeHandler._io_functions:
        old[f] = getattr(io, f)
        setattr(io, f, loggers[f])
    yield
    for f in old:
        setattr(io, f, old[f])

@contextmanager
def set_env_vars(**env_vars):
    old = {var: os.environ.get(var) for var in env_vars}
    os.environ.update(env_vars)
    yield
    for var, value in old.items():
        if value is None:
            del os.environ[var]
        else:
            os.environ[var] = value

def get_figure():
    if 'matplotlib.pyplot' not in sys.modules:
        return None
    import matplotlib.pyplot as plt
    fig = plt.gcf()
    if fig.get_axes():
        return fig

def display(*args, **kwargs):
    if kwargs.get('raw'):
        for arg in args:
            for mime_type in arg:
                if mime_type in MIME_RENDERERS:
                    out = MIME_RENDERERS[mime_type](arg[mime_type], {}, mime_type)
                    CELL_DISPLAY.append(out)
                    break
            else:
                CELL_DISPLAY.append(arg)
    else:
        CELL_DISPLAY.extend(args)

def extract_code(
    filehandle: IO, supported_syntax: tuple[str, ...] = ('{pyodide}', 'python')
) -> str:
    """
    Extracts Panel application code from a Markdown file.
    """
    inblock = False
    block_opener = None
    title = None
    markdown: list[str] = []
    out = []
    while True:
        line = filehandle.readline()
        if not line:
            # EOF
            break

        lsline = line.lstrip()
        if inblock:
            if lsline.startswith(block_opener):
                inblock = False
            else:
                out.append(line)
        elif lsline.startswith("```"):
            num_leading_backticks = len(lsline) - len(lsline.lstrip("`"))
            block_opener = '`'*num_leading_backticks
            syntax = line.strip()[num_leading_backticks:]
            if syntax in supported_syntax:
                if markdown:
                    md = ''.join(markdown)
                    markdown.clear()
                    if any('pn.extension' in o for o in out):
                        out.append(f"pn.pane.Markdown({md!r}).servable()\n")
                inblock = True
            else:
                markdown.append(line)
        elif line.startswith('# '):
            title = line[1:].lstrip()
        else:
            markdown.append(line)
    if markdown:
        md = ''.join(markdown)
        if any('pn.extension' in o for o in out):
            out.append(f"pn.pane.Markdown({md!r}).servable()\n")
    if title and any('template=' in o for o in out if 'pn.extension' in o):
        out.append(f'pn.state.template.title = {title.strip()!r}')
    return '\n'.join(out)


def capture_code_cell(cell):
    """
    Parses a code cell and generates wrapper code to capture the
    return value of the cell and any other outputs published inside
    the cell.
    """
    code = []
    if not len(cell['source']):
        return code

    source = cell['source'].split('\n')
    for line in source[:-1]:
        line = (line
            .replace('get_ipython().run_line_magic', '')
            .replace('get_ipython().magic', '')
        )
        code.append(line)
    cell_out = source[-1]

    # Expand last statement or expression until it can be parsed
    parses = False
    while not parses:
        try:
            if not cell_out.strip():
                raise SyntaxError
            ast.parse(cell_out)
            parses = True
        except SyntaxError:
            if not code:
                break
            cell_out = f'{code.pop()}\n{cell_out}'

    if not parses:
        # Skip cell if it cannot be parsed
        log.warn(
            "The following cell did not contain valid Python syntax "
            f"and was skipped:\n\n{cell['source']}"
        )
        return code
    elif cell_out.rstrip().endswith(';'):
        # Do not record output of cells ending in semi-colon
        code.append(cell_out)
        return code

    # Remove code comments
    if '#' in cell_out and not cell_out.count('\n'):
        try:
            # To not remove "#000000"
            cell_tmp = cell_out[:cell_out.index('#')].rstrip()
            ast.parse(cell_tmp)
            cell_out = cell_tmp
        except SyntaxError:
            pass

    # Use eval mode to check whether cell ends in a statement or an
    # expression that will be rendered
    try:
        ast.parse(cell_out, mode='eval')
    except SyntaxError:
        code.append(cell_out)
        return code

    # Capture cell outputs
    cell_id = cell['id']
    code.append(f"""\
_pn__state._cell_outputs[{cell_id!r}].append(({cell_out}))
for _cell__out in _CELL__DISPLAY:
    _pn__state._cell_outputs[{cell_id!r}].append(_cell__out)
_CELL__DISPLAY.clear()
_fig__out = _get__figure()
if _fig__out:
    _pn__state._cell_outputs[{cell_id!r}].append(_fig__out)
""")
    return code

def autoreload_handle_exception(handler, module, e):
    if not config.autoreload:
        handle_exception(handler, e)
        return

    from ..pane import Alert

    # Clean up module
    del sys.modules[module.__name__]
    try:
        state.curdoc.modules._modules.remove(module)
    except ValueError:
        pass

    # Serve error
    e_msg = str(e).replace('\033[1m', '<b>').replace('\033[0m', '</b>')
    tb = html.escape(traceback.format_exc()).replace('\033[1m', '<b>').replace('\033[0m', '</b>')
    Alert(
        f'<b>{type(e).__name__}</b>: {e_msg}\n<pre style="overflow-y: auto">{tb}</pre>',
        alert_type='danger', margin=5, sizing_mode='stretch_width'
    ).servable()

def run_app(handler, module, doc, post_run=None, allow_empty=False):
    try:
        old_doc = curdoc()
    except RuntimeError:
        old_doc = None
        bk_set_curdoc(doc)

    sessions = []

    def post_check():
        newdoc = curdoc()
        # Do not let curdoc track modules when autoreload is enabled
        # otherwise it will erroneously complain that there is
        # a memory leak
        if config.autoreload:
            newdoc.modules._modules = []

        # script is supposed to edit the doc not replace it
        if newdoc is not doc:
            raise RuntimeError(f"{handler._origin} at '{handler._runner.path}' replaced the output document")

    try:
        state._launching.add(doc)
        with _monkeypatch_io(handler._loggers):
            with patch_curdoc(doc):
                with profile_ctx(config.profiler) as sessions:
                    with record_modules(handler=handler):
                        runner = handler._runner
                        if runner.error:
                            from ..pane import Alert
                            Alert(
                                f'<b>{runner.error}</b>\n<pre style="overflow-y: auto">{runner.error_detail}</pre>',
                                alert_type='danger', margin=5, sizing_mode='stretch_width'
                            ).servable()
                        else:
                            handler._runner.run(module, post_check)
                            if post_run:
                                post_run()
                if not doc.roots and not allow_empty and config.autoreload and doc not in state._templates:
                    from ..pane import Alert
                    Alert(
                        ('<b>Application did not publish any contents</b>\n\n<span>'
                        'Ensure you have marked items as servable or added models to '
                        'the bokeh document manually.'),
                        alert_type='danger', margin=5, sizing_mode='stretch_width'
                    ).servable()
    finally:
        if config.profiler:
            try:
                path = doc.session_context.request.path
                state._profiles[(path, config.profiler)] += sessions
                state.param.trigger('_profiles')
            except Exception:
                pass
        state._launching.remove(doc)
        if old_doc is not None:
            bk_set_curdoc(old_doc)

def parse_notebook(
    filename: str | os.PathLike | IO,
    preamble: list[str] | None = None
) -> tuple[NotebookNode, str, dict[str, Any]]:
    """
    Parses a notebook on disk and returns a script.

    Parameters
    ----------
    filename: str | os.PathLike
      The notebook file to parse.
    preamble: list[str]
      Any lines of code to prepend to the parsed code output.

    Returns
    -------
    nb: nbformat.NotebookNode
      nbformat dictionary-like representation of the notebook
    code: str
      The parsed and converted script
    cell_layouts: dict
      Dictionary containing the layout and positioning of cells.
    """
    nbconvert = import_required('nbconvert', 'The Panel notebook application handler requires nbconvert to be installed.')
    nbformat = import_required('nbformat', 'The Panel notebook application handler requires Jupyter Notebook to be installed.')

    class StripMagicsProcessor(nbconvert.preprocessors.Preprocessor):  # type: ignore
        """
        Preprocessor to convert notebooks to Python source while stripping
        out all magics (i.e IPython specific syntax).
        """

        _magic_pattern = re.compile(r'^\s*(?P<magic>%%\w\w+)($|(\s+))')

        def strip_magics(self, source: str) -> str:
            """
            Given the source of a cell, filter out all cell and line magics.
            """
            filtered: list[str] = []
            for line in source.splitlines():
                match = self._magic_pattern.match(line)
                if match is None:
                    filtered.append(line)
                else:
                    msg = 'Stripping out IPython magic {magic} in code cell {cell}'
                    message = msg.format(cell=self._cell_counter, magic=match.group('magic'))
                    log.warning(message)
            return '\n'.join(filtered)

        def preprocess_cell(self, cell, resources, index):
            if cell['cell_type'] == 'code':
                self._cell_counter += 1
                cell['source'] = self.strip_magics(cell['source'])
            return cell, resources

        def __call__(self, nb, resources):
            self._cell_counter = 0
            return self.preprocess(nb,resources)

    preprocessors = [StripMagicsProcessor()]

    nb = nbformat.read(filename, nbformat.NO_CONVERT)
    exporter = nbconvert.NotebookExporter()

    for preprocessor in preprocessors:
        exporter.register_preprocessor(preprocessor)

    nb_string, _ = exporter.from_notebook_node(nb)
    nb = nbformat.reads(nb_string, 4)
    nb = nbformat.v4.upgrade(nb)

    cell_layouts = {}
    code = list(preamble or [])
    for cell in nb['cells']:
        cell_id = cell['id']
        cell_layouts[cell_id] = cell['metadata'].get('panel-layout', {})
        if cell['cell_type'] == 'code':
            cell_code = capture_code_cell(cell)
            code += cell_code
        elif cell['cell_type'] == 'markdown':
            md = ''.join(cell['source']).replace('"', r'\"')
            code.append(f'_pn__state._cell_outputs[{cell_id!r}].append("""{md}""")')
    code_string = '\n'.join(code)
    return nb, code_string, cell_layouts

#---------------------------------------------------------------------
# Handler classes
#---------------------------------------------------------------------

class PanelCodeRunner(CodeRunner):

    def run(self, module: ModuleType, post_check: Callable[[], None] | None = None) -> None:
        """
        Execute the configured source code in a module and run any post
        checks.

        See bokeh.application.handlers.code_runner for original implementation.
        """
        _cwd = os.getcwd()
        _sys_path = list(sys.path)
        _sys_argv = list(sys.argv)
        sys.path.insert(0, os.path.dirname(self._path))
        sys.argv = [os.path.basename(self._path), *self._argv]

        # XXX: self._code shouldn't be None at this point but types don't reflect this
        assert self._code is not None

        try:
            exec(self._code, module.__dict__)

            if post_check:
                post_check()
        except Exception as e:
            autoreload_handle_exception(self, module, e)
        finally:
            # undo sys.path, CWD fixups
            os.chdir(_cwd)
            sys.path = _sys_path
            sys.argv = _sys_argv
            self.ran = True


class PanelCodeHandler(CodeHandler):
    """Modify Bokeh documents by creating Dashboard from code.

    Additionally this subclass adds support for the ability to:

    - Log session launch, load and destruction
    - Capture document_ready events to track when app is loaded.
    - Add profiling support
    - Ensure that state.curdoc is set
    - Reload the application module if autoreload is enabled
    - Track modules loaded during app execution to enable autoreloading
    """

    def __init__(
        self,
        *,
        source: str | None = None,
        filename: PathLike, argv: list[str] = [],
        package: ModuleType | None = None,
        runner: PanelCodeRunner | None = None
    ) -> None:
        Handler.__init__(self)

        if runner:
            self._runner = runner
        elif source:
            self._runner = PanelCodeRunner(source, filename, argv, package=package)
        else:
            raise ValueError("Must provide source code to PanelCodeHandler")

        self._loggers = {}
        for f in PanelCodeHandler._io_functions:
            self._loggers[f] = self._make_io_logger(f)

    def url_path(self) -> str | None:
        if self.failed and not config.autoreload:
            return None

        # TODO should fix invalid URL characters
        return '/' + os.path.splitext(os.path.basename(self._runner.path))[0]

    def modify_document(self, doc: Document):
        if config.autoreload:
            path = self._runner.path
            argv = self._runner._argv
            handler = type(self)(filename=path, argv=argv)
            self._runner = handler._runner

        module = self._runner.new_module()

        # If no module was returned it means the code runner has some permanent
        # unfixable problem, e.g. the configured source code has a syntax error
        if module is None and not config.autoreload:
            return

        # One reason modules are stored is to prevent the module from being gc'd
        # before the document is. A symptom of a gc'd module is that its globals
        # become None. Additionally stored modules are used to provide correct
        # paths to custom models resolver.
        if module is not None:
            doc.modules.add(module)

        run_app(self, module, doc)

CodeHandler.modify_document = PanelCodeHandler.modify_document  # type: ignore


class ScriptHandler(PanelCodeHandler):
    """Modify Bokeh documents by creating Dashboard from a Python script.
    """


    _logger_text = "%s: call to %s() ignored when running scripts with the 'bokeh' command."

    _origin = "Script"

    def __init__(self, *, filename: PathLike, argv: list[str] = [], package: ModuleType | None = None) -> None:
        '''

        Keywords:
            filename (str) : a path to a Python source (".py") file

        '''
        with open(filename, encoding='utf-8') as f:
            source = f.read()

        super().__init__(source=source, filename=filename, argv=argv, package=package)

bokeh.application.handlers.directory.ScriptHandler = ScriptHandler  # type: ignore


class MarkdownHandler(PanelCodeHandler):
    """Modify Bokeh documents by creating Dashboard from a Markdown file.
    """

    _logger_text = "%s: call to %s() ignored when running Markdown files with the 'panel' command."

    _origin = "Markdown"

    def __init__(self, *args, **kwargs):
        '''

        Keywords:
            filename (str) : a path to a Markdown (".md") file

        '''
        if 'filename' not in kwargs:
            raise ValueError('Must pass a filename to Handler')
        filename = os.path.abspath(kwargs['filename'])
        with open(filename, encoding='utf-8') as f:
            code = extract_code(f)
        kwargs['source'] = code
        super().__init__(*args, **kwargs)


class NotebookHandler(PanelCodeHandler):
    """Modify Bokeh documents by creating Dashboard from a notebook file.
    """

    _imports = [
        'from panel import state as _pn__state',
        'from panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n'
    ]

    _logger_text = "%s: call to %s() ignored when running notebooks with the 'panel' command."

    _origin = "Notebook"

    def __init__(self, *, filename: PathLike, argv: list[str] = [], package: ModuleType | None = None) -> None:
        '''

        Keywords:
            filename (str) : a path to a Jupyter notebook (".ipynb") file

        '''
        self._load_layout(filename)
        super().__init__(source=self._parse(filename), filename=filename)
        self._stale = False

    def _parse(self, filename):
        nb, code, cell_layouts = parse_notebook(filename, preamble=self._imports)
        state._cell_layouts[self] = cell_layouts
        for cell_id, layout in self._layout.get('cells', {}).items():
            state._cell_layouts[self][cell_id] = layout
        self._nb = nb
        return code

    def _load_layout(self, filename):
        nb_path = pathlib.Path(filename)
        layout_path = nb_path.parent / f'.{nb_path.name}.layout'
        if layout_path.is_file():
            with open(layout_path) as f:
                self._layout = json.load(f)
        else:
            self._layout = {}
        return self._layout

    def _compute_layout(self, spec, panels):
        from ..pane import Plotly
        params = {}
        if 'width' in spec and 'height' in spec:
            params['sizing_mode'] = 'stretch_both'
        else:
            params['sizing_mode'] = 'stretch_width'
            if len(panels) == 1 and isinstance(panels[0], Plotly):
                params['min_height'] = 300
        return params

    def _render_template(self, doc, path):
        """Renders template containing cell outputs.

        Creates an EditableTemplate containing all cell outputs
        found in the notebook and lays them out according to the
        cell metadata (if present).

        Parameters
        -----------
        doc (Document)
            A ``Document`` to render the template into
        path (str):
            The path to the application code.
        """
        from ..config import config
        from ..layout import Column
        from ..pane import panel
        from .state import state

        config.template = 'editable'
        persist = state._jupyter_kernel_context
        editable = 'editable' in state.session_args
        reset = 'reset' in state.session_args
        if not (editable or persist):
            state.template.editable = False
        state.template.title = os.path.splitext(os.path.basename(path))[0].replace('_', ' ').title()

        layouts, outputs, cells = {}, {}, {}
        for cell_id, objects in state._cell_outputs.items():
            if reset:
                spec = {}
            elif cell_id in self._layout.get('cells', {}):
                spec = self._layout['cells'][cell_id]
            else:
                spec = state._cell_layouts[self].get(cell_id, {})
            panels = [panel(obj) for obj in objects if obj is not None]
            pout = Column(*panels, **self._compute_layout(spec, panels))
            for po in pout:
                po.sizing_mode = pout.sizing_mode
            outputs[cell_id] = pout
            layouts[id(pout)] = spec
            cells[cell_id] = id(pout)
            pout.servable()

        # Reorder outputs based on notebook metadata
        import nbformat
        nb = nbformat.read(self._runner._path, nbformat.NO_CONVERT)
        if 'order' in self._layout:
            cell_order = self._layout['order']
        else:
            cell_order = nb['metadata'].get('panel-cell-order', [])
        ordered = {}
        for cell_id in cell_order:
            if cell_id not in cells or reset:
                continue
            obj_id = cells[cell_id]
            ordered[obj_id] = layouts[obj_id]
            for cell_id in self._layout.get('order', []):
                if cell_id not in cells:
                    continue
                obj_id = cells[cell_id]
                ordered[obj_id] = layouts[obj_id]
            for obj_id, spec in layouts.items():
                if obj_id not in ordered:
                    ordered[obj_id] = spec

        # Set up state
        state.template.param.update(
            layout=ordered,
            local_save=not bool(state._jupyter_kernel_context)
        )
        if reset:
            def unset_reset():
                query = state.location.query_params
                query.pop('reset', None)
                search = urlparse.urlencode(query)
                state.location.search = f'?{search}' if search else ''
            state.onload(unset_reset)
        if persist:
            state.template.param.watch(self._update_position_metadata, 'layout')
        state._session_outputs[doc] = outputs

    def modify_document(self, doc: Document) -> None:
        """Run Bokeh application code to update a ``Document``

        Parameters
        -----------
        doc (Document) : a ``Document`` to update
        """
        path = self._runner._path
        if self._stale or config.autoreload:
            self._load_layout(path)
            source = self._parse(path)
            nodes = ast.parse(source, os.fspath(path))
            self._runner._code = compile(nodes, filename=path, mode='exec', dont_inherit=True)
            self._stale = False

        module = self._runner.new_module()

        # If no module was returned it means the code runner has some permanent
        # unfixable problem, e.g. the configured source code has a syntax error
        if module is None and not config.autoreload:
            return

        # One reason modules are stored is to prevent the module from being gc'd
        # before the document is. A symptom of a gc'd module is that its globals
        # become None. Additionally stored modules are used to provide correct
        # paths to custom models resolver.
        if module is not None:
            doc.modules.add(module)

        def post_run():
            if not (doc.roots or doc in state._templates or self._runner.error):
                self._render_template(doc, path)
            state._cell_outputs.clear()

        with _patch_ipython_display():
            with set_env_vars(MPLBACKEND='agg'):
                run_app(self, module, doc, post_run, allow_empty=True)

    def _update_position_metadata(self, event):
        """
        Maps EditableTemplate update events to cells in the original
        notebook and then overwrites notebook metadata with updated
        layout information.
        """
        nb = self._nb
        doc = event.obj._documents[-1]
        outputs = state._session_outputs[doc]
        cell_data, cell_ids = {}, {}
        for cell in nb['cells']:
            if cell['id'] in outputs:
                out = outputs[cell['id']]
                cell_ids[id(out)] = cell['id']
                spec = dict(event.new[id(out)])
                del spec['id']
                cell_data[cell['id']] = spec
        order = [cell_ids[obj_id] for obj_id in event.new]
        nb_layout = {
            'cells': cell_data,
            'order': order
        }
        nb_path = pathlib.Path(self._runner.path)
        path = nb_path.parent / f'.{nb_path.name}.layout'
        with open(path, 'w') as f:
            json.dump(nb_layout, f)
        self._stale = True

bokeh.application.handlers.directory.NotebookHandler = NotebookHandler  # type: ignore
