# Control `Pipeline` Flow

This guide addresses how to programmatically control the `Pipeline` UI flow.

```{admonition} Prerequisites
1. The [Create a Non-Linear Pipeline](./complex_pipeline.md) How-to Guide walks through the creation of branching pipeline that commonly used in the context of controlling pipeline flow.
```
---

By default, controlling the flow between different stages is done using the "Previous" and "Next" buttons. However, we often want to control the UI flow programmatically from within a stage. We can do this with the following parameters:

- The `ready_parameter` can block (`False`) or unblock (`True`) potential advancement to the next stage.
- The `auto_advance` parameter will automatically advance to the next stage if unblocked by the `ready_parameter`.
- The `next_parameter` argument can be used to dynamically set which stage will be next.

In this way we can control the workflow programmatically from inside the stages.

In the example below we create a branching and converging workflow that can be used without the buttons by declaring `ready_parameter` and `auto_advance` for each of the stages, which we can toggle with a custom button or simply set to `True` by default to automatically proceed to the next stage.

We will also control which branching stage to switch to from within a stage by declaring a parameter which will hold the name of the next stage to switch to. In this case, we create a parameter to select between `Add` and `Multiply` stages. Later, we will point the pipeline to this parameter using the `next_parameter` argument.

First, let's create our stages:

```{pyodide}
import param
import panel as pn
pn.extension() # for notebook

class Input(param.Parameterized):

    value1 = param.Integer(default=2, bounds=(0,10))
    value2 = param.Integer(default=3, bounds=(0,10))
    operator = param.Selector(default='Multiply', objects=['Multiply', 'Add'])
    ready = param.Boolean(default=False)

    def panel(self):
        button = pn.widgets.Button(name='Go', button_type='success')
        button.on_click(lambda event: setattr(self, 'ready', True)) # allows auto-advance to proceed
        widgets = pn.Row(self.param.value1, self.param.operator, self.param.value2)
        for w in widgets:
            w.width = 85
        return pn.Column(widgets, button)

class Multiply(param.Parameterized):

    value1 = param.Integer()
    value2 = param.Integer()
    ready = param.Boolean(default=True)

    def panel(self):
        return pn.pane.Markdown(f'# {self.value1} * {self.value2}')

    @param.output('equation')
    def output(self):
        return f'# {self.value1} * {self.value2} = {self.value1 * self.value2}'

class Add(param.Parameterized):

    value1 = param.Integer()
    value2 = param.Integer()
    ready = param.Boolean(default=True)

    def panel(self):
        return pn.pane.Markdown(f'# {self.value1} + {self.value2} =')

    @param.output('equation')
    def output(self):
        return f'# {self.value1} + {self.value2} = {self.value1 + self.value2}'

class Result(param.Parameterized):

    equation = param.String()

    def panel(self):
        return pn.pane.Markdown(self.equation)
```

Now let's add the stages to a pipeline and define the graph:

```{pyodide}
dag = pn.pipeline.Pipeline()

dag.add_stage('Input', Input, ready_parameter='ready', auto_advance=True, next_parameter='operator')
dag.add_stage('Multiply', Multiply, ready_parameter='ready', auto_advance=True)
dag.add_stage('Add', Add, ready_parameter='ready', auto_advance=True)
dag.add_stage('Result', Result)

dag.define_graph({'Input': ('Multiply', 'Add'), 'Multiply': 'Result', 'Add': 'Result'})

```

Finally we display the pipeline without the `Next` button, which is appropriate because all the flow control is now handled from within the stages:

```{pyodide}
pn.Column(
    dag.title,
    dag.network,
    dag.stage,
    dag.prev_button
)
```

As you can see, a panel Pipeline can be used to set up complex workflows when needed, with each stage controlled either manually or from within the stage, without having to define complex callbacks or other GUI logic.


Here is the complete code for this section in case you want to easily copy it:


```{pyodide}
import param
import panel as pn
pn.extension() # for notebook

class Input(param.Parameterized):

    value1 = param.Integer(default=2, bounds=(0,10))
    value2 = param.Integer(default=3, bounds=(0,10))
    operator = param.Selector(default='Multiply', objects=['Multiply', 'Add'])
    ready = param.Boolean(default=False)

    def panel(self):
        button = pn.widgets.Button(name='Go', button_type='success')
        button.on_click(lambda event: setattr(self, 'ready', True)) # allows auto-advance to proceed
        widgets = pn.Row(self.param.value1, self.param.operator, self.param.value2)
        for w in widgets:
            w.width = 85
        return pn.Column(widgets, button)

class Multiply(param.Parameterized):

    value1 = param.Integer()
    value2 = param.Integer()
    ready = param.Boolean(default=True)

    def panel(self):
        return pn.pane.Markdown(f'# {self.value1} * {self.value2}')

    @param.output('equation')
    def output(self):
        return f'# {self.value1} * {self.value2} = {self.value1 * self.value2}'

class Add(param.Parameterized):

    value1 = param.Integer()
    value2 = param.Integer()
    ready = param.Boolean(default=True)

    def panel(self):
        return pn.pane.Markdown(f'# {self.value1} + {self.value2} =')

    @param.output('equation')
    def output(self):
        return f'# {self.value1} + {self.value2} = {self.value1 + self.value2}'

class Result(param.Parameterized):

    equation = param.String()

    def panel(self):
        return pn.pane.Markdown(self.equation)

dag = pn.pipeline.Pipeline()

dag.add_stage('Input', Input, ready_parameter='ready', auto_advance=True, next_parameter='operator')
dag.add_stage('Multiply', Multiply, ready_parameter='ready', auto_advance=True)
dag.add_stage('Add', Add, ready_parameter='ready', auto_advance=True)
dag.add_stage('Result', Result)

dag.define_graph({'Input': ('Multiply', 'Add'), 'Multiply': 'Result', 'Add': 'Result'})

pn.Column(
    dag.title,
    dag.network,
    dag.stage,
    dag.prev_button
)
```

## Related Resources
- The [How to > Customize Pipeline Layout](./pipeline_layout.md) guide provides some context for the custom layout used here.
- The [How to > Create a Non-Linear Pipeline](./complex_pipeline.md) guide walks through the creation of branching pipeline that commonly used in the context of controlling pipeline flow.
