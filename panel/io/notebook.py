"""
Various utilities for loading JS dependencies and rendering plots
inside the Jupyter notebook.
"""
import json
import uuid
import sys

from contextlib import contextmanager
from collections import OrderedDict
from six import string_types

import bokeh
import bokeh.embed.notebook

from bokeh.core.json_encoder import serialize_json
from bokeh.core.templates import MACROS
from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.embed.elements import div_for_render_item, script_for_render_items
from bokeh.embed.util import standalone_docs_json_and_render_items
from bokeh.embed.wrappers import wrap_in_script_tag
from bokeh.models import LayoutDOM, Model
from bokeh.resources import CDN, INLINE
from bokeh.settings import settings, _Unset
from bokeh.util.serialization import make_id
from pyviz_comms import (
    PYVIZ_PROXY, Comm, JupyterCommManager as _JupyterCommManager, nb_mime_js
)

try:
    from bokeh.util.string import escape
except Exception:
    from html import escape

from ..compiler import require_components
from .embed import embed_state
from .model import add_to_doc, diff
from .resources import Bundle, Resources, _env, bundle_resources
from .server import _server_url, _origin_url, get_server
from .state import state


#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

LOAD_MIME = 'application/vnd.holoviews_load.v0+json'
EXEC_MIME = 'application/vnd.holoviews_exec.v0+json'
HTML_MIME = 'text/html'

def _jupyter_server_extension_paths():
    return [{"module": "panel.io.jupyter_server_extension"}]


def push(doc, comm, binary=True):
    """
    Pushes events stored on the document across the provided comm.
    """
    msg = diff(doc, binary=binary)
    if msg is None:
        return
    comm.send(msg.header_json)
    comm.send(msg.metadata_json)
    comm.send(msg.content_json)
    for header, payload in msg.buffers:
        comm.send(json.dumps(header))
        comm.send(buffers=[payload])


def push_on_root(ref):
    if ref not in state._views:
        return
    (self, root, doc, comm) = state._views[ref]
    if comm and 'embedded' not in root.tags:
        push(doc, comm)


def push_notebook(*objs):
    """
    A utility for pushing updates to the frontend given a Panel
    object.  This is required when modifying any Bokeh object directly
    in a notebook session.

    Arguments
    ---------
    objs: panel.viewable.Viewable
    """
    for obj in objs:
        for ref in obj._models:
            push_on_root(ref)


DOC_NB_JS = _env.get_template("doc_nb_js.js")
AUTOLOAD_NB_JS = _env.get_template("autoload_panel_js.js")
NB_TEMPLATE_BASE = _env.get_template('nb_template.html')

