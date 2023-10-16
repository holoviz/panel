"""
The icon module provides a low-level API for rendering chat related icons.
"""

from typing import ClassVar, List

import param
import requests

from ..io.cache import cache
from ..io.resources import CDN_DIST
from ..io.state import state
from ..pane.image import SVG
from ..reactive import ReactiveHTML

# if user cannot connect to internet
MISSING_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-help-square" width="15" height="15" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M3 5a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14z"></path>
        <path d="M12 16v.01"></path>
        <path d="M12 13a2 2 0 0 0 .914 -3.782a1.98 1.98 0 0 0 -2.414 .483"></path>
    </svg>
"""  # noqa: E501

MISSING_FILLED_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-help-square-filled" width="15" height="15" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M19 2a3 3 0 0 1 2.995 2.824l.005 .176v14a3 3 0 0 1 -2.824 2.995l-.176 .005h-14a3 3 0 0 1 -2.995 -2.824l-.005 -.176v-14a3 3 0 0 1 2.824 -2.995l.176 -.005h14zm-7 13a1 1 0 0 0 -.993 .883l-.007 .117l.007 .127a1 1 0 0 0 1.986 0l.007 -.117l-.007 -.127a1 1 0 0 0 -.993 -.883zm1.368 -6.673a2.98 2.98 0 0 0 -3.631 .728a1 1 0 0 0 1.44 1.383l.171 -.18a.98 .98 0 0 1 1.11 -.15a1 1 0 0 1 -.34 1.886l-.232 .012a1 1 0 0 0 .111 1.994a3 3 0 0 0 1.371 -5.673z" stroke-width="0" fill="currentColor"></path>
    </svg>
"""  # noqa: E501


class ChatReactionIcons(ReactiveHTML):
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

    active_icons = param.Dict(
        default={},
        doc="""
        The mapping of reactions to their corresponding active icon names;
        if not set, the active icon name will default to its "filled" version.""",
    )

    options = param.Dict(
        default={"favorite": "heart"},
        doc="""
        A key-value pair of reaction values and their corresponding tabler icon names
        found on https://tabler-icons.io.""",
    )

    value = param.List(doc="The active reactions.")

    _reactions = param.List(
        doc="""
        The list of reactions, which is the same as the keys of the options dict;
        primarily needed as a workaround for quirks of ReactiveHTML."""
    )

    _svgs = param.List(
        doc="""
        The list of SVGs corresponding to the active reactions."""
    )

    _base_url = param.String(
        default="https://tabler-icons.io/static/tabler-icons/icons/",
        doc="""
        The base URL for the SVGs.""",
    )

    _template = """
    <div id="reaction-icons" class="reaction-icons">
        {% for option in options %}
        <span
            type="button"
            id="reaction-{{ loop.index0 }}"
            onclick="${script('toggle_value')}"
            style="cursor: pointer; width: ${model.width}px; height: ${model.height}px;"
            title="{{ _reactions[loop.index0]|title }}"
        >
            ${_svgs[{{ loop.index0 }}]}
        </span>
        {% endfor %}
    </div>
    """

    _scripts = {
        "toggle_value": """
            svg = event.target.shadowRoot.querySelector("svg");
            const reaction = svg.getAttribute("alt");
            const icon_name = data.options[reaction];
            let src;
            if (data.value.includes(reaction)) {
                src = `${data._base_url}${icon_name}.svg`;
                data.value = data.value.filter(r => r !== reaction);
            } else {
                src = reaction in data.active_icons
                    ? `${data._base_url}${data.active_icons[reaction]}.svg`
                    : `${data._base_url}${icon_name}-filled.svg`;
                data.value = [...data.value, reaction];
            }
            event.target.src = src;
        """
    }

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_reaction_icons.css"]

    def _get_label(self, active: bool, reaction: str, icon: str):
        if active and reaction in self.active_icons:
            icon_label = self.active_icons[reaction]
        elif active:
            icon_label = f"{icon}-filled"
        else:
            icon_label = icon
        return icon_label

    @cache
    def _fetch_svg(self, icon_label: str):
        src = f"{self._base_url}{icon_label}.svg"
        with requests.get(src) as response:
            response.raise_for_status()
            svg = response.text
        return svg

    def _stylize_svg(self, svg, reaction):
        if b"dark" in state.session_args.get("theme", []):
            svg = svg.replace('stroke="currentColor"', 'stroke="white"')
            svg = svg.replace('fill="currentColor"', 'fill="white"')
        if self.width:
            svg = svg.replace('width="24"', f'width="{self.width}px"')
        if self.height:
            svg = svg.replace('height="24"', f'height="{self.height}px"')
        svg = svg.replace("<svg", f'<svg alt="{reaction}"')
        return svg

    @param.depends(
        "value",
        "options",
        "active_icons",
        "width",
        "height",
        watch=True,
        on_init=True,
    )
    def _update_icons(self):
        self._reactions = list(self.options.keys())
        svgs = []
        for reaction, icon in self.options.items():
            active = reaction in self.value
            icon_label = self._get_label(active, reaction, icon)
            try:
                svg = self._fetch_svg(icon_label)
            except Exception:
                svg = MISSING_FILLED_SVG if active else MISSING_SVG
            svg = self._stylize_svg(svg, reaction)
            # important not to encode to keep the alt text!
            svg_pane = SVG(
                svg,
                sizing_mode=None,
                alt_text=reaction,
                encode=False,
                margin=0,
            )
            svgs.append(svg_pane)
        self._svgs = svgs

        for reaction in self.value:
            if reaction not in self._reactions:
                self.value.remove(reaction)


class ChatCopyIcon(ReactiveHTML):
    value = param.String(default=None, doc="The text to copy to the clipboard.")

    fill = param.String(default="none", doc="The fill color of the icon.")

    _template = """
        <div
            type="button"
            id="copy-button"
            onclick="${script('copy_to_clipboard')}"
            style="cursor: pointer; width: ${model.width}px; height: ${model.height}px;"
            title="Copy message to clipboard"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-copy" id="copy-icon"
                width="${model.width}" height="${model.height}" viewBox="0 0 24 24"
                stroke-width="2" stroke="currentColor" fill=${fill} stroke-linecap="round" stroke-linejoin="round"
            >
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                <path d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z"></path>
                <path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2"></path>
            </svg>
        </div>
    """

    _scripts = {"copy_to_clipboard": """
        navigator.clipboard.writeText(`${data.value}`);
        data.fill = "currentColor";
        setTimeout(() => data.fill = "none", 50);
    """}

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_copy_icon.css"]
