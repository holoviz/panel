"""
These tests verify that all of the panes, layouts, and widgets defined by panel are
represented in the reference gallery.
"""
import os

from inspect import isclass

import pytest
import panel as pn

here = os.path.abspath(os.path.dirname(__file__))
ref = os.path.join(here, '..', '..', 'examples', 'reference')
docs_available = pytest.mark.skipif(not os.path.isdir(ref), reason="docs not found")


@docs_available
def test_layouts_are_in_reference_gallery():
    exceptions = set(['ListPanel', 'Panel'])
    docs = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(ref, 'layouts'))}

    def is_panel_layout(attr):
        layout = getattr(pn.layout, attr)
        return isclass(layout) and issubclass(layout, pn.layout.Panel)

    layouts = set(filter(is_panel_layout, dir(pn.layout)))
    assert layouts - exceptions - docs == set()


@docs_available
def test_widgets_are_in_reference_gallery():
    exceptions = set(['CompositeWidget', 'Widget', 'ToggleGroup', 'NumberInput', 'Spinner'])
    docs = {os.path.splitext(f)[0] for g in ('indicators', 'widgets') for f in os.listdir(os.path.join(ref, g))}

    def is_panel_widget(attr):
        widget = getattr(pn.widgets, attr)
        return isclass(widget) and issubclass(widget, pn.widgets.Widget)

    widgets = set(filter(is_panel_widget, dir(pn.widgets)))
    assert widgets - exceptions - docs == set()


@docs_available
def test_panes_are_in_reference_gallery():
    exceptions = set(['PaneBase', 'YT', 'RGGPlot', 'Interactive', 'ICO'])
    docs = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(ref, 'panes'))}

    def is_panel_pane(attr):
        pane = getattr(pn.pane, attr)
        return isclass(pane) and issubclass(pane, pn.pane.PaneBase)

    panes = set(filter(is_panel_pane, dir(pn.pane)))
    assert panes - exceptions - docs == set()
