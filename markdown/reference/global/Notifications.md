# Notifications
---
```python
import panel as pn

pn.extension(notifications=True)
```

The `NotificationsArea` component is a global component which allows users to display so called "toasts" that can provide information to a user. Notifications can be enabled by setting `notifications=True` via the `pn.extension` or by setting `pn.config.notifications = True` directly.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### NotificationArea

Parameters:

* **``position``** (str): The position of the notifications area.

Methods:

* **``.info()``**: Issues an info message
* **``.error()``**: Issues an error message
* **``.success()``**: Issues an success message
* **``.warning()``**: Issues an warning message

##### Notification

Parameters:

* **``duration``** (int): The duration to display the notification for (if set to zero the notification will be displayed until it has been destroyed or dismissed).
* **``type``** (str): Whether the widget is editable

Methods:

* **``.destroy()``**: Destroys the notification

___

By default notifications last for the specified duration specified in milliseconds and defaulting to 3 seconds:

```python
pn.state.notifications.error('This is an error notification.', duration=1000)
pn.state.notifications.info('This is a info notification.', duration=2000)
pn.state.notifications.success('This is a success notification.')
pn.state.notifications.warning('This is a warning notification.', duration=4000);
```

Setting a duration of zero will cause the notification to stay in place until it is either manually dismissed in the UI or destroyed programmatically:

```python
success = pn.state.notifications.success('This is a success notification.', duration=0)
```

We can destroy it programmatically using the destroy method:

```python
success.destroy()
```

#### Clear all

To clear out all current notifications we can call the clear method:

```python
pn.state.notifications.error('This is an error notification.', duration=0)
pn.state.notifications.info('This is a info notification.', duration=0)
pn.state.notifications.success('This is a success notification.', duration=0)
pn.state.notifications.warning('This is a warning notification.', duration=0);
```

```python
pn.state.notifications.clear()
```

#### Custom types

We are not limited by the four main types of notifications, by using the `.send` method we can provide a custom `background` and `icon`:

```python
pn.state.notifications.send('Fire!!!', background='red', icon='<i class="fas fa-burn"></i>');
```

#### Position

The position of the notification area can be controlled by setting the parameter on the `state.notifications` object, e.g.:

```python
pn.state.notifications.position = 'top-right'
```

If you are viewing this page in a live notebook you will be able to change the position dynamically:

```python
pn.state.notifications.send('Fire!!!', background='red', icon='<i class="fas fa-burn"></i>', duration=0);

pn.widgets.RadioButtonGroup.from_param(pn.state.notifications.param.position)
```

## Demo

To try notifications out yourself the `NotificationArea` components provide a convenient `.demo()` method. Note that to set a custom color you have to select the `'custom'` type:

```python
pn.io.notifications.NotificationArea.demo()
```

---
