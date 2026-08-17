# panel.models.markup module

Custom bokeh Markup models.

class panel.models.markup.HTML(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Markup`

A bokeh model to render HTML markup including embedded script tags.

Attributes:
**events**

**run_scripts**
Whether to run scripts defined within the HTML

run_scripts
Whether to run scripts defined within the HTML

class panel.models.markup.HTMLStreamEvent(model, patch=None, start=None)
Bases: `ModelEvent`

Methods

|                  |     |
|------------------|-----|
| **event_values** |     |

class panel.models.markup.JSON(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Markup`

A bokeh model that renders JSON as tree.

Attributes:
**depth**
Depth to which the JSON tree is expanded.

**hover_preview**
Whether to show a hover preview for collapsed nodes.

**theme**
Whether to expand all JSON nodes.

depth
Depth to which the JSON tree is expanded.

hover_preview
Whether to show a hover preview for collapsed nodes.

theme
Whether to expand all JSON nodes.

class panel.models.markup.PDF(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Markup`

Attributes:
**embed**
Whether to embed the file

**start_page**
Start page of the pdf, by default the first page.

embed
Whether to embed the file

start_page
Start page of the pdf, by default the first page.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
