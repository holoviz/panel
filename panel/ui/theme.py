"""
The Material UI design and the themes it renders.
"""
from panel_material_ui.theme import (
    MaterialDesign, MuiDarkTheme, MuiDefaultTheme,
)

# MaterialUIDesign is the name panel registers as the 'material-ui' design,
# spelled to distinguish it from the older panel.theme.material.Material design.
MaterialUIDesign = MaterialDesign

__all__ = (
    "MaterialDesign",
    "MaterialUIDesign",
    "MuiDarkTheme",
    "MuiDefaultTheme",
)
