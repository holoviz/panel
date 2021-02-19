"""
This module contains functionality to make any Panel component look
like it is loading and disabled.
"""

LOADING_INDICATOR_CSS_CLASS = "pn-loading"

def _add_css_class(item, css_class):
    if not item.css_classes:
        item.css_classes = [css_class]
    elif not css_class in item.css_classes:
        item.css_classes.append(css_class)


def _remove_css_class(item, css_class):
    if item.css_classes:
        if item.css_classes == [css_class]:
            item.css_classes = []
        elif css_class in item.css_classes:
            item.css_classes.remove(css_class)


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
    for item in objects:
        if hasattr(item, "css_classes"):
            _add_css_class(item, css_class=LOADING_INDICATOR_CSS_CLASS)


def stop_loading_spinner(*objects):
    """
    Removes the loading indicating from the specified panel objects.

    Arguments
    ---------
    objects: tuple
        The panels to remove the loading indicator from.
    """
    for item in objects:
        if hasattr(item, "css_classes"):
            _remove_css_class(item, css_class=LOADING_INDICATOR_CSS_CLASS)
