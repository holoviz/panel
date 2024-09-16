# Organize and Style with Templates

Streamlit always uses the same *template* with a *main* and *sidebar* area to layout and style your app.

With Panel you have the flexibility to use the *default, blank template*, one of the *built in templates* or even create your own *custom template*.

---

## Migration Steps

When migrating you will have to decide which template to use

- Blank (default)
- A built-in template like *vanilla*, *bootstrap*, *material* or *fast*. See the [Templates Section](../../reference/index.rst#templates) of the [Components Guide](../../reference/index.rst).
- A [custom template](../../how_to/templates/template_custom) declared using Jinja2 syntax.

## Example

### FastListTemplate Example

Here is an example with the [`FastListTemplate`](../../reference/templates/FastListTemplate).

```python
from asyncio import sleep
from datetime import datetime

import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast", theme="dark")

pn.Column(
    "# 📖 Info",
    """This app is an example of a built in template with a
*sidebar*, *header* and *main* area.

We have

- set the *header* background, site and title parameters
- set the default *theme* to `dark`

The app streams the current date and time using an *async generator function*.
""",
).servable(target="sidebar")

async def stream():
    for i in range(0, 100):
        await sleep(0.25)
        yield datetime.now()

pn.Column(
    "The current date and time:", *(stream for i in range(5))
).servable(target="main")

pn.state.template.param.update(
    site="Panel",
    title="Template Example",
    header_background="#E91E63",
    accent_base_color="#E91E63",
)
```

![Panel Template Example](https://assets.holoviz.org/panel/gifs/panel_app_example.gif)
