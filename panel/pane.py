"""
Panes allow wrapping external objects and rendering them as part of
a dashboard.
"""
from __future__ import absolute_import

import os
import sys
import inspect
import base64
from io import BytesIO

import param

from bokeh.layouts import Row as _BkRow, WidgetBox as _BkWidgetBox
from bokeh.models import LayoutDOM, CustomJS, Widget as _BkWidget, Div as _BkDiv

from .util import basestring, get_method_owner, push, remove_root, Div
from .viewable import Reactive, Viewable


def Pane(obj, **kwargs):
    """
    Converts any object to a Pane if a matching Pane class exists.
    """
    if isinstance(obj, Viewable):
        return obj
    return PaneBase.get_pane_type(obj)(obj, **kwargs)


class PaneBase(Reactive):
    """
    PaneBase is the abstract baseclass for all atomic displayable units
    in the panel library. Pane defines an extensible interface for
    wrapping arbitrary objects and transforming them into bokeh models.

    Panes are reactive in the sense that when the object they are
    wrapping is changed any dashboard containing the pane will update
    in response.

    To define a concrete Pane type subclass this class and implement
    the applies classmethod and the _get_model private method.
    """

    object = param.Parameter(default=None, doc="""
        The object being wrapped, which will be converted into a bokeh model.""")

    # When multiple Panes apply to an object the precedence is used
    precedence = 0

    # Declares whether Pane supports updates to the bokeh model
    _updates = False

    __abstract = True

    @classmethod
    def applies(cls, obj):
        """
        Given the object return a boolean indicating whether the Pane
        can render the object.
        """
        return None

    @classmethod
    def get_pane_type(cls, obj):
        if isinstance(obj, Viewable):
            return type(obj)
        descendents = [(p.precedence, p) for p in param.concrete_descendents(PaneBase).values()]
        pane_types = sorted(descendents, key=lambda x: x[0])
        for _, pane_type in pane_types:
            if not pane_type.applies(obj): continue
            return pane_type
        raise TypeError('%s type could not be rendered.' % type(obj).__name__)

    def __init__(self, object, **params):
        if not self.applies(object):
            name = type(self).__name__
            raise ValueError('%s object not understood by %s, '
                             'expected %s object.' %
                             (type(object).__name__, name, name[:-5]))

        # temporary flag denotes panes created for temporary, internal
        # use which should be garbage collected once they have been used
        self._temporary = params.pop('_temporary', False)

        super(PaneBase, self).__init__(object=object, **params)

    def _get_root(self, doc, comm=None):
        root = _BkRow()
        model = self._get_model(doc, root, root, comm)
        root.children = [model]
        return root

    def _cleanup(self, model, final=False):
        super(PaneBase, self)._cleanup(model, final)
        if final:
            self.object = None

    def _update(self, model):
        """
        If _updates=True this method is used to update an existing bokeh
        model instead of replacing the model entirely. The supplied model
        should be updated with the current state.
        """
        raise NotImplementedError

    def _link_object(self, model, doc, root, parent, comm=None):
        """
        Links the object parameter to the rendered bokeh model, triggering
        an update when the object changes.
        """
        def update_pane(change, history=[model]):
            old_model = history[0]

            # Pane supports model updates
            if self._updates:
                def update_models():
                    self._update(old_model)
                if comm:
                    update_models()
                    push(doc, comm)
                else:
                    doc.add_next_tick_callback(update_models)
                return

            # Otherwise replace the whole model
            new_model = self._get_model(doc, root, parent, comm)
            def update_models():
                self._cleanup(old_model)
                index = parent.children.index(old_model)
                parent.children[index] = new_model
                history[0] = new_model

            if comm:
                update_models()
                push(doc, comm)
            else:
                doc.add_next_tick_callback(update_models)
        self.param.watch(update_pane, 'object')
        self._callbacks[model.ref['id']]['object'] = update_pane


class Bokeh(PaneBase):
    """
    Bokeh panes allow including any bokeh model in a panel.
    """

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, LayoutDOM)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        model = self.object
        if isinstance(model, _BkWidget):
            model = _BkWidgetBox(model, width=model.width)

        if root:
            plot_id = root.ref['id']
            if plot_id:
                for js in model.select({'type': CustomJS}):
                    js.code = js.code.replace(self.object.ref['id'], plot_id)

        if model._document and doc is not model._document:
            remove_root(model, doc)

        self._link_object(model, doc, root, parent, comm)
        return model


