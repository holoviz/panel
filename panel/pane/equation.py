"""
Renders objects representing equations including LaTeX strings and
SymPy objects.
"""
from __future__ import annotations

import sys

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, ClassVar

import param  # type: ignore

from pyviz_comms import Comm, JupyterComm  # type: ignore

from ..io.resources import CDN_DIST
from ..util import lazy_load
from .base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model


class LaTeX(ModelPane):
    r"""
    The `LaTeX` pane allows rendering LaTeX equations. It uses either
    `KaTeX` or `MathJax` depending on the defined renderer.

    By default it will use the renderer loaded in the extension
    (e.g. `pn.extension('katex')`), defaulting to `KaTeX` if both are loaded.

    Reference: https://panel.holoviz.org/reference/panes/LaTeX.html

    :Example:

    >>> pn.extension('katex')
    >>> LaTeX(
    ...     'The LaTeX pane supports two delimiters: $LaTeX$ and \(LaTeX\)',
    ...     styles={'font-size': '18pt'}, width=800
    ... )
    """

    renderer = param.Selector(default=None, allow_None=True,
                                    objects=['katex', 'mathjax'], doc="""
        The JS renderer used to render the LaTeX expression. Defaults to katex.""")

    # Priority is dependent on the data type
    priority: ClassVar[float | bool | None] = None

    _rename: ClassVar[Mapping[str, str | None]] = {
        'renderer': None, 'object': 'text'
    }

    _updates: ClassVar[bool] = True

    _stylesheets: ClassVar[list[str]] = [
        f'{CDN_DIST}css/katex.css'
    ]

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if hasattr(obj, '_repr_latex_'):
            return 0.05
        elif isinstance(obj, str):
            return None
        else:
            return False

    def _get_model_type(self, root: Model | None, comm: Comm | None) -> type[Model]:
        module = self.renderer
        if module is None:
            if 'panel.models.mathjax' in sys.modules and 'panel.models.katex' not in sys.modules:
                module = 'mathjax'
            else:
                module = 'katex'
            self.renderer = module
        model = 'KaTeX' if module == 'katex' else 'MathJax'
        return lazy_load(f'panel.models.{module}', model, isinstance(comm, JupyterComm), root)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model_type = self._get_model_type(root, comm)
        model = model_type(**self._get_properties(doc))
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _transform_object(self, obj: Any) -> dict[str, Any]:
        if obj is None:
            obj = ''
        elif hasattr(obj, '_repr_latex_'):
            obj = obj._repr_latex_()
        if self.renderer == 'mathjax' and obj.startswith('$') and not obj.startswith('$$'):
            obj = f'${obj}$'
        return dict(object=obj)
