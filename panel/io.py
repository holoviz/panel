"""
The io module defines utilities for loading the notebook extension
and holding global state.
"""
from __future__ import absolute_import, division, unicode_literals

import json
import os
import sys
import uuid

from collections import defaultdict
from contextlib import contextmanager
from itertools import product

import param
import bokeh
import bokeh.embed.notebook

from bokeh.document import Document
from bokeh.core.templates import DOC_NB_JS
from bokeh.core.json_encoder import serialize_json
from bokeh.embed.elements import div_for_render_item
from bokeh.embed.util import standalone_docs_json_and_render_items
from bokeh.io.notebook import load_notebook as bk_load_notebook
from bokeh.models import CustomJS, LayoutDOM, Model
from bokeh.protocol import Protocol
from bokeh.resources import CDN, INLINE
from bokeh.util.string import encode_utf8
from pyviz_comms import (
    CommManager as _CommManager, JupyterCommManager as _JupyterCommManager,
    extension as _pyviz_extension, PYVIZ_PROXY, bokeh_msg_handler,
    nb_mime_js, embed_js)


#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

class _config(param.Parameterized):
    """
    Holds global configuration options for Panel. The options can be
    set directly on the global config instance, via keyword arguments
    in the extension or via environment variables. For example to set
    the embed option the following approaches can be used:

        pn.config.embed = True

        pn.extension(embed=True)

        os.environ['PANEL_EMBED'] = 'True'
    """

    _embed = param.Boolean(default=False, allow_None=True, doc="""
        Whether plot data will be embedded.""")

    _embed_json = param.Boolean(default=False, doc="""
        Whether to save embedded state to json files.""")

    _embed_save_path = param.String(default='./', doc="""
        Where to save json files for embedded state.""")

    _embed_load_path = param.String(default=None, doc="""
        Where to load json files for embedded state.""")

    _inline = param.Boolean(default=True, allow_None=True, doc="""
        Whether to inline JS and CSS resources.
        If disabled, resources are loaded from CDN if one is available.""")

    _truthy = ['True', 'true', '1', True, 1]

    @contextmanager
    def set(self, **kwargs):
        values = [(k, v) for k, v in self.param.get_param_values() if k != 'name']
        for k, v in kwargs.items():
            setattr(self, k, v)
        try:
            yield
        finally:
            self.set_param(**dict(values))

    @property
    def embed(self):
        if self._embed is not None:
            return self._embed
        else:
            return os.environ.get('PANEL_EMBED', _config._embed) in self._truthy

    @embed.setter
    def embed(self, value):
        self._embed = value

    @property
    def embed_json(self):
        if self._embed_json is not None:
            return self._embed_json
        else:
            return os.environ.get('PANEL_EMBED_JSON', _config._embed_json) in self._truthy

    @embed_json.setter
    def embed_json(self, value):
        self._embed_json = value

    @property
    def embed_save_path(self):
        if self._embed_save_path is not None:
            return self._embed_save_path
        else:
            return os.environ.get('PANEL_EMBED_SAVE_PATH', _config._embed_save_path) in self._truthy

    @embed_save_path.setter
    def embed_save_path(self, value):
        self._embed_save_path = value

    @property
    def embed_load_path(self):
        if self._embed_load_path is not None:
            return self._embed_load_path
        else:
            return os.environ.get('PANEL_EMBED_LOAD_PATH', _config._embed_load_path) in self._truthy

    @embed_load_path.setter
    def embed_load_path(self, value):
        self._embed_load_path = value

    @property
    def inline(self):
        if self._inline is not None:
            return self._inline
        else:
            return os.environ.get('PANEL_INLINE', _config._inline) in self._truthy

    @inline.setter
    def inline(self, value):
        self._inline = value

_params = _config.param.objects() if hasattr(_config.param, 'objects') else _config.params()
config = _config(**{k: None if p.allow_None else getattr(_config, k)
                    for k, p in _params.items() if k != 'name'})


class state(param.Parameterized):
    """
    Holds global state associated with running apps, allowing running
    apps to indicate their state to a user.
    """

    curdoc = param.ClassSelector(class_=Document, doc="""
        The bokeh Document for which a server event is currently being
        processed.""")

    # Whether to hold comm events
    _hold = False
    
    _comm_manager = _CommManager

    # An index of all currently active views
    _views = {}

    # An index of all curently active servers
    _servers = {}


