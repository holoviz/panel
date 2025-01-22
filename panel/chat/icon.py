"""
The icon module provides a low-level API for rendering chat related icons.
"""

from typing import ClassVar

import param

from .._param import Margin
from ..io.resources import CDN_DIST
from ..layout import Column, Panel
from ..reactive import ReactiveHTML
from ..widgets.base import CompositeWidget
from ..widgets.icon import ToggleIcon


class ChatReactionIcons(CompositeWidget):
    """
    A widget to display reaction icons that can be clicked on.

    Parameters
    ----------
    value : List
        The selected reactions.
    options : Dict
        A key-value pair of reaction values and their corresponding tabler icon names
        found on https://tabler-icons.io.
    active_icons : Dict
        The mapping of reactions to their corresponding active icon names;
        if not set, the active icon name will default to its "filled" version.

    Reference: https://panel.holoviz.org/reference/chat/ChatReactionIcons.html

    :Example:

    >>> ChatReactionIcons(value=["like"], options={"like": "thumb-up", "dislike": "thumb-down"})
    """

    active_icons = param.Dict(default={}, doc="""
        The mapping of reactions to their corresponding active icon names.
        If not set, the active icon name will default to its "filled" version.""")

    css_classes = param.List(default=["reaction-icons"], doc="The CSS classes of the widget.")

    margin = Margin(default=0, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    options = param.Dict(default={"favorite": "heart"}, doc="""
        A key-value pair of reaction values and their corresponding tabler icon names
        found on https://tabler-icons.io.""")

    value = param.List(default=[], doc="The active reactions.")

    default_layout = param.ClassSelector(
        default=Column, class_=Panel, is_instance=False)

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/chat_reaction_icons.css"]

    _composite_type = Column

    def __init__(self, **params):
        super().__init__(**params)
        self._render_icons()

    @param.depends("options", watch=True)
    def _render_icons(self):
        self._rendered_icons = {}
        for option, icon in self.options.items():
            active_icon = self.active_icons.get(option, "")
            icon = ToggleIcon(
                icon=icon,
                active_icon=active_icon,
                value=option in self.value,
                margin=0,
            )
            icon._reaction = option
            icon.param.watch(self._update_value, "value")
            self._rendered_icons[option] = icon
        self._composite[:] = [
            self.default_layout(
                *list(self._rendered_icons.values()),
                sizing_mode=self.param.sizing_mode,
                stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            )]

    @param.depends("value", watch=True)
    def _update_icons(self):
        for option, icon in self._rendered_icons.items():
            icon.value = option in self.value

    @param.depends("active_icons", watch=True)
    def _update_active_icons(self):
        for option, icon in self._rendered_icons.items():
            icon.active_icon = self.active_icons.get(option, "")

    def _update_value(self, event):
        reaction = event.obj._reaction
        icon_value = event.new
        reactions = self.value.copy()
        if icon_value and reaction not in self.value:
            reactions.append(reaction)
        elif not icon_value and reaction in self.value:
            reactions.remove(reaction)
        self.value = reactions


class ChatCopyIcon(ReactiveHTML):
    """
    ChatCopyIcon copies the value to the clipboard when clicked.
    To avoid sending the value to the frontend the value is only
    synced after the icon is clicked.
    """

    css_classes = param.List(default=["copy-icon"], doc="The CSS classes of the widget.")

    fill = param.String(default="none", doc="The fill color of the icon.")

    value = param.String(default=None, doc="The text to copy to the clipboard.", precedence=-1)

    _synced = param.String(default=None, doc="The text to copy to the clipboard.")

    _request_sync = param.Integer(default=0)

    _template = """
        <div
            type="button"
            id="copy-button"
            onclick="${script('request_value')}"
            style="cursor: pointer; width: ${model.width}px; height: ${model.height}px;"
            title="Copy message to clipboard"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-copy" id="copy_icon"
                width="${model.width}" height="${model.height}" viewBox="0 0 24 24"
                stroke-width="2" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"
            >
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                <path d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z"></path>
                <path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2"></path>
            </svg>
        </div>
    """

    _scripts = {
        "render": "copy_icon.setAttribute('fill', data.fill)",
        "fill": "copy_icon.setAttribute('fill', data.fill)",
        "request_value": """
          data._request_sync += 1;
          data.fill = "currentColor";
        """,
        "_synced": """
          navigator.clipboard.writeText(`${data._synced}`);
          data.fill = "none";
        """
    }

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/chat_copy_icon.css"]

    @param.depends('_request_sync', watch=True)
    def _sync(self):
        self._synced = self.value