def _autoload_js(bundle, configs, requirements, exports, skip_imports, ipywidget, load_timeout=5000):
    config = {'packages': {}, 'paths': {}, 'shim': {}}
    for conf in configs:
        for key, c in conf.items():
            config[key].update(c)
    return AUTOLOAD_NB_JS.render(
        bundle    = bundle,
        force     = True,
        timeout   = load_timeout,
        config    = config,
        requirements = requirements,
        exports   = exports,
        skip_imports = skip_imports,
        ipywidget = ipywidget
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
    elif isinstance(template, string_types):
        template = _env.from_string("{% extends base %}\n" + template)

    return template.render(context)


def render_template(document, comm=None, manager=None):
    ref = document.roots[0].ref['id']
    (docs_json, render_items) = standalone_docs_json_and_render_items(document, True)

    # We do not want the CommManager to appear in the roots because
    # the custom template may not reference it
    if manager:
        item = render_items[0]
        item.roots._roots = OrderedDict(list(item.roots._roots.items())[:-1])

    html = html_for_render_items(
        docs_json, render_items, template=document.template,
        template_variables=document.template_variables
    )
    return ({'text/html': html, EXEC_MIME: ''}, {EXEC_MIME: {'id': ref}})


def render_model(model, comm=None):
    if not isinstance(model, Model):
        raise ValueError("notebook_content expects a single Model instance")
    from ..config import panel_extension as pnext

    target = model.ref['id']

    (docs_json, [render_item]) = standalone_docs_json_and_render_items([model], True)
    div = div_for_render_item(render_item)
    render_item = render_item.to_json()
    requirements = [pnext._globals[ext] for ext in pnext._loaded_extensions
                    if ext in pnext._globals]
    ipywidget = 'ipywidgets_bokeh' in sys.modules

    script = DOC_NB_JS.render(
        docs_json=serialize_json(docs_json),
        render_items=serialize_json([render_item]),
        requirements=requirements,
        ipywidget=ipywidget
    )
    bokeh_script, bokeh_div = script, div
    html = "<div id='{id}'>{html}</div>".format(id=target, html=bokeh_div)

    data = {'text/html': html, 'application/javascript': bokeh_script}
    return ({'text/html': mimebundle_to_html(data), EXEC_MIME: ''},
            {EXEC_MIME: {'id': target}})


def render_mimebundle(model, doc, comm, manager=None, location=None):
    """
    Displays bokeh output inside a notebook using the PyViz display
    and comms machinery.
    """
    if not isinstance(model, LayoutDOM):
        raise ValueError('Can only render bokeh LayoutDOM models')
    add_to_doc(model, doc, True)
    if manager is not None:
        doc.add_root(manager)
    if location is not None:
        loc = location._get_model(doc, model, model, comm)
        doc.add_root(loc)
    return render_model(model, comm)


def mimebundle_to_html(bundle):
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
        html += '\n<script type="application/javascript">{js}</script>'.format(js=js)
    return html

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------


@contextmanager
def block_comm():
    """
    Context manager to temporarily block comm push
    """
    state._hold = True
    try:
        yield
    finally:
        state._hold = False


def load_notebook(inline=True, load_timeout=5000):
    from IPython.display import publish_display_data

    resources = INLINE if inline else CDN
    prev_resources = settings.resources(default="server")
    user_resources = settings.resources._user_value is not _Unset
    resources = Resources.from_bokeh(resources)
    try:
        bundle = bundle_resources(None, resources)
        bundle = Bundle.from_bokeh(bundle)
        configs, requirements, exports, skip_imports = require_components()
        ipywidget = 'ipywidgets_bokeh' in sys.modules
        bokeh_js = _autoload_js(bundle, configs, requirements, exports,
                                skip_imports, ipywidget, load_timeout)
    finally:
        if user_resources:
            settings.resources = prev_resources
        else:
            settings.resources.unset_value()

    publish_display_data({
        'application/javascript': bokeh_js,
        LOAD_MIME: bokeh_js,
    })
    bokeh.io.notebook.curstate().output_notebook()

    # Publish comm manager
    JS = '\n'.join([PYVIZ_PROXY, _JupyterCommManager.js_manager, nb_mime_js])
    publish_display_data(data={LOAD_MIME: JS, 'application/javascript': JS})


def show_server(panel, notebook_url, port):
    """
    Displays a bokeh server inline in the notebook.

    Arguments
    ---------
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

    if callable(notebook_url):
        origin = notebook_url(None)
    else:
        origin = _origin_url(notebook_url)
    server_id = uuid.uuid4().hex
    server = get_server(panel, port=port, websocket_origin=origin,
                        start=True, show=False, server_id=server_id)

    if callable(notebook_url):
        url = notebook_url(server.port)
    else:
        url = _server_url(notebook_url, server.port)

    script = server_document(url, resources=None)

    publish_display_data({
        HTML_MIME: script,
        EXEC_MIME: ""
    }, metadata={
        EXEC_MIME: {"server_id": server_id}
    })
    return server


def show_embed(panel, max_states=1000, max_opts=3, json=False,
               json_prefix='', save_path='./', load_path=None,
               progress=True, states={}):
    """
    Renders a static version of a panel in a notebook by evaluating
    the set of states defined by the widgets in the model. Note
    this will only work well for simple apps with a relatively
    small state space.

    Arguments
    ---------
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
    from IPython.display import publish_display_data
    from ..config import config

    doc = Document()
    comm = Comm()
    with config.set(embed=True):
        model = panel.get_root(doc, comm)
        embed_state(panel, model, doc, max_states, max_opts,
                    json, json_prefix, save_path, load_path, progress,
                    states)
    publish_display_data(*render_model(model))


def ipywidget(obj, **kwargs):
    """
    Creates a root model from the Panel object and wraps it in
    a jupyter_bokeh ipywidget BokehModel.

    Arguments
    ---------
    obj: object
      Any Panel object or object which can be rendered with Panel
    **kwargs: dict
      Keyword arguments passed to the pn.panel utility function

    Returns
    -------
    Returns an ipywidget model which renders the Panel object.
    """
    from jupyter_bokeh.widgets   import BokehModel
    from ..pane import panel
    model = panel(obj, **kwargs).get_root()
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
                new_model = obj.get_root()
                widget.update_from_model(new_model)
                current[:] = [new_model]
        widget.observe(view_count_changed, '_view_count')
    return widget
