# Create a `Pipeline`

This guide addresses how to create a simple linear Panel `Pipeline`.

___

A Panel `Pipeline` can be used to express complex multi-page workflows where the output of one stage feeds into the next stage.

Let's start by instantiating an empty ``Pipeline``. We will use the 'katex' extension to render some mathematical symbols later.

```{pyodide}
import param
import panel as pn
pn.extension('katex')

pipeline = pn.pipeline.Pipeline()
```

Now let's add a stage to our pipeline. Each stage is `Parameterized` class with:

1. Input parameters, e.g. `a = param.Number(default=5, bounds=(0, 10))`
2. At least one method decorated with the `param.output` decorator whose returned objects can be passed along to the next stage
3. A ``panel`` method that returns a view of the object that the ``Pipeline`` can render

The example below takes two inputs (``a`` and ``b``) and produces two outputs (``c``, computed by multiplying the inputs, and ``d``, computed by raising ``a`` to the power ``b``).

```{pyodide}
class Stage1(param.Parameterized):

    a = param.Number(default=5, bounds=(0, 10))

    b = param.Number(default=5, bounds=(0, 10))

    ready = param.Boolean(default=False, precedence=-1)

    @param.output(('c', param.Number), ('d', param.Number))
    def output(self):
        return self.a * self.b, self.a ** self.b

    @param.depends('a', 'b')
    def view(self):
        c, d = self.output()
        return pn.pane.LaTeX('${a} * {b} = {c}$\n${a}^{{{b}}} = {d}$'.format(
            a=self.a, b=self.b, c=c, d=d), style={'font-size': '2em'})

    def panel(self):
        return pn.Row(self.param, self.view)

stage1 = Stage1()
stage1.panel()
```

Now let us add this stage to our ``Pipeline`` using the ``add_stage`` method:


```{pyodide}
pipeline.add_stage('Stage 1', stage1)
```

Now let's add a second stage which .... and add it to our pipeline:

```{pyodide}
class Stage2(param.Parameterized):

    c = param.Number(default=5, bounds=(0, None))

    exp = param.Number(default=0.1, bounds=(0, 3))

    @param.depends('c', 'exp')
    def view(self):
        return pn.pane.LaTeX('${%s}^{%s}={%.3f}$' % (self.c, self.exp, self.c**self.exp),
                             style={'font-size': '2em'})

    def panel(self):
        return pn.Row(self.param, self.view)

stage2 = Stage2(c=stage1.output()[0])

pipeline.add_stage('Stage 2', stage2)
```

And that's it! we have now declared a two-stage pipeline, where the output ``c`` flows from the first stage into the second stage.

To display the `pipeline` we simply let it render itself:


```{pyodide}
pipeline
```








## Related Resources
- The [Param with Panel How-to Guides](../param/index.md) demonstrate how to set up classes that declare parameters and link them to some computation or visualization.
-
