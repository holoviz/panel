# Add notifications on connect and disconnect

This guide addresses how to add notifications when the server connection is established and when it disconnects.

---

Panel includes a notification system that is enabled by default. The notification system also allows registering notification messages when the server connection is ready and when the server connection is lost. These can be configured by setting the `disconnect_notification` and `ready_notification`.

```python
import panel as pn

pn.extension(
    disconnect_notification='Connection lost, try reloading the page!',
    ready_notification='Application fully loaded.',
    template='bootstrap'
)

slider = pn.widgets.IntSlider(name='Number', start=1, end=10, value=7)

pn.Column(
    slider,
    pn.bind(lambda n: '⭐' * n, slider)
).servable(title='Connection Notifications')
```

![Connection notifications](https://assets.holoviz.org/panel/gifs/connection_notifications.gif)
