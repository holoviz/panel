# Param
---
```python
import panel as pn
import param

pn.extension()
```

The ``panel.Param`` pane allows customizing the widgets, layout and style of the parameters of a `param.Parameterized` Class.

#### Parameters:

The basic parameters are:

* **`object`** (param.parameterized.Parameters): The `param` attribute of a `param.Parameterized` Class
* **`parameters`** (List[str]): A list identifying the subset of parameters to include in the Pane.
* **`widgets`** (Dict): A Dictionary specifying which parameters and widgets to use for a given parameter. You can also specify widget attributes.

The more advanced parameters which give you more control are:

* **`default_layout`** (ClassSelector): A layout like Column, Row, etc. or a Custom GridBox.
* **`display_threshold`** (float): Parameters with precedence below this value are not displayed.
* **`expand`** (bool): Whether parameterized subobjects are expanded or collapsed on instantiation.
* **`expand_button`** (bool): Whether to add buttons to expand and collapse sub-objects.
* **`expand_layout`** (layout): Layout to expand sub-objects into.
* **`name`** (str): The title of the pane.
* **`show_labels`** (bool): Whether or not to show labels
* **`show_name`** (bool): Whether or not to show the name of the Parameterized Class

For further layout and styling-related parameters see the [Control the size](../../tutorials/basic/size.md), [Align Content](../../tutorials/basic/align.md) and [Style](../../tutorials/basic/style.md) tutorials.

___

## Model building
Let's build a model of a cycling Athlete and her PowerCurve.

The PowerCurve is a recording of her maximum power output in Watt per kg for fixed durations of time.

```python
import datetime
import pandas as pd
import hvplot.pandas

DATE_BOUNDS = (datetime.date(1900, 1, 1), datetime.datetime.now().date())

class PowerCurve(param.Parameterized):
    ten_sec = param.Number(default=1079)
    ten_sec_date = param.Date(default=datetime.date(2018, 8, 21), bounds=DATE_BOUNDS)
    one_min = param.Number(default=684)
    one_min_date = param.Date(default=datetime.date(2017, 8, 31), bounds=DATE_BOUNDS)
    ten_min = param.Number(default=419)
    ten_min_date = param.Date(default=datetime.date(2017, 9, 22), bounds=DATE_BOUNDS)
    twenty_min = param.Number(default=398)
    twenty_min_date = param.Date(default=datetime.date(2017, 9, 22), bounds=DATE_BOUNDS)
    one_hour = param.Number(default=319)
    one_hour_date = param.Date(default=datetime.date(2017, 8, 6), bounds=DATE_BOUNDS)
    
    @param.depends("ten_sec", "one_min", "ten_min", "twenty_min", "one_hour")
    def plot(self):
        data = {
            "duration": [10 / 60, 1, 10, 20, 60],
            "power": [self.ten_sec, self.one_min, self.ten_min, self.twenty_min, self.one_hour],
        }
        dataframe = pd.DataFrame(data)
        line_plot = dataframe.hvplot.line(
            x="duration", y="power", line_color="#007BFF", line_width=3, responsive=True,
        )
        scatter_plot = dataframe.hvplot.scatter(
            x="duration", y="power", marker="o", size=6, color="#007BFF", responsive=True
        )
        fig = line_plot * scatter_plot
        gridstyle = {"grid_line_color": "black", "grid_line_width": 0.1}
        fig = fig.opts(
            min_height=400,
            toolbar=None,
            yticks=list(range(0, 1600, 200)),
            ylim=(0, 1500),
            gridstyle=gridstyle,
            show_grid=True,
        )
        return fig

class Athlete(param.Parameterized):
    name_ = param.String(default="P.A. Nelson")
    birthday = param.Date(default=datetime.date(1976, 9, 17), bounds=DATE_BOUNDS)
    weight = param.Number(default=82, bounds=(20,300))
    power_curve = param.ClassSelector(class_=PowerCurve, default=PowerCurve())
    
athlete = Athlete()
```

