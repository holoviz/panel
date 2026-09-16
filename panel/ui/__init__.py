"""
The ``panel.ui`` namespace, Panel's Material UI based component library.

The Material components are implemented by the ``panel-material-ui`` package,
which Panel depends on, and are re-exported here alongside the classic
components that have no Material equivalent, so that an application can import
everything it needs from one namespace. Panel 2.0 moves the implementation into
this package, at which point the imports below change source but not name.

Components are available both flat and per module::

    from panel.ui import Button
    from panel.ui.widgets import Button
"""
import importlib.metadata
import warnings

import param

from packaging.version import Version

from ..config import config

# The supported panel-material-ui range. Both bounds are enforced: panel.ui's
# public surface is versioned by another repository for the 1.x cycle, so a pmui
# minor must not be able to change panel's documented API without a panel
# release. Keep in sync with the pin in pyproject.toml.
_PMUI_MIN_VERSION = '0.11.2'
_PMUI_NEXT_VERSION = '0.12'


def _check_panel_material_ui() -> None:
    """
    Validates the installed panel-material-ui version, so that a version skew
    surfaces here rather than as a missing name further down.
    """
    try:
        version = importlib.metadata.version('panel-material-ui')
    except importlib.metadata.PackageNotFoundError:
        return
    if Version(version) < Version(_PMUI_MIN_VERSION):
        raise ImportError(
            f'panel.ui requires panel-material-ui >={_PMUI_MIN_VERSION}, but '
            f'{version} is installed. Upgrade it with '
            '`pip install -U panel-material-ui`.'
        )
    elif Version(version) >= Version(_PMUI_NEXT_VERSION):
        warnings.warn(
            f'panel.ui supports panel-material-ui >={_PMUI_MIN_VERSION},'
            f'<{_PMUI_NEXT_VERSION}, but {version} is installed. Components may '
            'not behave as documented; upgrade Panel or pin panel-material-ui '
            f'below {_PMUI_NEXT_VERSION}.',
            RuntimeWarning,
            stacklevel=2
        )


def _global_design():
    """
    The globally configured design, bypassing the per-session lookup in
    ``config.__getattribute__``.
    """
    return param.Parameterized.__getattribute__(config, 'design')


def _set_global_design(design):
    """
    Sets the design globally. ``config.design = ...`` is scoped to the current
    session, which would leave every other session on the classic design.
    """
    param.Parameterized.__setattr__(config, 'design', design)


_check_panel_material_ui()

# Captured before panel-material-ui is imported below, since it assigns
# config.design unconditionally at import time until 0.12.
_prior_design = _global_design()

from . import (  # noqa
    base, chat, designs, indicators, layout, notifications, pane, template,
    theme, widgets, wrappers,
)
from .chat import (
    ChatAreaInput, ChatFeed, ChatInterface, ChatMessage, ChatReactionIcons,
    ChatStep,
)
from .designs import Anaconda
from .indicators import String
from .layout import (
    Accordion, Alert, Backdrop, Card, Column, Container, Details, Dialog,
    Divider, Drawer, Feed, FlexBox, FloatPanel, Grid, GridBox, GridSpec,
    GridStack, HSpacer, Modal, Paper, Popup, Row, Spacer, Swipe, Tabs, VSpacer,
    WidgetBox,
)
from .notifications import NotificationArea
from .pane import (
    AVIF, GIF, HTML, ICO, JPG, JSON, PDF, PNG, SVG, VTK, YT, Audio, Bokeh,
    DataFrame, DeckGL, ECharts, HoloViews, Interactive, IPyLeaflet, IPyWidget,
    LaTeX, Markdown, Matplotlib, ParamFunction, ParamMethod, ParamRef,
    Perspective, Placeholder, Plotly, ReactiveExpr, Reacton, RGGPlot, Str,
    Streamz, Textual, Typography, Vega, Video, Vizzu, VTKVolume,
)
from .template import (
    AppBar, BreakpointSwitcher, Page, ThemeToggle,
)
from .theme import (
    MaterialDesign, MaterialUIDesign, MuiDarkTheme, MuiDefaultTheme,
)
from .widgets import (
    ArrayInput, AutocompleteInput, Avatar, BooleanStatus, Breadcrumbs, Button,
    ButtonIcon, Checkbox, CheckBoxGroup, CheckButtonGroup, Chip,
    CircularProgress, CodeEditor, ColorPicker, CrossSelector, DatePicker,
    DateRangePicker, DateRangeSlider, DateSlider, DatetimeInput,
    DatetimePicker, DatetimeRangeInput, DatetimeRangePicker,
    DatetimeRangeSlider, DatetimeSlider, Debugger, Dial, DictInput,
    DiscretePlayer, DiscreteSlider, EditableFloatSlider,
    EditableIntRangeSlider, EditableIntSlider, EditableRangeSlider, Fab,
    FileDownload, FileDropper, FileInput, FileSelector, FloatInput,
    FloatSlider, Gauge, IconButton, IntInput, IntRangeSlider, IntSlider,
    JSONEditor, LinearGauge, LinearProgress, ListInput, LiteralInput,
    LoadingSpinner, MenuBar, MenuButton, MenuList, MenuToggle, MultiChoice,
    MultiPill, MultiSelect, NestedBreadcrumbs, NestedSelect, Number,
    NumberInput, Pagination, PasswordInput, Pill, Player, Progress,
    RadioBoxGroup, RadioButtonGroup, RangeSlider, Rating, Select, SpeechToText,
    SpeedDial, SplitButton, StaticText, StepperMenu, Switch, TabMenu,
    Tabulator, Terminal, TextAreaInput, TextEditor, TextInput, TextToSpeech,
    TimePicker, Toggle, ToggleGroup, ToggleIcon, TooltipIcon, Tqdm, Tree,
    Trend, TupleInput, VideoStream,
)
from .wrappers import (
    Badge, Clickable, Skeleton, Tooltip, Transition, Wrapper,
)

