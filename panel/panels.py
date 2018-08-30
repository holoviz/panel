"""
Panels allow wrapping external objects and rendering them as part of
a dashboard.
"""
import os
import inspect
import base64
from io import BytesIO

import param

from bokeh.layouts import Column as BkColumn
from bokeh.models import LayoutDOM, CustomJS

from .util import get_method_owner, push, Div
from .viewable import Reactive, Viewable


def Panel(obj, **kwargs):
    """
    Converts any object to a Panel if a matching Panel class exists.
    """
    if isinstance(obj, Viewable):
        return obj
    return PanelBase.get_panel_type(obj)(obj, **kwargs)



class PanelBase(Reactive):
    """
    PanelBase is the abstract baseclass for all atomic displayable units
    in the panel library. Panel defines an extensible interface for
    wrapping arbitrary objects and transforming them into bokeh models.
    allowing the panel to display itself in the notebook or be served
    using bokeh server.

    Panels are reactive in the sense that when the object they are
    wrapping is changed any dashboard containing the panel will update
    in response.

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
    def get_panel_type(cls, obj):
        if isinstance(obj, Viewable):
            return type(obj)
        descendents = [(p.precedence, p) for p in param.concrete_descendents(PanelBase).values()]
        panel_types = sorted(descendents, key=lambda x: x[0])
        for _, panel_type in panel_types:
            if not panel_type.applies(obj): continue
            return panel_type
        raise TypeError('%s type could not be rendered.' % type(obj).__name__)

    def __init__(self, object, **params):
        if not self.applies(object):
            name = type(self).__name__
            raise ValueError('%s object not understood by %s, '
                             'expected %s object.' %
                             (type(object).__name__, name, name[:-5]))

        # temporary flag denotes panels created for temporary, internal
        # use which should be garbage collected once they have been used
        self._temporary = params.pop('_temporary', False)

        super(PanelBase, self).__init__(object=object, **params)

    def _get_root(self, doc, comm=None):
        root = BkColumn()
        model = self._get_model(doc, root, root, comm)
        root.children = [model]
        return root

    def _cleanup(self, model):
        super(PanelBase, self)._cleanup(model)
        if self._temporary:
            self.object = None

    def _link_object(self, model, doc, root, parent, comm=None, panel=None):
        """
        Links the object parameter to the rendered bokeh model, triggering
        an update when the object changes.
        """
        if self._temporary:
             # If the object has no user handle don't bother linking params
            return

        def update_panel(change, history=[(panel, model)]):
            new_model, new_panel = self._get_model(doc, root, parent, comm, rerender=True)
            old_panel, old_model = history[0]
            if old_model is new_model:
                return
            elif old_panel is not None:
                old_panel._cleanup(old_model)
            def update_models():
                index = parent.children.index(old_model)
                parent.children[index] = new_model
                history[:] = [(new_panel, new_model)]
            if comm:
                update_models()
                push(doc, comm)
            else:
                doc.add_next_tick_callback(update_models)
        self.param.watch(update_panel, 'object')
        self._callbacks[model.ref['id']]['object'] = update_panel


class BokehPanel(PanelBase):
    """
    BokehPanel allows including any bokeh model in a plot directly.
    """

    object = param.Parameter(default=None)

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, LayoutDOM)

    def _get_model(self, doc, root, parent=None, comm=None, rerender=False):
        """
        Should return the bokeh model to be rendered.
        """
        model = self.object
        plot_id = root.ref['id']
        if plot_id:
            for js in model.select({'type': CustomJS}):
                js.code = js.code.replace(self.object.ref['id'], plot_id)

        if rerender:
            return model, None

        self._link_object(model, doc, root, parent, comm)
        return model


class HoloViewsPanel(PanelBase):
    """
    HoloViewsPanel renders any HoloViews object to a corresponding
    bokeh model while respecting the currently selected backend.
    """

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

    def _cleanup(self, model):
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
        super(HoloViewsPanel, self)._cleanup(model)

    def _get_model(self, doc, root, parent=None, comm=None, rerender=False):
        """
        Should return the bokeh model to be rendered.
        """
        from holoviews import Store
        renderer = Store.renderers[Store.current_backend]
        renderer = renderer.instance(mode='server' if comm is None else 'default')
        kwargs = {'doc': doc} if renderer.backend == 'bokeh' else {}
        plot = renderer.get_plot(self.object, **kwargs)
        self._patch_plot(plot, root.ref['id'], comm)
        child_panel = Panel(plot.state, _temporary=True)
        model = child_panel._get_model(doc, root, parent, comm)
        if rerender:
            return model, child_panel
        self._link_object(model, doc, root, parent, comm, child_panel)
        return model


class ParamMethodPanel(PanelBase):
    """
    ParamMethodPanel wraps methods annotated with the param.depends
    decorator and rerenders the plot when any of the methods parameters
    change. The method may return any object which itself can be rendered
    as a Panel.
    """

    @classmethod
    def applies(cls, obj):
        return inspect.ismethod(obj) and isinstance(get_method_owner(obj), param.Parameterized)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        parameterized = get_method_owner(self.object)
        params = parameterized.param.params_depended_on(self.object.__name__)
        panel = Panel(self.object(), _temporary=True)
        model = panel._get_model(doc, root, parent, comm)
        history = [(panel, model)]
        for p in params:
            def update_panel(change, history=history):
                if change.what != 'value': return
                old_panel, old_model = history[0]
                old_panel._cleanup(old_model)
                new_panel = Panel(self.object(), _temporary=True)
                new_model = new_panel._get_model(doc, root, parent, comm)
                def update_models():
                    if old_model is new_model: return
                    index = parent.children.index(old_model)
                    parent.children[index] = new_model
                    history[:] = [(new_panel, new_model)]
                if comm:
                    update_models()
                    push(doc, comm)
                else:
                    doc.add_next_tick_callback(update_models)
            parameterized.param.watch(update_panel, p.name, p.what)
        return model

    def _cleanup(self, model):
        """
        Clean up method which is called when a Viewable is destroyed.
        """
        model_id = model.ref['id']
        callbacks = self._callbacks[model_id]
        parameterized = get_method_owner(self.object)
        for p, cb in callbacks.items():
            parameterized.param.unwatch(fn, cb)
        super(ParamMethodPanel, self)._cleanup(model)


class MatplotlibPanel(PanelBase):
    """
    A MatplotlibPanel renders a matplotlib figure to png and wraps
    the base64 encoded data in a bokeh Div model.
    """

    @classmethod
    def applies(cls, obj):
        return obj.__class__.__name__ == 'Figure' and hasattr(obj, '_cachedRenderer')

    def _get_model(self, doc, root=None, parent=None, comm=None, rerender=False):
        bytes_io = BytesIO()
        self.object.canvas.print_figure(bytes_io)
        data = bytes_io.getvalue()
        b64 = base64.b64encode(data).decode("utf-8")
        src = "data:image/png;base64,{b64}".format(b64=b64)
        width, height = self.object.canvas.get_width_height()
        html = "<img src='{src}'></img>".format(src=src)
        model = Div(text=html, width=width, height=height)

        if rerender:
            return model, None
        self._link_object(model, doc, root, parent, comm)
        return model


class HTMLPanel(PanelBase):
    """
    HTMLPanel renders any object which has a _repr_html_ method and wraps
    the HTML in a bokeh Div model.
    """

    precedence = 1

    @classmethod
    def applies(cls, obj):
        return hasattr(obj, '_repr_html_')

    def _get_model(self, doc, root=None, parent=None, comm=None, rerender=False):
        model = Div(text=self.object._repr_html_())

        if rerender:
            return model, None
        self._link_object(model, doc, root, parent, comm)
        return model


class GGPlotPanel(PanelBase):
    """
    A GGPlotPanel renders a r2py based ggplot to png and wraps
    the base64 encoded data in a bokeh Div model.
    """

    height = param.Integer(default=400, bounds=(0, None))

    width = param.Integer(default=400, bounds=(0, None))

    dpi = param.Integer(default=72, bounds=(1, None))

    @classmethod
    def applies(cls, obj):
        return type(obj).__name__ == 'GGPlot' and hasattr(obj, 'r_repr')

    def _get_model(self, doc, root=None, parent=None, comm=None, rerender=False):
        from rpy2.robjects.lib import grdevices
        from rpy2 import robjects
        with grdevices.render_to_bytesio(grdevices.png,
                                         type="cairo-png",
                                         width=self.width,
                                         height=self.height,
                                         res=self.dpi,
                                         antialias="subpixel") as b:
            robjects.r("print")(self.object)
        data = b.getvalue()
        b64 = base64.b64encode(data).decode("utf-8")
        src = "data:image/png;base64,{b64}".format(b64=b64)
        html = "<img src='{src}'></img>".format(src=src)
        model = Div(text=html, width=self.width, height=self.height)
        if rerender:
            return model, None
        self._link_object(model, doc, root, parent, comm)
        return model
