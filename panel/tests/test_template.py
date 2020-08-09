"""
These that verify Templates are working correctly.
"""
from __future__ import absolute_import, division, unicode_literals

from distutils.version import LooseVersion

try:
    import holoviews as hv
except Exception:
    hv = None

import param
import pytest

latest_param = pytest.mark.skipif(LooseVersion(param.__version__) < '1.10.0a4',
                                  reason="requires param>=1.10.0a4")

from panel.layout import Row
from panel.pane import HoloViews, Markdown
from panel.template import Template
from panel.template.base import BasicTemplate
from panel.widgets import FloatSlider

from .util import hv_available

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

    p1 = HoloViews(hv.Curve([1, 2, 3]))
    p2 = HoloViews(hv.Curve([1, 2, 3]))
    p3 = HoloViews(hv.Curve([1, 2, 3]))
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


@latest_param
@pytest.mark.parametrize('template', list(param.concrete_descendents(BasicTemplate).values()))
def test_basic_template(template, document, comm):
    tmplt = template(title='BasicTemplate', header_background='blue', header_color='red')

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

    assert titems[str(id(markdown))] == (markdown, ['main'])

    slider = FloatSlider()
    tmplt.sidebar.append(slider)

    assert titems[str(id(slider))] == (slider, ['nav'])
    assert tvars['nav'] == True
    
    tmplt.sidebar[:] = []
    assert tvars['nav'] == False
    assert str(id(slider)) not in titems

    subtitle = Markdown('## Some subtitle')
    tmplt.header.append(subtitle)

    assert titems[str(id(subtitle))] == (subtitle, ['header'])
    assert tvars['header'] == True

    tmplt.header[:] = []
    assert str(id(subtitle)) not in titems
    assert tvars['header'] == False

    
