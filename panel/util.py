from __future__ import absolute_import, division, unicode_literals

import re
import os
import io
import json
import sys
import inspect
import numbers
import hashlib
import threading
import textwrap

from collections import defaultdict, MutableSequence, MutableMapping, OrderedDict
from contextlib import contextmanager
from datetime import datetime
from six import string_types

import param
import bokeh
import bokeh.embed.notebook

from bokeh.document import Document
from bokeh.io.notebook import load_notebook as bk_load_notebook
from bokeh.models import Model, LayoutDOM, Box
from bokeh.protocol import Protocol
from bokeh.resources import CDN, INLINE
from bokeh.util.string import encode_utf8
from pyviz_comms import (PYVIZ_PROXY, JupyterCommManager, bokeh_msg_handler,
                         nb_mime_js, embed_js)

# Global variables
CUSTOM_MODELS = {}
BLOCKED = False

if sys.version_info.major > 2:
    unicode = str


def load_compiled_models(custom_model, implementation):
    """
    Custom hook to load cached implementation of custom models.
    """
    compiled = old_hook(custom_model, implementation)
    if compiled is not None:
        return compiled

    model = CUSTOM_MODELS.get(custom_model.full_name)
    if model is None:
        return
    ts_file = model.__implementation__
    json_file = ts_file.replace('.ts', '.json')
    if not os.path.isfile(json_file):
        return
    with io.open(ts_file, encoding="utf-8") as f:
        code = f.read()
    with io.open(json_file, encoding="utf-8") as f:
        compiled = json.load(f)
    hashed = hashlib.sha256(code.encode('utf-8')).hexdigest()
    if compiled['hash'] == hashed:
        return AttrDict(compiled)
    return None


try:
    from bokeh.util.compiler import AttrDict, get_cache_hook, set_cache_hook
    old_hook = get_cache_hook()
    set_cache_hook(load_compiled_models)
except:
    pass


def hashable(x):
    if isinstance(x, MutableSequence):
        return tuple(x)
    elif isinstance(x, MutableMapping):
        return tuple([(k,v) for k,v in x.items()])
    else:
        return x


def as_unicode(obj):
    """
    Safely casts any object to unicode including regular string
    (i.e. bytes) types in python 2.
    """
    if sys.version_info.major < 3 and isinstance(obj, str):
        obj = obj.decode('utf-8')
    return unicode(obj)


def param_name(name):
    """
    Removes the integer id from a Parameterized class name.
    """
    match = re.match('(.)+(\d){5}', name)
    return name[:-5] if match else name


def unicode_repr(obj):
    """
    Returns a repr without the unicode prefix.
    """
    if sys.version_info.major == 2 and isinstance(obj, unicode):
        return repr(obj)[1:]
    return repr(obj)


