# panel.models.location module

This module provides a Bokeh Location Model as a wrapper around the JS
window.location api

class panel.models.location.Location(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Model`

A python wrapper around the JS window.location api. See
[https://www.w3schools.com/js/js_window_location.asp](https://www.w3schools.com/js/js_window_location.asp)
and [https://www.w3.org/TR/html52/browsers.html#the-location-interface](https://www.w3.org/TR/html52/browsers.html#the-location-interface)

You can use this model to provide (parts of) the app state to the user
as a bookmarkable and shareable link.

Attributes:
**hash**
hash in window.location e.g. ‘#interact’

**hostname**
hostname in window.location e.g. ‘panel.holoviz.org’

**href**
The full url, e.g. ‘[https://localhost:80?color=blue#interact](https://localhost:80?color=blue#interact)’

**pathname**
pathname in window.location e.g. ‘/user_guide/Interact.html’

**port**
port in window.location e.g. 80

**protocol**
protocol in window.location e.g. ‘https’

**reload**
Reload the page when the location is updated. For multipage apps this
should be set to True, For single page apps this should be set to False

**search**
search in window.location e.g. ‘?color=blue’

hash
hash in window.location e.g. ‘#interact’

hostname
hostname in window.location e.g. ‘panel.holoviz.org’

href
The full url, e.g. ‘[https://localhost:80?color=blue#interact](https://localhost:80?color=blue#interact)’

pathname
pathname in window.location e.g. ‘/user_guide/Interact.html’

port
port in window.location e.g. 80

protocol
protocol in window.location e.g. ‘https’

reload
Reload the page when the location is updated. For multipage apps this
should be set to True, For single page apps this should be set to False

search
search in window.location e.g. ‘?color=blue’

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
