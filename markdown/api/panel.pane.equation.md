# panel.pane.equation module

Renders objects representing equations including LaTeX strings and SymPy
objects.

class panel.pane.equation.LaTeX(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)

The LaTeX pane allows rendering LaTeX equations. It uses either KaTeX or
MathJax depending on the defined renderer.

By default it will use the renderer loaded in the extension (e.g.
pn.extension(‘katex’)), defaulting to KaTeX if both are loaded.

Reference:
[https://panel.holoviz.org/reference/panes/LaTeX.html](https://panel.holoviz.org/reference/panes/LaTeX.html)

Example:

\>\>\>
pn.extension('katex')
\>\>\>
LaTeX(
...  'The LaTeX pane supports
two delimiters: \$LaTeX\$ and \\LaTeX\\',
...
styles={'font-size':
'18pt'},
width=800
... )

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.equation.LaTeX.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
>

`renderer`` ``=`` ``Selector(allow_None=True,`` ``label='Renderer',`` ``names={},`` ``objects=['katex',`` ``'mathjax'])`
The JS renderer used to render the LaTeX expression. Defaults to katex.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
