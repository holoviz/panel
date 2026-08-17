# panel.io.application module

Extensions for Bokeh application handling.

class panel.io.application.Application(\*args, **kwargs)
Bases: `Application`

Extends Bokeh Application with ability to add global session creation
callbacks, support for the admin dashboard and the ability to globally
define a template.

Methods

|  |  |
|----|----|
| [add](#panel.io.application.Application.add)(handler) | Override default DocumentLifeCycleHandler |
| [initialize_document](#panel.io.application.Application.initialize_document)(doc) | Fills in a new document using the Application's handlers. |
| [on_session_created](#panel.io.application.Application.on_session_created)(session_context) | Invoked to execute code when a new session is created. |
| [process_request](#panel.io.application.Application.process_request)(request) | Processes incoming HTTP request returning a dictionary of additional data to add to the session_context. |

add(handler: Handler) → None
Override default DocumentLifeCycleHandler

initialize_document(doc)
Fills in a new document using the Application’s handlers.

async on_session_created(session_context)
Invoked to execute code when a new session is created.

This method calls `on_session_created` on each
handler, in order, with the session context passed as the only argument.

May return a `Future` which will delay session
creation until the `Future` completes.

process_request(request) → dict\[str, Any\]
Processes incoming HTTP request returning a dictionary of additional
data to add to the session_context.

Args:
request: HTTP request

Returns:
A dictionary of JSON serializable data to be included on the session
context.

panel.io.application.build_applications(panel: TViewableFuncOrPath \| dict\[str, TViewableFuncOrPath\], title: str \| dict\[str, str\] \| None = None, location: bool \| Location = True, admin: bool = False, server_id: str \| None = None, custom_handlers: Sequence\[Callable\[\[str, TViewableFuncOrPath\], TViewableFuncOrPath\]\] \| None = None) → dict\[str, BkApplication\]
Converts a variety of objects into a dictionary of Applications.

Parameters:
**panel: Viewable, function or {str: Viewable}**
A Panel object, a function returning a Panel object or a dictionary
mapping from the URL slug to either.

title : str or {str: str} (optional, default=None)
An HTML title for the application or a dictionary mapping from the URL
slug to a customized title.

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

**admin: boolean (default=False)**
Whether to enable the admin panel

**server_id: str**
ID of the server running the application(s)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
