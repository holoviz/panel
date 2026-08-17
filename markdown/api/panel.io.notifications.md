# panel.io.notifications module

class panel.io.notifications.Notification(\*, \_destroyed, \_rendered, background, duration, icon, message, notification_area, notification_type, name)
Bases: `Parameterized`

Methods

|             |     |
|-------------|-----|
| **destroy** |     |

**Parameter Definitions**

------------------------------------------------------------------------

`background`` ``=`` ``Color(allow_None=True,`` ``allow_named=True,`` ``label='Background')`

`duration`` ``=`` ``Integer(constant=True,`` ``default=3000,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Duration')`

`icon`` ``=`` ``String(allow_None=True,`` ``label='Icon')`

`message`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Message')`

`notification_area`` ``=`` ``Parameter(allow_None=True,`` ``constant=True,`` ``label='Notification`` ``area')`

`notification_type`` ``=`` ``String(allow_None=True,`` ``constant=True)`

`_rendered`` ``=`` ``Boolean(default=False,`` ``label='`` ``rendered')`

`_destroyed`` ``=`` ``Boolean(default=False,`` ``label='`` ``destroyed')`

class panel.io.notifications.NotificationArea(\*, \_clear, types, js_events, max_notifications, notifications, position, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [NotificationAreaBase](#panel.io.notifications.NotificationAreaBase),
[ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

A notification area that displays notifications using the Notyf library.

Methods

|  |  |
|----|----|
| [demo](#panel.io.notifications.NotificationArea.demo)(**params) | Generates a layout which allows demoing the component. |
| [get_root](#panel.io.notifications.NotificationArea.get_root)(\[doc, comm, preprocess\]) | Returns the root model and applies pre-processing hooks |
| [send](#panel.io.notifications.NotificationArea.send)(message\[, duration, type, background, icon\]) | Sends a notification to the frontend. |

|           |     |
|-----------|-----|
| **clear** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal"
> title="panel.io.notifications.NotificationAreaBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.io.notifications.NotificationAreaBase](#panel.io.notifications.NotificationAreaBase):
> js_events, max_notifications, notifications, position
>
>

`_clear`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``clear')`

`types`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[{'type':`` ``'warning',`` ``'background':`` ``'#ffc107',`` ``'icon':`` ``{'className':`` ``'fas`` ``fa-exclamation-triangle',`` ``'tagName':`` ``'i',`` ``'color':`` ``'white'}},`` ``{'type':`` ``'info',`` ``'background':`` ``'#007bff',`` ``'icon':`` ``{'className':`` ``'fas`` ``fa-info-circle',`` ``'tagName':`` ``'i',`` ``'color':`` ``'white'}}],`` ``label='Types')`
A list of notification types, each defined by a dictionary with keys: -
‘type’: The type of notification (e.g., ‘info’, ‘warning’). -
‘background’: The background color of the notification. - ‘icon’: An
icon configuration dictionary with keys: - ‘className’: The CSS class
for the icon. - ‘tagName’: The HTML tag for the icon. - ‘color’: The
color of the icon.

classmethod demo(**params)
Generates a layout which allows demoing the component.

Parameters:
****params: dict**
Additional parameters to pass to the component.

Returns:
layout: Layout
A layout containing the demo components.

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

send(message, duration=3000, type=None, background=None, icon=None)
Sends a notification to the frontend.

Parameters:
**message: str**
The message to display in the notification.

**duration: int**
The duration of the notification in milliseconds.

**type: str**
The type of the notification.

**background: str**
The background color of the notification.

**icon: str**
The icon of the notification.

class panel.io.notifications.NotificationAreaBase(\*, js_events, max_notifications, notifications, position, name)
Bases: `Parameterized`

Methods

|  |  |
|----|----|
| [send](#panel.io.notifications.NotificationAreaBase.send)(message\[, duration, type, background, icon\]) | Sends a notification to the frontend. |

|             |     |
|-------------|-----|
| **clear**   |     |
| **error**   |     |
| **info**    |     |
| **success** |     |
| **warning** |     |

**Parameter Definitions**

------------------------------------------------------------------------

`js_events`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Js`` ``events')`
A dictionary that configures notifications for specific Bokeh Document
events, e.g.: {‘connection_lost’: {‘type’: ‘error’, ‘message’:
‘Connection Lost!’, ‘duration’: 5}} will trigger a warning on the Bokeh
ConnectionLost event.

`max_notifications`` ``=`` ``Integer(default=5,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``notifications')`
The maximum number of notifications to display at once.

`notifications`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.io.notifications.Notification'>,`` ``label='Notifications')`
A list of notifications to display in the notification area.

`position`` ``=`` ``Selector(default='bottom-right',`` ``label='Position',`` ``names={},`` ``objects=['bottom-right',`` ``'bottom-left',`` ``'bottom-center',`` ``'top-left',`` ``'top-right',`` ``'top-center',`` ``'center-center',`` ``'center-left',`` ``'center-right'])`
Position of the notification area on the screen (e.g., ‘top-right’,
‘bottom-left’).

send(message, duration=3000, type=None, background=None, icon=None)
Sends a notification to the frontend.

Parameters:
**message: str**
The message to display in the notification.

**duration: int**
The duration of the notification in milliseconds.

**type: str**
The type of the notification.

**background: str**
The background color of the notification.

**icon: str**
The icon of the notification.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
