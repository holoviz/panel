from __future__ import annotations

import ast
import dataclasses
import os
import pathlib
import pkgutil
import sys

from textwrap import dedent
from typing import List

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
from typing_extensions import Literal

from .. import __version__, config
from ..util import escape
from .resources import (
    INDEX_TEMPLATE, Resources, _env as _pn_env, bundle_resources,
)
from .state import set_curdoc, state

WEB_WORKER_TEMPLATE = _pn_env.get_template('pyodide_worker.js')

PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.21.0/full/pyodide.js'
PYSCRIPT_CSS = '<link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />'
PYSCRIPT_JS = '<script defer src="https://pyscript.net/latest/pyscript.js"></script>'
PYODIDE_JS = f'<script src="{PYODIDE_URL}"></script>'

def _stdlibs():
    env_dir = str(pathlib.Path(sys.executable).parent.parent)
    modules = list(sys.builtin_module_names)
    for m in pkgutil.iter_modules():
        mpath = m.module_finder.path
        if mpath.startswith(env_dir) and not 'site-packages' in mpath:
            modules.append(m.name)
    return modules

_STDLIBS = _stdlibs()
_PACKAGE_MAP = {
    'sklearn': 'scikit-learn'
}

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
    await micropip.install([{{ env_spec }}]);
  `);
  code = `{{ code }}`
  await pyodide.runPythonAsync(code);
}
main();
</script>
"""

PYODIDE_WORKER_SCRIPT = """
<script type="text/javascript">
const pyodideWorker = new Worker("./{{ name }}.js");

function send_change(jsdoc, event) {
  if (event.setter_id != null)
    return
  const patch = jsdoc.create_json_patch_string([event])
  pyodideWorker.postMessage({type: 'patch', patch: patch})
}

pyodideWorker.onmessage = async (event) => {
  if (event.data.type === 'render') {
    const docs_json = JSON.parse(event.data.docs_json)
    const render_items = JSON.parse(event.data.render_items)
    const root_ids = JSON.parse(event.data.root_ids)

    // Remap roots in message to element IDs
    const root_els = document.getElementsByClassName('bk-root')
    const data_roots = []
    for (const el of root_els) {
       el.innerHTML = ''
       data_roots.push([parseInt(el.getAttribute('data-root-id')), el.id])
    }
    data_roots.sort((a, b) => a[0]<b[0] ? -1: 1)
    const roots = {}
    for (let i=0; i<data_roots.length; i++) {
      roots[root_ids[i]] = data_roots[i][1]
    }
    render_items[0]['roots'] = roots
    render_items[0]['root_ids'] = root_ids

    // Embed content
    const [views] = await Bokeh.embed.embed_items(docs_json, render_items)

    // Remove loading spinner
    body = document.getElementsByTagName('body')[0]
    body.classList.remove("bk", "pn-loading")

    // Setup bi-directional syncing
    pyodideWorker.jsdoc = jsdoc = views[0].model.document
    jsdoc.on_change(send_change.bind(null, jsdoc), false)
    pyodideWorker.postMessage({'type': 'rendered'})
  } else if (event.data.type === 'patch') {
    pyodideWorker.jsdoc.apply_json_patch(JSON.parse(event.data.patch), event.data.buffers, setter_id='js')
  }
};
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

    packages = [_PACKAGE_MAP.get(pkg, pkg) for pkg in sorted(imports) if pkg not in _STDLIBS]
    if 'bokeh.sampledata' in code and 'pandas' not in packages:
        packages.append('pandas')
    return packages


def make_index(files):
    items = ['/'+os.path.basename(f) for f in files]
    return INDEX_TEMPLATE.render({'items': items})


def script_to_html(
    filename: str,
    requirements: Literal['auto'] | List[str] = 'auto',
    js_resources: Literal['auto'] | List[str] = 'auto',
    css_resources: Literal['auto'] | List[str] | None = None,
    runtime: Literal['pyodide', 'pyscript'] = 'pyscript',
    prerender: bool = True,
    panel_version: Literal['auto'] | str = 'auto',
) -> str:
    """
    Converts a Panel or Bokeh script to a standalone WASM Python
    application.

    Arguments
    ---------
    filename : str
      The filename of the Panel/Bokeh application to convert.
    requirements: 'auto' | List[str]
      The list of requirements to include (in addition to Panel).
    js_resources: 'auto' | List[str]
      The list of JS resources to include in the exported HTML.
    css_resources: 'auto' | List[str] | None
      The list of CSS resources to include in the exported HTML.
    runtime: 'pyodide' | 'pyscript' | 'pwa'
      The runtime to use for running Python in the browser.
    prerender: bool
      Whether to pre-render the components so the page loads.
    panel_version: 'auto' | str
      The panel release version to use in the exported HTML.
    """
    # Configure resources
    _settings.resources.set_value('cdn')

    # Run script
    path = pathlib.Path(filename)
    name = '.'.join(path.name.split('.')[:-1])
    app = build_single_handler_application(str(path.absolute()))
    document = Document()
    document._session_context = lambda: MockSessionContext(document=document)
    with set_curdoc(document):
        app.initialize_document(document)
        state._on_load(None)
    source = app._handlers[0]._runner.source

    if not document.roots:
        raise RuntimeError(
            f'The file {filename} does not publish any Panel contents. '
            'Ensure you have marked items as servable or added models to '
            'the bokeh document manually.'
        )

    if requirements == 'auto':
        requirements = find_imports(source)

    # Environment
    if panel_version == 'auto':
        panel_version = '.'.join(__version__.split('.')[:3])
    reqs = [f'panel-lite=={panel_version}'] + [
        req for req in requirements if req != 'panel'
    ]

    # Execution
    code = '\n'.join([PRE, source, POST])
    web_worker = None
    if css_resources is None:
        css_resources = []
    if runtime == 'pyscript':
        if js_resources == 'auto':
            js_resources = [PYSCRIPT_JS]
        css_resources = []
        if css_resources == 'auto':
            css_resources = [PYSCRIPT_CSS]
        pyenv = '\n'.join([f'- {req}' for req in reqs])
        plot_script = f'<py-env>\n{pyenv}\n</py-env>\n<py-script>{code}</py-script>'
    else:
        if css_resources == 'auto':
            css_resources = []
        env_spec = ', '.join([repr(req) for req in reqs])
        code = code.replace('`', '\`').replace('\\n', r'\\n')
        if runtime == 'pyodide-worker':
            if js_resources == 'auto':
                js_resources = []
            script_template = _pn_env.from_string(PYODIDE_WORKER_SCRIPT)
            plot_script = script_template.render({
                'name': name
            })
            web_worker = WEB_WORKER_TEMPLATE.render({
                'PYODIDE_URL': PYODIDE_URL,
                'env_spec': env_spec,
                'code': code
            })
        else:
            if js_resources == 'auto':
                js_resources = [PYODIDE_JS]
            script_template = _pn_env.from_string(PYODIDE_SCRIPT)
            plot_script = script_template.render({
                'env_spec': env_spec,
                'code': code
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
    return html, web_worker
