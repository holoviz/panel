import param

from ..models import Card as BkCard
from .base import Column, Row, ListPanel


class Card(Column):
    """
    A Card layout allows arranging multiple panel objects in a
    collapsible, vertical container with a header bar.
    """

    active_header_background = param.String(doc="""
        A valid CSS color for the header background when not collapsed.""")

    button_css_classes = param.List(['card-button'], doc="""
        CSS classes to apply to the button element.""")

    collapsible = param.Boolean(default=True, doc="""
        Whether the Card should be expandable and collapsible.""")

    collapsed = param.Boolean(default=False, doc="""
        Whether the contents of the Card are collapsed.""")

    css_classes = param.List(['card'], doc="""
        CSS classes to apply to the overall Card.""")

    header = param.Parameter(doc="""
        A Panel component to display in the header bar of the Card.
        Will override the given title if defined.""")

    header_background = param.String(doc="""
        A valid CSS color for the header background.""")

    header_color = param.String(doc="""
        A valid CSS color to apply to the header text.""")

    header_css_classes = param.List(['card-header'], doc="""
        CSS classes to apply to the header element.""")

    title_css_classes = param.List(['card-title'], doc="""
        CSS classes to apply to the header title.""")

    margin = param.Parameter(default=5)

    title = param.String(doc="""
        A title to be displayed in the Card header, will be overridden
        by the header if defined.""")

    _bokeh_model = BkCard
    
    _rename = dict(Column._rename, title=None, header=None, title_css_classes=None)

    def __init__(self, *objects, **params):
        self._header_layout = Row(css_classes=['card-header-row'],
                                  sizing_mode='stretch_width')
        super().__init__(*objects, **params)
        self.param.watch(self._update_header, ['title', 'header', 'title_css_classes'])
        self._update_header()

    def _cleanup(self, root):
        super()._cleanup(root)
        self._header_layout._cleanup(root)

    def _process_param_change(self, params):
        scroll = params.pop('scroll', None)
        css_classes = self.css_classes or []
        if scroll:
            params['css_classes'] = css_classes + ['scrollable']
        elif scroll == False:
            params['css_classes'] = css_classes
        return super(ListPanel, self)._process_param_change(params)

    def _update_header(self, *events):
        from ..pane import HTML, panel
        if self.header is None:
            item = HTML('%s' % (self.title or "&#8203;"),
                        css_classes=self.title_css_classes,
                        sizing_mode='stretch_width',
                        margin=(2, 5))
        else:
            item = panel(self.header)
        self._header_layout[:] = [item]

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        ref = root.ref['id']
        if ref in self._header_layout._models:
            header = self._header_layout._models[ref][0]
        else:
            header = self._header_layout._get_model(doc, root, model, comm)
        objects = super()._get_objects(model, old_objects, doc, root, comm)
        return [header]+objects
