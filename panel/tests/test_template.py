"""
These that verify Templates are working correctly.
"""
from __future__ import absolute_import, division, unicode_literals

try:
    import holoviews as hv
except:
    hv = None

from panel.layout import Row
from panel.pane import HoloViews
from panel.template import Template

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
    assert m1.x_range is not m2.x_range
    assert m1.y_range is not m2.y_range
    assert m2.x_range is m3.x_range
    assert m2.y_range is m3.y_range
