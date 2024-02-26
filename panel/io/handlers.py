from __future__ import annotations

import ast
import json
import logging
import os
import pathlib
import re
import sys

from contextlib import contextmanager
from types import ModuleType
from typing import IO, Any, Callable

import bokeh.command.util

from bokeh.application.handlers.code import CodeHandler
from bokeh.command.util import (
    build_single_handler_application as _build_application,
)
from bokeh.core.types import PathLike
from bokeh.document import Document
from bokeh.io.doc import patch_curdoc
from bokeh.util.dependencies import import_required

from .state import state

log = logging.getLogger('panel.io.handlers')

CELL_DISPLAY = []


@contextmanager
def _monkeypatch_io(loggers: dict[str, Callable[..., None]]) -> dict[str, Any]:
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
    markdown = []
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
            ast.parse(cell_out)
            parses = True
        except SyntaxError:
            cell_out = f'{code.pop()}\n{cell_out}'

    # Skip cells ending in semi-colon
    if cell_out.rstrip().endswith(';'):
        code.append(cell_out)
        return code

    # Remove code comments
    if '#' in cell_out:
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
    code.append(f"""
_pn__state._cell_outputs[{cell_id!r}].append(({cell_out}))
for _cell__out in _CELL__DISPLAY:
    _pn__state._cell_outputs[{cell_id!r}].append(_cell__out)
_CELL__DISPLAY.clear()
_fig__out = _get__figure()
if _fig__out:
    _pn__state._cell_outputs[{cell_id!r}].append(_fig__out)
""")
    return code


class MarkdownHandler(CodeHandler):
    ''' Modify Bokeh documents by creating Dashboard from a Markdown file.

    '''

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


class NotebookHandler(CodeHandler):
    ''' Modify Bokeh documents by creating Dashboard from a notebook file.

    '''

    _imports = [
        'from panel import state as _pn__state',
        'from panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n'
    ]

    def __init__(self, *, filename: PathLike, argv: list[str] = [], package: ModuleType | None = None) -> None:
        '''

        Keywords:
            filename (str) : a path to a Jupyter notebook (".ipynb") file

        '''
        self._load_layout(filename)
        super().__init__(source=self._parse(filename), filename=filename)
        self._stale = False

    def _parse(self, filename):
        nbformat = import_required('nbformat', 'The Bokeh notebook application handler requires Jupyter Notebook to be installed.')
        nbconvert = import_required('nbconvert', 'The Bokeh notebook application handler requires Jupyter Notebook to be installed.')

        class StripMagicsProcessor(nbconvert.preprocessors.Preprocessor):
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

        code = list(self._imports)
        for cell in nb['cells']:
            cell_id = cell['id']
            state._cell_layouts[self][cell_id] = cell['metadata'].get('panel-layout', {})
            if cell['cell_type'] == 'code':
                cell_code = capture_code_cell(cell)
                code += cell_code
            elif cell['cell_type'] == 'markdown':
                md = ''.join(cell['source'])
                code.append(f'_pn__state._cell_outputs[{cell_id!r}].append("""{md}""")')
        code = '\n'.join(code)

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

    def modify_document(self, doc: Document) -> None:
        ''' Run Bokeh application code to update a ``Document``

        Args:
            doc (Document) : a ``Document`` to update

        '''
        path = self._runner._path
        if self._stale:
            self._load_layout(path)
            source = self._parse(path)
            nodes = ast.parse(source, os.fspath(path))
            self._runner._code = compile(nodes, filename=path, mode='exec', dont_inherit=True)
            self._stale = False

        module = self._runner.new_module()

        # If no module was returned it means the code runner has some permanent
        # unfixable problem, e.g. the configured source code has a syntax error
        if module is None:
            return

        # One reason modules are stored is to prevent the module from being gc'd
        # before the document is. A symptom of a gc'd module is that its globals
        # become None. Additionally stored modules are used to provide correct
        # paths to custom models resolver.
        doc.modules.add(module)

        with _monkeypatch_io(self._loggers):
            with patch_curdoc(doc):
                from ..config import config
                from ..layout import Column
                from .state import state

                with set_env_vars(MPLBACKEND='agg'):
                    self._runner.run(module, self._make_post_doc_check(doc))

                if doc.roots or doc in state._templates:
                    state._cell_outputs.clear()
                    return

                # If no contents we add all cell outputs to the editable template
                config.template = 'editable'
                persist = state._jupyter_kernel_context
                editable = 'editable' in state.session_args
                if not (editable or persist):
                    state.template.editable = False
                state.template.title = os.path.basename(path)

                layouts, outputs, cells = {}, {}, {}
                for cell_id, out in state._cell_outputs.items():
                    spec = state._cell_layouts[self].get(cell_id, {})
                    if 'width' in spec and 'height' in spec:
                        sizing_mode = 'stretch_both'
                    else:
                        sizing_mode = 'stretch_width'
                    pout = Column(
                        *(o for o in out if o is not None),
                        sizing_mode=sizing_mode
                    )
                    for po in pout:
                        po.sizing_mode = sizing_mode
                    outputs[cell_id] = pout
                    layouts[id(pout)] = state._cell_layouts[self][cell_id]
                    cells[cell_id] = id(pout)
                    pout.servable()

                # Reorder outputs based on notebook metadata
                import nbformat
                nb = nbformat.read(self._runner._path, nbformat.NO_CONVERT)
                ordered = {}
                for cell_id in nb['metadata'].get('panel-cell-order', []):
                    if cell_id not in cells:
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
                state.template.layout = ordered
                if persist:
                    state.template.param.watch(self._update_position_metadata, 'layout')
                state._session_outputs[doc] = outputs
                state._cell_outputs.clear()

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


def build_single_handler_application(path, argv=None):
    if not os.path.isfile(path) or not path.endswith((".md", ".ipynb")):
        return _build_application(path, argv)

    from .server import Application
    code_handler = NotebookHandler if path.endswith('.ipynb') else MarkdownHandler
    handler = code_handler(filename=path)
    if handler.failed:
        raise RuntimeError("Error loading %s:\n\n%s\n%s " % (path, handler.error, handler.error_detail))

    application = Application(handler)

    return application

bokeh.command.util.build_single_handler_application = build_single_handler_application
