# Create a `Pipeline`

This guide addresses how to connect multiple panels into a `Pipeline` to express complex multi-page workflows where the output of one stage feeds into the next stage.

```{admonition} Prerequisites
1. The [Param with Panel How-to Guides](../param/index.md) describe how to set up classes that declare parameters and link them to some computation or visualization.
```

---

To start, lets instantiate an empty `Pipeline`. We will use the 'katex' extension to render mathematical notation in this example.

```{pyodide}
import param
import panel as pn
pn.extension('katex')

pipeline = pn.pipeline.Pipeline()
```

Now let's populate the pipeline with our first stage which takes two inputs (`a` and `b`) and produces two outputs (`c`, computed by multiplying the inputs, and `d`, computed by raising `a` to the power `b`).

To create this stage, let's:

1. Declare a Parameterized class with some input parameters (e.g. `a = param.Integer`)
2. Decorate a method with `@param.output` to declare outputs (we'll discuss this more later)
3. Declare a `panel` method that returns a view of this stage's object

```{pyodide}
class Stage1(param.Parameterized):

    a = param.Integer(default=2, bounds=(0, 10))
    b = param.Integer(default=3, bounds=(0, 10))

    @param.output(('c', param.Integer), ('d', param.Integer))
    def output(self):
        return self.a * self.b, self.a ** self.b

    @param.depends('a', 'b')
    def view(self):
        c, d = self.output()
        c_out = pn.pane.LaTeX('${a} * {b} = {c}$'.format(
            a=self.a, b=self.b, c=c), styles={'font-size': '2em'})
        d_out = pn.pane.LaTeX('${a}^{{{b}}} = {d}$'.format(
            a=self.a, b=self.b, d=d), styles={'font-size': '2em'})
        return pn.Column(
		    c_out, d_out,  margin=(40, 10), styles={'background': '#f0f0f0'}
		)

    def panel(self):
        return pn.Row(self.param, self.view,)
```

We can now render this stage on its own:

```{pyodide}
stage1 = Stage1()
stage1.panel()
```

Before we create a second stage let's briefly discuss the some details about the system of outputs that links the stages. To declare the output for our first stage, we decorated one of its methods with `@param.output(('c', param.Integer), ('d', param.Integer))`. However, there are multiple ways to declare outputs with this decorator:

* `param.output()`: Declaring an output without arguments will declare that the method returns an output that will inherit the **name of the method** and does not make any specific type declarations.
* `param.output(param.Integer)`: Declaring an output with a specific `Parameter` or Python type also declares an output with the name of the method but declares that the output will be of a specific type.
* `param.output(c=param.Integer)`: Declaring an output using a keyword argument allows overriding the method name as the name of the output and declares the type.

It is also possible to declare multiple outputs, either as keywords or tuples:

* `param.output(c=param.Integer, d=param.String)` or
* `param.output(('c', param.Integer), ('d', param.String))`

Importantly, in addition to passing along the outputs designated with `param.output()`, the Pipeline will also pass along the values of any input parameters whose names match input parameters on the next stage (unless `inherit_params` is set to `False`).

Ok, enough explanation, let's take a look at the outputs of our first stage:

```{pyodide}
stage1.param.outputs()
```

Our `Pipeline` will use this information to determine what outputs are available to be fed into the next stage of the workflow.

Now let's set up a second stage that will also declare a `c` input Parameter to consume the `c` output of the first stage. Note, the second stage does not have to consume all parameters, and here we will ignore the first stage's output `d`. Otherwise, the second stage below is very similar to the first one; it declares both a ``view`` method that depends on the parameters of the class, and a ``panel`` method that returns a view of the object. As this is our last stage, we don't need to define any further outputs.

```{pyodide}
class Stage2(param.Parameterized):

    c = param.Integer(default=6, bounds=(0, None))
    exp = param.Number(default=0.1, bounds=(0, 3))

    @param.depends('c', 'exp')
    def view(self):
        out = pn.pane.LaTeX('${%s}^{%s}={%.3f}$' % (self.c, self.exp, self.c**self.exp),
                      styles={'font-size': '2em'})
        return pn.Column(out, margin=(40, 10), styles={'background': '#f0f0f0'})

    def panel(self):
        return pn.Row(self.param, self.view)
```

Now let's add our stages to our `Pipeline` using the `add_stage` method

```{pyodide}
pipeline.add_stage('Stage 1', Stage1)
pipeline.add_stage('Stage 2', Stage2)
```

Finally, to display the `pipeline` UI we simply let it render itself:

```{pyodide}
pipeline
```

As you can see the ``Pipeline`` renders a diagram displaying the available stages in the workflow along with previous and next buttons to move between each stage. Note also when progressing to Stage 2, the `c` parameter widget is not rendered because its value has been provided by the previous stage.

Here is the complete code for this section in case you want to easily copy it:

```{pyodide}
import param
import panel as pn
pn.extension('katex')

pipeline = pn.pipeline.Pipeline()

class Stage1(param.Parameterized):

    a = param.Integer(default=2, bounds=(0, 10))
    b = param.Integer(default=3, bounds=(0, 10))

    @param.output(('c', param.Integer), ('d', param.Integer))
    def output(self):
        return self.a * self.b, self.a ** self.b

    @param.depends('a', 'b')
    def view(self):
        c, d = self.output()
        c_out = pn.pane.LaTeX('${a} * {b} = {c}$'.format(
            a=self.a, b=self.b, c=c), styles={'font-size': '2em'})
        d_out = pn.pane.LaTeX('${a}^{{{b}}} = {d}$'.format(
            a=self.a, b=self.b, d=d), styles={'font-size': '2em'})
        return pn.Column(c_out, d_out,  margin=(40, 10), styles={'background': '#f0f0f0'})

    def panel(self):
        return pn.Row(self.param, self.view,)

class Stage2(param.Parameterized):

    c = param.Integer(default=6, bounds=(0, None))
    exp = param.Number(default=0.1, bounds=(0, 3))

    @param.depends('c', 'exp')
    def view(self):
        out = pn.pane.LaTeX('${%s}^{%s}={%.3f}$' % (self.c, self.exp, self.c**self.exp),
                      styles={'font-size': '2em'})
        return pn.Column(out, margin=(40, 10), styles={'background': '#f0f0f0'})

    def panel(self):
        return pn.Row(self.param, self.view)

pipeline.add_stage('Stage 1', Stage1)
pipeline.add_stage('Stage 2', Stage2)

pipeline
```

## Related Resources

- The [How to > Param with Panel](../param/index) guides demonstrate how to set up classes that declare parameters and link them to some computation or visualization.
