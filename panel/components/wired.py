"""Implementation of the wired WebComponents"""
import param

from panel.pane import WebComponent

# Todo: Determine if the bundle should be loaded or only files for individual components
# Todo: Determine if the webcomponents-loader should be included for older browsers
JS_FILES = {
    "webcomponents-loader": "https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js",
    "wired-bundle": "https://wiredjs.com/dist/showcase.min.js"
    }

class Button(WebComponent):
    """A Wired RadioButton"""
    # Todo: If the innerHTML/ label is not set the the elements is not really clickable
    # I need to find out how to handle this. Guess it something about width, height etc.
    # Todo: support setting label via parameter
    html = param.String('<wired-button>Button</wired-radio>')
    events_to_watch = param.Dict(default={"click": "clicks"})

    clicks = param.Integer()

class RadioButton(WebComponent):
    """A Wired RadioButton"""
    # Todo: If the innerHTML/ label is not set the the elements is not really clickable
    # I need to find out how to handle this. Guess it something about width, height etc.
    # Todo: support setting label via parameter
    html = param.String('<wired-radio>Radio Button Label</wired-radio>')
    properties_to_watch= param.Dict({"checked": "checked"})

    checked = param.Boolean(default=False)

class CheckBox(WebComponent):
    # Todo: If the innerHTML/ label is not set the the elements is not really clickable
    # I need to find out how to handle this. Guess it something about width, height etc.
    # Todo: support setting label via parameter
    html = param.String('<wired-checkbox>CheckBox Label</wired-checkbox>')
    properties_to_watch= param.Dict({"checked": "checked"})

    checked = param.Boolean(default=False)

class Slider(WebComponent):
    # Todo: The slider is not working due to https://github.com/wiredjs/wired-elements/issues/121#issue-573516963
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