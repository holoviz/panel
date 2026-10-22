"""
The classic panes, plus the Material UI Typography pane and the Param and
HoloViews panes that always generate Material UI widgets.
"""
from panel_material_ui.pane import MaterialPaneBase, Typography

from ...pane import (
    AVIF, GIF, HTML, ICO, JPG, JSON, PDF, PNG, SVG, VTK, YT, Audio, Bokeh,
    DataFrame, DeckGL, ECharts, HoloViews as _HoloViews, Image, Interactive,
    IPyLeaflet, IPyWidget, LaTeX, Markdown, Matplotlib, Pane, PaneBase,
    ParamFunction, ParamMethod, ParamRef, Perspective, Placeholder, Plotly,
    ReactiveExpr, Reacton, RGGPlot, Str, Streamz, Textual, Vega, Video, Vizzu,
    VTKVolume, panel as _panel,
)
from ...param import Param as _Param
from ...viewable import ServableMixin, Viewable


def _material_ui_design():
    from ..theme import MaterialUIDesign
    return MaterialUIDesign


class Param(_Param):
    """
    Param generates Material UI widgets for the parameters of a Parameterized
    object, whichever design is active.

    Reference: https://panel.holoviz.org/reference/panes/Param.html
    """

    # Selected through panel.ui.panel, so that panel.panel keeps
    # returning the classic pane.
    priority = False

    @classmethod
    def _widget_design(cls):
        return _material_ui_design()


class HoloViews(_HoloViews):
    """
    HoloViews renders a HoloViews object and generates Material UI widgets for
    its dimensions, whichever design is active.

    Reference: https://panel.holoviz.org/reference/panes/HoloViews.html
    """

    priority = False

    @classmethod
    def _widget_design(cls):
        return _material_ui_design()


_MATERIAL_PANES = {_Param: Param, _HoloViews: HoloViews}


def panel(obj, **kwargs):
    """
    Creates a displayable Panel object given any valid Python object, like
    `panel.panel`, but renders Parameterized and HoloViews objects with the
    panel.ui Param and HoloViews panes.

    >>> pn.ui.panel(some_python_object, width=500)
    """
    if isinstance(obj, (Viewable, ServableMixin)) or hasattr(obj, '__panel__'):
        return _panel(obj, **kwargs)
    if kwargs.get('name', False) is None:
        kwargs.pop('name')
    pane_type = PaneBase.get_pane_type(obj, **kwargs)
    pane = _MATERIAL_PANES.get(pane_type, pane_type)(obj, **kwargs)
    if len(pane.layout) == 1 and pane._unpack:
        return pane.layout[0]
    return pane.layout


__all__ = (
    "Audio",
    "AVIF",
    "Bokeh",
    "DataFrame",
    "DeckGL",
    "ECharts",
    "GIF",
    "HoloViews",
    "HTML",
    "ICO",
    "Image",
    "Interactive",
    "IPyLeaflet",
    "IPyWidget",
    "JPG",
    "JSON",
    "LaTeX",
    "Markdown",
    "MaterialPaneBase",
    "Matplotlib",
    "Pane",
    "PaneBase",
    "panel",
    "Param",
    "ParamFunction",
    "ParamMethod",
    "ParamRef",
    "PDF",
    "Perspective",
    "Placeholder",
    "Plotly",
    "PNG",
    "ReactiveExpr",
    "Reacton",
    "RGGPlot",
    "Str",
    "Streamz",
    "SVG",
    "Textual",
    "Typography",
    "Vega",
    "Video",
    "Vizzu",
    "VTK",
    "VTKVolume",
    "YT",
)
