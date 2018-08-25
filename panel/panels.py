import inspect
import base64
from io import BytesIO

import param

from bokeh.layouts import Column as BkColumn
from bokeh.models import LayoutDOM, CustomJS

from .util import get_method_owner, push, Div
from .viewable import Reactive, Viewable


class Panel(Reactive):
    """
    Panel is the abstract baseclass for all atomic displayable units
    in the panel library. Panel defines an extensible interface for
    wrapping arbitrary objects and transforming them into bokeh models
    allowing the panel to display itself in the notebook or be served
    using bokeh server.

    Panels are reactive in the sense that when the object they are
    wrapping is changed any plots containing the panel will update
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

    def _link_object(self, model, doc, root, parent, comm=None, panel=None):
        """
        Links the object parameter to the rendered bokeh model, triggering
        an update when the object changes.
        """
        def update_panel(change, history=[(panel, model)]):
            new_model, new_panel = self._get_model(doc, root, parent, comm, rerender=True)
            old_panel, old_model = history[0]
            if old_panel is not None:
                old_panel.cleanup()
            def update_models():
                if old_model is new_model: return
                index = parent.children.index(old_model)
                parent.children[index] = new_model
                history[:] = [new_model]
            if comm:
                update_models()
                push(doc, comm)
            else:
                doc.add_next_tick_callback(update_models)
        self.param.watch('object', 'value', update_panel)



class BokehPanel(Panel):
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
        plot_id = root.ref['id']
        if plot_id:
            for js in self.object.select({'type': CustomJS}):
                js.code = js.code.replace(self.object.ref['id'], plot_id)
        if rerender:
            self._link_object(self.object, doc, root, parent, comm)
            return self.object, None
        return self.object


class HoloViewsPanel(Panel):
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
        panel = Panel.to_panel(plot.state)
        model = panel._get_model(doc, root, parent, comm)
        if rerender:
            self._link_object(model, doc, root, parent, comm, panel)
            return model, panel
        return model


class ParamMethodPanel(Panel):
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
        panel = self.to_panel(self.object())
        model = panel._get_model(doc, root, parent, comm)
        for p in params:
            def update_panel(change, history=[(panel, model)]):
                if change.what != 'value': return
                old_panel, old_model = history[0]
                old_panel.cleanup(old_model)
                new_panel = self.to_panel(self.object())
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
            parameterized.param.watch(p.name, p.what, update_panel)
        return model


class MatplotlibPanel(Panel):
    """
    A MatplotlibPanel renders a matplotlib figure to png and wraps
    the base64 encoded data in a bokeh Div model.
    """

    @classmethod
    def applies(self, obj):
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
            self._link_object(model, doc, root, parent, comm)
            return model, None
        return model


class HTML(Panel):
    """
    HTML renders any object which has a _repr_html_ method and wraps
    the HTML in a bokeh Div model.
    """

    precedence = 1

    @classmethod
    def applies(self, obj):
        return hasattr(obj, '_repr_html_')

    def _get_model(self, doc, root=None, parent=None, comm=None, rerender=False):
        model = Div(text=self.object._repr_html_())
        if rerender:
            self._link_object(model, doc, root, parent, comm)
            return model, None
        return model
