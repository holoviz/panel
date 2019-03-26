"""
Various utilities for loading JS dependencies and rendering plots
inside the Jupyter notebook.
"""
from __future__ import absolute_import, division, unicode_literals

import json
import os
import uuid

from contextlib import contextmanager

import bokeh
import bokeh.embed.notebook

from bokeh.core.templates import DOC_NB_JS
from bokeh.core.json_encoder import serialize_json
from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.embed.elements import div_for_render_item
from bokeh.embed.util import standalone_docs_json_and_render_items
from bokeh.models import CustomJS, LayoutDOM, Model
from bokeh.resources import CDN, INLINE
from bokeh.util.compiler import bundle_all_models
from bokeh.util.string import encode_utf8
from jinja2 import Environment, Markup, FileSystemLoader
from pyviz_comms import (
    JS_CALLBACK, PYVIZ_PROXY, Comm, JupyterCommManager as _JupyterCommManager,
    bokeh_msg_handler, nb_mime_js)

from ..compiler import require_components
from .embed import embed_state
from .model import add_to_doc, diff
from .server import _server_url, _origin_url, get_server
from .state import state


#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

LOAD_MIME = 'application/vnd.holoviews_load.v0+json'
EXEC_MIME = 'application/vnd.holoviews_exec.v0+json'
HTML_MIME = 'text/html'

ABORT_JS = """
if (!window.PyViz) {{
  return;
}}
var receiver = window.PyViz.receivers['{plot_id}'];
var events = receiver ? receiver._partial.content.events : [];
for (var event of events) {{
  if ((event.kind == 'ModelChanged') && (event.attr == '{change}') &&
      (cb_obj.id == event.model.id) &&
      (cb_obj['{change}'] == event.new)) {{
    events.pop(events.indexOf(event))
    return;
  }}
}}
"""

def get_comm_customjs(change, client_comm, plot_id, timeout=5000, debounce=50):
    """
    Returns a CustomJS callback that can be attached to send the
    model state across the notebook comms.
    """
    # Abort callback if value matches last received event
    abort = ABORT_JS.format(plot_id=plot_id, change=change)
    data_template = "data = {{{change}: cb_obj['{change}'], 'id': cb_obj.id}};"
    fetch_data = data_template.format(change=change)
    self_callback = JS_CALLBACK.format(
        comm_id=client_comm.id, timeout=timeout, debounce=debounce,
        plot_id=plot_id)
    return CustomJS(code='\n'.join([abort, fetch_data, self_callback]))



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


def get_env():
    ''' Get the correct Jinja2 Environment, also for frozen scripts.
    '''
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_templates'))
    return Environment(loader=FileSystemLoader(local_path))

_env = get_env()
_env.filters['json'] = lambda obj: Markup(json.dumps(obj))
AUTOLOAD_NB_JS = _env.get_template("autoload_panel_js.js")


def _autoload_js(resources, custom_models_js, configs, requirements, exports, load_timeout=5000):
    return AUTOLOAD_NB_JS.render(
        js_urls   = resources.js_files,
        css_urls  = resources.css_files,
        js_raw    = resources.js_raw + [custom_models_js],
        css_raw   = resources.css_raw_str,
        force     = True,
        timeout   = load_timeout,
        configs   = configs,
        requirements = requirements,
        exports   = exports
    )


def render_model(model, comm=None):
    if not isinstance(model, Model):
        raise ValueError("notebook_content expects a single Model instance")

    target = model.ref['id']

    (docs_json, [render_item]) = standalone_docs_json_and_render_items([model])
    div = div_for_render_item(render_item)
    render_item = render_item.to_json()
    script = DOC_NB_JS.render(
        docs_json=serialize_json(docs_json),
        render_items=serialize_json([render_item]),
    )
    bokeh_script, bokeh_div = encode_utf8(script), encode_utf8(div)
    html = "<div id='{id}'>{html}</div>".format(id=target, html=bokeh_div)

    # Publish bokeh plot JS
    msg_handler = bokeh_msg_handler.format(plot_id=target)

    if comm:
        comm_js = comm.js_template.format(plot_id=target, comm_id=comm.id, msg_handler=msg_handler)
        bokeh_js = '\n'.join([comm_js, bokeh_script])
    else:
        bokeh_js = bokeh_script

    data = {'text/html': html, 'application/javascript': bokeh_js}
    return ({'text/html': mimebundle_to_html(data), EXEC_MIME: ''},
            {EXEC_MIME: {'id': target}})


def render_mimebundle(model, doc, comm):
    """
    Displays bokeh output inside a notebook using the PyViz display
    and comms machinery.
    """
    if not isinstance(model, LayoutDOM):
        raise ValueError('Can only render bokeh LayoutDOM models')
    add_to_doc(model, doc, True)
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
    yield
    state._hold = False


def load_notebook(inline=True, load_timeout=5000):
    from IPython.display import publish_display_data

    resources = INLINE if inline else CDN
    custom_models_js = bundle_all_models() or ""

    configs, requirements, exports = require_components()
    bokeh_js = _autoload_js(resources, custom_models_js, configs,
                            requirements, exports, load_timeout)
    publish_display_data({
        'application/javascript': bokeh_js,
        LOAD_MIME : bokeh_js
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
    server = get_server(panel, port, origin, start=True, show=False,
                        server_id=server_id)

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
              save_path='./', load_path=None):
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
    save_path: str (default='./')
      The path to save json files to
    load_path: str (default=None)
      The path or URL the json files will be loaded from.
    """
    from IPython.display import publish_display_data
    from ..config import config

    doc = Document()
    comm = Comm()
    with config.set(embed=True):
        model = panel.get_root(doc, comm)
        embed_state(panel, model, doc, max_states, max_opts,
                    json, save_path, load_path)
    publish_display_data(*render_model(model))
