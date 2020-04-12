import param

from bokeh.models import Div as BkDiv

from ..models import Card as BkCard
from .base import Column


class Card(Column):
    
    collapsed = param.Boolean(default=False)
    
    title = param.String()
    
    margin = param.Parameter(default=5)
    
    _bokeh_model = BkCard
    
    _rename = dict(Column._rename, title=None)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        from ..pane import panel
        header = BkDiv(text='<h3>%s</h3>' % self.title, margin=(0, 10))
        objects = super(Card, self)._get_objects(model, old_objects, doc, root)
        return [header]+objects

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = super(Card, self)._get_model(doc, root, parent, comm)
        model.update(
            button_css_classes=['card-button'],
            css_classes=['card'],
            header_css_classes=['card-header']
        )
        return model
