from __future__ import annotations

import ast
import json
import logging
import os
import re

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

log = logging.get_logger('panel.io.handlers')

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

def extract_cells(
    filehandle: IO, supported_syntax: tuple[str, ...] = ('{pyodide}', 'python')
) -> str:
    notebook = json.loads(filehandle.read())
    code = ['import panel as pn', "pn.extension(template='interact')"]
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            if not len(cell['source']):
                continue
            for line in cell['source'][:-1]:
                code.append(line)
            cell_out = cell['source'][-1]
            if not cell_out.rstrip().endswith(';') and not cell_out.startswith('import '):
                code.append(f'pn.panel({cell_out}).servable()')
            else:
                code.append(cell_out)
    return '\n'.join(code)

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

    def __init__(self, *, filename: PathLike, argv: list[str] = [], package: ModuleType | None = None) -> None:
        '''

        Keywords:
            filename (str) : a path to a Jupyter notebook (".ipynb") file

        '''
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

        with open(filename, encoding="utf-8") as f:
            nb_string = nbformat.read(f, nbformat.NO_CONVERT)
        exporter = nbconvert.NotebookExporter()

        for preprocessor in preprocessors:
            exporter.register_preprocessor(preprocessor)

        nb_string, _ = exporter.from_notebook_node(nb_string)
        nb = json.loads(nb_string)

        cell_count = 0
        code = ['from panel import state as _pn_state']
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                if not len(cell['source']):
                    continue
                for line in cell['source'][:-1]:
                    line = (line
                        .replace('get_ipython().run_line_magic', '')
                        .replace('get_ipython().magic', '')
                    )
                    code.append(line)
                cell_out = cell['source'][-1]
                if not cell_out.rstrip().endswith(';'):
                    try:
                        ast.parse(cell_out, mode='eval')
                        code.append(f'_cell_out__{cell_count} = {cell_out}')
                        code.append(f'_pn_state._cell_outputs.append(_cell_out__{cell_count})')
                    except SyntaxError:
                        code.append(cell_out)
                else:
                    code.append(cell_out)
        code = '\n'.join(code)
        super().__init__(source=code, filename=filename)

    def modify_document(self, doc: Document) -> None:
        ''' Run Bokeh application code to update a ``Document``

        Args:
            doc (Document) : a ``Document`` to update

        '''

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
                self._runner.run(module, self._make_post_doc_check(doc))
                if not doc.roots:
                    from ..config import panel_extension
                    from ..pane import panel
                    from .state import state
                    panel_extension(template='interact')
                    state.template.title = os.path.basename(self._runner._path)
                    for out in state._cell_outputs:
                        panel(out).servable()
                state._cell_outputs.clear()


def build_single_handler_application(path, argv=None):
    if not os.path.isfile(path) and not (path.endswith(".md") or path.endswith(".ipynb")):
        return _build_application(path, argv)

    from .server import Application
    code_handler = NotebookHandler if path.endswith('.ipynb') else MarkdownHandler
    handler = code_handler(filename=path)
    if handler.failed:
        raise RuntimeError("Error loading %s:\n\n%s\n%s " % (path, handler.error, handler.error_detail))

    application = Application(handler)

    return application

bokeh.command.util.build_single_handler_application = build_single_handler_application
