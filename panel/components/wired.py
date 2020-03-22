"""Implementation of the wired WebComponents"""
import ast
import datetime
import json
from typing import Set, Optional

import param

from panel.components.material import MWC_ICONS
from panel.pane import WebComponent

# @Philippfr. Should we load the full bundle or individual bundles?
# @Philippfr. How should users load the js pn.extions("wired") or?
# @Philippfr. Should we include the webcomponents-loader for older browsers?
JS_FILES = {
    "webcomponents-loader": "https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js",
    "wired-bundle": "https://wiredjs.com/dist/showcase.min.js",
}


class WiredBase(WebComponent):
    """Inherit from this class"""

    def __init__(self, **params):
        if not self.param.attributes_to_watch.default:
            self.param.attributes_to_watch.default = {}
        self.attributes_to_watch["disabled"] = "disabled"

        super().__init__(**params)

    def _child_parameters(self):
        parameters = super()._child_parameters()
        parameters.add("disabled")
        return parameters


ELEVATION_DEFAULT = 0
ELEVATION_BOUNDS = (0, 10)


class Button(WiredBase):
    """A Wired RadioButton

    - You can set the `text` shown via the `name` parameter.
    """

    html = param.String("<wired-button></wired-button>")
    attributes_to_watch = param.Dict({"elevation": "elevation"})
    events_to_watch = param.Dict(default={"click": "clicks"})
    parameters_to_watch = param.List(["name"])

    clicks = param.Integer()
    elevation = param.Integer(ELEVATION_DEFAULT, bounds=ELEVATION_BOUNDS)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-button>{params['name']}</wired-button>"

class Checkbox(WiredBase):
    html = param.String("<wired-checkbox></wired-checkbox>")
    properties_to_watch = param.Dict({"checked": "value"})
    parameters_to_watch = param.List(["name"])

    value = param.Boolean()

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-checkbox>{params['name']}</wired-checkbox>"

class DatePicker(WiredBase):
    component_type = param.String("inputgroup")
    html = param.String(
        '<wired-calendar initials="" role="dialog tabindex="0">Button</wired-calendar>'
    )
    attributes_to_watch = param.Dict(
        {
            "elevation": "elevation",
            "firstdate": "firstdate",
            "lastdate": "lastdate",
            "locale": "locale",
        }
    )
    properties_to_watch = param.Dict({"selected": "selected"})
    events_to_watch = param.Dict(default={"selected": "selects"})

    elevation = param.Integer(ELEVATION_DEFAULT, bounds=ELEVATION_BOUNDS)
    # Todo: Support more datatime datahandling instead of strings if possible.
    firstdate = param.String(
        doc="""
    Example: firstdate="Apr 15, 2019"""
    )
    lastdate = param.String(
        doc="""
    Example: lastdate="Jul 15, 2019"""
    )
    locale = param.ObjectSelector("en", objects=["en", "fr", "de"])
    selected = param.String(
        doc="""
    Example: selected="Jul 4, 2019"""
    )
    selects = param.Integer(bounds=(0, None))
    value = param.Date(default=None)
    start = param.Date(default=None)
    end = param.Date(default=None)

    def __init__(self, min_height=340, min_width=300, **params):
        super().__init__(min_height=min_height, min_width=min_width, **params)

    @staticmethod
    def _to_date(value: Optional[str]) -> Optional[datetime.date]:
        """Converts a date string to a date

        Parameters
        ----------
        value : str
            The str date value
        """
        if value:
            return datetime.datetime.strptime(value, "%b %d, %Y").date()
        return None

    @staticmethod
    def _to_string(value: datetime.date) -> str:
        """Converts a date to a string

        Parameters
        ----------
        value : date
            The date value to convert
        """
        if value:
            return value.strftime("%b %e, %Y").replace("  ", " ")
        return None

    @param.depends("selected", watch=True)
    def _set_value(self):
        value = self._to_date(self.selected)
        if value != self.value:
            self.value = value

    @param.depends("value", watch=True)
    def _set_selected(self):
        selected = self._to_string(self.value)
        if selected != self.selected:
            self.selected = selected

    @param.depends("firstdate", watch=True)
    def _set_start(self):
        start = self._to_date(self.firstdate)
        if start != self.start:
            self.start = start

    @param.depends("start", watch=True)
    def _set_firstdate(self):
        firstdate = self._to_string(self.start)
        if firstdate != self.firstdate:
            self.firstdate = firstdate

    @param.depends("lastdate", watch=True)
    def _set_end(self):
        end = self._to_date(self.lastdate)
        if end != self.end:
            self.end = end

    @param.depends("end", watch=True)
    def _set_lastdate(self):
        lastdate = self._to_string(self.end)
        if lastdate != self.lastdate:
            self.lastdate = lastdate


