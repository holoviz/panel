"""
The Material UI progress indicators, plus the classic indicators.
"""
from panel_material_ui.widgets.indicators import (
    CircularProgress, LinearProgress, LoadingSpinner, Progress,
)

from ...widgets.indicators import (
    BooleanIndicator, BooleanStatus, Dial, Gauge, LinearGauge, Number, String,
    TooltipIcon, Tqdm as _ClassicTqdm, Trend, ValueIndicator,
)


class Tqdm(_ClassicTqdm):
    _progress_type = Progress


__all__ = (
    "BooleanIndicator",
    "BooleanStatus",
    "CircularProgress",
    "Dial",
    "Gauge",
    "LinearGauge",
    "LinearProgress",
    "LoadingSpinner",
    "Number",
    "Progress",
    "String",
    "TooltipIcon",
    "Tqdm",
    "Trend",
    "ValueIndicator",
)
