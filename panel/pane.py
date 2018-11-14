"""
Panes allow wrapping external objects and rendering them as part of
a dashboard.
"""
from __future__ import absolute_import

import os
import sys
import base64
from io import BytesIO

try:
    from html import escape
except:
    from cgi import escape

import param

from bokeh.layouts import WidgetBox as _BkWidgetBox
from bokeh.models import LayoutDOM, CustomJS, Widget as _BkWidget, Div as _BkDiv

from .layout import Panel, Row
from .util import Div, basestring, param_reprs, push, remove_root
from .viewable import Reactive, Viewable


def panel(obj, **kwargs):
    """
    Creates a panel from any supplied object by wrapping it in a pane
    and returning a corresponding Panel.

    Arguments
    ---------
    obj: object
       Any object to be turned into a Panel
    **kwargs: dict
       Any keyword arguments to be passed to the applicable Pane

    Returns
    -------
    layout: Viewable
       A Viewable representation of the input object
    """
    if isinstance(obj, Viewable):
        return obj
    internal = kwargs.pop('_internal', False)
    pane = PaneBase.get_pane_type(obj)(obj, **kwargs)
    if internal and len(pane.layout) == 1:
        return pane.layout[0]
    return pane.layout


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

    default_layout = param.ClassSelector(default=Row, class_=(Panel),
                                         is_instance=False)

    object = param.Parameter(default=None, doc="""
        The object being wrapped, which will be converted into a Bokeh model.""")

    # When multiple Panes apply to an object, the one with the highest
    # numerical precedence is selected. The default is an intermediate value.
    # If set to None, applies method will be called to get a precedence
    # value for a specific object type.
    precedence = 0.5

    # Declares whether Pane supports updates to the Bokeh model
    _updates = False

    __abstract = True

    @classmethod
    def applies(cls, obj):
        """
        Given the object return a boolean indicating whether the Pane
        can render the object. If the precedence of the pane is set to
        None, this method may also be used to define a precedence
        depending on the object being rendered.
        """
        return None

    @classmethod
    def get_pane_type(cls, obj):
        if isinstance(obj, Viewable):
            return type(obj)
        descendents = []
        for p in param.concrete_descendents(PaneBase).values():
            precedence = p.applies(obj) if p.precedence is None else p.precedence
            if isinstance(precedence, bool) and precedence:
                raise ValueError('If a Pane declares no precedence '
                                 'the applies method should return a '
                                 'precedence value specific to the '
                                 'object type or False, but the %s pane '
                                 'declares no precedence.' % p.__name__)
            elif precedence is None or precedence is False:
                continue
            descendents.append((precedence, p))
        pane_types = reversed(sorted(descendents, key=lambda x: x[0]))
        for _, pane_type in pane_types:
            applies = pane_type.applies(obj)
            if isinstance(applies, bool) and not applies: continue
            return pane_type
        raise TypeError('%s type could not be rendered.' % type(obj).__name__)

    def __repr__(self, depth=0):
        cls = type(self).__name__
        params = param_reprs(self, ['object'])
        obj = type(self.object).__name__
        template = '{cls}({obj}, {params})' if params else '{cls}({obj})'
        return template.format(cls=cls, params=', '.join(params), obj=obj)

    def __init__(self, object, **params):
        applies = self.applies(object)
        if isinstance(applies, bool) and not applies:
            raise ValueError("%s pane does not support objects of type '%s'" %
                             (type(self).__name__, type(object).__name__))

        super(PaneBase, self).__init__(object=object, **params)
        self.layout = self.default_layout(self)

    def _get_root(self, doc, comm=None):
        root = self.layout._get_model(doc, comm=comm)
        self._preprocess(root)
        return root

    def _cleanup(self, root=None, final=False):
        super(PaneBase, self)._cleanup(root, final)
        if final:
            self.object = None

    def _update(self, model):
        """
        If _updates=True this method is used to update an existing Bokeh
        model instead of replacing the model entirely. The supplied model
        should be updated with the current state.
        """
        raise NotImplementedError

    def _link_object(self, doc, root, parent, comm=None):
        """
        Links the object parameter to the rendered Bokeh model, triggering
        an update when the object changes.
        """
        ref = root.ref['id']

        def update_pane(change):
            old_model = self._models[ref]

            # Pane supports model updates
            if self._updates:
                def update_models():
                    self._update(old_model)
            else:
                # Otherwise replace the whole model
                new_model = self._get_model(doc, root, parent, comm)
                def update_models():
                    try:
                        index = parent.children.index(old_model)
                    except IndexError:
                        self.warning('%s pane model %s could not be replaced '
                                     'with new model %s, ensure that the '
                                     'parent is not modified at the same '
                                     'time the panel is being updated.' %
                                     (type(self).__name__, old_model, new_model))
                    else:
                        parent.children[index] = new_model

            if comm:
                update_models()
                push(doc, comm)
            else:
                doc.add_next_tick_callback(update_models)

        if ref not in self._callbacks:
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

        ref = root.ref['id']
        for js in model.select({'type': CustomJS}):
            js.code = js.code.replace(model.ref['id'], ref)

        if model._document and doc is not model._document:
            remove_root(model, doc)

        self._models[ref] = model
        self._link_object(doc, root, parent, comm)
        return model



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
        self._models[root.ref['id']] = model
        self._link_object(doc, root, parent, comm)
        return model

    def _update(self, model):
        div = model if isinstance(model, _BkDiv) else model.children[0].children[0]
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
        if isinstance(data, str):
            data = base64.b64decode(data)
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


