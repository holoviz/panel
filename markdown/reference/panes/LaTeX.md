# LaTeX
---
```python
import panel as pn

pn.extension('katex', 'mathjax')
```

The `LaTeX` pane enables rendering LaTeX equations as HTML using either the [KaTeX](https://katex.org/) or [MathJax](https://www.mathjax.org) renderer.

You must load the desired renderer manually (e.g., `pn.extension('katex')` or `pn.extension('mathjax')`). If both are loaded, KaTeX is used by default.

Please note that both [KaTeX](https://katex.org/) and [MathJax](https://www.mathjax.org) support only a subset of the features available in a full LaTeX renderer. For detailed information on supported features, refer to their respective documentation.

#### Parameters:

For details on additional options for customizing the component, refer to the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **`object`** (str or object): A string containing LaTeX code, an object with a `_repr_latex_` method, or a [SymPy](https://www.sympy.org/en/index.html) expression.
* **`renderer`** (object): The current renderer; must be one of the available options.
* **`styles`** (dict): A dictionary specifying CSS styles.

___

A `LaTeX` pane will render any object with a `_repr_latex_` method, [SymPy](https://www.sympy.org/en/index.html) expressions, or any string containing LaTeX. Any LaTeX content should be wrapped in `$...$` or `\(...\)` delimiters, for example:

```python
latex = pn.pane.LaTeX(
    r'The LaTeX pane supports two delimiters: $LaTeX$ and \(LaTeX\)', styles={'font-size': '18pt'}
)

latex
```

Its important to prefix your LaTeX strings with an `r` to make the string a *raw* string and not escape the \\ character.

```python
pn.Column(
    pn.pane.LaTeX("$\frac{1}{n}$"), # Will not work
    pn.pane.LaTeX(r"$\frac{1}{n}$")
)
```

The ``LaTeX`` pane can be updated like other panes:

```python
latex.object = r'$\sum_{j}{\sum_{i}{a*w_{j, i}}}$'
```

Lets change it back:

```python
latex.object = r'The LaTeX pane supports two delimiters: $LaTeX$ and \(LaTeX\)'
```

If both renderers have been loaded we can override the default renderer:

```python
pn.pane.LaTeX(r'The LaTeX pane supports two delimiters: $LaTeX$ and \(LaTeX\)', renderer='mathjax', styles={'font-size': '18pt'})
```

And can also be composed like any other pane:

```python
maxwell = pn.pane.LaTeX(r"""
$\begin{aligned}
  \nabla \times \vec{\mathbf{B}} -\, \frac1c\, \frac{\partial\vec{\mathbf{E}}}{\partial t} & = \frac{4\pi}{c}\vec{\mathbf{j}} \\
  \nabla \cdot \vec{\mathbf{E}} & = 4 \pi \rho \\
  \nabla \times \vec{\mathbf{E}}\, +\, \frac1c\, \frac{\partial\vec{\mathbf{B}}}{\partial t} & = \vec{\mathbf{0}} \\
  \nabla \cdot \vec{\mathbf{B}} & = 0
\end{aligned}
$""", styles={'font-size': '24pt'})

cauchy_schwarz = pn.pane.LaTeX(object=r"""
$\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)$
""", styles={'font-size': '24pt'})

cross_product = pn.pane.LaTeX(object=r"""
$\mathbf{V}_1 \times \mathbf{V}_2 =  \begin{vmatrix}
\mathbf{i} & \mathbf{j} & \mathbf{k} \\
\frac{\partial X}{\partial u} &  \frac{\partial Y}{\partial u} & 0 \\
\frac{\partial X}{\partial v} &  \frac{\partial Y}{\partial v} & 0
\end{vmatrix}
$""", styles={'font-size': '24pt'})

spacer = pn.Spacer(width=50)

pn.Column(
    pn.pane.Markdown('# The LaTeX Pane'),
    pn.Row(maxwell, spacer, cross_product, spacer, cauchy_schwarz)
)
```

## Sympy

Panels LaTeX pane can render Sympy expressions as shown below:

```python
import sympy as sp
import panel as pn

pn.extension("mathjax")

# Define a symbol and a symbolic expression using SymPy
x = sp.symbols('x')
expression = sp.integrate(sp.sin(x)**2, x)

# Create a LaTeX pane to display the expression
latex_pane = pn.pane.LaTeX(expression, styles={'font-size': '20px'})

# Serve the panel
pn.Column(
    "# A sympy expression rendered in Panel: ", latex_pane
)
```

![Sympy in LaTeX pane](../../assets/panel-sympy.png)

### Controls

The `LaTeX` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(latex.controls(jslink=True), latex)
```

---
