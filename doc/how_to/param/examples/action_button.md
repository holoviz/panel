# param.Action Example

```{pyodide}
import param
import panel as pn

pn.extension(template='bootstrap')
```

This example demonstrates how to use ``param.Action`` to trigger an update in a method that depends on that parameter. Actions can trigger any function, but if we simply want to trigger a method that depends on that action, then we can define a small ``lambda`` function that triggers the parameter explicitly:

```{pyodide}
class ActionExample(param.Parameterized):
    """
    Demonstrates how to use param.Action to trigger an update.
    """

    action = param.Action(default=lambda x: x.param.trigger('action'), label='Click here!')

    number = param.Integer(default=0)

    @param.depends('action')
    def get_number(self):
        self.number += 1
        return f'Number: {self.number}'

action_example = ActionExample()

pn.Row(
    pn.Column(
        pn.panel(action_example, show_name=False, margin=0, widgets={"action": {"button_type": "primary"}, "number": {"disabled": True}}),
        '**Click the button** to trigger an update in the output.'
    ),
    action_example.get_number,
).servable()
```
