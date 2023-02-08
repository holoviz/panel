# Create a Non-Linear `Pipeline`

This guide addresses how to build a non-linear Panel Pipeline with branching and converging steps, i.e., an acyclic graph.

```{admonition} Prerequisites
1. The [Param with Panel](../param/index.md) How-to Guides describe how to set up classes that declare parameters and link them to some computation or visualization.
2. The [Create a `Pipeline`](./simple_pipeline.md) How-to Guide walks through the essential components of a pipeline.
```

---

An example of a non-linear pipeline might be a workflow with two alternative stages that rejoin at a later point. Let's create a pipeline with alternative stages (`Add` or `Multiply`) by declaring how each stage feeds into the other stages.

First, we declare four simple stages: `Input`, `Multiply`, `Add`, and `Result`.

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

    def panel(self):
        return pn.pane.Markdown('# %d * %d' % (self.value1, self.value2))

    @param.output('result')
    def output(self):
        return self.value1 * self.value2

class Add(Input):

    def panel(self):
        return pn.pane.Markdown('# %d + %d' % (self.value1, self.value2))

    @param.output('result')
    def output(self):
        return self.value1 + self.value2

class Result(Input):

    result = param.Number(default=0)

    def panel(self):
        return pn.pane.Markdown('# %d' % self.result)
```

Now let's add these stages to a new Pipeline:

```{pyodide}
dag = pn.pipeline.Pipeline()

dag.add_stage('Input', Input)
dag.add_stage('Multiply', Multiply)
dag.add_stage('Add', Add)
dag.add_stage('Result', Result)
```

Now comes the important part that differs from a simple linear pipeline. After adding all the stages we have to express the alternative branching aspect. We can use the `define_graph` method to provide an adjacency map which declares how each stage feeds into the other stages. In this case the `Input` feeds into both `Multiply` and `Add` and both those stages feed into the `Result`:

```{pyodide}
dag.define_graph({'Input': ('Multiply', 'Add'), 'Multiply': 'Result', 'Add': 'Result'})
```

Now let's view our result:

```{pyodide}
dag
```

This is of course a very simple example of a non-linear pipeline but it demonstrates the ability to express arbitrary workflows with branching and converging steps

## Related Resources
- The [Param with Panel](../param/index.md) How-to Guides describe how to set up classes that declare parameters and link them to some computation or visualization.
- The [Create a `Pipeline`](./simple_pipeline.md) How-to Guide walks through the essential components of a pipeline.
