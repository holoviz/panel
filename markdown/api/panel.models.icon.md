# panel.models.icon module

class panel.models.icon.ButtonIcon(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `_ClickableIcon`,
`AbstractButton`

A ButtonIcon is a clickable icon that toggles between an active and
inactive state and keeps track of the number of times it has been
clicked.

Attributes:
**clicks**
The number of times the button has been clicked.

**toggle_duration**
The number of milliseconds the active_icon should be shown for and how
long the button should be disabled for.

clicks
The number of times the button has been clicked.

toggle_duration
The number of milliseconds the active_icon should be shown for and how
long the button should be disabled for.

class panel.models.icon.ToggleIcon(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `_ClickableIcon`

A ToggleIcon is a clickable icon that toggles between an active and
inactive state.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
