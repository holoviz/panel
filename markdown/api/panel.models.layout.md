# panel.models.layout module

class panel.models.layout.Card(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: [Column](#panel.models.layout.Column)

Attributes:
**active_header_background**
Background color of active Card header.

**button_css_classes**
CSS classes to add to the Card collapse button.

**collapsed**
Whether the Card is collapsed.

**collapsible**
Whether the Card should have a button to collapse it.

**header_background**
Background color of the Card header.

**header_color**
Color of the header text and button.

**header_css_classes**
CSS classes to add to the Card header.

**header_tag**
HTML tag to use for the Card header.

**hide_header**
Whether to hide the Card header

**tag**
CSS class to use for the Card as a whole.

active_header_background
Background color of active Card header.

button_css_classes
CSS classes to add to the Card collapse button.

collapsed
Whether the Card is collapsed.

collapsible
Whether the Card should have a button to collapse it.

header_background
Background color of the Card header.

header_color
Color of the header text and button.

header_css_classes
CSS classes to add to the Card header.

header_tag
HTML tag to use for the Card header.

hide_header
Whether to hide the Card header

tag
CSS class to use for the Card as a whole.

class panel.models.layout.Column(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Column`

Attributes:
**auto_scroll_limit**
Max pixel distance from the latest object in the Column to activate
automatic scrolling upon update. Setting to 0 disables auto-scrolling.

**scroll_button_threshold**
Min pixel distance from the latest object in the Column to display the
scroll button. Setting to 0 disables the scroll button.

**scroll_index**
Index of the object to scroll to. Setting this value will scroll the
Column to the object at the given index.

**scroll_position**
Current scroll position of the Column. Setting this value will update
the scroll position of the Column. Setting to 0 will scroll to the top.

**view_latest**
Whether to scroll to the latest object on init. If not enabled the view
will be on the first object.

auto_scroll_limit
Max pixel distance from the latest object in the Column to activate
automatic scrolling upon update. Setting to 0 disables auto-scrolling.

scroll_button_threshold
Min pixel distance from the latest object in the Column to display the
scroll button. Setting to 0 disables the scroll button.

scroll_index
Index of the object to scroll to. Setting this value will scroll the
Column to the object at the given index.

scroll_position
Current scroll position of the Column. Setting this value will update
the scroll position of the Column. Setting to 0 will scroll to the top.

view_latest
Whether to scroll to the latest object on init. If not enabled the view
will be on the first object.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
