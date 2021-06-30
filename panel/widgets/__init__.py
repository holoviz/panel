"""
The widgets module contains Widget which provide bi-directional
communication between a rendered panel and the Widget parameters.
"""
from .ace import Ace  # noqa
from .base import Widget, CompositeWidget  # noqa
from .button import Button, MenuButton, Toggle  # noqa
from .file_selector import FileSelector  # noqa
from .indicators import ( # noqa
    BooleanStatus,
    Dial,
    Gauge,
    LoadingSpinner,
    Number,
    Progress,
    Trend,
    Tqdm,
)
from .input import (  # noqa
    ColorPicker,
    Checkbox,
    DatetimeInput,
    DatePicker,
    DatetimePicker,
    DatetimeRangeInput,
    DatetimeRangePicker,
    FileInput,
    LiteralInput,
    StaticText,
    TextInput,
    IntInput,
    FloatInput,
    NumberInput,
    Spinner,
    PasswordInput,
    TextAreaInput,
)
from .misc import FileDownload, VideoStream # noqa
from .player import DiscretePlayer, Player # noqa
from .slider import ( # noqa
    DateSlider, DateRangeSlider, DiscreteSlider, EditableRangeSlider,
    EditableFloatSlider, EditableIntSlider, FloatSlider, IntSlider,
    IntRangeSlider, RangeSlider
)
from .select import ( # noqa
    AutocompleteInput, CheckBoxGroup, CheckButtonGroup, CrossSelector,
    MultiChoice, MultiSelect, RadioButtonGroup, RadioBoxGroup, Select,
    ToggleGroup
)
from .speech_to_text import SpeechToText, Grammar, GrammarList # noqa
from .tables import DataFrame, Tabulator  # noqa
from .terminal import Terminal # noqa
from .text_to_speech import TextToSpeech, Utterance, Voice # noqa
