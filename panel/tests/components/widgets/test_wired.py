from panel.components import wired
import panel as pn

def test_wired_base():
    base = wired.WiredBase()

    assert base.disabled == False
    assert "disabled" in base._child_parameters()

def test_wired_button():
    button = wired.Button()

    assert "disabled" in button.attributes_to_watch
    assert "elevation" in button.attributes_to_watch

    # When/Then
    button.disabled=True
    assert "disabled" in button.html

    # When/Then
    button.disabled=False
    assert "disabled" not in button.html

def test_wired_checkbox():
    checkbox = wired.Button()

    assert "disabled" in checkbox.attributes_to_watch
    assert "elevation" in checkbox.attributes_to_watch

    # When/Then
    checkbox.disabled=True
    assert "disabled" in checkbox.html

    # When/Then
    checkbox.disabled=False
    assert "disabled" not in checkbox.html

def test_dialog():
    dialog = wired.Dialog(text="a")

    # When/ Then
    assert dialog.text == "a"
    assert dialog.html == '<wired-dialog>a</wired-dialog>'

    # When/ Then
    dialog.text = "b"
    assert dialog.html == '<wired-dialog>b</wired-dialog>'

def test_slider():
    # When/ Then
    slider = wired.Slider(attributes_to_watch={"value": "value"})
    slider.html = '<wired-slider id="slider" value="40.507407407407406" knobradius="15" class="wired-rendered" style="margin: 0px"></wired-slider>'
    assert slider.value == 40.507407407407406

def test_slider_properties_last_change():
    slider = wired.Slider()

    # When/ Then
    slider.properties_last_change = {'input.value': '13'}
    assert slider.value==13

def test_input():
    # Given
    wired_input = wired.Input()

    # When/ Then
    wired_input.type_ = "password"
    assert "password" in wired_input.html

def test_link():
    # Given
    wired_link = wired.Link(href="www.google.com", target="_blank", text="link")


    # Then
    assert wired_link.href == "www.google.com"
    assert wired_link.target == "_blank"
    assert wired_link.text == "link"
    assert wired_link.html == '<wired-link href="www.google.com" target="_blank">link</wired-link>'

    # When/ Then
    wired_link.text = "another link"
    assert wired_link.href == "www.google.com"
    assert wired_link.target == "_blank"
    assert wired_link.text == "another link"
    assert wired_link.html == '<wired-link href="www.google.com" target="_blank">another link</wired-link>'


def test_view():
    js = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js"></script>
<script src="https://wiredjs.com/dist/showcase.min.js"></script>
"""
    # https://wiredjs.com/dist/showcase.min.js
    # <script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.0.0/webcomponents-loader.js"></script>
    # https://wiredjs.com/dist/showcase.min.js
    # pn.config.js_files["webcomponents-loaded"]="https://unpkg.com/@webcomponents/webcomponentsjs@latest/webcomponents-loader.js"
    # pn.config.js_files["wired-button"]="https://unpkg.com/wired-button@1.0.0/lib/wired-button.js"

    js_pane = pn.pane.HTML(js)

    def section(component, message=None):
        title = "## " + str(type(component)).split(".")[3][:-2]

        if message:
            return (title, component, pn.Param(component, parameters=["html"] + list(component._child_parameters())), pn.pane.Markdown(message), pn.layout.Divider())
        return (title, component, pn.Param(component, parameters=["html"] + list(component._child_parameters())), pn.layout.Divider())

    button = wired.Button()
    calendar = wired.Calendar()
    check_box = wired.CheckBox()
    check_box_checked = wired.CheckBox(checked=True)
    combobox = wired.ComboBox(html="""<wired-combo id="colorCombo" selected="red" role="combobox" aria-haspopup="listbox" tabindex="0" class="wired-rendered" aria-expanded="false"><wired-item value="red" aria-selected="true" role="option" class="wired-rendered">Red</wired-item><wired-item value="green" role="option" class="wired-rendered">Green</wired-item><wired-item value="blue" role="option" class="wired-rendered">Blue</wired-item></wired-combo>""")
    dialog = wired.Dialog(text="Lorum Ipsum. Panel is awesome!")
    divider = wired.Divider()
    fab = wired.Fab()
    icon_button = wired.IconButton()
    image = wired.Image(src="https://www.gstatic.com/webp/gallery/1.sm.jpg", height=200, width=300)
    link = wired.Link(href="https://panel.holoviz.org/", target="_blank")
    wired_input = wired.Input()
    radio_button = wired.RadioButton()
    spinner = wired.Spinner()
    slider = wired.Slider(html="""<wired-slider id="slider" value="33.1" knobradius="15" class="wired-rendered" style="margin: 0px">Slider Label</wired-slider>""")
    # video = Video(height=500)
    return pn.Column(
        js_pane,
        *section(button),
        *section(calendar),
        *section(check_box),
        *section(check_box_checked),
        *section(combobox),
        *section(dialog, "Todo: Find a way to add a close button and size the Dialog."),
        *section(divider),
        *section(fab),
        *section(icon_button),
        *section(image),
        *section(wired_input),
        *section(link, "Normally you would just use the `<wired-link>` tag directly in your html or markdown text"),
        *section(radio_button),
        *section(spinner),
        *section(slider, "**The slider value cannot be set programmatically**. See [Wired Issue](https://github.com/wiredjs/wired-elements/issues/121#issue-573516963)"),
        # video, pn.Param(video.param.html),
    )


if __name__.startswith("bk"):
    pn.config.sizing_mode = "stretch_width"
    test_view().servable()
