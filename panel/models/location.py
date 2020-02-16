"""This module provides a Bokeh Location Model as a wrapper around the JS window.location api"""
from bokeh.models import Model
from bokeh.core.properties import Bool, String, Int
import param
from typing import Optional, List


class Location(Model):
    """A python wrapper around the JS `window.location` api. See
    https://www.w3schools.com/js/js_window_location.asp and
    https://www.w3.org/TR/html52/browsers.html#the-location-interface

    You can use this model to provide (parts of) the app state to the user as a bookmarkable and
    shareable link.
    """

    href = String(
        help="""The full url, e.g. \
            'https://panel.holoviz.org/user_guide/Interact.html:80?color=blue#interact'"""
    )
    hostname = String(help="hostname in window.location e.g. 'panel.holoviz.org'")
    pathname = String(help="pathname in window.location e.g. 'user_guide/Interact.html'")
    protocol = String(help="protocol in window.location e.g. 'https:'")
    port = Int(help="port in window.location e.g. 80")
    search = String(help="search in window.location e.g. '?color=blue'")
    hash_ = String(help="hash in window.location e.g. '#interact'")

    refresh = Bool(
        default=False,
        help="""Refresh the page when the location is updated. For multipage apps this should be \
        set to True, For single page apps this should be set to False""",
    )

    # Maybe Later ?
    # - Add assign function to open a new window location.
    # - Add reload function to force a reload
    # - Add replace function to

    # Maybe ?
    # we should provide the below helper functionality to easily
    # keep a Parameterized class in sync with the search string

    # maybe ?
    # we can only keep a dictionary in sync and the user has to specify how
    # to serialize the Parameterized Class?

    # Maybe the param_class and parameters should be parameters on the model?

    def sync_search(self, param_class: param.Parameterized, parameters: List[str] = None):
        """Updates the search string from the specified parameters

        Parameters
        ----------
        param_class : param.Parameterized
            The Parameterized Class containing the Parameters
        parameters : [type], optional
            The parameters to provide in the search string. If None is provided then all, by default None
        """
        raise NotImplementedError()

    def sync_param_class(self, parameters=None):
        """Updates the Parameterized Class from the parameters

        Parameters
        ----------
        param_class : param.Parameterized
            The Parameterized Class containing the Parameters
        parameters : [type], optional
            [description], by default None
        """
        raise NotImplementedError()
