from bokeh.core.properties import String, List, Bool

from bokeh.models import Column

class Card(Column):

    active_header_background = String(help="Background color of active Card header.")

    button_css_classes = List(String, help="CSS classes to add to the Card collapse button.")

    collapsed = Bool(True, help="Whether the Card is collapsed.")

    collapsible = Bool(True, help="Whether the Card should have a button to collapse it.")

    header_background = String(help="Background color of the Card header.")

    header_color = String(help="Color of the header text and butotn.")

    header_css_classes = List(String, help="CSS classes to add to the Card header.")

    header_tag = String('div', help="HTML tag to use for the Card header.")

    tag = String('tag', help="CSS class to use for the Card as a whole.")
