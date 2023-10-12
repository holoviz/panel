from __future__ import annotations

import concurrent.futures
import dataclasses
import os
import pathlib
import uuid

from typing import (
    IO, Any, Dict, List,
)

import bokeh

from bokeh.application.application import Application, SessionContext
from bokeh.application.handlers.code import CodeHandler
from bokeh.core.json_encoder import serialize_json
from bokeh.core.templates import MACROS, get_env
from bokeh.document import Document
from bokeh.embed.elements import script_for_render_items
from bokeh.embed.util import RenderItem, standalone_docs_json_and_render_items
from bokeh.embed.wrappers import wrap_in_script_tag
from bokeh.util.serialization import make_id
from typing_extensions import Literal

from .. import __version__, config
from ..util import base_version, escape
from .loading import LOADING_INDICATOR_CSS_CLASS
from .markdown import build_single_handler_application
from .mime_render import find_imports
from .resources import (
    BASE_TEMPLATE, CDN_DIST, DIST_DIR, INDEX_TEMPLATE, Resources,
    _env as _pn_env, bundle_resources, loading_css, set_resource_mode,
)
from .state import set_curdoc, state

PWA_MANIFEST_TEMPLATE = _pn_env.get_template('site.webmanifest')
SERVICE_WORKER_TEMPLATE = _pn_env.get_template('serviceWorker.js')
WEB_WORKER_TEMPLATE = _pn_env.get_template('pyodide_worker.js')
WORKER_HANDLER_TEMPLATE  = _pn_env.get_template('pyodide_handler.js')

PANEL_ROOT = pathlib.Path(__file__).parent.parent
BOKEH_VERSION = base_version(bokeh.__version__)
PY_VERSION = base_version(__version__)
PYODIDE_VERSION = 'v0.23.4'
PYSCRIPT_VERSION = '2023.03.1'
PANEL_LOCAL_WHL = DIST_DIR / 'wheels' / f'panel-{__version__.replace("-dirty", "")}-py3-none-any.whl'
BOKEH_LOCAL_WHL = DIST_DIR / 'wheels' / f'bokeh-{BOKEH_VERSION}-py3-none-any.whl'
PANEL_CDN_WHL = f'{CDN_DIST}wheels/panel-{PY_VERSION}-py3-none-any.whl'
BOKEH_CDN_WHL = f'{CDN_DIST}wheels/bokeh-{BOKEH_VERSION}-py3-none-any.whl'
PYODIDE_URL = f'https://cdn.jsdelivr.net/pyodide/{PYODIDE_VERSION}/full/pyodide.js'
PYODIDE_PYC_URL = f'https://cdn.jsdelivr.net/pyodide/{PYODIDE_VERSION}/pyc/pyodide.js'
PYSCRIPT_CSS = f'<link rel="stylesheet" href="https://pyscript.net/releases/{PYSCRIPT_VERSION}/pyscript.css" />'
PYSCRIPT_JS = f'<script defer src="https://pyscript.net/releases/{PYSCRIPT_VERSION}/pyscript.js"></script>'
PYODIDE_JS = f'<script src="{PYODIDE_URL}"></script>'
PYODIDE_PYC_JS = f'<script src="{PYODIDE_URL}"></script>'

MINIMUM_VERSIONS = {}

ICON_DIR = DIST_DIR / 'images'
PWA_IMAGES = [
    ICON_DIR / 'favicon.ico',
    ICON_DIR / 'icon-vector.svg',
    ICON_DIR / 'icon-32x32.png',
    ICON_DIR / 'icon-192x192.png',
    ICON_DIR / 'icon-512x512.png',
    ICON_DIR / 'apple-touch-icon.png',
    ICON_DIR / 'index_background.png'
]

Runtimes = Literal['pyodide', 'pyscript', 'pyodide-worker']

PRE = """
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()
"""

POST = """
await write_doc()"""

POST_PYSCRIPT = """
asyncio.ensure_future(write_doc());"""

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

