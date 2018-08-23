import sys
import base64
import inspect
from io import BytesIO

import param
import bokeh
import bokeh.embed.notebook
from bokeh.models import Model, CustomJS, LayoutDOM, Div as BkDiv, Spacer, Row
from bokeh.protocol import Protocol
from bokeh.util.string import encode_utf8

from .comms import JupyterCommManager, bokeh_msg_handler, PYVIZ_PROXY, embed_js


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


######################
# Matplotlib support #
######################


def is_mpl(obj):
    return obj.__class__.__name__ == 'Figure' and hasattr(obj, '_cachedRenderer')


def render_mpl(plot, doc, plot_id, comm, container):
    """
    Renders a matplotlib object
    """
    bytes_io = BytesIO()
    plot.canvas.print_figure(bytes_io)
    data = bytes_io.getvalue()
    b64 = base64.b64encode(data).decode("utf-8")
    src = "data:image/png;base64,{b64}".format(b64=b64)
    width, height = plot.canvas.get_width_height()
    html = "<img src='{src}'></img>".format(src=src)
    return Div(text=html, width=width, height=height)


#####################
# Holoviews Support #
#####################


def is_hv(obj):
    return hasattr(obj, 'kdims') and hasattr(obj, 'vdims')


def render_hv(plot, doc, plot_id, comm, container):
    from holoviews import Store
    renderer = Store.renderers[Store.current_backend]
    renderer = renderer.instance(mode='server' if comm is None else 'default')
    plot = renderer.get_plot(plot, doc=doc)
    patch_hv_plot(plot, plot_id, comm)
    return Renderer.render(plot.state, doc, plot_id, comm)


def patch_hv_plot(plot, plot_id, comm):
    """
    Update the plot id and comm on a HoloViews plot to allow embedding
    it in a bokeh layout.
    """
    if not hasattr(plot, '_update_callbacks'):
        return

    for subplot in plot.traverse(lambda x: x):
        subplot.comm = comm
        for cb in getattr(subplot, 'callbacks', []):
            for c in cb.callbacks:
                c.code = c.code.replace(plot.id, plot_id)


def cleanup_hv(obj, plot):
    from holoviews.core.spaces import DynamicMap, get_nested_streams
    dmaps = obj.traverse(lambda x: x, [DynamicMap])
    for dmap in dmaps:
        for stream in get_nested_streams(dmap):
            for _, sub in stream._subscribers:
                if inspect.ismethod(sub):
                    owner = get_method_owner(sub)
                    if owner.state is plot:
                        owner.cleanup()


#################
# Bokeh support #
#################

                        
def patch_bk_plot(plot, plot_id):
    """
    Patches bokeh CustomJS models with top-level plot_id
    """
    if not plot_id: return
    for js in plot.select({'type': CustomJS}):
        js.code = js.code.replace(plot.ref['id'], plot_id)


def render_bokeh(plot, doc, plot_id, comm, container):
    patch_bk_plot(plot, plot_id)
    return plot


#################
# Param support #
#################


def is_param_method(plot):
    return inspect.ismethod(plot) and isinstance(get_method_owner(plot), param.Parameterized)


def render_param(plot, doc, plot_id, comm, container=None):
    method = plot
    raw = method()
    plot = Renderer.render(raw, doc, plot_id, comm, container)
    parameterized = get_method_owner(method)
    for p in parameterized.param.params_depended_on(method.__name__):
        def update_viewable(change, history=[]):
            if change.what != 'value': return
            old_plot, handle = history[0] if history else (plot, raw)
            Renderer.cleanup(handle, old_plot)
            new_handle = method()
            new_plot = Renderer.render(new_handle, doc, plot_id, comm, container)
            def update_models():
                index = container.children.index(old_plot)
                container.children[index] = new_plot
                history[:] = [(new_plot, new_handle)]
            if comm:
                update_models()
                push(doc, comm)
            else:
                doc.add_next_tick_callback(update_models)
        parameterized.param.watch(p.name, p.what, update_viewable)
    return plot


