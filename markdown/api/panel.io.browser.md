# panel.io.browser module

Defines a BrowserInfo component exposing the browser window and
navigator APIs.

class panel.io.browser.BrowserInfo(\*, dark_mode, device_pixel_ratio, language, timezone, timezone_offset, webdriver, webgl, name)
Bases: `Syncable`

The Location component can be made available in a server context to
provide read and write access to the URL components in the browser.

Methods

|  |  |
|----|----|
| [get_root](#panel.io.browser.BrowserInfo.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |

**Parameter Definitions**

------------------------------------------------------------------------

`dark_mode`` ``=`` ``Boolean(allow_None=True,`` ``label='Dark`` ``mode')`
Whether the user prefers dark mode.

`device_pixel_ratio`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Device`` ``pixel`` ``ratio')`
Provides the ratio of the resolution in physical pixels to the
resolution in CSS pixels for the current display device.

`language`` ``=`` ``String(allow_None=True,`` ``label='Language')`
The preferred language of the user, usually the language of the browser
UI.

`timezone`` ``=`` ``String(allow_None=True,`` ``label='Timezone')`
The timezone configured as the local timezone of the user.

`timezone_offset`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Timezone`` ``offset')`
The time offset from UTC in minutes.

`webdriver`` ``=`` ``Boolean(allow_None=True,`` ``label='Webdriver')`
Indicates whether the user agent is controlled by automation.

`webgl`` ``=`` ``Boolean(allow_None=True,`` ``label='Webgl')`
Indicates whether the browser has WebGL support.

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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
