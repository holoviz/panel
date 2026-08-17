# ReactiveExpr
---
```python
import panel as pn

pn.extension('tabulator', design="material")
```

The `panel.ReactiveExpr` pane renders a [Param `rx` object](https://param.holoviz.org/user_guide/Reactive_Expressions.html) which represents a reactive expression, displaying both the widgets that are part of the expression and the final output of the expression. The position of the widgets relative to the output can be set, or widgets can be removed entirely.

Please note that you can use use `pn.rx` instead of `param.rx` when you `import panel as pn`.

See the [`param.rx` documentation](https://param.holoviz.org/user_guide/Reactive_Expressions.html) for details on using `rx`.

#### Parameters:

The basic parameters are:

* **`object`** (param.reactive): A `param.reactive` expression

The more advanced parameters which give you more control are:

* **`center`** (bool): Whether to center the output horizontally.
* **`show_widgets`** (bool): Whether to show the widgets.
* **`widget_layout`** (ListPanel): The layout object to display the widgets in. For example `pn.WidgetBox` (default), `pn.Column` or `pn.Row`.
* **`widget_location`** (str): The location of the widgets relative to the output of the reactive expression. One of  'left', 'right', 'top', 'bottom', 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'left_top' (default), 'right_top',right_bottom'.

#### Properties

* **`widgets`** (ListPanel): Returns the widgets in a `widget_layout`.

For more layout and styling related parameters see the [Sizing how-to guide](../../how_to/layout/size.md).
___

The `param.rx` API is a powerful tool for building declarative and reactive UIs.

Lets take a few examples

```python
def model(n):
    return f"🤖 {n}x2 is {n*2}"

n = pn.widgets.IntSlider(value=2, start=0, end=10)
pn.rx(model)(n=n)
```

Behind the scenes panel has made sure the *reactive expression* above is rendered in a `pn.ReactiveExpr` pane. You can also do this explicitly

```python
n = pn.widgets.IntSlider(value=2, start=0, end=10)
pn.ReactiveExpr(pn.rx(model)(n=n))
```

A reactive expression is never a *dead end*. You can always update and change a *reactive expression*.

```python
n = pn.widgets.IntSlider(value=2, start=0, end=10)

pn.rx(model)(n=n) + "\n\n🧑 Thanks"
```

You can also combine *reactive expressions*

```python
x = pn.widgets.IntSlider(value=2, start=0, end=10, name="x")
y = pn.widgets.IntSlider(value=2, start=0, end=10, name="y")

expr = x.rx()*"⭐" + y.rx()*"⭐"
expr
```

## Layouts

You can change the `widget_location`.

```python
x = pn.widgets.IntSlider(value=2, start=0, end=10, name="x")
y = pn.widgets.IntSlider(value=2, start=0, end=10, name="y")

expr = x.rx()*"⭐" + "\n\n" + y.rx()*"❤️"

pn.ReactiveExpr(expr, widget_location="top")
```

You can change the `widget_layout` to `Row`

```python
pn.ReactiveExpr(expr, widget_layout=pn.Row)
```

You can `center` the output horizontally

```python
pn.ReactiveExpr(expr, center=True)
```

You can hide the widgets by setting `show_widgets=False`

```python
pn.ReactiveExpr(expr, show_widgets=False)
```

You can access the `.widgets` in a `widget_layout` and lay them out as you please

```python
pn.ReactiveExpr(expr).widgets
```

## Reactive expressions as references

Using the `pn.ReactiveExpr` pane implicitly or explicitly is great for exploration in a notebook. But its not very performant because every time the reactive expression rerenders, Panel has to create a new pane to render your output in.

Instead you can and should pass the *reactive expression* as a *reference* to a specific Panel component. The Panel component can resolve the value of the expression dynamically:

```python
x = pn.widgets.IntSlider(value=2, start=0, end=10, name="x")
y = pn.widgets.IntSlider(value=2, start=0, end=10, name="y")

ref = x.rx() + y.rx()
```

```python
pn.pane.Str(ref)
```

```python
pn.indicators.Progress(name='Progress', value=ref, max=20)
```

Try changing the `x` and `y` values using the widgets below!

```python
pn.ReactiveExpr(ref).widgets
```

<b>The reference approach should generally be preferred</b> as it is more declarative and explicit, allowing Panel to efficiently update the existing view(s) rather than completely re-rendering the output.

## Styled DataFrame Example

Let us work through this in a slightly more complex example, and build an expression to dynamically load some data and sample N rows from it:

```python
import pandas as pd

dataset = pn.widgets.Select(name='Pick a dataset', options={
    'penguins': 'https://datasets.holoviz.org/penguins/v1/penguins.csv',
    'stocks': 'https://datasets.holoviz.org/stocks/v1/stocks.csv'
})
nrows = pn.widgets.IntSlider(value=5, start=0, end=20, name='N rows')

# Load the currently selected dataset and sample nrows from it
df_rx = pn.rx(pd.read_csv)(dataset).sample(n=nrows)

df_rx
```

Now that we have an expression that does what we want we can use it as a reference to reactive update the `value` of a `Tabulator` widget:

```python
table = pn.widgets.Tabulator(df_rx, page_size=5, pagination='remote')

table.style.bar(cmap='RdYlGn_r')

pn.Row(pn.Column(dataset, nrows), table)
```

However, particularly for complex expressions with tons of inputs it may still be useful to use the `ReactiveExpr` object to render all the widget inputs:

```python
pn.Row(pn.ReactiveExpr(df_rx).widgets, table)
```

---
