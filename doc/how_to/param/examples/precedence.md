# Param Precedence

```{pyodide}
import panel as pn
import param

pn.extension(template='bootstrap')
````

This example demonstrates how to order and hide widgets by means of the ``precedence`` and  ``display_threshold`` attributes.

Each ``Parameter`` object has a ``precedence`` attribute that is defined as follows  in the documentation of ``param``:

> ``precedence`` is a value, usually in the range 0.0 to 1.0, that allows the order of Parameters in a class to be defined (for e.g. in GUI menus).
> A negative precedence indicates a parameter that should be hidden in e.g. GUI menus.

A `Param` pane has a ``display_threshold`` attribute defaulting to 0 and defined as follows:

> Parameters with precedence below this value are not displayed.

The interactive example below helps to understand how the interplay between these two attributes affects the display of widgets.

The ``PrecedenceTutorial`` class emulates a dummy app whose display we want to control and that consists of three input parameters, ``x``, ``y`` and ``z``. These parameters will be displayed by `panel` with their associated default widgets. Additionally, the class declares the four parameters that will control the dummy app display: ``x_precedence``, ``y_precedence`` and ``z_precedence`` and ``dummy_app_display_threshold``.

```{pyodide}
class Precedence(param.Parameterized):

    # Parameters of the dummy app.
    x = param.Number(precedence=-1)
    y = param.Boolean(precedence=3)
    z = param.String(precedence=2)

    # Parameters of the control app.
    x_precedence = param.Number(default=x.precedence, bounds=(-10, 10), step=1)
    y_precedence = param.Number(default=y.precedence, bounds=(-10, 10), step=1)
    z_precedence = param.Number(default=z.precedence, bounds=(-10, 10), step=1)
    dummy_app_display_threshold = param.Number(default=1, bounds=(-10, 10), step=1)

    def __init__(self):
        super().__init__()
        # Building the dummy app as a Param pane in here so that its ``display_threshold``
        # parameter can be accessed and linked via @param.depends(...).
        self.dummy_app = pn.Param(
            self.param,
            parameters=["x", "y", "z"],
            widgets={
                "x": {"styles": {"background": "#fac400"}},
                "y": {"styles": {"background": "#07d900"}},
                "z": {"styles": {"background": "#00c0d9"}},
            },
            show_name=False
        )

    # Linking the two apps here.
    @param.depends("dummy_app_display_threshold", "x_precedence", "y_precedence", "z_precedence", watch=True)
    def update_precedences_and_threshold(self):
        self.param.x.precedence = self.x_precedence
        self.param.y.precedence = self.y_precedence
        self.param.z.precedence = self.z_precedence
        self.dummy_app.display_threshold = self.dummy_app_display_threshold

precedence_model = Precedence()

# Building the control app as a Param pane too.
control_app = pn.Param(
    precedence_model.param,
    parameters=["x_precedence", "y_precedence", "z_precedence", "dummy_app_display_threshold"],
    widgets={
        "x_precedence": {"styles": {"background": "#fac400"}},
        "y_precedence": {"styles": {"background": "#07d900"}},
        "z_precedence": {"styles": {"background": "#00c0d9"}},
    },
    show_name=False
)

# Building the complete interactive example.
pn.Column(
    "## Precedence Example",
    "Moving the sliders of the control app should update the display of the dummy app.",
    pn.Row(
        pn.Column("**Control app**", control_app),
        pn.Column("**Dummy app**", precedence_model.dummy_app)
    )
).servable()
```