class SVG(Image):

    imgtype = 'svg'

    @classmethod
    def applies(cls, obj):
        return (super(SVG, cls).applies(obj) or
                (isinstance(obj, basestring) and obj.lstrip().startswith('<svg')))

    def _img(self):
        if (isinstance(self.object, basestring) and
            self.object.lstrip().startswith('<svg')):
            return self.object
        return super(SVG, self)._img()

    def _imgshape(self, data):
        return (self.width, self.height)

    def _get_properties(self):
        p = super(Image, self)._get_properties()
        data = self._img()
        width, height = self._imgshape(data)
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        b64 = base64.b64encode(data).decode("utf-8")
        src = "data:image/svg+xml;base64,{b64}".format(b64=b64)
        html = "<img src='{src}' width={width} height={height}></img>".format(
            src=src, width=width, height=height
        )
        return dict(p, width=width, height=height, text=html)


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


def latex_to_img(text, size=25, dpi=100):
    """
    Returns PIL image for LaTeX equation text, using matplotlib's rendering.
    Usage: latex_to_img(r'$\frac(x}{y^2}$')
    From https://stackoverflow.com/questions/1381741.
    """
    import matplotlib.pyplot as plt
    from PIL import Image, ImageChops
    import io

    buf = io.BytesIO()
    with plt.rc_context({'text.usetex': False, 'mathtext.fontset': 'stix'}):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.axis('off')
        ax.text(0.05, 0.5, '{text}'.format(text=text), size=size)
        fig.set_dpi(dpi)
        fig.canvas.print_figure(buf)
        plt.close(fig)

    im = Image.open(buf)
    bg = Image.new(im.mode, im.size, (255, 255, 255, 255))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    return im.crop(bbox)


def make_transparent(img, bg=(255, 255, 255, 255)):
    """Given a PIL image, makes the specified background color transparent."""
    img = img.convert("RGBA")
    clear = bg[0:3]+(0,)
    pixdata = img.load()

    width, height = img.size
    for y in range(height):
        for x in range(width):
            if pixdata[x,y] == bg:
                pixdata[x,y] = clear
    return img


def is_sympy_expr(obj):
    """Test for sympy.Expr types without usually needing to import sympy"""
    if 'sympy' in sys.modules and 'sympy' in str(type(obj).__class__):
        import sympy
        if isinstance(obj, sympy.Expr):
            return True
    return False


class LaTeX(PNG):
    """
    Matplotlib-based LaTeX-syntax equation.
    Requires matplotlib and pillow.
    See https://matplotlib.org/users/mathtext.html for what is supported.
    """

    # Precedence is dependent on the data type
    precedence = None

    size = param.Number(default=25, bounds=(1, 100), doc="""
        Size of the rendered equation.""")

    dpi = param.Number(default=72, bounds=(1, 1900), doc="""
        Resolution per inch for the rendered equation.""")

    @classmethod
    def applies(cls, obj):
        if is_sympy_expr(obj) or hasattr(obj, '_repr_latex_'):
            try:
                import matplotlib, PIL # noqa
            except ImportError:
                return False
            return 0.05
        elif isinstance(obj, basestring):
            return None
        else:
            return False

    def _imgshape(self, data):
        """Calculate and return image width,height"""
        w, h = super(LaTeX, self)._imgshape(data)
        w, h = (w/self.dpi), (h/self.dpi)
        return int(w*72), int(h*72)

    def _img(self):
        obj=self.object # Default: LaTeX string

        if hasattr(obj, '_repr_latex_'):
            obj = obj._repr_latex_()
        elif is_sympy_expr(obj):
            import sympy
            obj = r'$'+sympy.latex(obj)+'$'

        return make_transparent(latex_to_img(obj, self.size, self.dpi))._repr_png_()


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

    # Precedence is dependent on the data type
    precedence = None

    @classmethod
    def applies(cls, obj):
        if hasattr(obj, '_repr_html_'):
            return 0.2
        elif isinstance(obj, basestring):
            return None
        else:
            return False

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


class Markdown(DivPaneBase):
    """
    A Markdown pane renders the markdown markup language to HTML and
    displays it inside a bokeh Div model. It has no explicit
    precedence since it cannot be easily be distinguished from a
    standard string, therefore it has to be invoked explicitly.
    """

    # Precedence depends on the data type
    precedence = None

    @classmethod
    def applies(cls, obj):
        if hasattr(obj, '_repr_markdown_'):
            return 0.3
        elif isinstance(obj, basestring):
            return 0.1
        else:
            return False

    def _get_properties(self):
        import markdown
        data = self.object
        if not isinstance(data, basestring):
            data = data._repr_markdown_()
        properties = super(Markdown, self)._get_properties()
        extensions = ['markdown.extensions.extra', 'markdown.extensions.smarty']
        html = markdown.markdown(self.object, extensions=extensions,
                                 output_format='html5')
        return dict(properties, text=html)


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
