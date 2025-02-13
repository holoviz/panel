"""
Various utilities for loading JS dependencies and rendering plots
inside the Jupyter notebook.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
import warnings

from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING, Any, Literal

import bokeh
import bokeh.embed.notebook
import param

from bokeh.core.json_encoder import serialize_json
from bokeh.core.templates import MACROS
from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.embed.elements import div_for_render_item, script_for_render_items
from bokeh.embed.util import standalone_docs_json_and_render_items
from bokeh.embed.wrappers import wrap_in_script_tag
from bokeh.models import Model
from bokeh.resources import CDN, INLINE
from bokeh.settings import _Unset, settings
from bokeh.util.serialization import make_id
from param.display import (
    register_display_accessor, unregister_display_accessor,
)
from pyviz_comms import (
    PYVIZ_PROXY, Comm, JupyterCommJS,
    JupyterCommManager as _JupyterCommManager, nb_mime_js,
)

from ..util import escape
from .embed import embed_state
from .model import add_to_doc, diff
from .resources import (
    PANEL_DIR, Resources, _env, bundle_resources, patch_model_css,
)
from .state import state

if TYPE_CHECKING:
    from bokeh.protocol.message import Message
    from bokeh.server.server import Server
    from jinja2 import Template

    from ..models.comm_manager import CommManager
    from ..viewable import Viewable
    from ..widgets.base import Widget
    from .location import Location


#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

LOAD_MIME: str = 'application/vnd.holoviews_load.v0+json'
EXEC_MIME: str = 'application/vnd.holoviews_exec.v0+json'
HTML_MIME: str = 'text/html'

def _jupyter_server_extension_paths() -> list[dict[str, str]]:
    return [{"module": "panel.io.jupyter_server_extension"}]

def push(doc: Document, comm: Comm, binary: bool = True, msg: Message | None = None) -> None:
    """
    Pushes events stored on the document across the provided comm.
    """
    if msg is None:
        msg = diff(doc, binary=binary)
    if msg is None:
        return
    elif not comm._comm:
        try:
            from tornado.ioloop import IOLoop
            IOLoop.current().call_later(0.1, partial(push, doc, comm, binary, msg=msg))
        except Exception:
            warnings.warn(
                'Attempted to send message over Jupyter Comm but it was not '
                'yet open and also could not be rescheduled to a later time. '
                'The update will not be sent.', UserWarning, stacklevel=0
            )
    else:
        send(comm, msg)

def send(comm: Comm, msg: Message):
    """
    Sends a bokeh message across a pyviz_comms.Comm.
    """
    # WARNING: CommManager model assumes that either JSON content OR a buffer
    #          is sent. Therefore we must NEVER(!!!) send both at once.
    comm.send(msg.header_json)
    comm.send(msg.metadata_json)
    comm.send(msg.content_json)

    for buffer in msg.buffers:
        header = json.dumps(buffer.ref)
        payload = buffer.to_bytes()
        comm.send(header)
        comm.send(buffers=[payload])

def push_on_root(ref: str):
    if ref not in state._views:
        return
    (self, root, doc, comm) = state._views[ref]
    if comm and 'embedded' not in root.tags:
        push(doc, comm)

DOC_NB_JS: Template = _env.get_template("doc_nb_js.js")
AUTOLOAD_NB_JS: Template = _env.get_template("autoload_panel_js.js")
NB_TEMPLATE_BASE: Template = _env.get_template('nb_template.html')

def _autoload_js(
    *, bundle, configs, requirements, exports, skip_imports, ipywidget,
    reloading=False, load_timeout=5000
):
    config = {'packages': {}, 'paths': {}, 'shim': {}}
    for conf in configs:
        for key, c in conf.items():
            config[key].update(c)
    return AUTOLOAD_NB_JS.render(
        bundle    = bundle,
        force     = not reloading,
        reloading = reloading,
        timeout   = load_timeout,
        config    = config,
        requirements = requirements,
        exports   = exports,
        skip_imports = skip_imports,
        ipywidget = ipywidget,
        version = bokeh.__version__
    )

def html_for_render_items(docs_json, render_items, template=None, template_variables={}):
    json_id = make_id()
    json = escape(serialize_json(docs_json), quote=False)
    json = wrap_in_script_tag(json, "application/json", json_id)

    script = wrap_in_script_tag(script_for_render_items(json_id, render_items))

    context = template_variables.copy()

    context.update(dict(
        title = '',
        plot_script = json + script,
        docs = render_items,
        base = NB_TEMPLATE_BASE,
        macros = MACROS,
    ))

    if len(render_items) == 1:
        context["doc"] = context["docs"][0]
        context["roots"] = context["doc"].roots

    if template is None:
        template = NB_TEMPLATE_BASE
    elif isinstance(template, str):
        template = _env.from_string("{% extends base %}\n" + template)

    return template.render(context)

def render_template(
    document: Document, comm: Comm | None = None, manager: CommManager | None = None
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    ref = document.roots[0].ref['id']
    (docs_json, render_items) = standalone_docs_json_and_render_items(document, suppress_callback_warning=True)

    # We do not want the CommManager to appear in the roots because
    # the custom template may not reference it
    if manager:
        item = render_items[0]
        item.roots._roots = dict(list(item.roots._roots.items())[:-1])

    html = html_for_render_items(
        docs_json, render_items, template=document.template,
        template_variables=document.template_variables
    )
    return ({'text/html': html, EXEC_MIME: ''}, {EXEC_MIME: {'id': ref}})

def render_model(
    model: Model, comm: Comm | None = None, resources: str = 'cdn'
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    if not isinstance(model, Model):
        raise ValueError("notebook_content expects a single Model instance")
    from ..config import panel_extension as pnext

    target = model.ref['id']

    if not state._is_pyodide and resources == 'server':
        # ALERT: Replace with better approach before Bokeh 3.x compatible release
        dist_url = '/panel-preview/static/extensions/panel/'
        patch_model_css(model, dist_url=dist_url)
        if model.document:
            model.document._template_variables['dist_url'] = dist_url

    (docs_json, [render_item]) = standalone_docs_json_and_render_items([model], suppress_callback_warning=True)
    div = div_for_render_item(render_item)
    render_json = render_item.to_json()
    requirements = [pnext._globals[ext] for ext in pnext._loaded_extensions
                    if ext in pnext._globals]

    ipywidget = 'ipywidgets_bokeh' in sys.modules
    if not state._is_pyodide:
        ipywidget &= "PANEL_IPYWIDGET" in os.environ

    script = DOC_NB_JS.render(
        docs_json=serialize_json(docs_json),
        render_items=serialize_json([render_json]),
        requirements=requirements,
        ipywidget=ipywidget
    )
    bokeh_script, bokeh_div = script, div
    html = f"<div id='{target}'>{bokeh_div}</div>"

    data = {'text/html': html, 'application/javascript': bokeh_script}
    return ({'text/html': mimebundle_to_html(data), EXEC_MIME: ''},
            {EXEC_MIME: {'id': target}})


def mime_renderer(obj):
    """
    Generates a function that will render the supplied object as a
    mimebundle, e.g. to monkey-patch a _repr_mimebundle_ method onto
    an existing object.
    """
    from ..pane import panel
    def _repr_mimebundle_(include=None, exclude=None):
        return panel(obj)._repr_mimebundle_(include, exclude)
    return _repr_mimebundle_


def render_mimebundle(
    model: Model, doc: Document, comm: Comm,
    manager: CommManager | None = None,
    location: Location | None = None,
    resources: str = 'cdn'
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """
    Displays bokeh output inside a notebook using the PyViz display
    and comms machinery.
    """
    # WARNING: Patches the client comm created by some external library
    #          e.g. HoloViews, with an on_open handler that will initialize
    #          the server comm.
    if manager and manager.client_comm_id in _JupyterCommManager._comms:
        client_comm = _JupyterCommManager._comms[manager.client_comm_id]
        if not client_comm._on_open:
            client_comm._on_open = lambda _: comm.init()
    if not isinstance(model, Model):
        raise ValueError('Can only render bokeh LayoutDOM models')
    add_to_doc(model, doc, True)
    if manager is not None:
        doc.add_root(manager)
    if location is not None:
        loc = location._get_model(doc, model, model, comm)
        doc.add_root(loc)
    return render_model(model, comm, resources)


def mimebundle_to_html(bundle: dict[str, Any]) -> str:
    """
    Converts a MIME bundle into HTML.
    """
    if isinstance(bundle, tuple):
        data, metadata = bundle
    else:
        data = bundle
    html = data.get('text/html', '')
    if 'application/javascript' in data:
        js = data['application/javascript']
        html += f'\n<script type="application/javascript">{js}</script>'
    return html


def require_components():
    """
    Returns JS snippet to load the required dependencies in the classic
    notebook using REQUIRE JS.
    """
    from ..config import config

    configs, requirements, exports = [], [], {}
    js_requires = []

    for qual_name, model in Model.model_class_reverse_map.items():
        # We need to enable Models from Panel as well as Panel extensions
        # like awesome_panel_extensions.
        # The Bokeh models do not have "." in the qual_name
        if "." in qual_name:
            js_requires.append(model)

    from ..reactive import ReactiveHTML
    js_requires += list(param.concrete_descendents(ReactiveHTML).values())

    for export, js in config.js_files.items():
        name = js.split('/')[-1].replace('.min', '').split('.')[-2]
        conf = {'paths': {name: js[:-3]}, 'exports': {name: export}}
        js_requires.append(conf)

    skip_import = {}
    for model in js_requires:
        if not isinstance(model, dict) and issubclass(model, ReactiveHTML) and not model._loaded():
            continue

        if hasattr(model, '__js_skip__'):
            skip_import.update(model.__js_skip__)

        if not (hasattr(model, '__js_require__') or isinstance(model, dict)):
            continue

        if isinstance(model, dict):
            model_require = model
        else:
            model_require = dict(model.__js_require__)

        model_exports = model_require.pop('exports', {})
        if not any(model_require == config for config in configs):
            configs.append(model_require)

        for req in list(model_require.get('paths', [])):
            if isinstance(req, tuple):
                model_require['paths'] = dict(model_require['paths'])
                model_require['paths'][req[0]] = model_require['paths'].pop(req)

            reqs = req[1] if isinstance(req, tuple) else (req,)
            for r in reqs:
                if r not in requirements:
                    requirements.append(r)
                    if r in model_exports:
                        exports[r] = model_exports[r]

    return configs, requirements, exports, skip_import


class JupyterCommJSBinary(JupyterCommJS):
    """
    Extends pyviz_comms.JupyterCommJS with support for repacking
    binary buffers.
    """

    @classmethod
    def decode(cls, msg):
        buffers = {i: v for i, v in enumerate(msg['buffers'])}
        return dict(msg['content']['data'], _buffers=buffers)

class JupyterCommManagerBinary(_JupyterCommManager):

    client_comm = JupyterCommJSBinary


class Mimebundle:
    """
    Wraps a generated mimebundle.
    """
    def __init__(self, mimebundle):
        self._mimebundle = mimebundle

    def _repr_mimebundle_(self, include=None, exclude=None):
        return self._mimebundle

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def push_notebook(*objs: Viewable) -> None:
    """
    A utility for pushing updates to the frontend given a Panel
    object.  This is required when modifying any Bokeh object directly
    in a notebook session.

    Parameters
    ----------
    objs: panel.viewable.Viewable
    """
    for obj in objs:
        for ref in obj._models:
            push_on_root(ref)

@contextmanager
def block_comm() -> Iterator:
    """
    Context manager to temporarily block comm push
    """
    state._hold = True
    try:
        yield
    finally:
        state._hold = False

def load_notebook(
    inline: bool = True,
    reloading: bool = False,
    enable_mathjax: bool | Literal['auto'] = 'auto',
    load_timeout: int = 5000
) -> None:
    from IPython.display import publish_display_data

    resources = INLINE if inline and not state._is_pyodide else CDN
    prev_resources = settings.resources(default="server")
    user_resources = settings.resources._user_value is not _Unset
    nb_endpoint = not state._is_pyodide
    resources = Resources.from_bokeh(resources, notebook=nb_endpoint)
    try:
        bundle = bundle_resources(
            None, resources, notebook=nb_endpoint, reloading=reloading,
            enable_mathjax=enable_mathjax
        )
        configs, requirements, exports, skip_imports = require_components()
        ipywidget = 'ipywidgets_bokeh' in sys.modules
        bokeh_js = _autoload_js(
            bundle=bundle,
            configs=configs,
            requirements=requirements,
            exports=exports,
            skip_imports=skip_imports,
            ipywidget=ipywidget,
            reloading=reloading,
            load_timeout=load_timeout
        )
    finally:
        if user_resources:
            settings.resources = prev_resources
        else:
            settings.resources.unset_value()

    CSS = (PANEL_DIR / '_templates' / 'jupyter.css').read_text(encoding='utf-8')
    shim = '<script type="esms-options">{"shimMode": true}</script>'
    publish_display_data(data={'text/html': f'{shim}<style>{CSS}</style>'})
    publish_display_data({
        'application/javascript': bokeh_js,
        LOAD_MIME: bokeh_js,
    })
    bokeh.io.notebook.curstate().output_notebook()

    # Publish comm manager
    JS = '\n'.join([PYVIZ_PROXY, _JupyterCommManager.js_manager, nb_mime_js])
    publish_display_data(data={LOAD_MIME: JS, 'application/javascript': JS})


def show_server(panel: Any, notebook_url: str, port: int = 0) -> Server:
    """
    Displays a bokeh server inline in the notebook.

    Parameters
    ----------
    panel: Viewable
      Panel Viewable object to launch a server for
    notebook_url: str
      The URL of the running Jupyter notebook server
    port: int (optional, default=0)
      Allows specifying a specific port
    server_id: str
      Unique ID to identify the server with

    Returns
    -------
    server: bokeh.server.Server
    """
    from IPython.display import publish_display_data

    from .server import _origin_url, _server_url, get_server

    if callable(notebook_url):
        origin = notebook_url(None)
    else:
        origin = _origin_url(notebook_url)
    server_id = uuid.uuid4().hex
    server = get_server(
        panel, port=port, websocket_origin=origin, start=True, show=False,
        server_id=server_id
    )

    if callable(notebook_url):
        url = notebook_url(server.port)
    else:
        url = _server_url(notebook_url, server.port or port)

    script = server_document(url, resources=None)

    publish_display_data({
        HTML_MIME: script,
        EXEC_MIME: ""
    }, metadata={
        EXEC_MIME: {"server_id": server_id}
    })
    return server

def render_embed(
    panel, max_states: int = 1000, max_opts: int = 3, json: bool = False,
    json_prefix: str = '', save_path: str = './', load_path: str | None = None,
    progress: bool = True, states: dict[Widget, list[Any]] = {}
) -> Mimebundle:
    """
    Renders a static version of a panel in a notebook by evaluating
    the set of states defined by the widgets in the model. Note
    this will only work well for simple apps with a relatively
    small state space.

    Parameters
    ----------
    max_states: int
      The maximum number of states to embed
    max_opts: int
      The maximum number of states for a single widget
    json: boolean (default=True)
      Whether to export the data to json files
    json_prefix: str (default='')
      Prefix for JSON filename
    save_path: str (default='./')
      The path to save json files to
    load_path: str (default=None)
      The path or URL the json files will be loaded from.
    progress: boolean (default=False)
      Whether to report progress
    states: dict (default={})
      A dictionary specifying the widget values to embed for each widget
    """
    from ..config import config

    doc = Document()
    comm = Comm()
    with config.set(embed=True):
        model = panel.get_root(doc, comm)
        embed_state(panel, model, doc, max_states, max_opts,
                    json, json_prefix, save_path, load_path, progress,
                    states)
    return Mimebundle(render_model(model))

def show_embed(panel, *args, **kwargs):
    from IPython.display import publish_display_data
    return publish_display_data(render_embed(panel, *args, **kwargs))

def ipywidget(obj: Any, doc=None, **kwargs: Any):
    """
    Returns an ipywidget model which renders the Panel object.

    Requires `jupyter_bokeh` to be installed.

    Parameters
    ----------
    obj: object
      Any Panel object or object which can be rendered with Panel
    doc: bokeh.Document
        Bokeh document the bokeh model will be attached to.
    **kwargs: dict
      Keyword arguments passed to the pn.panel utility function

    Returns
    -------
    Returns an ipywidget model which renders the Panel object.
    """
    from jupyter_bokeh.widgets import BokehModel

    from ..pane import panel
    doc = doc if doc else Document()
    model = panel(obj, **kwargs).get_root(doc=doc)
    widget = BokehModel(model, combine_events=True)
    if hasattr(widget, '_view_count'):
        widget._view_count = 0
        def view_count_changed(change, current=[model]):
            new_model = None
            if change['old'] > 0 and change['new'] == 0 and current:
                try:
                    obj._cleanup(current[0])
                except Exception:
                    pass
                current[:] = []
            elif (change['old'] == 0 and change['new'] > 0 and
                  (not current or current[0] is not model)):
                if current:
                    try:
                        obj._cleanup(current[0])
                    except Exception:
                        pass
                new_model = obj.get_root(doc=widget._document)
                widget.update_from_model(new_model)
                current[:] = [new_model]
        widget.observe(view_count_changed, '_view_count')
    return widget


try:
    unregister_display_accessor('_ipython_display_')
except KeyError:
    pass

try:
    register_display_accessor('_repr_mimebundle_', mime_renderer)
except Exception:
    pass
