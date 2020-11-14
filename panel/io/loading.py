"""This module contains functionality to make any panel, i.e. layout, pane or widget, look like it's
loading and disabled.

This is very important for the user experience. A user that sees an unresponsive page without any
indication of something happening in the background with either perceive that the page is slow or
be in doubt if the page has stopped working.
"""
import panel as pn

_LOADING_INDICATOR_CSS_CLASS = "pn-loading"

DEFAULT_URL = "https://raw.githubusercontent.com/holoviz/panel/5ea166fdda6e1f958d2d9929ae2ed2b8e962156c/panel/assets/spinner_default.svg"
DARK_URL = "https://raw.githubusercontent.com/holoviz/panel/5ea166fdda6e1f958d2d9929ae2ed2b8e962156c/panel/assets/spinner_dark.svg"

# Todo: Find the place to add this style
STYLE = """
.bk.pn-loading:before {
    position: absolute;
    height: 100%;
    width: 100%;
    content: '';
    z-index: 1000;
    background-color: rgb(255,255,255,0.50);
    border-color: lightgray;
    background-image: url('https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/e6cb56375bb1c436975e09739a231fb31e628a63/spinners/default.svg');
    background-repeat: no-repeat;
    background-position: center;
    background-size: auto 50%;
    border-width: 1px;

}
.bk.pn-loading:hover:before {
    cursor: progress;
}
"""


def _add_css_class(*objects, css_class):
    for item in objects:
        if hasattr(item, "css_classes"):
            if not item.css_classes:
                item.css_classes = [css_class]
            elif not css_class in item.css_classes:
                item.css_classes.append(css_class)


def _remove_css_class(*objects, css_class):
    for item in objects:
        if hasattr(item, "css_classes"):
            if item.css_classes:
                if item.css_classes == [css_class]:
                    item.css_classes = None  # Will not work if set to []!
                elif css_class in item.css_classes:
                    item.css_classes.remove(css_class)


def start_loading_spinner(*objects):
    """
    Changes the appearance of the specified panel objects to indicate that they are loading.

    This is done by

    - adding a small spinner on top
    - graying out the panel
    - disabling the panel
    - and changing the mouse cursor to a spinner when hovering over the panel

    Arguments
    ---------
    objects: The panels to indicate are loading
    """
    _add_css_class(*objects, css_class=_LOADING_INDICATOR_CSS_CLASS)


def stop_loading_spinner(*objects):
    """Removes the loading indicating from the specified panel objects"""
    _remove_css_class(*objects, css_class=_LOADING_INDICATOR_CSS_CLASS)