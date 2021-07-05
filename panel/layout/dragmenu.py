from pathlib import Path

import param

from ..reactive import ReactiveHTML
from .base import ListLike

class DragMenu(ListLike, ReactiveHTML):

    clicks = param.Integer(default=0)
    icon = param.Parameter()
    label = param.String(default='')
    orientation = param.ObjectSelector(default="bl", objects=["bl","br","tl","tr"], 
        doc=""" Defines the position of the objects container relative to the control button.""")
    position = param.ObjectSelector(default="out", objects=["out","in"],
        doc=""" Render the element outside or inside the icon object""")
    color = param.Color(default='white')
    background_color = param.Color(default='#808080')
    theme = param.ObjectSelector(default="default", objects=["default", "dark"])  
       
    _template = (Path(__file__).parent / 'dragmenu.html').read_text('utf-8')

    _dom_events = {'drag_icon':['click']}

    render_script = (Path(__file__).parent / 'dragmenu_render.js').read_text('utf-8')
    clicks_script = (Path(__file__).parent / 'dragmenu_clicks.js').read_text('utf-8')

    _scripts = {'render': [render_script],
                'clicks': [clicks_script]
                }

    def __init__(self, *objects, **params):
        super().__init__(objects=list(objects), **params)
  
    def _drag_icon_click(self, event):
        self.clicks += 1
