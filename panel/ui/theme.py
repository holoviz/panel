"""
The Material UI design and the themes it renders.
"""
from panel_material_ui.theme import (
    MaterialDesign, MuiDarkTheme, MuiDefaultTheme,
)

from ..io.resources import CDN_DIST
from .layout import (
    Alert, Card, Details, Paper,
)
from .pane import DataFrame
from .widgets import Button


class MaterialUIDesign(MaterialDesign):
    """
    Panel's Material UI design defaults.
    """

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
    }

__all__ = (
    "MaterialDesign",
    "MaterialUIDesign",
    "MuiDarkTheme",
    "MuiDefaultTheme",
)
