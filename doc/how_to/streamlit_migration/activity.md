# Show Activity

Panel supports many ways of indicating activity

- Indicators. See the [Indicators Section](../../reference/index.md#indicators) of the [Component Gallery](../../reference/index.md).
- `disabled`/ `loading` parameters on Panel components
- `loading_indicator` parameter for `pn.panel` or `pn.config`. If `True` a loading indicator will be shown on your *bound functions* when they are re-run.

## Example

The example below showcases some of the ways Panel can show activity.

```python
import panel as pn

pn.extension(sizing_mode="stretch_width", template="bootstrap")

SPIN_CSS = """
@keyframes icon-rotation {
  from {transform: rotate(0deg);} to {transform: rotate(359deg);}
}
.bk-TablerIcon {animation: icon-rotation 2s infinite linear;}
"""

pn.Row(
    pn.Column(
        "## Loading Spinner",
        pn.Column(
            pn.indicators.LoadingSpinner(value=False, height=25, width=25),
            pn.indicators.LoadingSpinner(
                value=True, height=25, width=25, color="secondary"
            ),
        ),
    ),
    pn.Column(
        "## Progress",
        pn.Column(
            pn.indicators.Progress(
                name="Progress", value=20, width=150, bar_color="secondary"
            ),
            pn.indicators.Progress(
                name="Progress", active=True, width=150, bar_color="secondary"
            ),
        ),
    ),
    pn.Column(
        "## Disabled",
        pn.Column(
            pn.widgets.Button(name="Loading", icon="progress", disabled=True),
            pn.widgets.Button(
                name="Loading", icon="progress", disabled=True, stylesheets=[SPIN_CSS]
            ),
        ),
    ),
    pn.Column(
        "## Loading",
        pn.Column(
            pn.widgets.Button(name="Loading", loading=True, button_type="primary"),
            pn.WidgetBox(
                pn.widgets.Checkbox(name="Checked", value=True),
                pn.widgets.Button(name="Submit", button_type="primary"),
                loading=True, margin=(10,10),
            ),
        ),
    ),
).servable()
```

![Show Activity](https://user-images.githubusercontent.com/42288570/246325570-11484dd6-4523-401f-b709-6c0cc7996410.gif)

To learn more about migrating activity indicators check out the [Migrate Streamlit Interactivity Guide](interactivity.md).
