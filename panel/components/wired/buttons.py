"""Implementation of the wired WebComponent"""
import param

from panel.pane import WebComponent


class RadioButton(WebComponent):
    """A Wired RadioButton"""
    html = param.String('<wired-radio checked id="1" checked>Radio Two</wired-radio>')

class CheckBox(WebComponent):
    html = param.String('<wired-checkbox id="strokeShape" checked="" class="wired-rendered">Stroke shape</wired-checkbox>')

class Slider(WebComponent):
    html = param.String('<wired-slider id="slider" value="33" knobradius="15" class="wired-rendered" style="margin: 0px"></wired-slider>')
    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

class ComboBox(WebComponent):
    html = param.String("""<wired-combo id="colorCombo" selected="red" role="combobox" aria-haspopup="listbox" tabindex="0" class="wired-rendered" aria-expanded="false"><wired-item value="red" aria-selected="true" role="option" class="wired-rendered">Red</wired-item><wired-item value="green" role="option" class="wired-rendered">Green</wired-item><wired-item value="blue" role="option" class="wired-rendered">Blue</wired-item></wired-combo>""")
    def __init__(self, min_height=40, **params):
        super().__init__(min_height=min_height, **params)

class Video(WebComponent):
    html = param.String("""<wired-video autoplay="" playsinline="" muted="" loop="" style="height: 100%; margin: 0px" src="https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4" class="wired-rendered"></wired-video>""")

if __name__.startswith("bk"):
    import panel as pn
    pn.config.sizing_mode="stretch_width"

    js = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.0.0/webcomponents-loader.js"></script>
<script type="module" src="https://unpkg.com/wired-elements@0.6.4/dist/wired-elements.bundled.js"></script>
"""

    radio_button = RadioButton()
    check_box = CheckBox()
    slider = Slider()
    combobox = ComboBox()
    # video = Video(height=500)
    pn.Column(
        pn.pane.HTML(js),
        radio_button, pn.Param(radio_button.param.html),
        check_box, pn.Param(check_box.param.html),
        slider, pn.Param(slider.param.html),
        combobox, pn.Param(combobox.param.html),
        # video, pn.Param(video.param.html),
        ).servable()