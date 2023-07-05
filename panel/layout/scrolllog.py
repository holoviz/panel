from __future__ import annotations

from typing import ClassVar, List

import param

from ..layout.base import ListLike
from ..reactive import ReactiveHTML


class ScrollLog(ListLike, ReactiveHTML):
    objects = param.List(
        default=[],
        doc="""
        The list of child objects that make up the layout.""",
        precedence=-1,
    )

    height = param.Integer(
        default=250,
        doc="""
        The height of the scrollable area in pixels.""",
    )

    _stylesheets: ClassVar[List[str]] = [
        """
        .scroll-log {
            overflow-y: scroll;
        }

        .scroll-down-arrow {
            /* For location */
            position: absolute;
            bottom: 0%;
            left: 50%;
            transform: translate(0%, 0%);
            /* For icon */
            cursor: pointer;
            visibility: hidden;
            font-size: 18px;
            border-radius: 50%;
            background-color: rgba(0, 0, 0, 0.25);
            color: white;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            /* For animation */
            opacity: 0;
            transition: visibility 0s, opacity 0.2s ease-in-out;
        }

        .visible {
            visibility: visible;
            opacity: 1;
        }
    """
    ]

    _template = """
        <div id="scrollLog" class="scroll-log" style="height: {{ height }}px; min-width: 75px">
            <div id="scrollDownArrow" class="scroll-down-arrow">⬇</div>
            {% for obj in objects %}
            <div class="scroll-log-item" data-id="{{ id(obj) }}">
                <div id="content" class="scroll-log-content">${obj}</div>
            </div>
            {% endfor %}
        </div>
    """

    _scripts = {
        "render": """
            scrollDownArrow.addEventListener("click", () => {
                self.scroll_to_bottom();
            });

            var scrollThreshold = 20;
            scrollLog.addEventListener("scroll", () => {
                var scrollDistanceFromBottom = (
                    scrollLog.scrollHeight - scrollLog.scrollTop - scrollLog.clientHeight
                );
                if (scrollDistanceFromBottom < scrollThreshold) {
                    scrollDownArrow.classList.remove("visible");
                } else {
                    scrollDownArrow.classList.add("visible");
                }
            });
        """,
        "after_layout": """
            self.scroll_to_bottom();
        """,
        "scroll_to_bottom": """
            scrollLog.scrollTop = scrollLog.scrollHeight;
        """
    }

    def __init__(self, *objects, **params):
        if "sizing_mode" not in params:
            params["sizing_mode"] = "stretch_width"
        super().__init__(objects=list(objects), **params)