INIT_SERVICE_WORKER = """
<script type="text/javascript">
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./serviceWorker.js').then(reg => {
    reg.onupdatefound = () => {
      const installingWorker = reg.installing;
      installingWorker.onstatechange = () => {
        if (installingWorker.state === 'installed' &&
            navigator.serviceWorker.controller) {
          // Reload page if service worker is replaced
          location.reload();
        }
      }
    }
  })
}
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



def make_index(files, title=None, manifest=True):
    if manifest:
        manifest = 'site.webmanifest'
        favicon = 'images/favicon.ico'
        apple_icon = 'images/apple-touch-icon.png'
    else:
        manifest = favicon = apple_icon = None
    items = {label: './'+os.path.basename(f) for label, f in sorted(files.items())}
    return INDEX_TEMPLATE.render(
        items=items, manifest=manifest, apple_icon=apple_icon,
        favicon=favicon, title=title, PANEL_CDN=CDN_DIST
    )

def build_pwa_manifest(files, title=None, **kwargs):
    if len(files) > 1:
        title = title or 'Panel Applications'
        path = 'index.html'
    else:
        title = title or 'Panel Applications'
        path = list(files.values())[0]
    return PWA_MANIFEST_TEMPLATE.render(
        name=title,
        path=path,
        **kwargs
    )

def script_to_html(
    filename: str | os.PathLike | IO,
    requirements: Literal['auto'] | List[str] = 'auto',
    js_resources: Literal['auto'] | List[str] = 'auto',
    css_resources: Literal['auto'] | List[str] | None = None,
    runtime: Runtimes = 'pyodide',
    prerender: bool = True,
    panel_version: Literal['auto', 'local'] | str = 'auto',
    manifest: str | None = None,
    http_patch: bool = True,
    inline: bool = False,
    compiled: bool = True
) -> str:
    """
    Converts a Panel or Bokeh script to a standalone WASM Python
    application.

    Arguments
    ---------
    filename: str | Path | IO
        The filename of the Panel/Bokeh application to convert.
    requirements: 'auto' | List[str]
        The list of requirements to include (in addition to Panel).
    js_resources: 'auto' | List[str]
        The list of JS resources to include in the exported HTML.
    css_resources: 'auto' | List[str] | None
        The list of CSS resources to include in the exported HTML.
    runtime: 'pyodide' | 'pyscript'
        The runtime to use for running Python in the browser.
    prerender: bool
        Whether to pre-render the components so the page loads.
    panel_version: 'auto' | str
        The panel release version to use in the exported HTML.
    http_patch: bool
        Whether to patch the HTTP request stack with the pyodide-http library
        to allow urllib3 and requests to work.
    inline: bool
        Whether to inline resources.
    compiled: bool
        Whether to use pre-compiled pyodide bundles.
    """
    # Run script
    if hasattr(filename, 'read'):
        handler = CodeHandler(source=filename.read(), filename='convert.py')
        app_name = f'app-{str(uuid.uuid4())}'
        app = Application(handler)
    else:
        path = pathlib.Path(filename)
        app_name = '.'.join(path.name.split('.')[:-1])
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
    elif isinstance(requirements, str) and pathlib.Path(requirements).is_file():
        requirements = pathlib.Path(requirements).read_text(encoding='utf-8').splitlines()
        try:
            from packaging.requirements import Requirement
            requirements = [
                r2 for r in requirements
                if (r2 := r.split("#")[0].strip()) and Requirement(r2)
            ]
        except Exception as e:
            raise ValueError(
                f'Requirements parser raised following error: {e}'
            )

    # Environment
    if panel_version == 'local':
        panel_req = './' + str(PANEL_LOCAL_WHL.as_posix()).split('/')[-1]
        bokeh_req = './' + str(BOKEH_LOCAL_WHL.as_posix()).split('/')[-1]
    elif panel_version == 'auto':
        panel_req = PANEL_CDN_WHL
        bokeh_req = BOKEH_CDN_WHL
    else:
        panel_req = f'panel=={panel_version}'
        bokeh_req = f'bokeh=={BOKEH_VERSION}'
    base_reqs = [bokeh_req, panel_req]
    if http_patch:
        base_reqs.append('pyodide-http==0.2.1')
    reqs = base_reqs + [
        req for req in requirements if req not in ('panel', 'bokeh')
    ]
    for name, min_version in MINIMUM_VERSIONS.items():
        if any(name in req for req in reqs):
            reqs = [f'{name}>={min_version}' if name in req else req for req in reqs]

    # Execution
    post_code = POST_PYSCRIPT if runtime == 'pyscript' else POST
    code = '\n'.join([PRE, source, post_code])
    web_worker = None
    if css_resources is None:
        css_resources = []
    if runtime == 'pyscript':
        if js_resources == 'auto':
            js_resources = [PYSCRIPT_JS]
        css_resources = []
        if css_resources == 'auto':
            css_resources = [PYSCRIPT_CSS]
        pyenv = ','.join([repr(req) for req in reqs])
        plot_script = f'<py-config>\npackages = [{pyenv}]\n</py-config>\n<py-script>{code}</py-script>'
    else:
        if css_resources == 'auto':
            css_resources = []
        env_spec = ', '.join([repr(req) for req in reqs])
        code = code.replace('`', '\`').replace('\\n', r'\\n')
        if runtime == 'pyodide-worker':
            if js_resources == 'auto':
                js_resources = []
            worker_handler = WORKER_HANDLER_TEMPLATE.render({
                'name': app_name,
                'loading_spinner': config.loading_spinner
            })
            web_worker = WEB_WORKER_TEMPLATE.render({
                'PYODIDE_URL': PYODIDE_PYC_URL if compiled else PYODIDE_URL,
                'env_spec': env_spec,
                'code': code
            })
            plot_script = wrap_in_script_tag(worker_handler)
        else:
            if js_resources == 'auto':
                js_resources = [PYODIDE_PYC_JS if compiled else PYODIDE_JS]
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
    resources = Resources(mode='inline' if inline else 'cdn')
    loading_base = (DIST_DIR / "css" / "loading.css").read_text(encoding='utf-8')
    spinner_css = loading_css(
        config.loading_spinner, config.loading_color, config.loading_max_height
    )
    css_resources.append(
        f'<style type="text/css">\n{loading_base}\n{spinner_css}\n</style>'
    )
    with set_curdoc(document):
        bokeh_js, bokeh_css = bundle_resources(document.roots, resources)
    extra_js = [INIT_SERVICE_WORKER, bokeh_js] if manifest else [bokeh_js]
    bokeh_js = '\n'.join(js_resources+extra_js)
    bokeh_css = '\n'.join([bokeh_css]+css_resources)

    # Configure template
    template = document.template
    template_variables = document._template_variables
    context = template_variables.copy()
    context.update(dict(
        title=document.title,
        bokeh_js=bokeh_js,
        bokeh_css=bokeh_css,
        plot_script=plot_script,
        docs=render_items,
        base=BASE_TEMPLATE,
        macros=MACROS,
        doc=render_item,
        roots=render_item.roots,
        manifest=manifest,
        dist_url=CDN_DIST
    ))

    # Render
    if template is None:
        template = BASE_TEMPLATE
    elif isinstance(template, str):
        template = get_env().from_string("{% extends base %}\n" + template)
    html = template.render(context)
    html = (html
        .replace('<body>', f'<body class="{LOADING_INDICATOR_CSS_CLASS} pn-{config.loading_spinner}">')
    )
    return html, web_worker


def convert_app(
    app: str | os.PathLike,
    dest_path: str | os.PathLike | None = None,
    requirements: List[str] | Literal['auto'] | os.PathLike = 'auto',
    runtime: Runtimes = 'pyodide-worker',
    prerender: bool = True,
    manifest: str | None = None,
    panel_version: Literal['auto', 'local'] | str = 'auto',
    http_patch: bool = True,
    inline: bool = False,
    verbose: bool = True,
):
    if dest_path is None:
        dest_path = pathlib.Path('./')
    elif not isinstance(dest_path, pathlib.PurePath):
        dest_path = pathlib.Path(dest_path)

    try:
        with set_resource_mode('inline' if inline else 'cdn'):
            html, js_worker = script_to_html(
                app, requirements=requirements, runtime=runtime,
                prerender=prerender, manifest=manifest,
                panel_version=panel_version, http_patch=http_patch,
                inline=inline
            )
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f'Failed to convert {app} to {runtime} target: {e}')
        return
    name = '.'.join(os.path.basename(app).split('.')[:-1])
    filename = f'{name}.html'

    with open(dest_path / filename, 'w', encoding="utf-8") as out:
        out.write(html)
    if runtime == 'pyodide-worker':
        with open(dest_path / f'{name}.js', 'w', encoding="utf-8") as out:
            out.write(js_worker)
    if verbose:
        print(f'Successfully converted {app} to {runtime} target and wrote output to {filename}.')
    return (name.replace('_', ' '), filename)


def _convert_process_pool(
    apps: List[str],
    dest_path: str | None = None,
    max_workers: int = 4,
    requirements: List[str] | Literal['auto'] | os.PathLike = 'auto',
    **kwargs
):
    import multiprocessing as mp

    from concurrent.futures import ProcessPoolExecutor

    files = {}
    groups = [apps[i:i+max_workers] for i in range(0, len(apps), max_workers)]
    for group in groups:
        with ProcessPoolExecutor(
                max_workers=max_workers, mp_context=mp.get_context('spawn')
        ) as executor:
            futures = []
            for app in group:
                if isinstance(requirements, dict):
                    app_requires = requirements.get(app, 'auto')
                else:
                    app_requires = requirements
                f = executor.submit(
                    convert_app, app, dest_path, requirements=app_requires, **kwargs
                )
                futures.append(f)
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    name, filename = result
                    files[name] = filename
    return files

def convert_apps(
    apps: str | os.PathLike | List[str | os.PathLike],
    dest_path: str | os.PathLike | None = None,
    title: str | None = None,
    runtime: Runtimes = 'pyodide-worker',
    requirements: List[str] | Literal['auto'] | os.PathLike = 'auto',
    prerender: bool = True,
    build_index: bool = True,
    build_pwa: bool = True,
    pwa_config: Dict[Any, Any] = {},
    max_workers: int = 4,
    panel_version: Literal['auto', 'local'] | str = 'auto',
    http_patch: bool = True,
    inline: bool = False,
    verbose: bool = True,
):
    """
    Arguments
    ---------
    apps: str | List[str]
        The filename(s) of the Panel/Bokeh application(s) to convert.
    dest_path: str | pathlib.Path
        The directory to write the converted application(s) to.
    title: str | None
        A title for the application(s). Also used to generate unique
        name for the application cache to ensure.
    runtime: 'pyodide' | 'pyscript' | 'pyodide-worker'
        The runtime to use for running Python in the browser.
    requirements: 'auto' | List[str] | os.PathLike | Dict[str, 'auto' | List[str] | os.PathLike]
        The list of requirements to include (in addition to Panel).
        By default automatically infers dependencies from imports
        in the application. May also provide path to a requirements.txt
    prerender: bool
        Whether to pre-render the components so the page loads.
    build_index: bool
        Whether to write an index page (if there are multiple apps).
    build_pwa: bool
        Whether to write files to define a progressive web app (PWA) including
        a manifest and a service worker that caches the application locally
    pwa_config: Dict[Any, Any]
        Configuration for the PWA including (see https://developer.mozilla.org/en-US/docs/Web/Manifest)

          - display: Display options ('fullscreen', 'standalone', 'minimal-ui' 'browser')
          - orientation: Preferred orientation
          - background_color: The background color of the splash screen
          - theme_color: The theme color of the application
    max_workers: int
        The maximum number of parallel workers
    panel_version: 'auto' | 'local'] | str
