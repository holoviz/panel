"""
This module contains functionality to make any Panel component look
like it is loading and disabled.
"""

from ..config import config

LOADING_INDICATOR_CSS_CLASS = "pn-loading"

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

    Arguments
    ---------
    objects: tuple
        The panels to add the loading indicator to.
    """
    css_classes = [LOADING_INDICATOR_CSS_CLASS, config.loading_spinner]
    for item in objects:
        if hasattr(item, "css_classes"):
            _add_css_classes(item, css_classes)

def stop_loading_spinner(*objects):
    """
    Removes the loading indicating from the specified panel objects.

    Arguments
    ---------
    objects: tuple
        The panels to remove the loading indicator from.
    """
    css_classes = [LOADING_INDICATOR_CSS_CLASS, config.loading_spinner]
    for item in objects:
        if hasattr(item, "css_classes"):
            _remove_css_classes(item, css_classes)
