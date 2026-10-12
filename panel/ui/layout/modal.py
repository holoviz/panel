"""
A Material Dialog with the API of the classic Modal.
"""
from __future__ import annotations

import typing as t

import param

from panel_material_ui.layout import Dialog
from panel_material_ui.widgets import Button


class Modal(Dialog):
    """
    A modal dialog that can be opened and closed, implemented by the Material
    `Dialog` but keeping the classic `Modal` defaults and methods.

    :Example:

    >>> modal = Modal('Some content')
    >>> Column(modal.create_button('show', label='Open'), modal)
    """

    background_close = param.Boolean(default=True, doc="""
        Whether to enable closing the modal when clicking the background.
        Alias of `close_on_click`.""")

    close_on_click = param.Boolean(default=True, doc="""
        Close when clicking outside the Dialog area.""")

    show_close_button = param.Boolean(default=True, doc="""
        Whether to show a close button in the modal.""")

    _rename = {'background_close': None}

    def __init__(self, *objects, **params):
        if 'background_close' in params:
            params.setdefault('close_on_click', params['background_close'])
        elif 'close_on_click' in params:
            params['background_close'] = params['close_on_click']
        super().__init__(*objects, **params)

    @param.depends('background_close', watch=True)
    def _sync_close_on_click(self):
        self.close_on_click = self.background_close

    @param.depends('close_on_click', watch=True)
    def _sync_background_close(self):
        self.background_close = self.close_on_click

    def show(self):
        self.open = True

    def hide(self):
        self.open = False

    def toggle(self):
        self.open = not self.open

    def create_button(self, action: t.Literal["show", "hide", "toggle"], **kwargs) -> Button:
        """Create a button to show, hide or toggle the modal."""
        if action not in ('show', 'hide', 'toggle'):
            raise TypeError(f"Invalid action: {action}")
        callback = getattr(self, action)
        return Button(on_click=lambda *e: callback(), **kwargs)


__all__ = ("Modal",)
