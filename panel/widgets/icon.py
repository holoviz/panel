from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import ClassVar

import param

from ..io.resources import CDN_DIST
from ..models import (
    ButtonIcon as _PnButtonIcon, ToggleIcon as _PnToggleIcon,
    _ClickableIcon as _PnClickableIcon,
)
from ._mixin import TooltipMixin
from .base import Widget
from .button import ButtonClick, _ClickButton


class _ClickableIcon(Widget):

    active_icon = param.String(default='', doc="""
        The name of the icon to display when toggled from
        [tabler-icons.io](https://tabler-icons.io)/ or an SVG.""")

    icon = param.String(default='heart', doc="""
        The name of the icon to display from
        [tabler-icons.io](https://tabler-icons.io)/ or an SVG.""")

    size = param.String(default=None, doc="""
        An explicit size specified as a CSS font-size, e.g. '1.5em' or '20px'.""")

    value = param.Boolean(default=False, doc="""
        Whether the icon is toggled on or off.""")

    _widget_type = _PnClickableIcon

    _rename: ClassVar[Mapping[str, str | None]] = {
        **TooltipMixin._rename, 'name': 'title',
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'description': None,
    }

    _stylesheets: ClassVar[list[str]] = [f'{CDN_DIST}css/icon.css']

    def __init__(self, **params):
        super().__init__(**params)

    @param.depends('icon', 'active_icon', watch=True, on_init=True)
    def _update_icon(self):
        if not self.icon:
            raise ValueError('The icon parameter must not be empty.')

        icon_is_svg = self.icon.startswith('<svg')
        if icon_is_svg and not self.active_icon:
            raise ValueError(
                'The active_icon parameter must not be empty if icon is an SVG.'
            )


class ToggleIcon(_ClickableIcon, TooltipMixin):
    """
    The `ToggleIcon` widget allows toggling a single condition between True/False states. This
    widget is interchangeable with the `Checkbox` and `Toggle` widget.

    This widget incorporates a `value` attribute, which alternates between `False` and `True`.

    Reference: https://panel.holoviz.org/reference/widgets/ToggleIcon.html

    :Example:

    >>> pn.widgets.ToggleIcon(
    ...     icon="thumb-up", active_icon="thumb-down", size="4em", description="Like"
    ... )
    """

    _widget_type = _PnToggleIcon


class ButtonIcon(_ClickableIcon, _ClickButton, TooltipMixin):
    """
    The `ButtonIcon` widget facilitates event triggering upon button clicks.

    This widget displays a default `icon` initially. Upon being clicked, an `active_icon` appears
    for a specified `toggle_duration`.

    For instance, the `ButtonIcon` can be effectively utilized to implement a feature akin to
    ChatGPT's copy-to-clipboard button.

    The button incorporates a `value` attribute, which alternates between `False` and `True` as the
    click event is processed.

    Furthermore, it includes an `clicks` attribute, enabling subscription to click events for
    further actions or monitoring.

    Reference: https://panel.holoviz.org/reference/widgets/ButtonIcon.html

    :Example:

    >>> button_icon = pn.widgets.ButtonIcon(
    ...     icon='clipboard',
    ...     active_icon='check',
    ...     description='Copy',
    ...     toggle_duration=2000
    ... )
    """

    clicks = param.Integer(default=0, doc="""
        The number of times the button has been clicked.""")

    toggle_duration = param.Integer(default=75, doc="""
        The number of milliseconds the active_icon should be shown for
        and how long the button should be disabled for.""")

    value = param.Boolean(default=False, doc="""
        Toggles from False to True while the event is being processed.""")

    _widget_type = _PnButtonIcon

    _rename: ClassVar[Mapping[str, str | None]] = {
        **TooltipMixin._rename, 'name': 'title', 'clicks': None,
    }

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'event:button_click': None,
    }

    def __init__(self, **params):
        if "active_icon" not in params:
            params["active_icon"] = "check"
        click_handler = params.pop('on_click', None)
        super().__init__(**params)
        if click_handler:
            self.on_click(click_handler)

    def on_click(
        self, callback: Callable[[param.parameterized.Event], None]
    ) -> param.parameterized.Watcher:
        """
        Register a callback to be executed when the button is clicked.

        The callback is given an `Event` argument declaring the number of clicks.

        Parameters
        ----------
        callback: (Callable[[param.parameterized.Event], None])
            The function to run on click events. Must accept a positional `Event` argument

        Returns
        -------
        watcher: param.Parameterized.Watcher
          A `Watcher` that executes the callback when the MenuButton is clicked.
        """
        return self.param.watch(callback, 'clicks', onlychanged=False)

    def _process_event(self, event: ButtonClick) -> None:
        """
        Process a button click event.
        """
        self.param.trigger('value')
        self.clicks += 1
