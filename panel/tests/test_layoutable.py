from __future__ import absolute_import

import pytest

from panel.layout import Column, Row, Tabs, Spacer
from panel.pane import (HTML, Str, PNG, JPG, GIF, SVG, Markdown, LaTeX,
                        Matplotlib, RGGPlot, YT, Plotly, Vega)

from .test_widgets import all_widgets


def check_layoutable_properties(layoutable, model):
    layoutable.background = '#ffffff'
    assert model.background == '#ffffff'

    layoutable.css_classes = ['custom_class']
    assert model.css_classes == ['custom_class']

    layoutable.width = 500
    assert model.width == 500

    layoutable.height = 450
    assert model.height == 450

    layoutable.min_height = 300
    assert model.min_height == 300

    layoutable.min_width = 250
    assert model.min_width == 250

    layoutable.max_height = 600
    assert model.max_height == 600

    layoutable.max_width = 550
    assert model.max_width == 550

    layoutable.margin = 10
    assert model.margin == (10, 10, 10, 10)

    layoutable.sizing_mode = 'stretch_width'
    assert model.sizing_mode == 'stretch_width'

    layoutable.width_policy = 'max'
    assert model.width_policy == 'max'

    layoutable.height_policy = 'min'
    assert model.height_policy == 'min'


@pytest.mark.parametrize('pane', [Str, Markdown, HTML, PNG, JPG, SVG,
                                  GIF, LaTeX, Matplotlib, RGGPlot, YT,
                                  Plotly, Vega])
def test_pane_layout_properties(pane, document, comm):
    p = pane()
    model = p._get_root(document, comm)
    check_layoutable_properties(p, model)


@pytest.mark.parametrize('widget', all_widgets)
def test_widget_layout_properties(widget, document, comm):
    w = widget()
    model = w._get_root(document, comm)
    check_layoutable_properties(w, model)


@pytest.mark.parametrize('layout', [Column, Row, Tabs, Spacer])
def test_layout_properties(layout, document, comm):
    l = layout()
    model = l._get_root(document, comm)
    check_layoutable_properties(l, model)
