"""	
GoldenTemplate based on the golden-layout library.	
"""	
import pathlib	

import param	

from ...config import config	
from ...layout import Row, Column, HSpacer, Spacer, ListLike, Card	
from ...pane import HTML	
from ..base import BasicTemplate	


class GoldenTemplate(BasicTemplate):	
    """	
    GoldenTemplate is built on top of golden-layout library.	
    """	

    _css = pathlib.Path(__file__).parent / 'golden.css'	

    _template = pathlib.Path(__file__).parent / 'golden.html'	

    _modifiers = {	
        Card: {	
            'button_css_classes': ['golden-card-button']	
        },	
    }