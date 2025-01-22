# Create a Form with HoloViz Panel

Welcome to the "Create a Form" tutorial! In this guide, we will create an interactive and fully functional *form* using HoloViz Panel. By the end of this tutorial, you'll have built a form with validation that captures user input and processes it effectively. This tutorial adopts the `param.Parameterized` approach to ensure the form is extensible and maintainable.

<iframe src="https://panel-org-create-form.hf.space" frameborder="0" style="width: 100%;height:500px"></iframe>

---

## Key Objectives

- **Create an Interactive Form**: Build a form to capture Name, Email, and an optional Message.
- **Validate User Input**: Ensure the form inputs meet specified criteria.
- **Submit Data**: Simulate sending the form data for further processing.

---

## Implementation

Below is a step-by-step breakdown of the code to create the form.

### 1. Import Dependencies

```python
import panel as pn
import param
```

We use `panel` to build the interactive components and `param` for structured data handling and validation.

### 2. Define Form Text and Icons

We add some static elements to make the form visually appealing.

```python
FORM_TEXT = """\
<h1>Join Newsletter</h1>

Get the latest updates and news about Panel.
"""

FORM_ICON = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
  <path d="M3 7a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-10z"></path>
  <path d="M3 7l9 6l9 -6"></path>
</svg>
"""
```

### 3. Create a Parameterized Form State Class

The `FormState` class handles form inputs, validation, and state management.

```python
class FormState(param.Parameterized):
    name = param.String(default="", doc="The name of the user.")
    email = param.String(default="", doc="The email of the user.")
    message = param.String(default="", label="Message", doc="An optional message from the user")

    is_not_valid = param.Boolean(default=False)
    validation_errors = param.Dict()
    validation_message = param.String()

    def __init__(self, **params):
      params["name"]=params.get("name", "")
      super().__init__(**params)

    def _validate(self):
        errors = {}
        if not self.name:
            errors["name"] = "No *Name* entered."
        if not self.email:
            errors["email"] = "No *Email* entered."
        elif "@" not in self.email or "." not in self.email:
            errors["email"] = "Not a valid *Email*."

        self.validation_errors = errors
        self.is_not_valid = bool(errors)
        self.validation_message = "**Error**: " + " ".join(errors.values())

    def _to_dict(self):
        return {"name": self.name, "email": self.email, "message": self.message}

    def _reset_to_defaults(self):
        self.param.update(name="", email="", message="")

    def submit(self, event):
        self._validate()
        if not self.validation_errors:
            pn.state.notifications.success(f"Form submitted: {self._to_dict()}", duration=2000)
            self._reset_to_defaults()
```

### 4. Build the Form Layout

We use `pn.widgets` to create form inputs and buttons.

```python
def create_form():
    form_state = FormState()

    header = pn.Row(
        pn.pane.SVG(FORM_ICON, margin=0, height=80, sizing_mode="fixed"),
        FORM_TEXT,
    )

    error_pane = pn.pane.Alert(
        object=form_state.param.validation_message,
        visible=form_state.param.is_not_valid,
        alert_type="danger",
        stylesheets=["p {margin-bottom: 0}"]
    )

    name_input = pn.widgets.TextInput.from_param(form_state.param.name, name="Name*", placeholder="User Name")
    email_input = pn.widgets.TextInput.from_param(form_state.param.email, name="Email*", placeholder="Email Address")
    message_input = pn.widgets.TextAreaInput.from_param(form_state.param["message"], placeholder="An optional message")

    submit_button = pn.widgets.Button(name="Send", on_click=form_state.submit, button_type="primary")

    return pn.Column(
        header,
        error_pane,
        name_input,
        email_input,
        message_input,
        submit_button,
        sizing_mode="fixed",
        width=500,
        styles={"margin": "auto"}
    )
```

### 5. Serve the Application

Extend Panel with notifications, create the form, and mark it `.servable()`.

```python
pn.extension(notifications=True, design="bootstrap", sizing_mode="stretch_width")

form = create_form()
form.servable()
```

Finally you can serve the application with

```bash
panel serve app.py --dev --show
```

---

## Summary

In this tutorial, we built a fully functional form with the following features:

1. **User Input Fields**: Capturing Name, Email, and an optional Message.
2. **Input Validation**: Ensuring required fields are filled and valid.
3. **Form Submission**: Resetting the form upon successful submission and displaying notifications.

By structuring our app with `param.Parameterized`, we ensured that the form is easy to maintain and extend in the future.

---

## Full Code

Here's the complete code for reference:

```python
import panel as pn
import param
import json

FORM_TEXT = """\
<h1>Join Newsletter</h1>

Get the latest updates and news about Panel.
"""

FORM_ICON = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
  <path d="M3 7a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-10z"></path>
  <path d="M3 7l9 6l9 -6"></path>
</svg>
"""

class FormState(param.Parameterized):
    name = param.String(default="", doc="The name of the user.")
    email = param.String(default="", doc="The email of the user.")
    message = param.String(default="", label="Message", doc="An optional message from the user")

    is_not_valid = param.Boolean(default=False)
    validation_errors = param.Dict()
    validation_message = param.String()

    def __init__(self, **params):
      params["name"]=params.get("name", "")
      super().__init__(**params)

    def _validate(self):
        errors = {}
        if not self.name:
            errors["name"] = "No *Name* entered."
        if not self.email:
            errors["email"] = "No *Email* entered."
        elif "@" not in self.email or "." not in self.email:
            errors["email"] = "Not a valid *Email*."

        self.validation_errors = errors
        self.is_not_valid = bool(errors)
        self.validation_message = "**Error**: " + " ".join(errors.values())

    def _to_dict(self):
        return {"name": self.name, "email": self.email, "message": self.message}

    def _reset_to_defaults(self):
        self.param.update(name="", email="", message="")

    def submit(self, event):
        self._validate()
        if not self.validation_errors:
            pn.state.notifications.success(f"Form submitted: {self._to_dict()}", duration=2000)
            self._reset_to_defaults()


def create_form():
    form_state = FormState()

    header = pn.Row(
        pn.pane.SVG(FORM_ICON, margin=0, height=80, sizing_mode="fixed"),
        FORM_TEXT,
    )

    error_pane = pn.pane.Alert(
        object=form_state.param.validation_message,
        visible=form_state.param.is_not_valid,
        alert_type="danger",
        stylesheets=["p {margin-bottom: 0}"]
    )

    name_input = pn.widgets.TextInput.from_param(form_state.param.name, name="Name*", placeholder="User Name")
    email_input = pn.widgets.TextInput.from_param(form_state.param.email, name="Email*", placeholder="Email Address")
    message_input = pn.widgets.TextAreaInput.from_param(form_state.param["message"], placeholder="An optional message")

    submit_button = pn.widgets.Button(name="Send", on_click=form_state.submit, button_type="primary")

    return pn.Column(
        header,
        error_pane,
        name_input,
        email_input,
        message_input,
        submit_button,
        sizing_mode="fixed",
        width=500,
        styles={"margin": "auto"}
    )

pn.extension(notifications=True, design="bootstrap", sizing_mode="stretch_width")

form = create_form()
form.servable()
```