def abbreviated_repr(value, max_length=25, natural_breaks=(',', ' ')):
    """
    Returns an abbreviated repr for the supplied object. Attempts to
    find a natural break point while adhering to the maximum length.
    """
    vrepr = repr(value)
    if len(vrepr) > max_length:
        # Attempt to find natural cutoff point
        abbrev = vrepr[max_length//2:]
        natural_break = None
        for brk in natural_breaks:
            if brk in abbrev:
                natural_break = abbrev.index(brk) + max_length//2
                break
        if natural_break and natural_break < max_length:
            max_length = natural_break + 1

        end_char = ''
        if isinstance(value, list):
            end_char = ']'
        elif isinstance(value, OrderedDict):
            end_char = '])'
        elif isinstance(value, (dict, set)):
            end_char = '}'
        return vrepr[:max_length+1] + '...' + end_char
    return vrepr


def param_reprs(parameterized, skip=[]):
    """
    Returns a list of reprs for parameters on the parameterized object.
    Skips default and empty values.
    """
    cls = type(parameterized).__name__
    param_reprs = []
    for p, v in sorted(parameterized.get_param_values()):
        if v is parameterized.param[p].default: continue
        elif v is None: continue
        elif isinstance(v, string_types) and v == '': continue
        elif isinstance(v, list) and v == []: continue
        elif isinstance(v, dict) and v == {}: continue
        elif p in skip or (p == 'name' and v.startswith(cls)): continue
        param_reprs.append('%s=%s' % (p, abbreviated_repr(v)))
    return param_reprs


def full_groupby(l, key=lambda x: x):
    """
    Groupby implementation which does not require a prior sort
    """
    d = defaultdict(list)
    for item in l:
        d[key(item)].append(item)
    return d.items()


def get_method_owner(meth):
    """
    Returns the instance owning the supplied instancemethod or
    the class owning the supplied classmethod.
    """
    if inspect.ismethod(meth):
        if sys.version_info < (3,0):
            return meth.im_class if meth.im_self is None else meth.im_self
        else:
            return meth.__self__


def is_parameterized(obj):
    """
    Whether an object is a Parameterized class or instance.
    """
    return (isinstance(obj, param.Parameterized) or
            (isinstance(obj, type) and issubclass(obj, param.Parameterized)))


def value_as_datetime(value):
    """
    Retrieve the value tuple as a tuple of datetime objects.
    """
    if isinstance(value, numbers.Number):
        value = datetime.utcfromtimestamp(value / 1000)
    return value




class StoppableThread(threading.Thread):
    """Thread class with a stop() method."""

    def __init__(self, io_loop=None, timeout=1000, **kwargs):
        from tornado import ioloop
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_event = threading.Event()
        self.io_loop = io_loop
        self._cb = ioloop.PeriodicCallback(self._check_stopped, timeout)
        self._cb.start()

    def _check_stopped(self):
        if self.stopped:
            self._cb.stop()
            self.io_loop.stop()

    def stop(self):
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()


################################
# Display and update utilities #
################################


def diff(doc, binary=True, events=None):
    """
    Returns a json diff required to update an existing plot with
    the latest plot data.
    """
    events = list(doc._held_events) if events is None else events
    if not events or BLOCKED:
        return None
    msg = Protocol("1.0").create("PATCH-DOC", events, use_buffers=binary)
    doc._held_events = [e for e in doc._held_events if e not in events]
    return msg


@contextmanager
def block_comm():
    """
    Context manager to temporarily block comm push
    """
    global BLOCKED
    BLOCKED = True
    yield
    BLOCKED = False


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


LOAD_MIME = 'application/vnd.holoviews_load.v0+json'
EXEC_MIME = 'application/vnd.holoviews_exec.v0+json'
HTML_MIME = 'text/html'


def load_notebook(inline=True):
    from IPython.display import publish_display_data

    # Create a message for the logo (if shown)
    LOAD_MIME_TYPE = bokeh.io.notebook.LOAD_MIME_TYPE
    bokeh.io.notebook.LOAD_MIME_TYPE = LOAD_MIME
    bk_load_notebook(hide_banner=True, resources=INLINE if inline else CDN)
    bokeh.io.notebook.LOAD_MIME_TYPE = LOAD_MIME_TYPE
    bokeh.io.notebook.curstate().output_notebook()

    # Publish comm manager
    JS = '\n'.join([PYVIZ_PROXY, JupyterCommManager.js_manager, nb_mime_js])
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

    target = model.ref['id']

    # Publish plot HTML
    bokeh_script, bokeh_div, _ = bokeh.embed.notebook.notebook_content(model)
    html = "<div id='{id}'>{html}</div>".format(id=target, html=encode_utf8(bokeh_div))

    # Publish bokeh plot JS
    msg_handler = bokeh_msg_handler.format(plot_id=target)
    comm_js = comm.js_template.format(plot_id=target, comm_id=comm.id, msg_handler=msg_handler)
    bokeh_js = '\n'.join([comm_js, bokeh_script])
    bokeh_js = embed_js.format(widget_id=target, plot_id=target, html=html) + bokeh_js

    data = {EXEC_MIME: '', 'text/html': html, 'application/javascript': bokeh_js}
    metadata = {EXEC_MIME: {'id': target}}
    return data, metadata


def bokeh_repr(obj, depth=0, ignored=['children', 'text', 'name', 'toolbar', 'renderers', 'below', 'center', 'left', 'right']):
    from .viewable import Viewable
    if isinstance(obj, Viewable):
        obj = obj._get_root(Document())

    r = ""
    cls = type(obj).__name__
    properties = sorted(obj.properties_with_values(False).items())
    props = []
    for k, v in properties:
        if k in ignored:
            continue
        if isinstance(v, Model):
            v = '%s()' % type(v).__name__
        else:
            v = repr(v)
        if len(v) > 30:
            v = v[:30] + '...'
        props.append('%s=%s' % (k, v))
    props = ', '.join(props)
    if isinstance(obj, Box):
        r += '{cls}(children=[\n'.format(cls=cls)
        for obj in obj.children:
            r += textwrap.indent(bokeh_repr(obj, depth=depth+1) + ',\n', '  ')
        r += '], %s)' % props
    else:
        r += '{cls}({props})'.format(cls=cls,  props=props)
    return r
