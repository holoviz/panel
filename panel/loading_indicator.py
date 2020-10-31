"""This module contains functionality to make any panel, i.e. layout, pane or widget, look like it's
loading and disabled.

This is very important for the user experience. A user that sees an unresponsive page without any
indication of something happening in the background with either perceive that the page is slow or
be in doubt if the page has stopped working.
"""
import panel as pn

_LOADING_INDICATOR_CSS_CLASS = "panel-loading"

STYLE = """
.bk.panel-loading:before {
position: absolute;
height: 100%;
width: 100%;
content: '';
z-index: 1000;
background-color: rgb(255,255,255,0.50);
border-color: lightgray;
background-image: url('https://raw.githubusercontent.com/holoviz/panel/master/panel/assets/spinner.gif');
background-repeat: no-repeat;
background-position: center;
background-size: 40px 40px;
border-width: 1px;

}
.bk.panel-loading:hover:before {
    cursor: progress;
}
"""
pn.config.raw_css.append(STYLE)


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


def start_loading_indicator(*objects):
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


def stop_loading_indicator(*objects):
    """Removes the loading indicating from the specified panel objects"""
    _remove_css_class(*objects, css_class=_LOADING_INDICATOR_CSS_CLASS)
