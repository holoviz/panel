"""
A Material Paper with the disabled behavior of the classic WidgetBox.
"""
from __future__ import annotations

import param

from panel_material_ui.layout import Paper

from ...widgets.base import WidgetBase


class WidgetBox(Paper):
    """
    The `WidgetBox` groups widgets on a Material `Paper` surface and, like
    the classic `WidgetBox`, can disable all the widgets it contains.

    :Example:

    >>> WidgetBox(TextInput(label='Name'), Button(label='Submit'), disabled=True)
    """

    disabled = param.Boolean(default=False, doc="""
        Whether the widgets in the box are disabled.""")

    _rename = {'disabled': None}

    def __init__(self, *objects, **params):
        super().__init__(*objects, **params)
        if self.disabled:
            self._disable_widgets()

    @param.depends('disabled', 'objects', watch=True)
    def _disable_widgets(self) -> None:
        # The Material widgets derive from WidgetBase, not the classic Widget.
        for obj in self.select(WidgetBase):
            obj.disabled = self.disabled


__all__ = ("WidgetBox",)
