# panel.models.tabulator module

Implementation of the Tabulator model.

See [http://tabulator.info/](http://tabulator.info/)

class panel.models.tabulator.CellClickEvent(model, column, row, value=None)
Bases: `ModelEvent`

class panel.models.tabulator.DataTabulator(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `HTMLBox`

A Bokeh Model that enables easy use of Tabulator tables See
[http://tabulator.info/](http://tabulator.info/)

Attributes:
**aggregators**

**buttons**

**cell_styles**

**children**

**columns**
The list of child column widgets.

**configuration**

**container_popup**

**download**

**editable**

**embed_content**

**expanded**

**filename**

**filters**

**follow**

**frozen_rows**

**groupby**

**hidden_columns**

**indexes**

**layout**

**max_page**

**movable_columns**

**page**

**page_size**

**pagination**

**select_mode**

**selectable_rows**

**sorters**

**source**

**theme_classes**

columns
The list of child column widgets.

class panel.models.tabulator.SelectionEvent(model, indices, selected, flush)
Bases: `ModelEvent`

class panel.models.tabulator.TableEditEvent(model, column, row, pre=False, value=None, old=None)
Bases: `ModelEvent`

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
