from __future__ import absolute_import

import pytest

from bokeh.plotting import Figure

from panel.layout import Column, Row

try:
    import holoviews as hv
except:
    hv = None
hv_available = pytest.mark.skipif(hv is None, reason="requires holoviews")



@hv_available
def test_holoviews_axes_range_link(document, comm):
    from panel.links import RangeAxesLink
    
    c1 = hv.Curve([])
    c2 = hv.Curve([])
    c3 = hv.Curve([])
    c4 = hv.Curve([])
    c5 = hv.Curve([])
    
    RangeAxesLink(c1,c2) #across pane
    hv_layout = c3+c4 #inner hv layout
    RangeAxesLink(c4,c5) #inner outter
    
    layout = Column(Row(c1,c2), Row(hv_layout, c5))
    column = layout._get_root(document, comm=comm)

    assert len(column.children) == 3
    r1, r2, _ = column.children

    assert (len(list(r1.select({'type': Figure}))) == 2)
    p1, p2 = r1.select({'type': Figure})
    
    assert p1.x_range == p2.x_range
    assert p1.y_range == p2.y_range
    
    assert (len(list(r2.select({'type': Figure}))) == 3)
    p3, p4, p5 = r2.select({'type': Figure})
    
    assert p3.x_range == p4.x_range == p5.x_range
    assert p3.y_range == p4.y_range == p5.y_range
