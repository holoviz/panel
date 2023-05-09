"""
The theme module contains Design and Theme components.

Each Design applies a coherent design system (e.g. bootstrap or
material) to a template or a set of components, while Theme objects
implement different color palettes (e.g. dark or default).
"""

from .base import (  # noqa
    THEMES, DarkTheme, DefaultTheme, Design, Inherit, Theme,
)
from .bootstrap import Bootstrap
from .fast import Fast
from .material import Material
from .native import Native

__all__ = (
    "THEMES",
    "Bootstrap",
    "DarkTheme",
    "DefaultTheme",
    "Design",
    "Fast",
    "Inherit",
    "Material",
    "Native",
    "Theme"
)
