"""This module provides a Bokeh Location Model as a wrapper around the JS window.location api"""

from bokeh.core.properties import Bool, String
from bokeh.models import Model


class Location(Model):
    """
    A python wrapper around the JS `window.location` api. See
    https://www.w3schools.com/js/js_window_location.asp and
    https://www.w3.org/TR/html52/browsers.html#the-location-interface

    You can use this model to provide (parts of) the app state to the
    user as a bookmarkable and shareable link.
    """

    href = String(default="", help="""
      The full url, e.g. 'https://localhost:80?color=blue#interact'""")

    hostname = String(default="", help="""
      hostname in window.location e.g. 'panel.holoviz.org'""")

    pathname = String(default="", help="""
      pathname in window.location e.g. '/user_guide/Interact.html'""")

    protocol = String(default="", help="""
      protocol in window.location e.g. 'https'""")

    port = String(default="", help="""
      port in window.location e.g. 80""")

    search = String(default="", help="""
      search in window.location e.g. '?color=blue'""")

    hash = String(default="", help="""
      hash in window.location e.g. '#interact'""")

    reload = Bool(default=True, help="""
      Reload the page when the location is updated. For multipage apps
      this should be set to True, For single page apps this should be
      set to False""")
