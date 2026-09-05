"""
The theme module contains Design and Theme components.

Each Design applies a coherent design system (e.g. bootstrap or
material) to a template or a set of components, while Theme objects
implement different color palettes (e.g. dark or default).
"""

from .base import (  # noqa
    DESIGN_ALIASES, THEMES, DarkTheme, DefaultTheme, Design, Inherit, Theme,
    resolve_component, resolve_design, resolve_widget,
)
from .bootstrap import Bootstrap
from .fast import Fast
from .material import Material
from .native import Native

__all__ = (
    "DESIGN_ALIASES",
    "THEMES",
    "Bootstrap",
    "DarkTheme",
    "DefaultTheme",
    "Design",
    "Fast",
    "Inherit",
    "Material",
    "Native",
    "Theme",
    "resolve_component",
    "resolve_design",
    "resolve_widget"
)
