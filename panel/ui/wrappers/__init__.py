"""
Components that wrap another component, e.g. to add a badge or a tooltip.
"""
from panel_material_ui.wrappers import (
    Badge, Clickable, Skeleton, Tooltip, Transition, Wrapper,
)

__all__: tuple[str, ...] = (
    "Badge",
    "Clickable",
    "Skeleton",
    "Tooltip",
    "Transition",
    "Wrapper",
)

try:
    from panel_material_ui.wrappers import Fullscreen  # noqa: F401
except ImportError:  # panel-material-ui < 0.17
    pass
else:
    __all__ = tuple(sorted((*__all__, "Fullscreen"), key=str.lower))
