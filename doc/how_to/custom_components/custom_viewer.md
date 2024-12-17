# Combine Existing Components

This guide addresses how to build custom components that are combinations of existing components.

---

The simplest way to extend Panel is to implement a so called `Viewer` component that can wrap multiple existing Panel components into an easily reusable unit that behaves like a native Panel component.

Let's create a composite `EditableRange` component made up of two `FloatInput` widgets. First, we will create the widgets:

``` {code-block} python
:emphasize-lines: 13-14

import param
import panel as pn
from panel.viewable import Viewer
pn.extension() # for notebook

class EditableRange(Viewer):

    value = param.Range(doc="A numeric range.")

    width = param.Integer(default=300)

    def __init__(self, **params):
        self._start_input = pn.widgets.FloatInput()
        self._end_input = pn.widgets.FloatInput(align='end')
        super().__init__(**params)
        self._layout = pn.Row(self._start_input, self._end_input)
```

Then, we set up callbacks to sync the parameters on the underlying widgets with the parameters on the `Viewer` component.

``` {code-block} python
:emphasize-lines: 17, 19-29

import param
import panel as pn
from panel.viewable import Viewer
pn.extension() # for notebook

class EditableRange(Viewer):

    value = param.Range(doc="A numeric range.")

    width = param.Integer(default=300)

    def __init__(self, **params):
        self._start_input = pn.widgets.FloatInput()
        self._end_input = pn.widgets.FloatInput(align='end')
        super().__init__(**params)
        self._layout = pn.Row(self._start_input, self._end_input)
        self._sync_widgets()

    @param.depends('value', 'width', watch=True)
    def _sync_widgets(self):
        self._start_input.name = self.name
        self._start_input.value = self.value[0]
        self._end_input.value = self.value[1]
        self._start_input.width = self.width//2
        self._end_input.width = self.width//2

    @param.depends('_start_input.value', '_end_input.value', watch=True)
    def _sync_params(self):
        self.value = (self._start_input.value, self._end_input.value)

```

Finally, we'll implement the required ``__panel__`` method, which returns the Panel layout to be rendered. Panel will call this method when displaying the component.

```{pyodide}
import param
import panel as pn

from panel.viewable import Viewer

pn.extension() # for notebook

class EditableRange(Viewer):

    value = param.Range(doc="A numeric range.")

    width = param.Integer(default=300)

    def __init__(self, **params):
        self._start_input = pn.widgets.FloatInput()
        self._end_input = pn.widgets.FloatInput(align='end')
        super().__init__(**params)
        self._layout = pn.Row(self._start_input, self._end_input)
        self._sync_widgets()

    def __panel__(self):
        return self._layout

    @param.depends('value', 'width', watch=True)
    def _sync_widgets(self):
        self._start_input.name = self.name
        self._start_input.value = self.value[0]
        self._end_input.value = self.value[1]
        self._start_input.width = self.width//2
        self._end_input.width = self.width//2

    @param.depends('_start_input.value', '_end_input.value', watch=True)
    def _sync_params(self):
        self.value = (self._start_input.value, self._end_input.value)

range_widget = EditableRange(name='Range', value=(0, 10))

pn.Column(
    '#### This is a custom widget',
    range_widget
)
```

## Related Resources

- To create custom components from scratch, check out [How To > Build Components from Scratch](./reactive_html/reactive_html_widgets.md) and read the associated [Explanation > Building Custom Components](../../explanation/components/reactive_html_components.md) for further explanation.
