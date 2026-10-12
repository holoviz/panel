"""
The Material UI design and the themes it renders.
"""
import param

from panel_material_ui.theme import (
    MaterialDesign, MuiDarkTheme, MuiDefaultTheme,
)

from .. import widgets as _classic_widgets
from ..io.resources import CDN_DIST
from ..theme.base import Inherit
from . import widgets as _widgets
from .layout import (
    Alert, Card, Details, Paper,
)
from .pane import JSON, DataFrame, Markdown
from .widgets import (
    Button, CodeEditor, DictInput, FileDropper, JSONEditor, ListInput,
    Tabulator, Terminal, TextEditor, TupleInput,
)


def _material_equivalents() -> dict[type, type]:
    """
    Maps each classic widget to the Material widget panel.ui exports under the
    same name, so that widgets Panel generates (Param, interact, HoloViews)
    follow the design without enumerating them by hand.
    """
    mapping = {}
    for name in _widgets.__all__:
        material = getattr(_widgets, name)
        classic = getattr(_classic_widgets, name, None)
        if isinstance(classic, type) and material is not classic:
            mapping[classic] = material
    return mapping


def _tuple_widget(parameter: param.Parameter) -> type | None:
    # Ranges with bounds render as sliders through the component_mapping.
    return None if isinstance(parameter, param.Range) else TupleInput


class MaterialUIDesign(MaterialDesign):
    """
    Panel's Material UI design defaults.
    """

    component_mapping = _material_equivalents()

    # The classic LiteralInputTyped builds untyped LiteralInput subclasses,
    # which the component_mapping cannot match.
    widget_mapping = {
        param.Dict: DictInput,
        param.List: ListInput,
        param.Tuple: _tuple_widget,
    }

    modifiers = {
        **MaterialDesign.modifiers,
        Alert: {
            'margin': 10,
        },
        Card: {
            **MaterialDesign.modifiers.get(Card, {}),
            'margin': 10,
        },
        Details: {
            'margin': 10,
        },
        Paper: {
            'margin': 10,
        },
        Button: {
            'margin': (15, 10),
        },
        DataFrame: {
            'stylesheets': [f'{CDN_DIST}css/dataframe_mui.css'],
        },
        # The classic components below keep the Material stylesheet and
        # override its colors with the MUI palette variables, which follow
        # theme toggles unlike the theme dependent parameters.
        CodeEditor: {
            'stylesheets': [Inherit, f'{CDN_DIST}css/codeeditor_mui.css'],
        },
        FileDropper: {
            'stylesheets': [Inherit, f'{CDN_DIST}css/filedropper_mui.css'],
        },
        JSON: {
            'stylesheets': [Inherit, f'{CDN_DIST}css/json_mui.css'],
        },
        JSONEditor: {
            'stylesheets': [Inherit, f'{CDN_DIST}css/jsoneditor_mui.css'],
        },
        Markdown: {
            'stylesheets': [Inherit, f'{CDN_DIST}css/markdown_mui.css'],
        },
        Tabulator: {
            **MaterialDesign.modifiers.get(Tabulator, {}),
            'stylesheets': [Inherit, f'{CDN_DIST}css/tabulator_mui.css'],
        },
        Terminal: {
            'stylesheets': [Inherit, f'{CDN_DIST}css/terminal_mui.css'],
        },
        TextEditor: {
            'stylesheets': [Inherit, f'{CDN_DIST}css/texteditor_mui.css'],
        },
    }

__all__ = (
    "MaterialDesign",
    "MaterialUIDesign",
    "MuiDarkTheme",
    "MuiDefaultTheme",
)
