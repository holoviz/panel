"""In this module we test the ComponentViewer"""
from panel.themes.theme_builder import ComponentViewer

def test_view():
    """Can view"""
    ComponentViewer().view()

if __name__.startswith("bokeh"):
    ComponentViewer().view().servable()