"""
This module provides a Bokeh BrowserInfo Model exposing the browser
window and navigator APIs.
"""
from bokeh.core.properties import (
    Bool, Float, Nullable, String,
)
from bokeh.models import Model


class BrowserInfo(Model):
    """
    A python wrapper around the JS `window` and `navigator` APIs.
    """

    dark_mode = Nullable(Bool())

    device_pixel_ratio = Nullable(Float())

    language = Nullable(String())

    timezone = Nullable(String())

    timezone_offset = Nullable(Float())

    webdriver = Nullable(Bool())

    webgl = Nullable(Bool())
