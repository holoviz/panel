# panel.models.esm module

class panel.models.esm.AnyWidgetComponent(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases:
[ReactComponent](#panel.models.esm.ReactComponent)

Renders AnyWidget esm definitions by adding a compatibility layer.

class panel.models.esm.DataEvent(model, data=None)
Bases: `ModelEvent`

Methods

|                  |     |
|------------------|-----|
| **event_values** |     |

class panel.models.esm.ESMEvent(model, data=None)
Bases: [DataEvent](#panel.models.esm.DataEvent)

class panel.models.esm.ReactComponent(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `ReactiveESM`

Renders jsx/tsx based ESM bundles using React.

Attributes:
**root_node**

**use_shadow_dom**

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
