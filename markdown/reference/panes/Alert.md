# Alert
---
```python
import panel as pn
pn.extension()
```

The ``Alert`` pane allows providing **contextual feedback messages** for typical user actions with the handful of available and flexible alert messages.

It's heavily inspired by the [Bootstrap Alert](https://getbootstrap.com/docs/4.0/components/alerts/).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``object``** (str): The contextual feedback message.
* **``alert_type``** (str): The type of Alert and one of `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`.

___

The `Alert` pane supports Markdown and HTML syntax :

```python
pn.pane.Alert('## Alert\nThis is a warning!')
```

The `Alert` pane also a number of `alert_type` options which control the color of the alert message:

```python
text = (
    "This is a **{alert_type}** alert with [an example link]"
    "(https://panel.holoviz.org/). Give it a click if you like."
)

pn.Column(*[
    pn.pane.Alert(text.format(alert_type=at), alert_type=at)
    for at in pn.pane.Alert.param.alert_type.objects],
    sizing_mode="stretch_width"
).servable()
```

It may also be used for longer messages:

```python
text = """
### Well done!

Aww yeah, you successfully read this important alert message. This example text is going to run a bit longer so that you can see how spacing within an alert works with this kind of content.

<hr>

Did you notice the use of the divider?
"""
pn.pane.Alert(text, alert_type="success")
```

---
