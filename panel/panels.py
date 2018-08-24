import inspect
import base64
from io import BytesIO

import param

from bokeh.document import Document
from bokeh.io import curdoc, show
from bokeh.layouts import Column as BkColumn, Row as BkRow
from bokeh.models import LayoutDOM, CustomJS
from pyviz_comms import JupyterCommManager

from .util import render_mimebundle, add_to_doc, get_method_owner, push, Div


class Viewable(param.Parameterized):
    """
    Viewable is the baseclass all objects in the panel library are
    built on. It defines the interface for declaring any object that
    displays itself by transforming the object(s) being wrapped into
    models that can be served using bokeh's layout engine. The class
    also defines various methods that allow Viewable objects to be
    displayed in the notebook and on bokeh server.
    """

    __abstract = True

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Converts the objects being wrapped by the viewable into a
        bokeh model that can be composed in a bokeh layout.

        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.

        root: bokeh.Model
          The root layout the viewable will become part of.

        parent: bokeh.Model
          The parent layout the viewable will become part of.

        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook
        """

    def cleanup(self, model):
        """
        Clean up method which is called when a Viewable is destroyed.
        """
        pass

    def _repr_mimebundle_(self, include=None, exclude=None):
        doc = Document()
        comm = JupyterCommManager.get_server_comm()
        model = self._get_root(doc, comm)
        return render_mimebundle(model, doc, comm)

    def server_doc(self, doc=None):
        doc = doc or curdoc()
        model = self._get_root(doc)
        add_to_doc(model, doc)
        return doc

    def _modify_doc(self, doc):
        return self.server_doc(doc)

    def app(self, notebook_url="localhost:8888"):
        """
        Displays a bokeh server app in the notebook.
        """
        show(self._modify_doc, notebook_url=notebook_url)



class Panel(Viewable):
    """
    Panel is the abstract baseclass for all atomic displayable units
    in the panel library. Panel defines an extensible interface for
    wrapping arbitrary objects and transforming them into bokeh models
    which can be laid out.

    To define a concrete Panel type subclass this class and implement
    the applies classmethod and the _get_model private method.
    """

    object = param.Parameter(default=None, doc="""
        The object being wrapped, which will be converted into a bokeh model.""")

    # When multiple Panels apply to an object the precedence is used
    precedence = 0

    __abstract = True

    @classmethod
    def applies(cls, obj):
        """
        Given the object return a boolean indicating whether the Panel
        can render the object.
        """
        return None

    @classmethod
    def to_panel(cls, obj):
        if isinstance(obj, Viewable):
            return obj
        descendents = [(p.precedence, p) for p in param.concrete_descendents(Panel).values()]
        panel_types = sorted(descendents, key=lambda x: x[0])
        for _, panel_type in panel_types:
            if not panel_type.applies(obj): continue
            return panel_type(obj)
        raise TypeError('%s type could not be rendered.' % type(obj).__name__)

    def __init__(self, object, **params):
        if not self.applies(object):
            name = type(self).__name__
            raise ValueError('%s object not understood by %s, '
                             'expected %s object.' %
                             (type(object).__name__, name, name[:-5]))
        super(Panel, self).__init__(object=object, **params)

    def _get_root(self, doc, comm=None):
        root = BkColumn()
        model = self._get_model(doc, root, root, comm)
        root.children = [model]
        return root


class BokehPanel(Panel):
    """
    A wrapper for bokeh plots model that can be converted to
    bokeh plots.
    """

    object = param.Parameter(default=None)

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, LayoutDOM)

    def _get_model(self, doc, root, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered. 
        """
        plot_id = root.ref['id']
        if plot_id:
            for js in self.object.select({'type': CustomJS}):
                js.code = js.code.replace(self.object.ref['id'], plot_id)
        return self.object


class HoloViewsPanel(Panel):

    @classmethod
    def applies(cls, obj):
        return hasattr(obj, 'kdims') and hasattr(obj, 'vdims')

    def _patch_plot(self, plot, plot_id, comm):
        if not hasattr(plot, '_update_callbacks'):
            return

        for subplot in plot.traverse(lambda x: x):
            subplot.comm = comm
            for cb in getattr(subplot, 'callbacks', []):
                for c in cb.callbacks:
                    c.code = c.code.replace(plot.id, plot_id)

    def cleanup(self, model):
        """
        Traverses HoloViews object to find and clean up any streams
        connected to existing plots.
        """
        from holoviews.core.spaces import DynamicMap, get_nested_streams
        dmaps = self.object.traverse(lambda x: x, [DynamicMap])
        for dmap in dmaps:
            for stream in get_nested_streams(dmap):
                for _, sub in stream._subscribers:
                    if inspect.ismethod(sub):
                        owner = get_method_owner(sub)
                        if owner.state is model:
                            owner.cleanup()

    def _get_model(self, doc, root, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered. 
        """
        from holoviews import Store
        renderer = Store.renderers[Store.current_backend]
        renderer = renderer.instance(mode='server' if comm is None else 'default')
        kwargs = {'doc': doc} if renderer.backend == 'bokeh' else {}
        plot = renderer.get_plot(self.object, **kwargs)
        self._patch_plot(plot, root.ref['id'], comm)
        panel = Panel.to_panel(plot.state)
        model = panel._get_model(doc, root, parent, comm)
        return model


class ParamMethodPanel(Panel):

    @classmethod
    def applies(cls, obj):
        return inspect.ismethod(obj) and isinstance(get_method_owner(obj), param.Parameterized)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        parameterized = get_method_owner(self.object)
        params = parameterized.param.params_depended_on(self.object.__name__)
        panel = self.to_panel(self.object())
        model = panel._get_model(doc, root, parent, comm)
        history = []
        for p in params:
            def update_panel(change, history=history):
                if change.what != 'value': return
                old_panel, old_model = history[0] if history else (panel, model)
                old_panel.cleanup(old_model)
                new_panel = self.to_panel(self.object())
                new_model = new_panel._get_model(doc, root, parent, comm)
                def update_models():
                    if old_model is new_model:
                        old_model.update(**new_model.properties_with_values())
                    else:
                        index = parent.children.index(old_model)
                        parent.children[index] = new_model
                        history[:] = [(new_panel, new_model)]
                if comm:
                    update_models()
                    push(doc, comm)
                else:
                    doc.add_next_tick_callback(update_models)
            parameterized.param.watch(p.name, p.what, update_panel)
        return model


class MatplotlibPanel(Panel):

    @classmethod
    def applies(self, obj):
        return obj.__class__.__name__ == 'Figure' and hasattr(obj, '_cachedRenderer')

    def _get_model(self, doc, root=None, parent=None, comm=None):
        bytes_io = BytesIO()
        self.object.canvas.print_figure(bytes_io)
        data = bytes_io.getvalue()
        b64 = base64.b64encode(data).decode("utf-8")
        src = "data:image/png;base64,{b64}".format(b64=b64)
        width, height = self.object.canvas.get_width_height()
        html = "<img src='{src}'></img>".format(src=src)
        return Div(text=html, width=width, height=height)


class HTML(Panel):

    precedence = 1

    @classmethod
    def applies(self, obj):
        return hasattr(obj, '_repr_html_')

    def _get_model(self, doc, root=None, parent=None, comm=None):
        return Div(text=self.object._repr_html_())
