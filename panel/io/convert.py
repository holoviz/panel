from __future__ import annotations

import ast
import dataclasses
import os

from textwrap import dedent
from typing import List, Literal, Optional

from bokeh.application.application import SessionContext
from bokeh.command.util import build_single_handler_application
from bokeh.core.json_encoder import serialize_json
from bokeh.core.templates import FILE, MACROS, _env
from bokeh.document import Document
from bokeh.embed.elements import script_for_render_items
from bokeh.embed.util import RenderItem, standalone_docs_json_and_render_items
from bokeh.embed.wrappers import wrap_in_script_tag
from bokeh.settings import settings as _settings
from bokeh.util.serialization import make_id

from .. import __version__, config
from ..util import escape
from .resources import bundle_resources, Resources
from .state import state, set_curdoc

PYSCRIPT_CSS = '<link rel="stylesheet" href="https://pyscript.net/alpha/pyscript.css" />'
PYSCRIPT_JS = '<script defer src="https://pyscript.net/alpha/pyscript.js"></script>'
PYODIDE_JS = '<script src="https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js"></script>'

PRE = """
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()
"""

POST = """
await write_doc()
"""

PYODIDE_SCRIPT = """
<script type="text/javascript">
async function main() {
  let pyodide = await loadPyodide();
  await pyodide.loadPackage("micropip");
  await pyodide.runPythonAsync(`
    import micropip
    await micropip.install({{ env_spec }});
  `);
  code = `{{ code }}`
  await pyodide.runPythonAsync(code);
}
main();
</script>
"""

@dataclasses.dataclass
class Request:
    headers : dict
    cookies : dict
    arguments : dict


class MockSessionContext(SessionContext):

    def __init__(self, *args, document=None, **kwargs):
        self._document = document
        super().__init__(*args, server_context=None, session_id=None, **kwargs)

    def with_locked_document(self, *args):
        return

    @property
    def destroyed(self) -> bool:
        return False

    @property
    def request(self):
        return Request(headers={}, cookies={}, arguments={})


def find_imports(code: str) -> List[str]:
    """
    Finds the imports in a string of code.

    Parameters
    ----------
    code : str
       the Python code to run.

    Returns
    -------
    ``List[str]``
        A list of module names that are imported in the code.

    Examples
    --------
    >>> code = "import numpy as np; import scipy.stats"
    >>> find_imports(code)
    ['numpy', 'scipy']
    """
    # handle mis-indented input from multi-line strings
    code = dedent(code)

    mod = ast.parse(code)
    imports = set()
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            for name in node.names:
                node_name = name.name
                imports.add(node_name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            if module_name is None:
                continue
            imports.add(module_name.split(".")[0])
    return list(sorted(imports))


def script_to_html(
    filename: str, requirements: Literal['auto'] | List[str] = 'auto',
    js_resources: List[str] = 'auto', css_resources: List[str] = 'auto',
    runtime: Literal['pyodide', 'pyscript'] = 'pyscript', prerender=True
) -> str:
    """
    Converts a Panel or Bokeh script to a standalone WASM Python
    application.

    Arguments
    ---------
    filename : str
      The filename of the Panel/Bokeh application to convert
    requirements: 'auto' | list(str)
      The list of requirements to include (in addition to Panel).
    
    """
    # Configure resources
    _settings.resources.set_value('cdn')

    # Run script
    app = build_single_handler_application(os.path.abspath(filename))
    document = Document()
    document._session_context = lambda: MockSessionContext(document=document)
    with set_curdoc(document):
        app.initialize_document(document)
        state._on_load(None)
    source = app._handlers[0]._runner.source

    if requirements == 'auto':
        requirements = find_imports(source)

    # Environment
    pn_version = '.'.join(__version__.split('.')[:3])
    reqs = [f'panel=={pn_version}'] + [req for req in requirements if req != 'panel']

    # Execution
    code = '\n'.join([PRE, source, POST])
    if runtime == 'pyscript':
        if js_resources == 'auto':
            js_resources = [PYSCRIPT_JS]
        if css_resources == 'auto':
            css_resources = [PYSCRIPT_CSS]
        pyenv = '\n'.join([f'- {req}' for req in reqs])
        plot_script = f'<py-env>\n{pyenv}\n</py-env>\n<py-script>{code}</py-script>'
    else:
        if js_resources == 'auto':
            js_resources = [PYODIDE_JS]
        if css_resources == 'auto':
            css_resources = []
        script_template = _env.from_string(PYODIDE_SCRIPT)
        plot_script = script_template.render({
            'env_spec': ', '.join([repr(req) for req in reqs]),
            'code': code.replace('`', '\`')
        })

    if prerender:
        json_id = make_id()
        docs_json, render_items = standalone_docs_json_and_render_items(document)
        render_item = render_items[0]
        json = escape(serialize_json(docs_json), quote=False)
        plot_script += wrap_in_script_tag(json, "application/json", json_id)
        plot_script += wrap_in_script_tag(script_for_render_items(json_id, render_items))
    else:
        render_item = RenderItem(
            token = '',
            roots = document.roots,
            use_for_title = False
        )
        render_items = [render_item]

    # Collect resources
    resources = Resources(mode='cdn')
    bokeh_js, bokeh_css = bundle_resources(document.roots, resources)
    bokeh_js = '\n'.join([bokeh_js]+js_resources)
    bokeh_css = '\n'.join([bokeh_css]+css_resources)

    # Configure template
    template = document.template
    template_variables = document._template_variables
    context = template_variables.copy()
    context.update(dict(
        title = document.title,
        bokeh_js = bokeh_js,
        bokeh_css = bokeh_css,
        plot_script = plot_script,
        docs = render_items,
        base = FILE,
        macros = MACROS,
        doc = render_item,
        roots = render_item.roots
    ))

    # Render
    if template is None:
        template = FILE
    elif isinstance(template, str):
        template = _env.from_string("{% extends base %}\n" + template)
    html = template.render(context)
    html = (html
        .replace('<body>', f'<body class="bk pn-loading {config.loading_spinner}">')
    )

    _settings.resources.unset_value()
    return html
