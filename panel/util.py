from __future__ import absolute_import

import json
import sys
import inspect
import numbers
from datetime import datetime
from contextlib import contextmanager

import param
import bokeh
import bokeh.embed.notebook
from bokeh.io.notebook import load_notebook as bk_load_notebook
from bokeh.models import Model, LayoutDOM, Div as BkDiv, WidgetBox as BkWidgetBox
from bokeh.protocol import Protocol
from bokeh.resources import CDN, INLINE
from bokeh.util.string import encode_utf8
from pyviz_comms import (PYVIZ_PROXY, JupyterCommManager, bokeh_msg_handler,
                         nb_mime_js, embed_js)

try:
    unicode = unicode # noqa
    basestring = basestring # noqa
except:
    basestring = unicode = str


def as_unicode(obj):
    """
    Safely casts any object to unicode including regular string
    (i.e. bytes) types in python 2.
    """
    if sys.version_info.major < 3 and isinstance(obj, str):
        obj = obj.decode('utf-8')
    return unicode(obj)


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


def value_as_datetime(value):
    """
    Retrieve the value tuple as a tuple of datetime objects.
    """
    if isinstance(value, numbers.Number):
        value = datetime.utcfromtimestamp(value / 1000)
    return value


class default_label_formatter(param.ParameterizedFunction):
    "Default formatter to turn parameter names into appropriate widget labels."

    capitalize = param.Boolean(default=True, doc="""
        Whether or not the label should be capitalized.""")

    replace_underscores = param.Boolean(default=True, doc="""
        Whether or not underscores should be replaced with spaces.""")

    overrides = param.Dict(default={}, doc="""
        Allows custom labels to be specified for specific parameter
        names using a dictionary where key is the parameter name and the
        value is the desired label.""")

    def __call__(self, pname):
        if pname in self.overrides:
            return self.overrides[pname]
        if self.replace_underscores:
            pname = pname.replace('_',' ')
        if self.capitalize:
            pname = pname[:1].upper() + pname[1:]
        return pname


################################
# Display and update utilities #
################################


def Div(**kwargs):
    # Hack to work around issues with Div height in notebooks
    div = BkDiv(**kwargs)
    box_kws = {k: v for k, v in kwargs.items()
               if k in ['width', 'height', 'sizing_mode']}
    return BkWidgetBox(div, **box_kws)


def diff(doc, binary=True, events=None):
    """
    Returns a json diff required to update an existing plot with
    the latest plot data.
    """
    events = list(doc._held_events) if events is None else events
    if not events:
        return None
    msg = Protocol("1.0").create("PATCH-DOC", events, use_buffers=binary)
    doc._held_events = [e for e in doc._held_events if e not in events]
    return msg


@contextmanager
def batch(doc, comm):
    """
    Context manager to batch updates on a document. Depending on whether
    a Comm or bokeh server is used the batching is applied differently.
    """
    if comm:
        doc._batched = True
    else:
        doc.hold()
    yield
    if comm:
        doc._batched = False
    else:
        doc.unhold()


def push(doc, comm, binary=True):
    """
    Pushes events stored on the document across the provided comm.
    """
    if getattr(doc, '_batched'):
        return
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
    bokeh_script, bokeh_div, _ = bokeh.embed.notebook.notebook_content(model, comm.id)
    html = encode_utf8(bokeh_div)

    # Publish bokeh plot JS
    msg_handler = bokeh_msg_handler.format(plot_id=target)
    comm_js = comm.js_template.format(plot_id=target, comm_id=comm.id, msg_handler=msg_handler)
    bokeh_js = '\n'.join([comm_js, bokeh_script])
    bokeh_js = embed_js.format(widget_id=target, plot_id=target, html=html) + bokeh_js

    data = {EXEC_MIME: '', 'text/html': html, 'application/javascript': bokeh_js}
    metadata = {EXEC_MIME: {'id': target}}
    return data, metadata
