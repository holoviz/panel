"""
These that verify Templates are working correctly.
"""
import json

try:
    import holoviews as hv
except Exception:
    hv = None

import param
import pytest

from bokeh.document import Document
from bokeh.io.doc import patch_curdoc

from panel.layout import GridSpec, Row
from panel.pane import HoloViews, Markdown
from panel.template import (
    BootstrapTemplate, GoldenTemplate, MaterialTemplate, ReactTemplate,
    Template, VanillaTemplate,
)
from panel.template.base import BasicTemplate
from panel.widgets import FloatSlider

from .util import hv_available

TEMPLATES = [BootstrapTemplate, GoldenTemplate, MaterialTemplate, ReactTemplate, VanillaTemplate]
LIST_TEMPLATES = [item for item in TEMPLATES if item is not ReactTemplate]

template = """
{% extends base %}

{% block contents %}
{{ embed(roots.A) }}
{{ embed(roots.B) }}
{% endblock %}
"""


@hv_available
def test_template_links_axes(document, comm):
    tmplt = Template(template)

    p1 = HoloViews(hv.Curve([1, 2, 3]), backend='bokeh')
    p2 = HoloViews(hv.Curve([1, 2, 3]), backend='bokeh')
    p3 = HoloViews(hv.Curve([1, 2, 3]), backend='bokeh')
    row = Row(p2, p3)

    tmplt.add_panel('A', p1)
    tmplt.add_panel('B', row)

    tmplt._init_doc(document, comm, notebook=True)

    (_, (m1, _)) = list(p1._models.items())[0]
    (_, (m2, _)) = list(p2._models.items())[0]
    (_, (m3, _)) = list(p3._models.items())[0]
    assert m1.x_range is m2.x_range
    assert m1.y_range is m2.y_range
    assert m2.x_range is m3.x_range
    assert m2.y_range is m3.y_range


def test_template_session_destroy(document, comm):
    tmplt = Template(template)

    widget = FloatSlider()
    row = Row('A', 'B')

    tmplt.add_panel('A', widget)
    tmplt.add_panel('B', row)

    tmplt._init_doc(document, comm, notebook=True)
    session_context = param.Parameterized()
    session_context._document = document
    session_context.id = 'Some ID'

    assert len(widget._models) == 2
    assert len(row._models) == 2
    assert len(row[0]._models) == 2
    assert len(row[1]._models) == 2

    for cb in document.session_destroyed_callbacks:
        cb(session_context)

    assert len(widget._models) == 0
    assert len(row._models) == 0
    assert len(row[0]._models) == 0
    assert len(row[1]._models) == 0


list_templates = [
    t for t in param.concrete_descendents(BasicTemplate).values()
    if not issubclass(t, ReactTemplate)
]

@pytest.mark.parametrize('template', list_templates)
def test_basic_template(template, document, comm):
    tmplt = template(title='BasicTemplate', header_background='blue', header_color='red')

    tmplt._update_vars()
    tvars = tmplt._render_variables

    assert tvars['app_title'] == 'BasicTemplate'
    assert tvars['header_background'] == 'blue'
    assert tvars['header_color'] == 'red'
    assert tvars['nav'] == False
    assert tvars['busy'] == True
    assert tvars['header'] == False

    titems = tmplt._render_items

    assert titems['busy_indicator'] == (tmplt.busy_indicator, [])

    markdown = Markdown('# Some title')
    tmplt.main.append(markdown)

    assert titems[f'main-{id(markdown)}'] == (markdown, ['main'])

    slider = FloatSlider()
    tmplt.sidebar.append(slider)

    assert titems[f'nav-{id(slider)}'] == (slider, ['nav'])
    assert tvars['nav'] == True

    tmplt.sidebar[:] = []
    assert tvars['nav'] == False
    assert f'nav-{id(slider)}' not in titems

    subtitle = Markdown('## Some subtitle')
    tmplt.header.append(subtitle)

    assert titems[f'header-{id(subtitle)}'] == (subtitle, ['header'])
    assert tvars['header'] == True

    tmplt.header[:] = []
    assert f'header-{id(subtitle)}' not in titems
    assert tvars['header'] == False


def test_template_server_title():
    tmpl = VanillaTemplate(title='Main title')

    doc = Document()

    with patch_curdoc(doc):
        doc = tmpl.server_doc(title='Ignored title')

    assert doc.title == 'Main title'


def test_react_template(document, comm):
    tmplt = ReactTemplate(title='BasicTemplate', header_background='blue', header_color='red')

    tmplt._update_vars()
    tvars = tmplt._render_variables

    assert tvars['app_title'] == 'BasicTemplate'
    assert tvars['header_background'] == 'blue'
    assert tvars['header_color'] == 'red'
    assert tvars['nav'] == False
    assert tvars['busy'] == True
    assert tvars['header'] == False
    assert tvars['rowHeight'] == tmplt.row_height
    assert tvars['breakpoints'] == tmplt.breakpoints
    assert tvars['cols'] == tmplt.cols

    markdown = Markdown('# Some title')
    tmplt.main[:4, :6] = markdown

    markdown2 = Markdown('# Some title')
    tmplt.main[:4, 6:] = markdown2

    layouts = {'lg': [{'h': 4, 'i': '1', 'w': 6, 'x': 0, 'y': 0},
                      {'h': 4, 'i': '2', 'w': 6, 'x': 6, 'y': 0}],
               'md': [{'h': 4, 'i': '1', 'w': 6, 'x': 0, 'y': 0},
                      {'h': 4, 'i': '2', 'w': 6, 'x': 6, 'y': 0}]
               }

    for size in layouts:
        for layout in layouts[size]:
            layout.update({'minW': 0, 'minH': 0})

    assert json.loads(tvars['layouts']) == layouts

@pytest.mark.parametrize(["template_class"], [(t,) for t in LIST_TEMPLATES])
def test_list_template_insert_order(template_class):
    template = template_class()

    template.main.append(1)

    template.main.insert(0, 0)

    template.main.extend([2, 3])

    objs = list(template._render_items.values())[4:]
    ((obj1, tag1), (obj2, tag2), (obj3, tag3), (obj4, tag4)) = objs

    assert tag1 == tag2 == tag3 == tag4 == ['main']
    assert obj1.object == 0
    assert obj2.object == 1
    assert obj3.object == 2
    assert obj4.object == 3

@pytest.mark.parametrize(["template_class"], [(item,) for item in TEMPLATES])
def test_constructor(template_class):
    item = Markdown("Hello World")
    items = [item]
    template_class(header=item, sidebar=item, main=item)
    template_class(header=items, sidebar=items, main=items)

def test_constructor_grid_spec():
    item = Markdown("Hello World")
    grid = GridSpec(ncols=12)
    grid[0:2, 3:4]=item
    ReactTemplate(main=grid)

def test_grid_template_override():
    item = Markdown("First")
    override = Markdown("Second")
    template = ReactTemplate()
    template.main[0, 0] = item
    template.main[0, 0] = override

    objs = list(template._render_items.values())[4:]
    assert len(objs) == 1
    ((obj, tags),) = objs

    assert obj.object == "Second"
    assert tags == ['main']
