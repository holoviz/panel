"""Implementation of the wired WebComponents"""
from panel.components.material import MWC_ICONS
import param

from panel.pane import WebComponent
from typing import Set

# Todo: Determine if the bundle should be loaded or only files for individual components
# Todo: Determine if the webcomponents-loader should be included for older browsers
JS_FILES = {
    "webcomponents-loader": "https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js",
    "wired-bundle": "https://wiredjs.com/dist/showcase.min.js"
    }

class WiredBase(WebComponent):
    """Inherit from this class"""
    def __init__(self, **params):
        if not self.param.attributes_to_watch.default:
            self.param.attributes_to_watch.default = {}
        self.attributes_to_watch["disabled"]="disabled"

        super().__init__(**params)

    def _child_parameters(self):
        parameters = super()._child_parameters()
        parameters.add("disabled")
        return parameters

ELEVATION_DEFAULT = 0
ELEVATION_BOUNDS = (0,10)

class Button(WiredBase):
    """A Wired RadioButton"""
    # Todo: If the innerHTML/ label is not set the the elements is not really clickable
    # I need to find out how to handle this. Guess it something about width, height etc.
    # Todo: support setting label via parameter
    html = param.String('<wired-button>Button</wired-radio>')
    attributes_to_watch = param.Dict({"elevation": "elevation"})
    events_to_watch = param.Dict(default={"click": "clicks"})

    clicks = param.Integer()
    elevation = param.Integer(ELEVATION_DEFAULT, bounds=ELEVATION_BOUNDS)

class Calendar(WiredBase):
    html = param.String('<wired-calendar initials="" role="dialog tabindex="0">Button</wired-calendar>')
    attributes_to_watch = param.Dict({"elevation": "elevation", "firstdate": "firstdate", "lastdate": "lastdate", "locale": "locale"})
    properties_to_watch= param.Dict({"selected": "selected"})
    events_to_watch = param.Dict(default={"selected": "selects"})

    elevation = param.Integer(ELEVATION_DEFAULT, bounds=ELEVATION_BOUNDS)
    # Todo: Support more advanced date handling
    firstdate = param.String(doc="""
    Example: firstdate="Apr 15, 2019"""
    )
    lastdate = param.String(doc="""
    Example: lastdate="Jul 15, 2019"""
    )
    locale = param.ObjectSelector("en", objects=["en", "fr", "de"])
    selected = param.String(doc="""
    Example: selected="Jul 4, 2019""")
    selects = param.Integer(bounds=(0,None))

    def __init__(self, min_height=300, min_width=300, **params):
        super().__init__(min_height=min_height, min_width=min_width, **params)

class CheckBox(WiredBase):
    # Todo: If the innerHTML/ label is not set the the elements is not really clickable
    # I need to find out how to handle this. Guess it something about width, height etc.
    # Todo: support setting label via parameter
    html = param.String('<wired-checkbox>CheckBox Label</wired-checkbox>')
    properties_to_watch= param.Dict({"checked": "checked"})

    checked = param.Boolean()

