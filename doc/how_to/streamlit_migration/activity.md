# Show Activity

Panel supports many ways of indicating activity

- Indicators. See the [Indicators Section](../../reference/indicators/index#indicators) of the [Component Gallery](../../reference/index).
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

pn.ui.Row(
    pn.ui.Column(
        "## Loading Spinner",
        pn.ui.Column(
            pn.indicators.LoadingSpinner(value=False, height=25, width=25),
            pn.indicators.LoadingSpinner(
                value=True, height=25, width=25, color="secondary"
            ),
        ),
    ),
    pn.ui.Column(
        "## Progress",
        pn.ui.Column(
            pn.indicators.Progress(
                label="Progress", value=20, width=150, bar_color="secondary"
            ),
            pn.indicators.Progress(
                label="Progress", active=True, width=150, bar_color="secondary"
            ),
        ),
    ),
    pn.ui.Column(
        "## Disabled",
        pn.ui.Column(
            pn.ui.Button(label="Loading", icon="progress", disabled=True),
            pn.ui.Button(
                label="Loading", icon="progress", disabled=True, stylesheets=[SPIN_CSS]
            ),
        ),
    ),
    pn.ui.Column(
        "## Loading",
        pn.ui.Column(
            pn.ui.Button(label="Loading", loading=True, color="primary"),
            pn.ui.WidgetBox(
                pn.ui.Checkbox(label="Checked", value=True),
                pn.ui.Button(label="Submit", color="primary"),
                loading=True, margin=(10,10),
            ),
        ),
    ),
).servable()
```

![Show Activity](https://user-images.githubusercontent.com/42288570/246325570-11484dd6-4523-401f-b709-6c0cc7996410.gif)

To learn more about migrating activity indicators check out the [Migrate Streamlit Interactivity Guide](interactivity).
