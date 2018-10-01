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

try:
    from html import escape
except:
    from cgi import escape


import param

from bokeh.layouts import Row as _BkRow, WidgetBox as _BkWidgetBox
from bokeh.models import LayoutDOM, CustomJS, Widget as _BkWidget, Div as _BkDiv

from .util import (basestring, unicode, get_method_owner, push,
                   remove_root, full_groupby, Div)
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
    wrapping arbitrary objects and transforming them into Bokeh models.

    Panes are reactive in the sense that when the object they are
    wrapping is changed any dashboard containing the pane will update
    in response.

    To define a concrete Pane type subclass this class and implement
    the applies classmethod and the _get_model private method.
    """

    object = param.Parameter(default=None, doc="""
        The object being wrapped, which will be converted into a Bokeh model.""")

    # When multiple Panes apply to an object, the one with the highest
    # numerical precedence is selected. The default is an intermediate value.
    precedence = 0.5

    # Declares whether Pane supports updates to the Bokeh model
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
        pane_types = reversed(sorted(descendents, key=lambda x: x[0]))
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
        super(PaneBase, self).__init__(object=object, **params)

    def _get_root(self, doc, comm=None):
        root = _BkRow()
        model = self._get_model(doc, root, root, comm)
        root.children = [model]
        return root

    def _cleanup(self, model=None, final=False):
        super(PaneBase, self)._cleanup(model, final)
        if final:
            self.object = None

    def _update(self, model):
        """
        If _updates=True this method is used to update an existing Bokeh
        model instead of replacing the model entirely. The supplied model
        should be updated with the current state.
        """
        raise NotImplementedError

    def _link_object(self, model, doc, root, parent, comm=None):
        """
        Links the object parameter to the rendered Bokeh model, triggering
        an update when the object changes.
        """
        def update_pane(change, history=[model]):
            old_model = history[0]

            # Pane supports model updates
            if self._updates:
                def update_models():
                    self._update(old_model)
            else:
                # Otherwise replace the whole model
                self._cleanup(old_model)
                new_model = self._get_model(doc, root, parent, comm)
                def update_models():
                    index = parent.children.index(old_model)
                    parent.children[index] = new_model
                    history[0] = new_model

            if comm:
                update_models()
                push(doc, comm)
            else:
                doc.add_next_tick_callback(update_models)

        ref = model.ref['id']
        self._callbacks[ref].append(self.param.watch(update_pane, 'object'))


class Bokeh(PaneBase):
    """
    Bokeh panes allow including any Bokeh model in a panel.
    """

    precedence = 0.8

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, LayoutDOM)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the Bokeh model to be rendered.
        """
        model = self.object
        if isinstance(model, _BkWidget):
            box_kws = {k: getattr(model, k) for k in ['width', 'height', 'sizing_mode']
                       if k in model.properties()}
            model = _BkWidgetBox(model, **box_kws)

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
    Bokeh model while respecting the currently selected backend.
    """
    
    precedence = 0.8
    
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

    def _cleanup(self, model=None, final=False):
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
        Should return the Bokeh model to be rendered.
        """
        from holoviews import Store
        if not Store.renderers:
            import holoviews.plotting.bokeh # noqa
            Store.current_backend == 'bokeh'
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
        ref = model.ref['id']
        history = [model]
        def update_pane(*change, history=history):
            # Try updating existing pane
            old_model = history[0]
            new_object = self.object()
            pane_type = self.get_pane_type(new_object)
            if type(self._pane) is pane_type:
                if isinstance(new_object, PaneBase):
                    new_params = {k: v for k, v in new_object.get_param_values()
                                  if k != 'name'}
                    self._pane.set_param(**new_params)
                    new_object._cleanup(None, new_object._temporary)
                else:
                    self._pane.object = new_object
                return

            # Replace pane entirely
            self._pane._cleanup(old_model, self._pane._temporary)
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

        for _, params in full_groupby(params, lambda x: (x.inst or x.cls, x.what)):
            p = params[0]
            pobj = (p.inst or p.cls)
            ps = [p.name for p in params]
            watcher = pobj.param.watch(update_pane, ps, p.what)
            self._callbacks[ref].append(watcher)

        return model

    def _cleanup(self, model=None, final=False):
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


class Image(DivPaneBase):
    """
    Encodes an image as base64 and wraps it in a Bokeh Div model.  
    This is an abstract base class that needs the image type
    to be specified and specific code for determining the image shape.
    
    The imgtype determines the filetype, extension, and MIME type for
    this image. Each image type (png,jpg,gif) has a base class that
    supports anything with a `_repr_X_` method (where X is `png`,
    `gif`, etc.), a local file with the given file extension, or a
    HTTP(S) url with the given extension.  Subclasses of each type can
    provide their own way of obtaining or generating a PNG.
    """

    imgtype = 'None'

    @classmethod
    def applies(cls, obj):
        imgtype = cls.imgtype
        return (hasattr(obj, '_repr_'+imgtype+'_') or
                (isinstance(obj, basestring) and
                 ((os.path.isfile(obj) and obj.endswith('.'+imgtype)) or
                  ((obj.startswith('http://') or obj.startswith('https://'))
                   and obj.endswith('.'+imgtype)))))

    def _img(self):
        if not isinstance(self.object, basestring):
            return getattr(self.object, '_repr_'+self.imgtype+'_')()
        elif os.path.isfile(self.object):
            with open(self.object, 'rb') as f:
                return f.read()
        else:
            import requests
            r = requests.request(url=self.object, method='GET')
            return r.content

    def _imgshape(self, data):
        """Calculate and return image width,height"""
        raise NotImplementedError

    def _get_properties(self):
        p = super(Image,self)._get_properties()
        data = self._img()
        width, height = self._imgshape(data)
        if self.width is not None:
            if self.height is None:
                height = int((self.width/width)*height)
            else:
                height = self.height
            width = self.width
        elif self.height is not None:
            width = int((self.height/height)*width)
            height = self.height
        b64 = base64.b64encode(data).decode("utf-8")
        src = "data:image/"+self.imgtype+";base64,{b64}".format(b64=b64)
        html = "<img src='{src}' width={width} height={height}></img>".format(
            src=src, width=width, height=height
        )
        return dict(p, width=width, height=height, text=html)


