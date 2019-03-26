from __future__ import absolute_import

import pytest

from panel.pane import (HTML, Str, PNG, JPG, GIF, SVG, Markdown, LaTeX,
                        Matplotlib, RGGPlot, YT, Plotly, Vega, Pane)
from panel._testing.util import check_layoutable_properties


def test_pane_repr(document, comm):
    pane = Pane('Some text', width=400)
    assert repr(pane) == 'Markdown(str, width=400)'


@pytest.mark.parametrize('pane', [Str, Markdown, HTML, PNG, JPG, SVG,
                                  GIF, LaTeX, Matplotlib, RGGPlot, YT,
                                  Plotly, Vega])
def test_pane_layout_properties(pane, document, comm):
    p = pane()
    model = p.get_root(document, comm)
    check_layoutable_properties(p, model)
