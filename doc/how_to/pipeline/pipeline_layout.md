# Customize `Pipeline` Layout

This guide addresses how to customize the visual layout of the Panel `Pipeline` UI.

---

A `Pipeline` object has the following components that you can customize to display in any configuration.

- `layout`: The overall layout of the header and stage.
- `header`: The navigation components and network diagram.
- `title`: The name of the current stage.
- `network`: A network diagram representing the pipeline.
- `stage`: The contents of the current pipeline stage.
- `buttons`: All navigation buttons and selectors.
- `prev_button`: The button to go to the previous stage.
- `prev_selector`: The selector widget to select between previous branching stages.
- `next_button`:   The button to go to the previous stage
- `next_selector`: The selector widget to select the next branching stages.

For instance, let's rearrange the layout of a simple non-linear pipeline. For a walk-through of this type of pipeline, refer to the [Create a Non-Linear Pipeline](./complex_pipeline.md) How-to Guide.

First, let's create the stages and add them to a pipeline:

```{pyodide}
import param
import panel as pn
pn.extension() # for notebook

class Input(param.Parameterized):

    value1 = param.Integer(default=2, bounds=(0,10))
    value2 = param.Integer(default=3, bounds=(0,10))

    def panel(self):
        return pn.Column(self.param.value1, self.param.value2)

class Multiply(Input):

    value1 = param.Integer()
    value2 = param.Integer()
    operator = param.String(default='*')

    def panel(self):
        return pn.pane.Markdown(f'# {self.value1} * {self.value2}')

    @param.output('result')
    def output(self):
        return self.value1 * self.value2

class Add(Input):

    value1 = param.Integer()
    value2 = param.Integer()
    operator = param.String(default='+')

    def panel(self):
        return pn.pane.Markdown(f'# {self.value1} + {self.value2}')

    @param.output('result')
    def output(self):
        return self.value1 + self.value2

class Result(Input):

    value1 = param.Integer()
    value2 = param.Integer()
    operator = param.String(default='')
    result = param.Integer(default=0)

    def panel(self):
        return pn.pane.Markdown(f'# {self.value1} {self.operator} {self.value2} = {self.result}')

dag = pn.pipeline.Pipeline()

dag.add_stage('Input', Input)
dag.add_stage('Multiply', Multiply)
dag.add_stage('Add', Add)
dag.add_stage('Result', Result)

dag.define_graph({'Input': ('Multiply', 'Add'), 'Multiply': 'Result', 'Add': 'Result'})
```

Now we can use any of the layout components to arrange the UI:

```{pyodide}
pn.Column(
    dag.title,
    pn.Row(dag.buttons, pn.layout.HSpacer(), dag.stage),
    dag.network
)
```

## Related Resources
- The [How to > Create a Non-Linear Pipeline](./complex_pipeline.md) guide contains a walk-through of the type of pipeline used on the current page.
