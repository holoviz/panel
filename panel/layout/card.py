from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, ClassVar

import param

from ..models import Card as BkCard
from ..viewable import Child
from .base import Column, Row

if TYPE_CHECKING:
    from bokeh.model import Model

    from ..viewable import Viewable


class Card(Column):
    """
    A `Card` layout allows arranging multiple panel objects in a
    collapsible, vertical container with a header bar.

    Reference: https://panel.holoviz.org/reference/layouts/Card.html

    :Example:

    >>> pn.Card(
    ...     some_widget, some_pane, some_python_object,
    ...     title='Card', styles=dict(background='WhiteSmoke'),
    ... )
    """

    active_header_background = param.String(default=None, doc="""
        A valid CSS color for the header background when not collapsed.""")

    button_css_classes = param.List(default=['card-button'], doc="""
        CSS classes to apply to the button element.""")

    collapsible = param.Boolean(default=True, doc="""
        Whether the Card should be expandable and collapsible.""")

    collapsed = param.Boolean(default=False, doc="""
        Whether the contents of the Card are collapsed.""")

    css_classes = param.List(default=['card'], doc="""
        CSS classes to apply to the overall Card.""")

    header = Child(doc="""
        A Panel component to display in the header bar of the Card.
        Will override the given title if defined.""")

    header_background = param.String(doc="""
        A valid CSS color for the header background.""")

    header_color = param.String(doc="""
        A valid CSS color to apply to the header text.""")

    header_css_classes = param.List(default=['card-header'], doc="""
        CSS classes to apply to the header element.""")

    hide_header = param.Boolean(default=False, doc="""
        Whether to skip rendering the header.""")

    title_css_classes = param.List(default=['card-title'], doc="""
        CSS classes to apply to the header title.""")

    title = param.String(doc="""
        A title to be displayed in the Card header, will be overridden
        by the header if defined.""")

    _bokeh_model: ClassVar[type[Model]] = BkCard

    _rename: ClassVar[Mapping[str, str | None]] = {
        'title': None, 'header': None, 'title_css_classes': None
    }

    def __init__(self, *objects, **params):
        self._header_layout = Row(css_classes=['card-header-row'], sizing_mode='stretch_width')
        super().__init__(*objects, **params)
        self._header = None
        self.param.watch(self._update_header, ['title', 'header', 'title_css_classes'])
        self._update_header()

    def select(
        self, selector: type | Callable[[Viewable], bool] | None = None
    ) -> list[Viewable]:
        return self._header_layout.select(selector) + super().select(selector)

    def _cleanup(self, root: Model | None = None) -> None:
        super()._cleanup(root)
        self._header_layout._cleanup(root)

    def _update_header(self, *events):
        from ..pane import HTML, panel
        if self.header is None:
            params = {
                'object': f'<h3>{self.title}</h3>' if self.title else "&#8203;",
                'css_classes': self.title_css_classes,
                'margin': (5, 0),
            }
            if self.header_color:
                params['styles'] = {'color': self.header_color}
            if self._header is not None:
                self._header.param.update(**params)
                return
            else:
                self._header = item = HTML(**params)
        else:
            item = panel(self.header)
            self._header = None
        self._header_layout[:] = [item]

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        ref = root.ref['id']
        models, old_models = super()._get_objects(model, old_objects, doc, root, comm)
        if ref in self._header_layout._models:
            header = self._header_layout._models[ref][0]
            old_models.append(header)
        else:
            header = self._header_layout._get_model(doc, root, model, comm)
        return [header]+models, old_models

    def _compute_sizing_mode(self, children, props):
        return super()._compute_sizing_mode(children[1:], props)
