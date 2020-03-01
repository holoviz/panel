"""Implementation of the wired WebComponents"""
import param

from panel.pane import WebComponent


class RadioButton(WebComponent):
    """A Wired RadioButton"""
    html = param.String('<wired-radio>Radio Two</wired-radio>')
    attributes_to_watch= param.Dict({"checked": "checked"})

    checked = param.Boolean(default=False)

class CheckBox(WebComponent):
    html = param.String('<wired-checkbox id="strokeShape" checked="" class="wired-rendered">Stroke shape</wired-checkbox>')
    attributes_to_watch= param.Dict({"checked": "checked"})

    checked = param.Boolean(default=False)

class Slider(WebComponent):
    html = param.String('<wired-slider id="slider" value="33" knobradius="15" class="wired-rendered" style="margin: 0px"></wired-slider>')
    attributes_to_watch= param.Dict({"value": "value"})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    value = param.Boolean(default=33)

class ComboBox(WebComponent):
    html = param.String("""<wired-combo id="colorCombo" selected="red" role="combobox" aria-haspopup="listbox" tabindex="0" class="wired-rendered" aria-expanded="false"><wired-item value="red" aria-selected="true" role="option" class="wired-rendered">Red</wired-item><wired-item value="green" role="option" class="wired-rendered">Green</wired-item><wired-item value="blue" role="option" class="wired-rendered">Blue</wired-item></wired-combo>""")
    attributes_to_watch= param.Dict({"selected": "selected"})

    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

    selected = param.String(default="red")

class Video(WebComponent):
    html = param.String("""<wired-video autoplay="" playsinline="" muted="" loop="" style="height: 100%; margin: 0px" src="https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4" class="wired-rendered"></wired-video>""")