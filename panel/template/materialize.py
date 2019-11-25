from __future__ import absolute_import, division, unicode_literals

import param

from .base import Template
from ..pane import HTML
from ..layout import Panel, Row


class MaterializeTemplate(Template):

    nav_color = param.Color(default='#2f2f2f')

    sidebar = param.Boolean(default=True)

    modal = param.ClassSelector(default=Row(), class_=Panel)

    title = param.String(default='Panel App')

    logo = param.String()

    def __init__(self, **params):
        path = os.path.join(os.path.dirname(__file__), '..', '_templates',
                            'materialize', 'base.html')
        with open(os.path.abspath(path)) as f:
            template = f.read()
        self._icons = {}
        self._widths = {}
        super(MaterializeTemplate, self).__init__(template, **params)
        self._html = HTML()
        self._render_items['_modal'] = (self.modal, [])
        self._render_items['_hidden'] = (self._html, [])

    def add_card(self, name, panel, width=12):
        self._widths[name] = width
        self.add_panel(name, panel, tags=['card', 'main'])

    def add_collapsible(self, name, panel, active=False, icon='add', width=12):
        tags = ['collapsible', 'main']
        self._widths[name] = width
        if active:
            tags.append('active')
        self.add_panel(name, panel, tags=tags)

    def add_sidebar(self, name, panel):
        panel.sizing_mode = 'stretch_width'
        self.add_panel(name, panel, tags=['sidebar'])

    def toast(self, text):
        self._html.object = """
        <script>
        M.toast({html: "%s"})
        </script>
        """ % text

    @property
    def open_modal(self):
        return """
        M.Modal.getInstance(document.getElementById('modal1')).open()
        """

    def _init_doc(self, doc=None, comm=None, title=None, notebook=False):
        doc = super(MaterializeTemplate, self)._init_doc(doc, comm, title, notebook)
        doc._template_variables['sidebar'] = self.sidebar
        doc._template_variables['inner_title'] = self.title
        previous = None
        rows = (row,) = [{'names': [], 'objects': []}]
        counter = Counter()
        for name, (obj, tags) in self._render_items.items():
            if 'sidebar' in tags or name in ('_modal', '_hidden'):
                continue
            for otype in ('card', 'collapsible'):
                if otype in tags and previous != otype:
                    previous = otype
                    break
            if sum([self._widths[n] for n in row['names']]) >= 12:
                row = {'names': [], 'objects': []}
                rows.append(row)
            if not row['objects'] or row['objects'][-1]['type'] != previous:
                counter[previous] += 1
                row['objects'].append({
                    'type': previous, 'names': [name], 'width': self._widths.get(name),
                    'class': '%s-%d' % (previous, counter[previous])
                })
            else:
                row['objects'][-1]['names'].append(name)
            if previous != 'collapsible' or 'collapsible' not in tags:
                row['names'].append(name)
        doc._template_variables['rows'] = rows
        doc._template_variables['icons'] = self._icons
        doc._template_variables['widths'] = self._widths
        doc._template_variables['logo'] = self.logo
        doc._template_variables['nav_color'] = self.nav_color
        return doc