class PNG(Image):

    imgtype = 'png'
    
    @classmethod
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack('>LL', data[16:24])
        return int(w), int(h)


class GIF(Image):

    imgtype = 'gif'

    @classmethod    
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack("<HH", data[6:10])
        return int(w), int(h)
        

class JPG(Image):

    imgtype = 'jpg'
    
    @classmethod    
    def _imgshape(cls, data):
        import struct
        b = BytesIO(data)
        b.read(2)
        c = b.read(1)
        while (c and ord(c) != 0xDA):
            while (ord(c) != 0xFF): c = b.read(1)
            while (ord(c) == 0xFF): c = b.read(1)
            if (ord(c) >= 0xC0 and ord(c) <= 0xC3):
                b.read(3)
                h, w = struct.unpack(">HH", b.read(4))
                break
            else:
                b.read(int(struct.unpack(">H", b.read(2))[0])-2)
            c = b.read(1)
        return int(w), int(h)


class Matplotlib(PNG):
    """
    A Matplotlib pane renders a matplotlib figure to png and wraps the
    base64 encoded data in a bokeh Div model. The size of the image in
    pixels is determined by scaling the size of the figure in inches
    by a dpi of 72, increasing the dpi therefore controls the
    resolution of the image not the displayed size.
    """

    dpi = param.Integer(default=144, bounds=(1, None), doc="""
        Scales the dpi of the matplotlib figure.""")

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

    def _imgshape(self, data):
        """Calculate and return image width,height"""
        w, h = self.object.get_size_inches()
        return int(w*72), int(h*72)
    
    def _img(self):
        self.object.set_dpi(self.dpi)
        b = BytesIO()
        self.object.canvas.print_figure(b)
        return b.getvalue()


class RGGPlot(PNG):
    """
    An RGGPlot pane renders an r2py-based ggplot2 figure to png
    and wraps the base64-encoded data in a bokeh Div model.
    """

    height = param.Integer(default=400)

    width = param.Integer(default=400)

    dpi = param.Integer(default=144, bounds=(1, None))

    @classmethod
    def applies(cls, obj):
        return type(obj).__name__ == 'GGPlot' and hasattr(obj, 'r_repr')

    def _img(self):
        from rpy2.robjects.lib import grdevices
        from rpy2 import robjects
        with grdevices.render_to_bytesio(grdevices.png,
                 type="cairo-png", width=self.width, height=self.height,
                 res=self.dpi, antialias="subpixel") as b:
            robjects.r("print")(self.object)
        return b.getvalue()


class HTML(DivPaneBase):
    """
    HTML panes wrap HTML text in a bokeh Div model.  The
    provided object can either be a text string, or an object that
    has a `_repr_html_` method that can be called to get the HTML
    text string.  The height and width can optionally be specified, to
    allow room for whatever is being wrapped.
    """

    precedence = 0.2

    @classmethod
    def applies(cls, obj):
        return (hasattr(obj, '_repr_html_') or
                (isinstance(obj, basestring) or
                 (isinstance(obj, unicode))))

    def _get_properties(self):
        properties = super(HTML, self)._get_properties()
        text=self.object
        if hasattr(text, '_repr_html_'):
            text=text._repr_html_()
        return dict(properties, text=text)


class Str(DivPaneBase):
    """
    A Str pane renders any object for which `str()` can be called,
    escaping any HTML markup and then wrapping the resulting string in
    a bokeh Div model.  Set to a low precedence because generally one
    will want a better representation, but allows arbitrary objects to
    be used as a Pane (numbers, arrays, objects, etc.).
    """

    precedence = 0

    @classmethod
    def applies(cls, obj):
        return True
    
    def _get_properties(self):
        properties = super(Str, self)._get_properties()
        return dict(properties, text='<pre>'+escape(str(self.object))+'</pre>')



class YT(HTML):
    """
    YT panes wrap plottable objects from the YT library.  
    By default, the height and width are calculated by summing all
    contained plots, but can optionally be specified explicitly to
    provide additional space.
    """

    precedence = 0.5

    @classmethod
    def applies(cls, obj):
        return ('yt' in repr(obj) and
                hasattr(obj, "plots") and
                hasattr(obj, "_repr_html_"))

    def _get_properties(self):
        p = super(YT, self)._get_properties()

        width = height = 0
        if self.width  is None or self.height is None:
            for k,v in self.object.plots.items():
                if hasattr(v, "_repr_png_"):
                    img = v._repr_png_()
                    w,h = PNG._imgshape(img)
                    height += h
                    width = max(w, width)
        
        if self.width  is None: p["width"]  = width
        if self.height is None: p["height"] = height

        return p