###############
# Other types #
###############

def has_html_repr(obj):
    return hasattr(obj, '_repr_html_')


def render_html_repr(plot, doc, plot_id, comm, container=None):
    return Div(text=plot._repr_html_())


def patch_widgets(plot, doc, plot_id, comm):
    """
    Patches parambokeh Widgets instances with top-level document, comm and plot id
    """
    plot.comm = comm
    plot.document = doc
    patch_bk_plot(plot.container, plot_id)


################################
# Display and update utilities #
################################

class Renderer(object):

    _renderers = [(0, is_param_method, render_param),
                  (0, is_hv,    render_hv),
                  (0, is_mpl,   render_mpl),
                  (0, LayoutDOM, render_bokeh),
                  (1, has_html_repr, render_html_repr)]

    _cleanup = [(0, is_hv, cleanup_hv)]

    @classmethod
    def register(cls, type_or_predicate, renderer, patch=None, precedence=0):
        cls._renderers.append((precedence, predicate, renderer))
        if cleanup:
            cls._cleanup.append((precedence, predicate, cleanup))

    @classmethod
    def render(cls, plot, doc, plot_id, comm, container=None):
        """
        Converts all acceptable plot and widget objects into displayable
        bokeh models. Patches any HoloViews plots or parambokeh Widgets
        with the top-level comms and plot id.
        """
        for _, predicate, render in sorted(cls._renderers, key=lambda x: x[0]):
            if ((inspect.isfunction(predicate) and predicate(plot)) or
                (isinstance(predicate, type) and isinstance(plot, predicate))):
                return render(plot, doc, plot_id, comm, container)
        raise TypeError('%s type could not be rendered.' % type(plot.__name__))

    @classmethod
    def cleanup(cls, obj, plot):
        for _, predicate, cleanup in sorted(cls._cleanup, key=lambda x: x[0]):
            if ((inspect.isfunction(predicate) and predicate(obj)) or
                (isinstance(predicate, type) and isinstance(obj, predicate))):
                return cleanup(obj, plot)


def Div(**kwargs):
    # Hack to work around issues with Div height in notebooks 
    div = BkDiv(**kwargs)
    if 'height' in kwargs:
        return Row(div, Spacer(height=kwargs['height']))
    return div


def diff(doc, binary=True):
    """
    Returns a json diff required to update an existing plot with
    the latest plot data.
    """
    events = list(doc._held_events)
    if not events:
        return None
    msg = Protocol("1.0").create("PATCH-DOC", events, use_buffers=binary)
    doc._held_events = []
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


def render(obj, doc, comm):
    """
    Displays bokeh output inside a notebook using the PyViz display
    and comms machinery.
    """
    from IPython.display import publish_display_data
    if not isinstance(obj, LayoutDOM): 
        raise ValueError('Can only render bokeh LayoutDOM models')

    add_to_doc(obj, doc, True)

    target = obj.ref['id']
    load_mime = 'application/vnd.holoviews_load.v0+json'
    exec_mime = 'application/vnd.holoviews_exec.v0+json'

    # Publish plot HTML
    bokeh_script, bokeh_div, _ = bokeh.embed.notebook.notebook_content(obj, comm.id)
    html = encode_utf8(bokeh_div)

    # Publish comm manager
    JS = '\n'.join([PYVIZ_PROXY, JupyterCommManager.js_manager])
    publish_display_data(data={load_mime: JS, 'application/javascript': JS})

    # Publish bokeh plot JS
    msg_handler = bokeh_msg_handler.format(plot_id=target)
    comm_js = comm.js_template.format(plot_id=target, comm_id=comm.id, msg_handler=msg_handler)
    bokeh_js = '\n'.join([comm_js, bokeh_script])
    bokeh_js = embed_js.format(widget_id=target, plot_id=target, html=html) + bokeh_js

    data = {exec_mime: '', 'text/html': html, 'application/javascript': bokeh_js}
    metadata = {exec_mime: {'id': target}}
    return data, metadata