'       The panel version to include.
    http_patch: bool
        Whether to patch the HTTP request stack with the pyodide-http library
        to allow urllib3 and requests to work.
    inline: bool
        Whether to inline resources.
    """
    if isinstance(apps, str):
        apps = [apps]
    if dest_path is None:
        dest_path = pathlib.Path('./')
    elif not isinstance(dest_path, pathlib.PurePath):
        dest_path = pathlib.Path(dest_path)
    dest_path.mkdir(parents=True, exist_ok=True)

    manifest = 'site.webmanifest' if build_pwa else None

    if isinstance(requirements, dict):
        app_requirements = {}
        for app in apps:
            matches = [
                deps for name, deps in requirements.items()
                if app.endswith(name.replace(os.path.sep, '/'))
            ]
            app_requirements[app] = matches[0] if matches else 'auto'
    else:
        app_requirements = requirements

    kwargs = {
        'requirements': app_requirements, 'runtime': runtime,
        'prerender': prerender, 'manifest': manifest,
        'panel_version': panel_version, 'http_patch': http_patch,
        'inline': inline, 'verbose': verbose
    }

    if state._is_pyodide:
        files = dict((convert_app(app, dest_path, **kwargs) for app in apps))
    else:
        files = _convert_process_pool(
            apps, dest_path, max_workers=max_workers, **kwargs
        )

    if build_index and len(files) >= 1:
        index = make_index(files, manifest=build_pwa, title=title)
        with open(dest_path / 'index.html', 'w') as f:
            f.write(index)
        if verbose:
            print('Successfully wrote index.html.')

    if not build_pwa:
        return

    # Write icons
    imgs_path = (dest_path / 'images')
    imgs_path.mkdir(exist_ok=True)
    img_rel = []
    for img in PWA_IMAGES:
        with open(imgs_path / img.name, 'wb') as f:
            f.write(img.read_bytes())
        img_rel.append(f'images/{img.name}')
    if verbose:
        print('Successfully wrote icons and images.')

    # Write manifest
    manifest = build_pwa_manifest(files, title=title, **pwa_config)
    with open(dest_path / 'site.webmanifest', 'w', encoding="utf-8") as f:
        f.write(manifest)
    if verbose:
        print('Successfully wrote site.manifest.')

    # Write service worker
    worker = SERVICE_WORKER_TEMPLATE.render(
        uuid=uuid.uuid4().hex,
        name=title or 'Panel Pyodide App',
        pre_cache=', '.join([repr(p) for p in img_rel])
    )
    with open(dest_path / 'serviceWorker.js', 'w', encoding="utf-8") as f:
        f.write(worker)
    if verbose:
        print('Successfully wrote serviceWorker.js.')
