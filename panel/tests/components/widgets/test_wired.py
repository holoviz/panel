from panel.components.wired import RadioButton, CheckBox, Slider, ComboBox
import panel as pn


def test_view():
    js = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.0.0/webcomponents-loader.js"></script>
<script type="module" src="https://unpkg.com/wired-elements@0.6.4/dist/wired-elements.bundled.js"></script>
"""
    radio_button = RadioButton()
    check_box = CheckBox()
    slider = Slider()
    combobox = ComboBox()
    # video = Video(height=500)
    return pn.Column(
        pn.pane.HTML(js),
        radio_button,
        pn.Param(radio_button.param.html),
        check_box,
        pn.Param(check_box.param.html),
        slider,
        pn.Param(slider.param.html),
        combobox,
        pn.Param(combobox.param.html),
        # video, pn.Param(video.param.html),
    )


if __name__.startswith("bk"):
    pn.config.sizing_mode = "stretch_width"
    test_view().servable()