class panel_extension(_pyviz_extension):
    """
    Initializes the pyviz notebook extension to allow plotting with
    bokeh and enable comms.
    """

    _loaded = False

    _imports = {'katex': 'panel.models.katex',
                'mathjax': 'panel.models.mathjax',
                'plotly': 'panel.models.plotly',
                'vega': 'panel.models.vega'}

    def __call__(self, *args, **params):
        # Abort if IPython not found
        for arg in args:
            if arg not in self._imports:
                self.param.warning('%s extension not recognized and '
                                   'will be skipped.' % arg)
            else:
                __import__(self._imports[arg])

        try:
            ip = params.pop('ip', None) or get_ipython() # noqa (get_ipython)
        except:
            return

        for k, v in params.items():
            setattr(config, k, v)

        if hasattr(ip, 'kernel') and not self._loaded:
            # TODO: JLab extension and pyviz_comms should be changed
            #       to allow multiple cleanup comms to be registered
            _JupyterCommManager.get_client_comm(self._process_comm_msg,
                                                "hv-extension-comm")
        load_notebook(config.inline)
        self._loaded = True

        state._comm_manager = _JupyterCommManager

        if 'holoviews' in sys.modules:
            import holoviews as hv
            if hv.extension._loaded:
                return
            import holoviews.plotting.bokeh # noqa
            if hasattr(hv.Store, 'set_current_backend'):
                hv.Store.set_current_backend('bokeh')
            else:
                hv.Store.current_backend = 'bokeh'


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

STATE_JS = """
var state = null
for (var root of cb_obj.document.roots()) {{
  if (root.id == '{id}') {{
    state = root;
    break;
  }}
}}
if (!state) {{ return; }}
state.set_state(cb_obj, {js_getter})
"""


def diff(doc, binary=True, events=None):
    """
    Returns a json diff required to update an existing plot with
    the latest plot data.
    """
    events = list(doc._held_events) if events is None else events
    if not events or state._hold:
        return None
    msg = Protocol("1.0").create("PATCH-DOC", events, use_buffers=binary)
    doc._held_events = [e for e in doc._held_events if e not in events]
    return msg


@contextmanager
def block_comm():
    """
    Context manager to temporarily block comm push
    """
    state._hold = True
    yield
    state._hold = False


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


def remove_root(obj, replace=None):
    """
    Removes the document from any previously displayed bokeh object
    """
    for model in obj.select({'type': Model}):
        prev_doc = model.document
        model._document = None
        if prev_doc:
            prev_doc.remove_root(model)
        if replace:
            model._document = replace


def add_to_doc(obj, doc, hold=False):
    """
    Adds a model to the supplied Document removing it from any existing Documents.
    """
    # Add new root
    remove_root(obj)
    doc.add_root(obj)
    if doc._hold is None and hold:
        doc.hold()


def record_events(doc):
    msg = diff(doc, False)
    if msg is None:
        return {'header': '{}', 'metadata': '{}', 'content': '{}'}
    return {'header': msg.header_json, 'metadata': msg.metadata_json,
            'content': msg.content_json}


def embed_state(panel, model, doc, max_states=1000, max_opts=3,
                json=False, save_path='./', load_path=None):
    """
    Embeds the state of the application on a State model which allows
    exporting a static version of an app. This works by finding all
    widgets with a predefined set of options and evaluating the cross
    product of the widget values and recording the resulting events to
    be replayed when exported. The state is recorded on a State model
    which is attached as an additional root on the Document.

    Parameters
    ----------
    panel: panel.viewable.Reactive
      The Reactive component being exported
    model: bokeh.model.Model
      The bokeh model being exported
    doc: bokeh.document.Document
      The bokeh Document being exported
    max_states: int (default=1000)
      The maximum number of states to export
    max_opts: int (default=3)
      The maximum number of options for a single widget
    json: boolean (default=True)
      Whether to export the data to json files
    save_path: str (default='./')
      The path to save json files to
    load_path: str (default=None)
      The path or URL the json files will be loaded from.
    """
    from .models.state import State
    from .widgets import Widget, DiscreteSlider

    target = model.ref['id']
    _, _, _, comm = state._views[target]

    model.tags.append('embedded')
    widgets = [w for w in panel.select(Widget) if w._supports_embed]
    state_model = State()

    values = []
    for w in widgets:
        w, w_model, vals, getter, on_change, js_getter = w._get_embed_state(model, max_opts)
        if isinstance(w, DiscreteSlider):
            w_model = w._composite[1]._models[target][0].select_one({'type': w._widget_type})
        else:
            w_model = w._models[target][0].select_one({'type': w._widget_type})
        js_callback = CustomJS(code=STATE_JS.format(
            id=state_model.ref['id'], js_getter=js_getter))
        w_model.js_on_change(on_change, js_callback)
        values.append((w, w_model, vals, getter))

    add_to_doc(model, doc, True)
    doc._held_events = []

    restore = [w.value for w, _, _, _ in values]
    init_vals = [g(m) for _, m, _, g in values]
    cross_product = list(product(*[vals[::-1] for _, _, vals, _ in values]))

    if len(cross_product) > max_states:
        raise RuntimeError('The cross product of different application '
                           'states is too large to explore (N=%d), either reduce '
                           'the number of options on the widgets or increase '
                           'the max_states specified on static export.' %
                           len(cross_product))

    nested_dict = lambda: defaultdict(nested_dict)
    state_dict = nested_dict()
    for key in cross_product:
        sub_dict = state_dict
        skip = False
        for i, k in enumerate(key):
            w, m, _, g = values[i]
            try:
                w.value = k
            except:
                skip = True
                break
            sub_dict = sub_dict[g(m)]
        if skip:
            doc._held_events = []

        # Drop events originating from widgets being varied
        models = [v[1] for v in values]
        doc._held_events = [e for e in doc._held_events if e.model not in models]
        events = record_events(doc)
        if events:
            sub_dict.update(events)

    for (w, _, _, _), v in zip(values, restore):
        try:
            w.set_param(value=v)
        except:
            pass

    if json:
        random_dir = uuid.uuid4().hex
        save_path = os.path.join(save_path, random_dir)
        if load_path is not None:
            load_path = os.path.join(load_path, random_dir)
        state_dict = save_dict(state_dict, max_depth=len(widgets)-1,
                               save_path=save_path, load_path=load_path)

    state_model.update(json=json, state=state_dict, values=init_vals,
                       widgets={m.ref['id']: i for i, (_, m, _, _) in enumerate(values)})
    doc.add_root(state_model)


