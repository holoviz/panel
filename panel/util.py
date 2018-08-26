import json
import sys
import inspect

import param
import bokeh
import bokeh.embed.notebook
from bokeh.io.notebook import load_notebook as bk_load_notebook
from bokeh.models import Model, LayoutDOM, Div as BkDiv, Spacer, Row
from bokeh.protocol import Protocol
from bokeh.resources import CDN, INLINE
from bokeh.util.string import encode_utf8
from pyviz_comms import JupyterCommManager, bokeh_msg_handler, PYVIZ_PROXY

try:
    unicode = unicode # noqa
except:
    unicode = str


def as_unicode(obj):
    """
    Safely casts any object to unicode including regular string
    (i.e. bytes) types in python 2.
    """
    if sys.version_info.major < 3 and isinstance(obj, str):
        obj = obj.decode('utf-8')
    return unicode(obj)


def named_objs(objlist):
    """
    Given a list of objects, returns a dictionary mapping from
    string name for the object to the object itself.
    """
    objs = []
    for k, obj in objlist:
        if hasattr(k, '__name__'):
            k = k.__name__
        else:
            k = as_unicode(k)
        objs.append((k, obj))
    return objs


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
            pname = pname.capitalize()
        return pname


################################
# Display and update utilities #
################################


def Div(**kwargs):
    # Hack to work around issues with Div height in notebooks
    div = BkDiv(**kwargs)
    if 'height' in kwargs:
        return Row(div, Spacer(height=kwargs['height']))
    return div


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


def add_to_doc(obj, doc, hold=False):
    """
    Adds a model to the supplied Document removing it from any existing Documents.
    """
    # Handle previously displayed models
    for model in obj.select({'type': Model}):
        prev_doc = model.document
        model._document = None
        if prev_doc:
            prev_doc.remove_root(model)

    # Add new root
    doc.add_root(obj)
    if doc._hold is None and hold:
        doc.hold()


LOAD_MIME = 'application/vnd.holoviews_load.v0+json'
EXEC_MIME = 'application/vnd.holoviews_exec.v0+json'

embed_js = """
// Ugly hack - see HoloViews #2574 for more information
if (!(document.getElementById('{plot_id}')) && !(document.getElementById('_anim_img{widget_id}'))) {{
  console.log("Creating DOM nodes dynamically for assumed nbconvert export. To generate clean HTML output set HV_DOC_HTML as an environment variable.")
  var htmlObject = document.createElement('div');
  htmlObject.innerHTML = `{html}`;
  var scriptTags = document.getElementsByTagName('script');
  var parentTag = scriptTags[scriptTags.length-1].parentNode;
  parentTag.append(htmlObject)
}}
"""

def load_notebook(inline=True):
    from IPython.display import publish_display_data

    # Create a message for the logo (if shown)
    LOAD_MIME_TYPE = bokeh.io.notebook.LOAD_MIME_TYPE
    bokeh.io.notebook.LOAD_MIME_TYPE = LOAD_MIME
    bk_load_notebook(hide_banner=True, resources=INLINE if inline else CDN)
    bokeh.io.notebook.LOAD_MIME_TYPE = LOAD_MIME_TYPE
    bokeh.io.notebook.curstate().output_notebook()

    # Publish comm manager
    JS = '\n'.join([PYVIZ_PROXY, JupyterCommManager.js_manager])
    publish_display_data(data={LOAD_MIME: JS, 'application/javascript': JS})


def render_mimebundle(model, doc, comm):
    """
    Displays bokeh output inside a notebook using the PyViz display
    and comms machinery.
    """
    from IPython.display import publish_display_data
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
