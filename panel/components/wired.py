"""Implementation of the wired WebComponents"""
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
        if isinstance(self.attributes_to_watch, dict):
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

class RadioButton(WebComponent):
    """A Wired RadioButton"""
    # Todo: If the innerHTML/ label is not set the the elements is not really clickable
    # I need to find out how to handle this. Guess it something about width, height etc.
    # Todo: support setting label via parameter
    html = param.String('<wired-radio>Radio Button Label</wired-radio>')
    properties_to_watch= param.Dict({"checked": "checked"})

    checked = param.Boolean(default=False)

class CheckBox(WiredBase):
    # Todo: If the innerHTML/ label is not set the the elements is not really clickable
    # I need to find out how to handle this. Guess it something about width, height etc.
    # Todo: support setting label via parameter
    html = param.String('<wired-checkbox>CheckBox Label</wired-checkbox>')
    properties_to_watch= param.Dict({"checked": "checked"})

    checked = param.Boolean(default=False)

class Slider(WebComponent):
    # Todo: The slider is not working due to https://github.com/wiredjs/wired-elements/issues/121#issue-573516963
    # Todo: I need Philips help to understand how to avoid pn.Param(slider, parameters=["value"]) to turn red
    # It seems the value needs to be rounded?
    html = param.String('<wired-slider></wired-slider>')
    properties_to_watch= param.Dict({"value": "value"})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    value = param.Number(default=33.1)

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

class Input(WebComponent):
    # Todo: Implement api for added wired-combo-items to the innerhtml
    # Todo: The selected attribute/ parameter is not updated. Fix this
    html = param.String("""<wired-input></wired-input>""")
    properties_to_watch= param.Dict({"placeholder": "placeholder", "disabled": "disabled", "type": "type_", "value": "value"})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    placeholder = param.String(default="Enter Value")
    disabled = param.Boolean(default=False)
    type_ = param.String() # Todo: Change to ObjectSelect. Type can be password etc
    value = param.String()


class Video(WebComponent):
    html = param.String("""<wired-video autoplay="" playsinline="" muted="" loop="" style="height: 100%; margin: 0px" src="https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4" class="wired-rendered"></wired-video>""")