class HoloViews(PaneBase):
    """
    HoloViews panes render any HoloViews object to a corresponding
    bokeh model while respecting the currently selected backend.
    """

    @classmethod
    def applies(cls, obj):
        if 'holoviews' not in sys.modules:
            return False
        from holoviews import Dimensioned
        return isinstance(obj, Dimensioned)

    def _patch_plot(self, plot, plot_id, comm):
        if not hasattr(plot, '_update_callbacks'):
            return

        for subplot in plot.traverse(lambda x: x):
            subplot.comm = comm
            for cb in getattr(subplot, 'callbacks', []):
                for c in cb.callbacks:
                    c.code = c.code.replace(plot.id, plot_id)

    def _cleanup(self, model, final=False):
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
        super(HoloViews, self)._cleanup(model, final)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        from holoviews import Store
        renderer = Store.renderers[Store.current_backend]
        renderer = renderer.instance(mode='server' if comm is None else 'default')
        kwargs = {'doc': doc} if renderer.backend == 'bokeh' else {}
        plot = renderer.get_plot(self.object, **kwargs)
        self._patch_plot(plot, root.ref['id'], comm)
        child_pane = Pane(plot.state, _temporary=True)
        model = child_pane._get_model(doc, root, parent, comm)
        self._link_object(model, doc, root, parent, comm)
        return model


class ParamMethod(PaneBase):
    """
    ParamMethod panes wrap methods annotated with the param.depends
    decorator and rerenders the plot when any of the methods parameters
    change. The method may return any object which itself can be rendered
    as a Pane.
    """

    def __init__(self, object, **params):
        self._kwargs =  {p: params.pop(p) for p in list(params)
                         if p not in self.params()}
        super(ParamMethod, self).__init__(object, **params)
        self._pane = Pane(self.object(), name=self.name,
                          **dict(_temporary=True, **self._kwargs))

    @classmethod
    def applies(cls, obj):
        return inspect.ismethod(obj) and isinstance(get_method_owner(obj), param.Parameterized)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        parameterized = get_method_owner(self.object)
        params = parameterized.param.params_depended_on(self.object.__name__)
        model = self._pane._get_model(doc, root, parent, comm)
        history = [model]
        for p in params:
            def update_pane(change, history=history):
                if change.what != 'value': return

                # Try updating existing pane
                old_model = history[0]
                new_object = self.object()
                pane_type = self.get_pane_type(new_object)
                if type(self._pane) is pane_type:
                    if isinstance(new_object, PaneBase):
                        new_params = {k: v for k, v in new_object.get_param_values()
                                      if k != 'name'}
                        self._pane.set_param(**new_params)
                        new_object._cleanup(None, final=True)
                    else:
                        self._pane.object = new_object
                    return

                # Replace pane entirely
                self._pane._cleanup(old_model)
                self._pane = Pane(new_object, _temporary=True, **self._kwargs)
                new_model = self._pane._get_model(doc, root, parent, comm)
                def update_models():
                    if old_model is new_model: return
                    index = parent.children.index(old_model)
                    parent.children[index] = new_model
                    history[0] = new_model

                if comm:
                    update_models()
                    push(doc, comm)
                else:
                    doc.add_next_tick_callback(update_models)

            parameterized.param.watch(update_pane, p.name, p.what)
        return model

    def _cleanup(self, model, final=False):
        """
        Clean up method which is called when a Viewable is destroyed.
        """
        model_id = model.ref['id']
        callbacks = self._callbacks[model_id]
        parameterized = get_method_owner(self.object)
        for p, cb in callbacks.items():
            parameterized.param.unwatch(cb, p)
        self._pane._cleanup(model, final)
        super(ParamMethod, self)._cleanup(model, final)


