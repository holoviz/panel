"""This module provides a Bokeh Location Model as a wrapper around the JS window.location api"""
import pathlib
from typing import List, Optional

import param
from bokeh.core.properties import Bool, Instance, Int, String
from bokeh.layouts import column
from bokeh.models import HTMLBox, Model, Slider

import panel as pn

LOCATION_TS = pathlib.Path(__file__).parent / "location.ts"
LOCATION_TS_STR = str(LOCATION_TS.resolve())


class Location(HTMLBox):
    """A python wrapper around the JS `window.location` api. See
    https://www.w3schools.com/js/js_window_location.asp and
    https://www.w3.org/TR/html52/browsers.html#the-location-interface

    You can use this model to provide (parts of) the app state to the user as a bookmarkable and
    shareable link.
    """

    __implementation__ = LOCATION_TS_STR

    href = String(
        help="""The full url, e.g. \
            'https://panel.holoviz.org/user_guide/Interact.html:80?color=blue#interact'"""
    )
    hostname = String(help="hostname in window.location e.g. 'panel.holoviz.org'")
    pathname = String(help="pathname in window.location e.g. '/user_guide/Interact.html'")
    protocol = String(help="protocol in window.location e.g. 'https'")
    port = String(help="port in window.location e.g. 80")
    search = String(help="search in window.location e.g. '?color=blue'")
    hash_ = String(help="hash in window.location e.g. '#interact'")

    refresh = Bool(
        default=True,
        help="""Refresh the page when the location is updated. For multipage apps this should be \
        set to True, For single page apps this should be set to False""",
    )
