import param

from bokeh.models import Div as BkDiv

from ..models import Card as BkCard
from ..viewable import Viewable
from .base import Column, Row


class Card(Column):
    """
    A Card layout allows arranging multiple panel objects in a
    collapsible, vertical container with a header bar.
    """

    button_color = param.String(doc="""
        A valid CSS color to apply to the button.""")

    button_css_classes = param.List(['card-button'], doc="""
        CSS classes to apply to the button element.""")

    collapsed = param.Boolean(default=False, doc="""
        Whether the contents of the Card are collapsed.""")

    css_classes = param.List(['card'], doc="""
        CSS classes to apply to the overall Card.""")

    header = param.Parameter(doc="""
        A Panel component to display in the header bar of the Card.
        Will override the given title if defined.""")

    header_background = param.String(doc="""
        A valid CSS color to the header background.""")

    header_css_classes = param.List(['card-header'], doc="""
        CSS claasses to apply to the heaader element.""")

    margin = param.Parameter(default=5)

    title = param.String(doc="""
        A title to be displayed in the Card header, will be overridden
        by the header if defined.""")

    _bokeh_model = BkCard
    
    _rename = dict(Column._rename, title=None, header=None)

    def __init__(self, *objects, **params):
        self._header_layout = Row(css_classes=['card-header-row'])
        super(Card, self).__init__(*objects, **params)
        self.param.watch(self._update_header, ['title', 'header'])
        self._update_header()

    def _update_header(self, *events):
        from ..pane import HTML, panel
        if self.header is None:
            item = HTML('%s' % (self.title or "&#8203;"),
                        margin=(0, 10), css_classes=['card-title'])
        else:
            item = panel(self.header)
        self._header_layout[:] = [item]

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        ref = root.ref['id']
        if ref in self._header_layout._models:
            header = self._header_layout._models[ref][0]
        else:
            header = self._header_layout._get_model(doc, root, model, comm)
        objects = super(Card, self)._get_objects(model, old_objects, doc, root)
        return [header]+objects