class DivPaneBase(PaneBase):
    """
    Baseclass for Panes which render HTML inside a Bokeh Div.
    See the documentation for Bokeh Div for more detail about
    the supported options like style and sizing_mode.
    """

    # DivPane supports updates to the model
    _updates = True

    __abstract = True

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    sizing_mode = param.ObjectSelector(default=None, allow_None=True,
        objects=["fixed", "scale_width", "scale_height", "scale_both", "stretch_both"], 
        doc="How the item being displayed should size itself.")
                                       
    style = param.Dict(default=None, doc="""
        Dictionary of CSS property:value pairs to apply to this Div.""")

    def _get_properties(self):
        return {p : getattr(self,p) for p in ["width", "height", "sizing_mode", "style"]
                if getattr(self,p) is not None}

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = Div(**self._get_properties())
        self._link_object(model, doc, root, parent, comm)
        return model

    def _update(self, model):
        div = model if isinstance(model, _BkDiv) else model.children[0]
        div.update(**self._get_properties())


class PNG(DivPaneBase):
    """
    Encodes a PNG as base64 and wraps it in a Bokeh Div model.  This
    base class supports anything with a _repr_png_ method, a local
    file with a png file extension or a HTTP url, but subclasses can
    provide their own way of obtaining or generating a PNG.
    """

    @classmethod
    def applies(cls, obj):
        return (hasattr(obj, '_repr_png_') or
                (isinstance(obj, basestring) and
                 ((os.path.isfile(obj) and obj.endswith('.png')) or
                  ((obj.startswith('http://') or obj.startswith('https://'))
                   and obj.endswith('.png')))))

    def _png(self):
        if not isinstance(self.object, basestring):
            return self.object._repr_png_()
        elif os.path.isfile(self.object):
            with open(self.object, 'rb') as f:
                return f.read()
        else:
            import requests
            r = requests.request(url=self.object, method='GET')
            return r.content

    def _pngshape(self, data):
        """Calculate and return PNG width,height"""
        import struct
        w, h = struct.unpack('>LL', data[16:24])
        return int(w), int(h)
    
    def _get_properties(self):
        data = self._png()
        b64 = base64.b64encode(data).decode("utf-8")
        src = "data:image/png;base64,{b64}".format(b64=b64)
        html = "<img src='{src}'></img>".format(src=src)
        
        p = super(PNG,self)._get_properties()
        width, height = self._pngshape(data)
        if self.width  is None: p["width"]  = width
        if self.height is None: p["height"] = height
        p["text"]=html
        return p


class Matplotlib(PNG):
    """
    A Matplotlib panes render a matplotlib figure to png and wraps
    the base64 encoded data in a bokeh Div model.
    """

    @classmethod
    def applies(cls, obj):
        if 'matplotlib' not in sys.modules:
            return False
        from matplotlib.figure import Figure
        is_fig = isinstance(obj, Figure)
        if is_fig and obj.canvas is None:
            raise ValueError('Matplotlib figure has no canvas and '
                             'cannot be rendered.')
        return is_fig

    def _png(self):
        b = BytesIO()
        self.object.canvas.print_figure(b)
        return b.getvalue()


class HTML(DivPaneBase):
    """
    HTML panes render any object which has a _repr_html_ method and wraps
    the HTML in a bokeh Div model. The height and width can optionally
    be specified, to allow room for whatever is being wrapped.
    """

    precedence = 1

    @classmethod
    def applies(cls, obj):
        return hasattr(obj, '_repr_html_')

    def _get_properties(self):
        properties = super(HTML, self)._get_properties()
        return dict(properties, text=self.object._repr_html_())


class RGGPlot(PNG):
    """
    An RGGPlot panes render an r2py-based ggplot2 figure to png
    and wraps the base64-encoded data in a bokeh Div model.
    """

    height = param.Integer(default=400)

    width = param.Integer(default=400)

    dpi = param.Integer(default=144, bounds=(1, None))

    @classmethod
    def applies(cls, obj):
        return type(obj).__name__ == 'GGPlot' and hasattr(obj, 'r_repr')

    def _png(self):
        from rpy2.robjects.lib import grdevices
        from rpy2 import robjects
        with grdevices.render_to_bytesio(grdevices.png,
                 type="cairo-png", width=self.width, height=self.height,
                 res=self.dpi, antialias="subpixel") as b:
            robjects.r("print")(self.object)
        return b.getvalue()
