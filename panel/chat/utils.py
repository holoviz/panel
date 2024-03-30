from __future__ import annotations

import re

from io import BytesIO
from typing import Any, Dict, Union

from ..io.resources import CDN_DIST
from ..pane.image import ImageBase

Avatar = Union[str, BytesIO, bytes, ImageBase]
AvatarDict = Dict[str, Avatar]


def to_alpha_numeric(user: str) -> str:
    """
    Convert the user name to an alpha numeric string,
    removing all non-alphanumeric characters.
    """
    return re.sub(r"\W+", "", user).lower()


def avatar_lookup(
    user: str,
    avatar: Any,
    avatars: Dict[str, Any],
    default_avatars: Dict[str, Any],
) -> Avatar:
    """
    Lookup the avatar for the user.
    """
    alpha_numeric_key = to_alpha_numeric(user)
    # always use the default first
    updated_avatars = default_avatars.copy()
    # update with the user input
    updated_avatars.update(avatars)
    # correct the keys to be alpha numeric
    updated_avatars = {
        to_alpha_numeric(key): value for key, value in updated_avatars.items()
    }

    # now lookup the avatar
    avatar = updated_avatars.get(alpha_numeric_key, avatar)
    if isinstance(avatar, str):
        avatar = avatar.format(dist_path=CDN_DIST)
    return avatar


def stream_to(obj, token, replace=False):
    """
    Updates the message with the new token traversing the object to
    allow updating nested objects. When traversing a nested Panel
    the last object that supports rendering strings is updated, e.g.
    in a layout of `Column(Markdown(...), Image(...))` the Markdown
    pane is updated.

    Arguments
    ---------
    token: str
        The token to stream to the text pane.
    replace: bool (default=False)
        Whether to replace the existing text.
    """
    i = -1
    parent_panel = None
    object_panel = None
    attr = "object"
    if obj is None:
        obj = ""

    while not isinstance(obj, str) or isinstance(object_panel, ImageBase):
        object_panel = obj
        if hasattr(obj, "objects"):
            parent_panel = obj
            attr = "objects"
            obj = obj.objects[i]
            i = -1
        elif hasattr(obj, "object"):
            attr = "object"
            obj = obj.object
        elif hasattr(obj, "value"):
            attr = "value"
            obj = obj.value
        elif parent_panel is not None:
            obj = parent_panel
            parent_panel = None
            i -= 1
    contents = token if replace else obj + token
    setattr(object_panel, attr, contents)
    return object_panel
