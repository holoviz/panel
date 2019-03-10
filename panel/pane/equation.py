"""
Renders objects representing equations including LaTeX strings and
SymPy objects.
"""
from __future__ import absolute_import, division, unicode_literals

import sys

from six import string_types

import param

from .image import PNG


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

    # Priority is dependent on the data type
    priority = None

    size = param.Number(default=25, bounds=(1, 100), doc="""
        Size of the rendered equation.""")

    dpi = param.Number(default=72, bounds=(1, 1900), doc="""
        Resolution per inch for the rendered equation.""")

    _rerender_params = ['object', 'size', 'dpi']

    @classmethod
    def applies(cls, obj):
        if is_sympy_expr(obj) or hasattr(obj, '_repr_latex_'):
            try:
                import matplotlib, PIL # noqa
            except ImportError:
                return False
            return 0.05
        elif isinstance(obj, string_types):
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