def save_dict(state, key=(), depth=0, max_depth=None, save_path='', load_path=None):
    filename_dict = {}
    for k, v in state.items():
        curkey = key+(k,)
        if depth < max_depth:
            filename_dict[k] = save_dict(v, curkey, depth+1, max_depth,
                                         save_path, load_path)
        else:
            filename = '_'.join([str(i) for i in curkey]) +'.json'
            filepath = os.path.join(save_path, filename)
            directory = os.path.dirname(filepath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(filepath, 'w') as f:
                json.dump(v, f)
            refpath = filepath
            if load_path:
                refpath = os.path.join(load_path, filename)
            filename_dict[k] = refpath
    return filename_dict


def load_notebook(inline=True):
    from IPython.display import publish_display_data

    # Create a message for the logo (if shown)
    LOAD_MIME_TYPE = bokeh.io.notebook.LOAD_MIME_TYPE
    bokeh.io.notebook.LOAD_MIME_TYPE = LOAD_MIME
    bk_load_notebook(hide_banner=True, resources=INLINE if inline else CDN)
    bokeh.io.notebook.LOAD_MIME_TYPE = LOAD_MIME_TYPE
    bokeh.io.notebook.curstate().output_notebook()

    # Publish comm manager
    JS = '\n'.join([PYVIZ_PROXY, _JupyterCommManager.js_manager, nb_mime_js])
    publish_display_data(data={LOAD_MIME: JS, 'application/javascript': JS})


def _origin_url(url):
    if url.startswith("http"):
        url = url.split("//")[1]
    return url

def _server_url(url, port):
    if url.startswith("http"):
        return '%s:%d%s' % (url.rsplit(':', 1)[0], port, "/")
    else:
        return 'http://%s:%d%s' % (url.split(':')[0], port, "/")


def show_server(server, notebook_url, server_id):
    """
    Displays a bokeh server inline in the notebook.

    Parameters
    ----------
    server: bokeh.server.server.Server
        Bokeh server instance which is already running
    notebook_url: str
        The URL of the running Jupyter notebook server
    server_id: str
        Unique ID to identify the server with
    """
    from bokeh.embed import server_document
    from IPython.display import publish_display_data

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
    bokeh_js = embed_js.format(widget_id=target, plot_id=target, html=bokeh_div) + bokeh_js

    data = {EXEC_MIME: '', 'text/html': html, 'application/javascript': bokeh_js}
    metadata = {EXEC_MIME: {'id': target}}
    return data, metadata


def _cleanup_panel(msg_id):
    """
    A cleanup action which is called when a plot is deleted in the notebook
    """
    if msg_id not in state._views:
        return
    viewable, model, _, _ = state._views.pop(msg_id)
    viewable._cleanup(model)


def _cleanup_server(server_id):
    """
    A cleanup action which is called when a server is deleted in the notebook
    """
    if server_id not in state._servers:
        return
    server, viewable, docs = state._servers.pop(server_id)
    server.stop()
    for doc in docs:
        for root in doc.roots:
            if root.ref['id'] in viewable._models:
                viewable._cleanup(root)


panel_extension.add_delete_action(_cleanup_panel)
if hasattr(panel_extension, 'add_server_delete_action'):
    panel_extension.add_server_delete_action(_cleanup_server)
