# panel.interact module

Interact with functions using widgets.

The interact Pane implemented in this module mirrors ipywidgets.interact
in its API and implementation. Large parts of the code were copied
directly from ipywidgets:

Copyright (c) Jupyter Development Team and PyViz Development Team.
Distributed under the terms of the Modified BSD License.

class panel.interact.interactive(object, params={}, **kwargs)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

Attributes:
**kwargs**

Methods

|  |  |
|----|----|
| [applies](#panel.interact.interactive.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| `factory`() |  |
| [find_abbreviations](#panel.interact.interactive.find_abbreviations)(kwargs) | Find the abbreviations for the given function and kwargs. |
| [widgets_from_abbreviations](#panel.interact.interactive.widgets_from_abbreviations)(seq) | Given a sequence of (name, abbrev, default) tuples, return a sequence of Widgets. |

|               |     |
|---------------|-----|
| **signature** |     |

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
> margin, object
>
>

`default_layout`` ``=`` ``ClassSelector(class_=<class`` ``'panel.layout.base.ListLike'>,`` ``default=<class`` ``'panel.layout.base.Column'>,`` ``label='Default`` ``layout')`
Defines the layout the model(s) returned by the pane will be placed in.

`manual_update`` ``=`` ``Boolean(default=False,`` ``label='Manual`` ``update')`
Whether to update manually by clicking on button.

`manual_name`` ``=`` ``String(default='Run`` ``Interact',`` ``label='Manual`` ``name')`
The name of the button to run the interact function manually. Only used
if manual_update is True.

`_pane`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.viewable.Viewable'>,`` ``label='`` ``pane')`

classmethod applies(object)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

default_layout
alias of [Column](panel.layout.base.md#panel.layout.base.Column)

find_abbreviations(kwargs)
Find the abbreviations for the given function and kwargs. Return (name,
abbrev, default) tuples.

widgets_from_abbreviations(seq)
Given a sequence of (name, abbrev, default) tuples, return a sequence of
Widgets.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