# Todo: The Dialog is really a layout
# Find a way to add a close button
# Find a way to let the user include panes and widgets in the Dialog
class Dialog(WebComponent):
    # Todo: Find a way to handle the innerHTML part
    html = param.String('<wired-dialog></wired-checkbox>')
    attributes_to_watch= param.Dict({"open": "is_open"})
    parameters_to_watch = param.List(["text"])

    is_open = param.Boolean(default=False)
    text = param.String()


    def __init__(self, **params):
        super().__init__(**params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-dialog>{params['text']}</wired-dialog>"

class Divider(WebComponent):
    html = param.String('<wired-divider></wired-divider>')

    def __init__(self, min_height=20, **params):
        super().__init__(min_height=min_height, **params)

    attributes_to_watch = param.Dict({"elevation": "elevation"})
    elevation = param.Integer(ELEVATION_DEFAULT, bounds=ELEVATION_BOUNDS)

class Fab(WiredBase):
    html = param.String('<wired-fab><mwc-icon>favorite</mwc-icon></wired-fab>')
    parameters_to_watch = param.List(["icon"])

    icon = param.ObjectSelector("favorite", objects=MWC_ICONS, doc="""
    The name of an `mwc-icon <https://github.com/material-components/material-components-web-components/tree/master/packages/icon>`_
    """)
    def __init__(self, min_height=40, **params, ):
        super().__init__(min_height=min_height, **params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-fab><mwc-icon>{params['icon']}</mwc-icon></wired-fab>"

class IconButton(WiredBase):
    html = param.String("<wired-icon-button><mwc-icon>favorite</mwc-icon><wired-icon-button>")
    parameters_to_watch = param.List(["icon"])

    icon = param.ObjectSelector("favorite", objects=MWC_ICONS, doc="""
    The name of an `mwc-icon <https://github.com/material-components/material-components-web-components/tree/master/packages/icon>`_
    """)
    def __init__(self, min_height=40, **params, ):
        super().__init__(min_height=min_height, **params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-icon-button><mwc-icon>{params['icon']}</mwc-icon></wired-icon-button>"

class Image(WebComponent):
    """The wired-image element"""
    html = param.String('<wired-image style="width:100%;height:100%"></wired-image>')
    attributes_to_watch = param.Dict({"elevation": "elevation", "src": "src"})

    # Todo: Find out how to handle height and width in general
    def __init__(self, height=100, **params):
        super().__init__(height=height, **params)

    src = param.String()
    elevation = param.Integer(ELEVATION_DEFAULT, bounds=ELEVATION_BOUNDS)

class Input(WiredBase):
    html = param.String("""<wired-input></wired-input>""")
    attributes_to_watch= param.Dict({"placeholder": "placeholder", "type": "type_"})
    # The wired-base value property does not update.
    # Insted the wired-base change event fires and the textInput.value property updates
    # See https://github.com/wiredjs/wired-elements/issues/123
    properties_to_watch= param.Dict({"textInput.value": "value"})
    events_to_watch = param.Dict({"change": None})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    placeholder = param.String(default="Enter Value")
    type_ = param.ObjectSelector("", objects=["", "password"])
    value = param.String()

class Link(WebComponent):
    html = param.String("<wired-link></wired-link>")
    attributes_to_watch=param.Dict({"href": "href", "target": "target"})
    parameters_to_watch=param.List(["text"])

    href=param.String()
    target=param.ObjectSelector("_blank", objects=["_self", "_blank", "_parent", "_top"])
    text=param.String()

    # Todo: Can we make some general functionality on WebComponentto set inner html on construction?
    def __init__(self, **params):
        super().__init__(**params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        return f"<wired-link>{params['text']}</wired-link>"

# Todo: Implement Wired wired-listbox

class Progress(WebComponent):
    html = param.String("<wired-progress></wired-progress>")
    attributes_to_watch = param.Dict({"value": "value", "percentage": "percentage", "max": "max_"})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

        if "max_" in params:
            self._handle_max_changed()

    value = param.Integer(0, bounds=(0,100))
    max_ = param.Integer(100, bounds=(0,None))
    percentage = param.Boolean()

    @param.depends("max_", watch=True)
    def _handle_max_changed(self):
        self.param.value.bounds=(0, self.max_)




class RadioButton(WebComponent):
    """A Wired RadioButton"""
    # Todo: If the innerHTML/ label is not set the the elements is not really clickable
    # I need to find out how to handle this. Guess it something about width, height etc.
    # Todo: support setting label via parameter
    html = param.String('<wired-radio>Radio Button Label</wired-radio>')
    properties_to_watch= param.Dict({"checked": "checked"})

    checked = param.Boolean(default=False)

class SearchInput(WiredBase):
    html = param.String('<wired-search-input></wired-search-input>')
    attributes_to_watch = param.Dict({"placeholder": "placeholder", "autocomplete": "autocomplete"})
    properties_to_watch = param.Dict({"value": "value"})
    events_to_watch=param.Dict({"input": None})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    placeholder=param.String("Search Here")
    value = param.String()
    autocomplete=param.ObjectSelector("off", objects=["on", "off"])

# Todo: Implement Tabs. It's really a layout. Don't yet know how to support this.

class TextArea(WiredBase):
    html = param.String('<wired-textarea placeholder="Enter text"></wired-textarea>')
    attributes_to_watch = param.Dict({"placeholder": "placeholder"})
    properties_to_watch = param.Dict({"value": "value", "rows": "rows"})
    events_to_watch=param.ObjectSelector({"change": None}, objects=[{"change": None}, {"input": None}],
    doc="""
    The event(s) to watch. When the event(s) are catched the js model properties are checked and
    any changed values are sent to the python model. The event can be
    - `change` (when done) or
    - `input` (for every character change)
    """)

    placeholder = param.String("Enter Text")
    value = param.String()
    rows = param.Integer(2, bounds=(1,100))

    def __init__(self, **params):
        super().__init__(**params)

        if not "min_height" in params:
            self._set_height()

    @param.depends("rows", "disabled", watch=True)
    def _set_height(self):
        height = 20+19*self.rows
        if self.disabled:
            height += 4
        if height!=self.height:
            self.height=height

class Slider(WebComponent):
    # Todo: I need Philips help to understand how to avoid pn.Param(slider, parameters=["value"]) to turn red
    # It seems the value needs to be rounded?
    html = param.String('<wired-slider></wired-slider>')
    properties_to_watch= param.Dict({"input.value": "value"})
    events_to_watch=param.Dict({"change": None})
    # https://github.com/wiredjs/wired-elements/issues/121#issue-573516963

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    value = param.Number(default=33.1)

class Spinner(WebComponent):
    html = param.String('<wired-spinner></wired-spinner>')
    attributes_to_watch = param.Dict({"spinning": "spinning", "duration": "duration"})

    spinning = param.Boolean(default=True)
    duration = param.Integer(default=1000, bounds=(1, 10000))

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

class Toggle(WiredBase):
    html=param.String("<wired-toggle></wired-toggle>")
    properties_to_watch = param.Dict({"checked": "checked"})
    events_to_watch = param.Dict({"change": None})


    def __init__(self, min_height=20, **params):
        super().__init__(min_height=min_height, **params)

    checked = param.Boolean(False)

# Todo
class ComboBox(WebComponent):
    # Todo: Implement api for added wired-combo-items to the innerhtml
    # Todo: The selected attribute/ parameter is not updated. Fix this
    html = param.String("""<wired-combo></wired-combo>""")
    properties_to_watch= param.Dict({"selected": "selected"})
    events_to_watch = param.Dict(default={"selected": "selects"})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    selected = param.String(default="red")
    selects = param.Integer()

class Video(WebComponent):
    html = param.String("""<wired-video autoplay="" playsinline="" muted="" loop="" style="height: 80%;" src="https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4"></wired-video>""")
    attributes_to_watch = param.Dict({"autoplay": "autoplay", "playsinline": "playsinline", "loop":"loop", "src": "src"})

    def __init__(self, min_height=250, margin=50, **params):
        super().__init__(min_height=min_height, **params)

    src=param.String()
    autoplay=param.Boolean()
    playsinline=param.Boolean()
    muted=param.Boolean()
    loop=param.Boolean()