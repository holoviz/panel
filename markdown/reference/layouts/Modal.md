# Modal
---
```python
import panel as pn
pn.extension('modal')
```

The `Modal` layout provides a dialog windows on top of the layout. It is built on-top of [a11y-dialog](https://a11y-dialog.netlify.app/). It has a list-like API with methods to `append`, `extend`, `clear`, `insert`, `pop`, `remove` and `__setitem__`, which make it possible to interactively update and modify the layout. Components inside it are laid out like a `Column`.

#### Parameters:

* **`open`** (boolean): Whether to open the modal.
* **`show_close_button`** (boolean): Whether to show a close button in the modal.
* **`background_close`** (boolean): Whether to enable closing the modal when clicking outside the modal.

#### Methods:

* **`show`**: Show the modal.
* **`hide`**: Hide the modal.
* **`toggle`**: toggle the modal.
* **`create_button`**: Create a button which can either show, hide, or toggle the modal.

A `Modal` layout can either be instantiated as empty and populated after the fact or using a list of objects provided as positional arguments. If the objects are not already panel components they will each be converted to one using the `pn.panel` conversion method.

```python
w1 = pn.widgets.TextInput(label='Text:')
w2 = pn.widgets.FloatSlider(label='Slider')

modal = pn.Modal(w1, w2, name='Basic FloatPanel', margin=20)
toggle_button = modal.create_button("toggle", label="Toggle modal")

pn.Column('**Example: Basic `Modal`**', toggle_button, modal)
```

### Controls

The `Modal` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
modal.controls(jslink=True)
```

---
