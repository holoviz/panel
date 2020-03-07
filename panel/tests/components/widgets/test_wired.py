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

def test_fab():
    fab = wired.Fab(icon="fast_rewind")

    # When/ Then
    assert fab.icon=="fast_rewind"
    assert fab.html=='<wired-fab><mwc-icon>fast_rewind</mwc-icon></wired-fab>'

    # When/ Then
    fab.icon="favorite"
    assert fab.html=='<wired-fab><mwc-icon>favorite</mwc-icon></wired-fab>'

def test_icon_button():
    icon = wired.IconButton(icon="fast_rewind")

    # When/ Then
    assert icon.icon=="fast_rewind"
    assert icon.html=='<wired-icon-button><mwc-icon>fast_rewind</mwc-icon></wired-icon-button>'

    # When/ Then
    icon.icon="favorite"
    assert icon.html=='<wired-icon-button><mwc-icon>favorite</mwc-icon></wired-icon-button>'



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

def test_progress():
    progress = wired.Progress(value=4, max_=9)

    # Then
    assert progress.value==4
    assert progress.max_==9
    assert progress.param.value.bounds==(0,9)

    # # When/ Then
    progress.max_=5
    assert progress.value==4
    assert progress.max_==5
    assert progress.param.value.bounds==(0,5)

def test_searchinput():
    # When
    search = wired.SearchInput()
    search.placeholder = "New Search"
    search.disabled = True
    search.autocomplete="on"

    # Then
    assert search.html == '<wired-search-input placeholder="New Search" autocomplete="on" disabled></wired-search-input>'

def test_text_area():
    # When/ Then
    text_area = wired.TextArea(placeholder="a", rows=3)
    assert text_area.html== '<wired-textarea placeholder="a"></wired-textarea>'

    # When/ Then
    text_area.placeholder="b"
    assert text_area.html== '<wired-textarea placeholder="b"></wired-textarea>'

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

def test_toggle():
    # When/ Then
    toggle = wired.Toggle()
    assert toggle.html == "<wired-toggle></wired-toggle>"
    assert toggle.disabled == False


def test_view():
    js = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js"></script>
<script src="https://wiredjs.com/dist/showcase.min.js"></script>
"""
    show_html=True

    # https://wiredjs.com/dist/showcase.min.js
    # <script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.0.0/webcomponents-loader.js"></script>
    # https://wiredjs.com/dist/showcase.min.js
    # pn.config.js_files["webcomponents-loaded"]="https://unpkg.com/@webcomponents/webcomponentsjs@latest/webcomponents-loader.js"
    # pn.config.js_files["wired-button"]="https://unpkg.com/wired-button@1.0.0/lib/wired-button.js"

    js_pane = pn.pane.HTML(js)

    def section(component, message=None, show_html=show_html):
        title = "## " + str(type(component)).split(".")[3][:-2]

        parameters = list(component._child_parameters())
        if show_html:
            parameters = ["html"] + parameters

        if message:
            return (title, component, pn.Param(component, parameters=parameters), pn.pane.Markdown(message), pn.layout.Divider())
        return (title, component, pn.Param(component, parameters=parameters), pn.layout.Divider())

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
    progress = wired.Progress(value=50)
    wired_input = wired.Input()
    radio_button = wired.RadioButton()
    search_input = wired.SearchInput()
    spinner = wired.Spinner()
    slider = wired.Slider(html="""<wired-slider id="slider" value="33.1" knobradius="15" class="wired-rendered" style="margin: 0px">Slider Label</wired-slider>""")
    text_area = wired.TextArea()
    toggle = wired.Toggle()
    video = wired.Video(autoplay=True, loop=True, src="https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4")
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
        *section(progress),
        *section(radio_button),
        *section(search_input),
        *section(spinner),
        *section(slider, "Todo: Currently an error is raised because the slider value is not rounded to 1 decimal"),
        *section(text_area),
        *section(toggle),
        *section(video),
    )


if __name__.startswith("bk"):
    pn.config.sizing_mode = "stretch_width"
    test_view().servable()