The `pn.Param` pane can be used to view and edit the models.

Try clicking the `...` button. This will expand the PowerCurve if running in an interactive notebook.

```python
pn.Param(athlete)
```

The default Name and Birthday widgets are slow to use. So let's change them to a `DatePicker` and a `LiteralInput`.

```python
pn.Param(athlete, widgets={"birthday": pn.widgets.DatePicker, "weight": pn.widgets.LiteralInput})
```

Let's expand the power curve by default:

```python
pn.Param(
    athlete, 
    widgets={
        "birthday": pn.widgets.DatePicker, 
        "weight": pn.widgets.LiteralInput
    }, expand=True)
```

Now let's try to display the Name and Birthday only and in a Row.

```python
pn.Param(
    athlete,
    widgets={"birthday": pn.widgets.DatePicker},
    parameters=["name_", "birthday"],
    show_name=False,
    default_layout=pn.Row,
    width=400
)
```

Let's customize the view of the `Athlete` some more.

```python
athlete_view = pn.Param(
    athlete,
    widgets={
        "birthday": pn.widgets.DatePicker, 
        "weight": {"type": pn.widgets.LiteralInput, "width": 100}
    },
    parameters=["name_", "birthday", "weight"],
    show_name=False,
    default_layout=pn.Row,
    width=600
)
athlete_view
```

Let's take a look at the PowerCurve.

```python
pn.Param(athlete.power_curve)
```

The PowerCurve layout is not that tidy. Let's change the layout to two columns.

```python
def new_class(cls, **kwargs):
    "Creates a new class which overrides parameter defaults."
    return type(type(cls).__name__, (cls,), kwargs)

power_curve_columns_view = pn.Param(
    athlete.power_curve,
    default_layout=new_class(pn.GridBox, ncols=2),
    show_name=False,
    widgets = {
        "ten_sec_date": pn.widgets.DatePicker, 
        "one_min_date": pn.widgets.DatePicker, 
        "ten_min_date": pn.widgets.DatePicker,
        "twenty_min_date": pn.widgets.DatePicker, 
        "one_hour_date": pn.widgets.DatePicker
    }
)

power_curve_columns_view
```

Let's put a plot of the PowerCurve in the mix.

```python
power_curve_view = pn.Row(
    power_curve_columns_view,
    athlete.power_curve.plot,
    sizing_mode='stretch_width'
)
power_curve_view
```

And finally, let's put things together.

```python
pn.Column(
    pn.pane.Markdown("### Athlete"), 
    athlete_view, 
    pn.pane.Markdown("#### Power Curve"), 
    power_curve_view,
    sizing_mode='stretch_width'
)
```

## Disabling continuous updates for slider widgets
When a function takes a long time to run and depends on a parameter, realtime feedback can be a burden instead of being helpful.

Therefore if a slider widget is used for a parameter and you have a function which takes long time to calculate, you can set the `throttled` keyword in the `panel.param.widgets` to `True` for the given parameter. This will then first run the function after the release of the mouse button of the slider.

An example can be seen below where two parameters is connected to two sliders, one with and one without `throttled` enabled.

```python
class A(param.Parameterized):

    without_throttled_enabled = param.Range(
        default=(100, 250),
        bounds=(0, 250),
    )

    with_throttled_enabled = param.Range(
        default=(100, 250),
        bounds=(0, 250),
    )

    def __init__(self, **params):
        super().__init__(**params)
        widgets = {
            "without_throttled_enabled": pn.widgets.IntRangeSlider,
            "with_throttled_enabled": {
                "type": pn.widgets.IntRangeSlider,
                "throttled": True,
            },
        }
        self.controls = pn.Param(self, widgets=widgets)

    def calculation(self):
        return self.without_throttled_enabled, self.with_throttled_enabled

a = A()
pn.Column(a.controls, a.calculation)
```

---
