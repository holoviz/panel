# Textual
---
The `Textual` pane allows rendering a [Textual](https://textual.textualize.io/) application inside a Panel application. It patches a custom Panel driver and renders the application into a `Terminal` component with full support for mouse and keyboard events.

There are a few things to note:

- Once an `App` instance is bound to a `Textual` pane it cannot be reused in another pane or otherwise and you can only bind an App instance to a single session.
- The application must be instantiated on the same thread as the server it will be running on, i.e. if you serve the app with `pn.serve(..., threaded=True)` you must instantiate the `App` inside a function.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``object``** (`textual.app.App`): The Textual application to render.

___

A Textual `App` can be passed directly to the `Textual` pane and Panel will handle the rest, i.e. it will start the application, handle inputs, re-rendering and so on. In other words the application will work just as if it was running inside a regular terminal.

Let us start with a very simple example:

```python
import panel as pn

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Footer, Header, Static

pn.extension("terminal")

QUESTION = "Do you want to learn about Textual CSS?"

class ExampleApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Static(QUESTION, classes="question"),
            Horizontal(
                Button("Yes", variant="success"),
                Button("No", variant="error"),
                classes="buttons",
            ),
            id="dialog",
        )

example_app = ExampleApp()

pn.pane.Textual(example_app, width=600, height=400)
```

This will work just as well for simple apps as it does for more complex applications. As an example here we have embedded the Calculator example application from the Textual documentation.

```python
import panel as pn

from decimal import Decimal

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Digits

from pathlib import Path
import requests

pn.extension("terminal")

def _download_file_if_not_exists(url: str, local_path: str) -> Path:
    local_file_path = Path(local_path)

    if not local_file_path.exists():
        response = requests.get(url)
        response.raise_for_status()
        local_file_path.write_bytes(response.content)

    return local_file_path

file_url = "https://raw.githubusercontent.com/holoviz/panel/main/examples/assets/calculator.tcss"
local_file_path = "calculator.tcss"
calculator_tcss = _download_file_if_not_exists(file_url, local_file_path)

class CalculatorApp(App):
    """A working 'desktop' calculator."""

    CSS_PATH = calculator_tcss.absolute()

    numbers = var("0")
    show_ac = var(True)
    left = var(Decimal("0"))
    right = var(Decimal("0"))
    value = var("")
    operator = var("plus")

    NAME_MAP = {
        "asterisk": "multiply",
        "slash": "divide",
        "underscore": "plus-minus",
        "full_stop": "point",
        "plus_minus_sign": "plus-minus",
        "percent_sign": "percent",
        "equals_sign": "equals",
        "minus": "minus",
        "plus": "plus",
    }

    def watch_numbers(self, value: str) -> None:
        """Called when numbers is updated."""
        self.query_one("#numbers", Digits).update(value)

    def compute_show_ac(self) -> bool:
        """Compute switch to show AC or C button"""
        return self.value in ("", "0") and self.numbers == "0"

    def watch_show_ac(self, show_ac: bool) -> None:
        """Called when show_ac changes."""
        self.query_one("#c").display = not show_ac
        self.query_one("#ac").display = show_ac

    def compose(self) -> ComposeResult:
        """Add our buttons."""
        with Container(id="calculator"):
            yield Digits(id="numbers")
            yield Button("AC", id="ac", variant="primary")
            yield Button("C", id="c", variant="primary")
            yield Button("+/-", id="plus-minus", variant="primary")
            yield Button("%", id="percent", variant="primary")
            yield Button("÷", id="divide", variant="warning")
            yield Button("7", id="number-7", classes="number")
            yield Button("8", id="number-8", classes="number")
            yield Button("9", id="number-9", classes="number")
            yield Button("×", id="multiply", variant="warning")
            yield Button("4", id="number-4", classes="number")
            yield Button("5", id="number-5", classes="number")
            yield Button("6", id="number-6", classes="number")
            yield Button("-", id="minus", variant="warning")
            yield Button("1", id="number-1", classes="number")
            yield Button("2", id="number-2", classes="number")
            yield Button("3", id="number-3", classes="number")
            yield Button("+", id="plus", variant="warning")
            yield Button("0", id="number-0", classes="number")
            yield Button(".", id="point")
            yield Button("=", id="equals", variant="warning")

    def on_key(self, event: events.Key) -> None:
        """Called when the user presses a key."""

        def press(button_id: str) -> None:
            """Press a button, should it exist."""
            try:
                self.query_one(f"#{button_id}", Button).press()
            except NoMatches:
                pass

        key = event.key
        if key.isdecimal():
            press(f"number-{key}")
        elif key == "c":
            press("c")
            press("ac")
        else:
            button_id = self.NAME_MAP.get(key)
            if button_id is not None:
                press(self.NAME_MAP.get(key, key))

    @on(Button.Pressed, ".number")
    def number_pressed(self, event: Button.Pressed) -> None:
        """Pressed a number."""
        assert event.button.id is not None
        number = event.button.id.partition("-")[-1]
        self.numbers = self.value = self.value.lstrip("0") + number

    @on(Button.Pressed, "#plus-minus")
    def plus_minus_pressed(self) -> None:
        """Pressed + / -"""
        self.numbers = self.value = str(Decimal(self.value or "0") * -1)

    @on(Button.Pressed, "#percent")
    def percent_pressed(self) -> None:
        """Pressed %"""
        self.numbers = self.value = str(Decimal(self.value or "0") / Decimal(100))

    @on(Button.Pressed, "#point")
    def pressed_point(self) -> None:
        """Pressed ."""
        if "." not in self.value:
            self.numbers = self.value = (self.value or "0") + "."

    @on(Button.Pressed, "#ac")
    def pressed_ac(self) -> None:
        """Pressed AC"""
        self.value = ""
        self.left = self.right = Decimal(0)
        self.operator = "plus"
        self.numbers = "0"

    @on(Button.Pressed, "#c")
    def pressed_c(self) -> None:
        """Pressed C"""
        self.value = ""
        self.numbers = "0"

    def _do_math(self) -> None:
        """Does the math: LEFT OPERATOR RIGHT"""
        try:
            if self.operator == "plus":
                self.left += self.right
            elif self.operator == "minus":
                self.left -= self.right
            elif self.operator == "divide":
                self.left /= self.right
            elif self.operator == "multiply":
                self.left *= self.right
            self.numbers = str(self.left)
            self.value = ""
        except Exception:
            self.numbers = "Error"

    @on(Button.Pressed, "#plus,#minus,#divide,#multiply")
    def pressed_op(self, event: Button.Pressed) -> None:
        """Pressed one of the arithmetic operations."""
        self.right = Decimal(self.value or "0")
        self._do_math()
        assert event.button.id is not None
        self.operator = event.button.id

    @on(Button.Pressed, "#equals")
    def pressed_equals(self) -> None:
        """Pressed ="""
        if self.value:
            self.right = Decimal(self.value)
        self._do_math()

calculator = CalculatorApp()
textual_pane = pn.pane.Textual(calculator, height=600, width=400)

pn.template.FastListTemplate(
    site="Panel",
    title="Textual",
    main=[textual_pane],
    main_max_width="610px",
    main_layout=None,
    theme_toggle=False,   
).servable();
```

---
