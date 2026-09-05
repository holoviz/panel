"""
This module contains functionality to make any Panel component look
like it is loading and disabled.
"""
from __future__ import annotations

import typing as t

from ..config import config

LOADING_INDICATOR_CSS_CLASS = "pn-loading"

def _design() -> type:
    """
    Resolves the Design that declares the loading indicator behavior,
    falling back to the Design baseclass which implements the classic,
    CSS driven loading indicator.
    """
    from ..theme.base import Design
    return config.design or Design


def loading_options() -> dict[str, t.Any]:
    """
    Returns the options that control the appearance of the loading
    indicator, i.e. the spinner, color and max_height.
    """
    return _design().loading_options()


def loading_css_classes() -> list[str]:
    """
    Returns the CSS classes that mark a component as loading.
    """
    return _design().loading_css_classes()


def loading_css() -> str:
    """
    Returns the CSS that styles the loading indicator.
    """
    return _design().loading_css()


def loading_resources(
    inline: bool = False, include_base: bool = True, dist_path: str | None = None
) -> dict[str, list[str]]:
    """
    Returns the resources required to render the loading indicator.

    Parameters
    ----------
    inline: bool
        Whether to inline the stylesheets instead of linking them.
    include_base: bool
        Whether to include the base loading stylesheet.
    dist_path: str | None
        The path the Panel distribution is served from.

    Returns
    -------
    Dictionary containing stylesheet URLs and raw CSS.
    """
    return _design().loading_resources(
        inline=inline, include_base=include_base, dist_path=dist_path
    )


def _loading_css_classes(item) -> list[str]:
    """
    Resolves the loading CSS classes for a specific component, honoring
    the Design it was rendered with over the globally configured Design.
    """
    design = getattr(item, '_design', None)
    return design.loading_css_classes() if design else loading_css_classes()


def _add_css_classes(item, css_classes):
    if not item.css_classes:
        item.css_classes = css_classes
    else:
        new_classes = [css_class for css_class in css_classes
                       if css_class not in item.css_classes]
        item.css_classes = item.css_classes + new_classes


def _remove_css_classes(item, css_classes):
    if not item.css_classes:
        return
    item.css_classes = [css_class for css_class in item.css_classes
                        if css_class not in css_classes]


def start_loading_spinner(*objects):
    """
    Changes the appearance of the specified panel objects to indicate
    that they are loading.

    This is done by

    * adding a small spinner on top
    * graying out the panel
    * disabling the panel
    * and changing the mouse cursor to a spinner when hovering over the panel

    Parameters
    ----------
    objects: tuple
        The panels to add the loading indicator to.
    """
    for item in objects:
        if hasattr(item, "css_classes"):
            _add_css_classes(item, _loading_css_classes(item))

def stop_loading_spinner(*objects):
    """
    Removes the loading indicating from the specified panel objects.

    Parameters
    ----------
    objects: tuple
        The panels to remove the loading indicator from.
    """
    for item in objects:
        if hasattr(item, "css_classes"):
            _remove_css_classes(item, _loading_css_classes(item))
