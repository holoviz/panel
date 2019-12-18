"""
Defines Icons which can be used inside a button view.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from bokeh.core.properties import String, Seq, List
from bokeh.core.has_props import abstract
from bokeh.models.widgets.icons import AbstractIcon

@abstract
class IconBase(AbstractIcon):
    
    css_classes = List(String, help="""
    A list of CSS class names to add to this DOM element. Note: the class names are
    simply added as-is, no other guarantees are provided.

    It is also permissible to assign from tuples, however these are adapted -- the
    property will always contain a list.
    """).accepts(Seq(String), lambda x: list(x))


class FontAwesomeIcon(IconBase):

    icon = String("", help="""
    The font-awesome icon to render as the icon.
    """)