# @Philppfr: The Dialog is really a layout
# I would like to support WebComponent layouts in general.
# The user should be able to include panes and widgets like buttons in the Dialog.
# How would I do that?
class Dialog(WebComponent):
    html = param.String("<wired-dialog></wired-checkbox>")
    attributes_to_watch = param.Dict({"open": "is_open"})
    parameters_to_watch = param.List(["text"])

    is_open = param.Boolean(default=False)
    text = param.String()

    def __init__(self, **params):
        super().__init__(**params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-dialog>{params['text']}</wired-dialog>"


class Divider(WebComponent):
    html = param.String("<wired-divider></wired-divider>")

    def __init__(self, min_height=20, **params):
        super().__init__(min_height=min_height, **params)

    attributes_to_watch = param.Dict({"elevation": "elevation"})
    elevation = param.Integer(ELEVATION_DEFAULT, bounds=ELEVATION_BOUNDS)


class Fab(WiredBase):
    html = param.String("<wired-fab><mwc-icon>favorite</mwc-icon></wired-fab>")
    parameters_to_watch = param.List(["icon"])

    icon = param.ObjectSelector(
        "favorite",
        objects=MWC_ICONS,
        doc="""
    The name of an `mwc-icon <https://github.com/material-components/material-components-web-components/tree/master/packages/icon>`_
    """,
    )

    def __init__(
        self, min_height=40, **params,
    ):
        super().__init__(min_height=min_height, **params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-fab><mwc-icon>{params['icon']}</mwc-icon></wired-fab>"

# Issue: Value is not set on construction. See
# https://github.com/wiredjs/wired-elements/issues/121#issue-573516963
# Todo: Add slider value to label
class FloatSlider(WebComponent):
    component_type = param.String("inputgroup")
    html = param.String("<wired-slider style='width: 100%;height:100%'></wired-slider>")
    attributes_to_watch = param.Dict({"min": "start", "max": "end", "step": "step"})
    properties_to_watch = param.Dict({"input.value": "value"})
    events_to_watch = param.Dict({"change": None})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    start = param.Number(0.0)
    end = param.Number(1.0)
    step = param.Number(0.1)
    value = param.Number(default=0.0)
    orientation = param.String()

class IconButton(WiredBase):
    html = param.String("<wired-icon-button><mwc-icon>favorite</mwc-icon><wired-icon-button>")
    parameters_to_watch = param.List(["icon"])
    events_to_watch = param.Dict(default={"click": "clicks"})

    icon = param.ObjectSelector(
        "favorite",
        objects=MWC_ICONS,
        doc="""
    The name of an `mwc-icon <https://github.com/material-components/material-components-web-components/tree/master/packages/icon>`_
    """,
    )
    clicks = param.Integer()

    def __init__(
        self, min_height=40, **params,
    ):
        super().__init__(min_height=min_height, **params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-icon-button><mwc-icon>{params['icon']}</mwc-icon></wired-icon-button>"


class Image(WebComponent):
    """The wired-image element"""

    html = param.String('<wired-image style="width:100%;height:100%"></wired-image>')
    attributes_to_watch = param.Dict({"elevation": "elevation", "src": "object", "alt": "alt_text"})

    # @Philippfr: How do I handle height and width in general in the .ts model?
    def __init__(self, height=100, **params):
        super().__init__(height=height, **params)

    object = param.String(default=None, doc="""Currently only an url is supported""")
    alt_text = param.String(default=None)
    elevation = param.Integer(ELEVATION_DEFAULT, bounds=ELEVATION_BOUNDS)

# Issue: Value is not set on construction. See
# https://github.com/wiredjs/wired-elements/issues/121#issue-573516963
# Todo: Add slider value to label
class IntSlider(FloatSlider):

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    start = param.Integer(0)
    end = param.Integer(1)
    step = param.Integer(1)
    value = param.Integer(0)

class Link(WebComponent):
    html = param.String("<wired-link></wired-link>")
    attributes_to_watch = param.Dict({"href": "href", "target": "target"})
    parameters_to_watch = param.List(["text"])

    href = param.String()
    target = param.ObjectSelector("_blank", objects=["_self", "_blank", "_parent", "_top"])
    text = param.String()

    def __init__(self, **params):
        super().__init__(**params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-link>{params['text']}</wired-link>"

class LiteralInput(WiredBase):
    component_type = param.String("inputgroup")
    html = param.String("""<wired-input style="width:100%"></wired-input>""")
    attributes_to_watch = param.Dict(
        {
            "placeholder": "placeholder",
        }
    )
    properties_to_watch = param.Dict({"textInput.value": "value"})
    events_to_watch = param.Dict({"change": None})

    # @Philippff. I sthis the right place to define height? And what about width?
    def __init__(self, min_height=60, **params):
        # Hack: To solve https://github.com/wiredjs/wired-elements/issues/123
        if "value" in params:
            self.param.html.default = f'<wired-input value="{params["value"]}" style="width:100%;height:100%"></wired-input>'
        elif self.param.value.default:
            self.param.html.default = f'<wired-input value="{self.param.value.default}" style="width:100%;height:100%"></wired-input>'

        super().__init__(min_height=min_height, **params)

    placeholder = param.String(default="Enter Value")
    value = param.Parameter()
    type = param.ClassSelector(default=None, class_=(type, tuple),
                               is_instance=True)
    serializer = param.ObjectSelector(default='ast', objects=['ast', 'json'], doc="""
       The serialization (and deserialization) method to use. 'ast'
       uses ast.literal_eval and 'json' uses json.loads and json.dumps.
    """)



    def _handle_properties_last_change(self, event):
        if "textInput.value" in event.new:
            value = event.new["textInput.value"]
            if not value or not isinstance(value, str):
                pass
            elif self.serializer == 'json':
                value = json.loads(value)
            else:
                value = ast.literal_eval(value)
            if value != self.value:
                self.value=value
        else:
            super()._handle_properties_last_change(event)


    def _handle_parameter_property_change(self, event):
        if event.name=="value":
            value = event.new

            if not value or isinstance(value, str):
                pass
            else:
                if self.serializer == 'json':
                    value = json.dumps(value)
                else:
                    value = repr(value)
            properties_last_change = {"textInput.value": value}

            if properties_last_change != self.properties_last_change:
                self.properties_last_change = properties_last_change
        else:
            super()._handle_parameter_property_change(event)


# Todo: Implement Wired wired-listbox


class Progress(WebComponent):
    html = param.String("<wired-progress></wired-progress>")
    attributes_to_watch = param.Dict({"value": "value", "percentage": "percentage", "max": "max"})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

        if "max" in params:
            self._handle_max_changed()

    value = param.Integer(None, bounds=(0, 100))
    max = param.Integer(100, bounds=(0, None))
    percentage = param.Boolean()

    @param.depends("max", watch=True)
    def _handle_max_changed(self):
        self.param.value.bounds = (0, self.max)


class RadioButton(WebComponent):
    """A Wired RadioButton"""

    html = param.String("<wired-radio>Radio Button</wired-radio>")
    properties_to_watch = param.Dict({"checked": "value"})
    parameters_to_watch = param.List(["name"])

    value = param.Boolean(default=False)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-radio>{params['name']}</wired-radio>"

# Todo: Implement RadioBoxGroup
# Todo: Implement PasswordInput


class SearchInput(WiredBase):
    html = param.String("<wired-search-input></wired-search-input>")
    attributes_to_watch = param.Dict({"placeholder": "placeholder", "autocomplete": "autocomplete"})
    properties_to_watch = param.Dict({"value": "value"})
    events_to_watch = param.Dict({"input": None})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    placeholder = param.String("")
    value = param.String()
    autocomplete = param.ObjectSelector("off", objects=["on", "off"])


# Todo: Implement Tabs. It's really a layout. Don't yet know how to support this.

# @Philippfr: Should we merge the wired Progress and wired ProgressSpinner into one with
# functionality similar to the Panel Progress?
class ProgressSpinner(WebComponent):
    html = param.String("<wired-spinner></wired-spinner>")
    attributes_to_watch = param.Dict({"spinning": "active", "duration": "duration"})

    active = param.Boolean(default=True)
    duration = param.Integer(default=1000, bounds=(1, 10000))

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

class TextAreaInput(WiredBase):
    html = param.String('<wired-textarea placeholder="Enter text"></wired-textarea>')
    attributes_to_watch = param.Dict({"placeholder": "placeholder"})
    properties_to_watch = param.Dict({"value": "value", "rows": "rows", "maxlength": "max_length"})
    events_to_watch = param.ObjectSelector(
        {"change": None},
        objects=[{"change": None}, {"input": None}],
        doc="""
    The event(s) to watch. When the event(s) are catched the js model properties are checked and
    any changed values are sent to the python model. The event can be
    - `change` (when done) or
    - `input` (for every character change)
    """,
    )

    placeholder = param.String("")
    value = param.String()
    rows = param.Integer(2, bounds=(1, 100))
    max_length = param.Integer(default=5000)

    def __init__(self, **params):
        super().__init__(**params)

        if not "min_height" in params:
            self._set_height()

    @param.depends("rows", "disabled", watch=True)
    def _set_height(self):
        height = 20 + 19 * self.rows
        if self.disabled:
            height += 4
        if height != self.height:
            self.height = height


class TextInput(WiredBase):
    component_type = param.String("inputgroup")
    html = param.String("""<wired-input style="width:100%;height:100%"></wired-input>""")
    attributes_to_watch = param.Dict(
        {
            "placeholder": "placeholder",
            "type": "type_",
            # "min": "start",
            # "max": "end",
            # "step": "step",
        }
    )
    properties_to_watch = param.Dict({"textInput.value": "value"})
    events_to_watch = param.Dict({"change": None})

    # @Philippff. I sthis the right place to define height? And what about width?
    def __init__(self, min_height=50, **params):
        # Hack: To solve https://github.com/wiredjs/wired-elements/issues/123
        if "value" in params:
            self.param.html.default = f'<wired-input value="{params["value"]}" style="width:100%;height:100%"></wired-input>'
        elif self.param.value.default:
            self.param.html.default = f'<wired-input value="{self.param.value.default}" style="width:100%;height:100%"></wired-input>'

        super().__init__(min_height=min_height, **params)

    placeholder = param.String(default="")
    type_ = param.ObjectSelector("", objects=["", "number", "password"])
    value = param.String()
    # start = param.Integer(None)
    # end = param.Integer(None)
    # step = param.Parameter(None)

class Toggle(WiredBase):
    html = param.String("<wired-toggle></wired-toggle>")
    properties_to_watch = param.Dict({"checked": "value"})
    events_to_watch = param.Dict({"change": None})

    def __init__(self, min_height=20, **params):
        super().__init__(min_height=min_height, **params)

    value = param.Boolean(False)


class Select(WebComponent):
    # Todo: Implement api for added wired-combo-items to the innerhtml
    # Todo: The selected attribute/ parameter is not updated. Fix this
    component_type = param.String("inputgroup")
    html = param.String("""<wired-combo></wired-combo>""")
    properties_to_watch = param.Dict({"selected": "value"})
    events_to_watch = param.Dict(default={"selected": "selects"})
    parameters_to_watch = param.List(["options"])

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

        self._set_class_()

    value = param.Parameter()
    selects = param.Integer()
    options = param.ClassSelector(default=[], class_=(dict, list))

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        options = params["options"]
        if not options:
            return """<wired-combo></wired-combo>"""

        innerhtml = []
        if isinstance(options, list):
            for obj in options:
                item = f'<wired-item value"{str(obj)}" role="option">{str(obj)}</wired-item>'
                innerhtml.append(item)
        if isinstance(options, dict):
            for key, value in options.items():
                item = f'<wired-item value"{str(key)}" role="option">{str(value)}</wired-item>'
                innerhtml.append(item)

        return f"""<wired-combo>{"".join(innerhtml)}</wired-combo>"""

    # @Phillipfr: Don't understand why this is nescessary. But get error if I don't do it.
    @param.depends("options", watch=True)
    def _set_class_(self):
        if isinstance(self.options, list):
            self.param.options.class_ = list
        if isinstance(self.options, dict):
            self.param.options.class_ = dict


class Video(WebComponent):
    html = param.String(
        """<wired-video autoplay="" playsinline="" muted="" loop="" style="height: 80%;" src="https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4"></wired-video>"""
    )
    attributes_to_watch = param.Dict(
        {"autoplay": "autoplay", "playsinline": "playsinline", "loop": "loop", "src": "object"}
    )

    def __init__(self, min_height=250, margin=50, **params):
        super().__init__(min_height=min_height, **params)

    object = param.String(doc="""Currently only an url is supported""")
    autoplay = param.Boolean()
    playsinline = param.Boolean()
    muted = param.Boolean()
    loop = param.Boolean()
