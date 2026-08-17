# Reacton
---
```python
import numpy as np
import panel as pn
import reacton
import reacton.ipywidgets as w

pn.extension('ipywidgets')
```

The ``Reacton`` pane renders [Reacton](https://reacton.solara.dev/en/latest/) components both in the notebook and in a deployed server. Reacton provides a way to write reusable components in a React-like way, to make Python-based UI's using the ipywidgets ecosystem (ipywidgets, ipyvolume, bqplot, threejs, leaflet, ipyvuetify, ...). Note that Reacton is primarily a way to write apps

In the notebook this is not necessary since Panel simply uses the regular notebook ipywidget renderer. Particularly in JupyterLab importing the ipywidgets extension in this way may interfere with the UI and render the JupyterLab UI unusable, so enable the extension with care.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``object``** (object): The ipywidget object being displayed

##### Display

* **``default_layout``** (pn.layout.Panel, default=Row): Layout to wrap the plot and widgets in

___

The `panel` function will automatically convert any ``ipywidgets`` object into a displayable panel, while keeping all of its interactive features:

```python
@reacton.component
def ButtonClick():
    # first render, this return 0, after that, the last argument
    # of set_clicks
    clicks, set_clicks = reacton.use_state(0)
    
    def my_click_handler():
        # trigger a new render with a new value for clicks
        set_clicks(clicks+1)

    button = w.Button(description=f"Clicked {clicks} times",
                      on_click=my_click_handler)
    return button

pn.panel(ButtonClick())
```

## Combining Reacton and Panel components

Reacton can be used in conjunction with Panel components however we have to make two modifications:

1. Panel components have to be wrapped as an ipywidget using the `pn.ipywidget` wrapper (this requires `jupyter_bokeh`).
2. The wrapped Panel component must be added to a reacton layout component.

In the example below we swap out the `reacton.ipywidgets.Button` for a `pn.widgets.Button` and then wrap it in `pn.ipywidgets` and a `reacton.ipywidgets.VBox`:

```python
@reacton.component
def PanelButtonClick():
    # first render, this return 0, after that, the last argument
    # of set_clicks
    clicks, set_clicks = reacton.use_state(0)
    
    def my_click_handler(event):
        # trigger a new render with a new value for clicks
        set_clicks(clicks+1)

    button = pn.widgets.Button(label=f'Clicked {clicks} times')
    button.on_click(my_click_handler)

    return w.VBox(children=[pn.ipywidget(button)])

pn.panel(PanelButtonClick(), height=50)
```

## Complex examples

Even more complex applications can be built in Reacton and displayed in Panel. Here is a Calculator example from the Reacton documentation.

### Logic

```python
import ast
import dataclasses
import operator
from typing import Any, Optional

DEBUG = False
operator_map = {
    "x": operator.mul,
    "/": operator.truediv,
    "+": operator.add,
    "-": operator.sub,
}

@dataclasses.dataclass(frozen=True)
class CalculatorState:
    input: str = ""
    output: str = ""
    left: float = 0
    right: Optional[float] = None
    operator: Any = operator.add
    error: str = ""

initial_state = CalculatorState()

def calculate(state: CalculatorState):
    result = state.operator(state.left, state.right)
    return dataclasses.replace(state, left=result)

def calculator_reducer(state: CalculatorState, action):
    action_type, payload = action
    if DEBUG:
        print("reducer", state, action_type, payload)  # noqa
    state = dataclasses.replace(state, error="")

    if action_type == "digit":
        digit = payload
        input = state.input + digit
        return dataclasses.replace(state, input=input, output=input)
    elif action_type == "percent":
        if state.input:
            try:
                value = ast.literal_eval(state.input)
            except Exception as e:
                return dataclasses.replace(state, error=str(e))
            state = dataclasses.replace(state, right=value / 100)
            state = calculate(state)
            output = f"{value / 100:,}"
            return dataclasses.replace(state, output=output, input="")
        else:
            output = f"{state.left / 100:,}"
            return dataclasses.replace(state, left=state.left / 100, output=output)
    elif action_type == "negate":
        if state.input:
            input = state.output
            input = input[1:] if input[0] == "-" else "-" + input
            output = input
            return dataclasses.replace(state, input=input, output=output)
        else:
            output = f"{-state.left:,}"
            return dataclasses.replace(state, left=-state.left, output=output)
    elif action_type == "clear":
        return dataclasses.replace(state, input="", output="")
    elif action_type == "reset":
        return initial_state
    elif action_type == "calculate":
        if state.input:
            try:
                value = ast.literal_eval(state.input)
            except Exception as e:
                return dataclasses.replace(state, error=str(e))
            state = dataclasses.replace(state, right=value)
        state = calculate(state)
        output = f"{state.left:,}"
        state = dataclasses.replace(state, output=output, input="")
        return state
    elif action_type == "operator":
        if state.input:
            state = calculator_reducer(state, ("calculate", None))
            state = dataclasses.replace(state, operator=payload, input="")
        else:
            # e.g. 2+3=*= should give 5,25
            state = dataclasses.replace(state, operator=payload, right=state.left)
        return state
    else:
        print("invalid action", action)  # noqa
        return state

```

### UI

#### ipywidgets

```python
@reacton.component
def Calculator():
    state, dispatch = reacton.use_reducer(calculator_reducer, initial_state)
    with w.VBox() as main:
        w.HTML(value="<b>Calculator Using Reacton</b>")
        with w.VBox():
            w.HTML(value=state.error or state.output or "0")
            with w.HBox():
                if state.input:
                    w.Button(description="C", on_click=lambda: dispatch(("clear", None)))
                else:
                    w.Button(description="AC", on_click=lambda: dispatch(("reset", None)))
                w.Button(description="+/-", on_click=lambda: dispatch(("negate", None)))
                w.Button(description="%", on_click=lambda: dispatch(("percent", None)))
                w.Button(description="/", on_click=lambda: dispatch(("operator", operator_map["/"])))

            column_op = ["x", "-", "+"]
            for i in range(3):
                with w.HBox():
                    for j in range(3):
                        digit = str(j + (2 - i) * 3 + 1)
                        w.Button(description=digit, on_click=lambda digit=digit: dispatch(("digit", digit)))
                    op_symbol = column_op[i]
                    op = operator_map[op_symbol]
                    w.Button(description=op_symbol, on_click=lambda op=op: dispatch(("operator", op)))
            with w.HBox():
                def boom():
                    print("boom")
                    raise ValueError("boom")

                w.Button(description="?", on_click=boom)

                w.Button(description="0", on_click=lambda: dispatch(("digit", "0")))
                w.Button(description=".", on_click=lambda: dispatch(("digit", ".")))

                w.Button(description="=", on_click=lambda: dispatch(("calculate", None)))

    return main

calculator = Calculator()
    
pn.pane.Reacton(calculator, width=500, height=250)
```

#### ipyvuetify

```python
import reacton.ipyvuetify as v

@reacton.component
def CalculatorVuetify():
    state, dispatch = reacton.use_reducer(calculator_reducer, initial_state)
    with v.Card(elevation=10, class_="ma-4") as main:
        with v.CardTitle(children=["Calculator"]):
            pass
        with v.CardSubtitle(children=["With ipyvuetify and Reacton"]):
            pass
        with v.CardText():
            with w.VBox():
                w.HTML(value=state.error or state.output or "0")
                class_ = "pa-0 ma-1"

                with w.HBox():
                    if state.input:
                        btn = v.Btn(children="C", dark=True, class_=class_)
                        v.use_event(btn, 'click', lambda _, __, ___: dispatch(("clear", None)))
                    else:
                        btn = v.Btn(children="AC", dark=True, class_=class_)
                        v.use_event(btn, 'click', lambda _, __, ___: dispatch(("clear", None)))
                    btn = v.Btn(children="+/-", dark=True, class_=class_)
                    v.use_event(btn, 'click', lambda _, __, ___: dispatch(("negate", None)))
                    btn = v.Btn(children="%", dark=True, class_=class_)
                    v.use_event(btn, 'click', lambda _, __, ___: dispatch(("percent", None)))
                    btn = v.Btn(children="/", color="primary", class_=class_)
                    v.use_event(btn, 'click', lambda _, __, ___: dispatch(("operator", operator_map["/"])))
                column_op = ["x", "-", "+"]
                for i in range(3):
                    with w.HBox():
                        for j in range(3):
                            digit = str(j + (2 - i) * 3 + 1)
                            btn = v.Btn(children=digit, class_=class_)
                            v.use_event(btn, 'click', lambda _, __, ___, digit=digit: dispatch(("digit", digit)))
                        op_symbol = column_op[i]
                        op = operator_map[op_symbol]
                        btn = v.Btn(children=op_symbol, color="primary", class_=class_)
                        v.use_event(btn, 'click', lambda _, __, ___, op=op: dispatch(("operator", op)))
                with w.HBox():
                    def boom():
                        print("boom")
                        raise ValueError("boom")

                    v.Btn(children="?", on_click=boom, class_=class_)

                    btn = v.Btn(children="0", class_=class_)
                    v.use_event(btn, 'click', lambda _, __, ___: dispatch(("digit", 0)))
                    btn = v.Btn(children=".", class_=class_)
                    v.use_event(btn, 'click', lambda _, __, ___: dispatch(("digit", ".")))
                    btn = v.Btn(children="=", color="primary", class_=class_)
                    v.use_event(btn, 'click', lambda _, __, ___: dispatch(("calculate", None)))
    return main

pn.pane.Reacton(CalculatorVuetify(), width=500, height=420)
```

---
