# panel.io.location module

Defines the Location widget which allows changing the href of the
window.

class panel.io.location.Location(\*, hash, pathname, reload, search, name)
Bases: `Syncable`

The Location component can be made available in a server context to
provide read and write access to the URL components in the browser.

Attributes:
**query_params**

Methods

|  |  |
|----|----|
| [get_root](#panel.io.location.Location.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |
| [sync](#panel.io.location.Location.sync)(parameterized\[, parameters, on_error\]) | Syncs the parameters of a Parameterized object with the query parameters in the URL. |
| [unsync](#panel.io.location.Location.unsync)(parameterized\[, parameters\]) | Unsyncs the parameters of the Parameterized with the query params in the URL. |

|                  |     |
|------------------|-----|
| **from_request** |     |
| **update_query** |     |

**Parameter Definitions**

------------------------------------------------------------------------

`href`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Href',`` ``readonly=True)`
The full url, e.g. ‘[https://localhost:80?color=blue#interact](https://localhost:80?color=blue#interact)’

`hostname`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Hostname',`` ``readonly=True)`
hostname in window.location e.g. ‘panel.holoviz.org’

`pathname`` ``=`` ``String(default='',`` ``label='Pathname',`` ``regex='^$|[\\/]|srcdoc$')`
pathname in window.location e.g. ‘/user_guide/Interact.html’

`protocol`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Protocol',`` ``readonly=True)`
protocol in window.location e.g. ‘http:’ or ‘https:’

`port`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Port',`` ``readonly=True)`
port in window.location e.g. ‘80’

`search`` ``=`` ``String(default='',`` ``label='Search',`` ``regex='^$|\\?')`
search in window.location e.g. ‘?color=blue’

`hash`` ``=`` ``String(default='',`` ``label='Hash',`` ``regex='^$|#')`
hash in window.location e.g. ‘#interact’

`reload`` ``=`` ``Boolean(default=False,`` ``label='Reload')`
Reload the page when the location is updated. For multipage apps this
should be set to True, For single page apps this should be set to False

get_root(doc: Document \| None = None, comm: Comm \| None = None, preprocess: bool = True) → Model
Returns the root model and applies pre-processing hooks

Parameters:
**doc: bokeh.Document**
Bokeh document the bokeh model will be attached to.

**comm: pyviz_comms.Comm**
Optional pyviz_comms when working in notebook

**preprocess: boolean (default=True)**
Whether to run preprocessing hooks

Returns:
Returns the bokeh model corresponding to this panel object

sync(parameterized: param.Parameterized, parameters: list\[str\] \| dict\[str, str\] \| None = None, on_error: Callable\[\[dict\[str, t.Any\]\], None\] \| None = None) → None
Syncs the parameters of a Parameterized object with the query parameters
in the URL. If no parameters are supplied all parameters except the name
are synced.

Parameters:
**parameterized (param.Parameterized):**
The Parameterized object to sync query parameters with

**parameters (list or dict):**
A list or dictionary specifying parameters to sync. If a dictionary is
supplied it should define a mapping from the Parameterized’s parameters
to the names of the query parameters.

**on_error: (callable):**
Callback when syncing Parameterized with URL parameters fails. The
callback is passed a dictionary of parameter values, which could not be
applied.

unsync(parameterized: Parameterized, parameters: list\[str\] \| None = None) → None
Unsyncs the parameters of the Parameterized with the query params in the
URL. If no parameters are supplied all parameters except the name are
unsynced.

Parameters:
**parameterized (param.Parameterized):**
The Parameterized object to unsync query parameters with

**parameters (list):**
A list of parameters to unsync.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