__all__ = (
    "Accordion",
    "Alert",
    "Anaconda",
    "AppBar",
    "ArrayInput",
    "Audio",
    "AutocompleteInput",
    "Avatar",
    "AVIF",
    "Backdrop",
    "Badge",
    "Bokeh",
    "BooleanStatus",
    "Breadcrumbs",
    "BreakpointSwitcher",
    "Button",
    "ButtonIcon",
    "Card",
    "ChatAreaInput",
    "ChatFeed",
    "ChatInterface",
    "ChatMessage",
    "ChatReactionIcons",
    "ChatStep",
    "Checkbox",
    "CheckBoxGroup",
    "CheckButtonGroup",
    "Chip",
    "CircularProgress",
    "Clickable",
    "CodeEditor",
    "ColorPicker",
    "Column",
    "Container",
    "CrossSelector",
    "DataFrame",
    "DatePicker",
    "DateRangePicker",
    "DateRangeSlider",
    "DateSlider",
    "DatetimeInput",
    "DatetimePicker",
    "DatetimeRangeInput",
    "DatetimeRangePicker",
    "DatetimeRangeSlider",
    "DatetimeSlider",
    "Debugger",
    "DeckGL",
    "Details",
    "Dial",
    "Dialog",
    "DictInput",
    "DiscretePlayer",
    "DiscreteSlider",
    "Divider",
    "Drawer",
    "ECharts",
    "EditableFloatSlider",
    "EditableIntRangeSlider",
    "EditableIntSlider",
    "EditableRangeSlider",
    "Fab",
    "Feed",
    "FileDownload",
    "FileDropper",
    "FileInput",
    "FileSelector",
    "FlexBox",
    "FloatInput",
    "FloatPanel",
    "FloatSlider",
    "Gauge",
    "GIF",
    "Grid",
    "GridBox",
    "GridSpec",
    "GridStack",
    "HoloViews",
    "HSpacer",
    "HTML",
    "ICO",
    "IconButton",
    "Interactive",
    "IntInput",
    "IntRangeSlider",
    "IntSlider",
    "IPyLeaflet",
    "IPyWidget",
    "JPG",
    "JSON",
    "JSONEditor",
    "LaTeX",
    "LinearGauge",
    "LinearProgress",
    "ListInput",
    "LiteralInput",
    "LoadingSpinner",
    "Markdown",
    "MaterialDesign",
    "MaterialUIDesign",
    "Matplotlib",
    "MenuBar",
    "MenuButton",
    "MenuList",
    "MenuToggle",
    "Modal",
    "MuiDarkTheme",
    "MuiDefaultTheme",
    "MultiChoice",
    "MultiPill",
    "MultiSelect",
    "NestedBreadcrumbs",
    "NestedSelect",
    "NotificationArea",
    "Number",
    "NumberInput",
    "Page",
    "Pagination",
    "Paper",
    "ParamFunction",
    "ParamMethod",
    "ParamRef",
    "PasswordInput",
    "PDF",
    "Perspective",
    "Pill",
    "Placeholder",
    "Player",
    "Plotly",
    "PNG",
    "Popup",
    "Progress",
    "RadioBoxGroup",
    "RadioButtonGroup",
    "RangeSlider",
    "Rating",
    "ReactiveExpr",
    "Reacton",
    "RGGPlot",
    "Row",
    "Select",
    "Skeleton",
    "Spacer",
    "SpeechToText",
    "SpeedDial",
    "SplitButton",
    "StaticText",
    "StepperMenu",
    "Str",
    "Streamz",
    "String",
    "SVG",
    "Swipe",
    "Switch",
    "TabMenu",
    "Tabs",
    "Tabulator",
    "Terminal",
    "TextAreaInput",
    "TextEditor",
    "TextInput",
    "TextToSpeech",
    "Textual",
    "ThemeToggle",
    "TimePicker",
    "Toggle",
    "ToggleGroup",
    "ToggleIcon",
    "Tooltip",
    "TooltipIcon",
    "Tqdm",
    "Transition",
    "Tree",
    "Trend",
    "TupleInput",
    "Typography",
    "Vega",
    "Video",
    "VideoStream",
    "Vizzu",
    "VSpacer",
    "VTK",
    "VTKVolume",
    "WidgetBox",
    "Wrapper",
    "YT",
)

if _global_design() is not _prior_design:
    _set_global_design(_prior_design)

if config.design is None:
    # Importing panel.ui opts in to the Material design, but never over an
    # explicit choice made with pn.extension(design=...) or config.design.
    _set_global_design(MaterialUIDesign)
