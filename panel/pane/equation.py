"""
Renders objects representing equations including LaTeX strings and
SymPy objects.
"""
from __future__ import absolute_import, division, unicode_literals

import sys

from six import string_types

import param

from ..models import KaTeX
from .markup import DivPaneBase


def is_sympy_expr(obj):
    """Test for sympy.Expr types without usually needing to import sympy"""
    if 'sympy' in sys.modules and 'sympy' in str(type(obj).__class__):
        import sympy
        if isinstance(obj, sympy.Expr):
            return True
    return False


class LaTeX(DivPaneBase):

    _bokeh_model = KaTeX

    @classmethod
    def applies(cls, obj):
        if is_sympy_expr(obj) or hasattr(obj, '_repr_latex_'):
            return 0.05
        elif isinstance(obj, string_types):
            return None
        else:
            return False

    def _get_properties(self):
        properties = super(KaTeX, self)._get_properties()
        obj = self.object
        if hasattr(obj, '_repr_latex_'):
            obj = obj._repr_latex_()
        elif is_sympy_expr(obj):
            import sympy
            obj = r'$'+sympy.latex(obj)+'$'
        return dict(properties, text=obj)
