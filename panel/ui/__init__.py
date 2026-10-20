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
import sys
import types

import param

from ..config import config
from ..io.state import state


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


# Captured before panel-material-ui is imported below, since it assigns
# config.design unconditionally at import time.
_prior_design = _global_design()

from . import (  # noqa
    base, chat, indicators, layout, notifications, pane, template, theme,
    widgets, wrappers,
)
from .chat import (
    ChatAreaInput, ChatFeed, ChatInterface, ChatMessage, ChatReactionIcons,
    ChatStep,
)
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
    DataFrame, DeckGL, ECharts, HoloViews, Image, Interactive, IPyLeaflet,
    IPyWidget, LaTeX, Markdown, Matplotlib, Param, ParamFunction, ParamMethod,
    ParamRef, Perspective, Placeholder, Plotly, ReactiveExpr, Reacton, RGGPlot,
    Str, Streamz, Textual, Typography, Vega, Video, Vizzu, VTKVolume, panel,
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
    CircularProgress, CodeEditor, ColorMap, ColorPicker, CrossSelector,
    DatePicker, DateRangePicker, DateRangeSlider, DateSlider, DatetimeInput,
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
    "ColorMap",
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
    "Image",
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
    "panel",
    "Paper",
    "Param",
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


def _select_design():
    """
    Selects the Material UI design unless another one is configured. Within a
    session only that session is switched, so classic applications served from
    the same process keep their design.
    """
    if state.curdoc is None:
        if _global_design() is None:
            _set_global_design(MaterialUIDesign)
    elif config.design is None:
        config.design = MaterialUIDesign


class _DesignSelectingModule(types.ModuleType):
    """
    The module is imported once per process, so the sessions after the first
    select the design whenever they access a component through it.
    """

    def __getattribute__(self, name):
        if not name.startswith('__') and state.curdoc is not None:
            _select_design()
        return super().__getattribute__(name)


if _global_design() is not _prior_design:
    _set_global_design(_prior_design)

if _prior_design is MaterialDesign:
    # panel-material-ui was imported first and selected its design globally.
    _set_global_design(MaterialUIDesign)
else:
    _select_design()
    for _name, _module in list(sys.modules.items()):
        if _name == __name__ or _name.startswith(f'{__name__}.'):
            _module.__class__ = _DesignSelectingModule
