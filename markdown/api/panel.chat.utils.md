# panel.chat.utils module

panel.chat.utils.avatar_lookup(user: str, avatar: Any, avatars: dict\[str, Any\], default_avatars: dict\[str, Any\]) → str \| BytesIO \| bytes \| ImageBase
Lookup the avatar for the user.

panel.chat.utils.get_obj_label(obj)
Get the label for the object; defaults to specified object name; if
unspecified, defaults to the type name.

panel.chat.utils.serialize_recursively(obj: Any, prefix_with_viewable_label: bool = True, prefix_with_container_label: bool = True) → str
Recursively serialize the object to a string.

panel.chat.utils.stream_to(obj, token: str, replace: bool = False, object_panel: Viewable \| None = None)
Updates the message with the new token traversing the object to allow
updating nested objects. When traversing a nested Panel the last object
that supports rendering strings is updated, e.g. in a layout of
Column(Markdown(…), Image(…)) the Markdown pane is updated.

Parameters:
**token: str**
The token to stream to the text pane.

**replace: bool (default=False)**
Whether to replace the existing text.

panel.chat.utils.to_alpha_numeric(user: str) → str
Convert the user name to an alpha numeric string, removing all
non-alphanumeric characters.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
