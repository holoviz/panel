"""
Renders objects representing equations including LaTeX strings and
SymPy objects.
"""
from __future__ import absolute_import, division, unicode_literals

import sys

from six import string_types

import param

from pyviz_comms import JupyterComm

from .markup import DivPaneBase


def is_sympy_expr(obj):
    """Test for sympy.Expr types without usually needing to import sympy"""
    if 'sympy' in sys.modules and 'sympy' in str(type(obj).__class__):
        import sympy
        if isinstance(obj, sympy.Expr):
            return True
    return False


class LaTeX(DivPaneBase):

    renderer = param.ObjectSelector(default=None, allow_None=True,
                                    objects=['katex', 'mathjax'], doc="""
        The JS renderer used to render the LaTeX expression.""")

    # Priority is dependent on the data type
    priority = None

    _rename = {"renderer": None}

    @classmethod
    def applies(cls, obj):
        if is_sympy_expr(obj) or hasattr(obj, '_repr_latex_'):
            return 0.05
        elif isinstance(obj, string_types):
            return None
        else:
            return False

    def _get_model_type(self, comm):
        module = self.renderer
        if module is None:
            if 'panel.models.mathjax' in sys.modules and 'panel.models.katex' not in sys.modules:
                module = 'mathjax'
            else:
                module = 'katex'
        model = 'KaTeX' if module == 'katex' else 'MathJax'
        if 'panel.models.'+module not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning('{model} model was not imported on instantiation '
                                   'and may not render in a notebook. Restart '
                                   'the notebook kernel and ensure you load '
                                   'it as part of the extension using:'
                                   '\n\npn.extension(\'{module}\')\n'.format(
                                       module=module, model=model))
            __import__('panel.models.'+module)
        return getattr(sys.modules['panel.models.'+module], model)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._get_model_type(comm)(**self._get_properties())
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _get_properties(self):
        properties = super(LaTeX, self)._get_properties()
        obj = self.object
        if obj is None:
            obj = ''
        elif hasattr(obj, '_repr_latex_'):
            obj = obj._repr_latex_()
        elif is_sympy_expr(obj):
            import sympy
            obj = r'$'+sympy.latex(obj)+'$'
        return dict(properties, text=obj)
