"""Test of the wired components"""
# pylint: disable=protected-access
import datetime as dt

import pandas as pd
import param
import pytest

import panel as pn
from panel.components import wired
from collections import OrderedDict


def test_base():
    base = wired.WiredBase()

    assert not base.disabled
    assert "disabled" in base._child_parameters()


def test_button_constructor():
    button = wired.Button()

    assert "disabled" in button.attributes_to_watch
    assert "elevation" in button.attributes_to_watch
    assert "name" in button.parameters_to_watch

    assert button.html.startswith("<wired-button")
    assert button.html.endswith("</wired-button>")
    assert 'elevation="0"' in button.html
    assert "disabled" not in button.html


def test_button_disabled():
    button = wired.Button()

    # When/Then
    button.disabled = True
    assert button.attributes_last_change == {"disabled": ""}
    button.update_html_from_attributes_to_watch()
    assert "disabled" in button.html

    # When/Then
    button.disabled = False
    assert button.attributes_last_change == {"disabled": None}
    button.update_html_from_attributes_to_watch()
    assert "disabled" not in button.html


def test_button_elevation():
    button = wired.Button()
    # When/Then: Elevation
    button.elevation = 1
    assert button.attributes_last_change == {"elevation": "1"}


def test_button_name():
    button = wired.Button()
    # When/ Then
    button.name = "Click Test"
    assert ">Click Test</wired-button" in button.html


@pytest.mark.parametrize(
    ["value", "expected"],
    [(dt.date(2020, 5, 3), "May 3, 2020"), (dt.date(2020, 5, 13), "May 13, 2020"),],
)
def test_datepicker_to_string(value, expected):
    assert wired.DatePicker._to_string(value) == expected


def test_datepicker():
    calendar = wired.DatePicker()

    calendar.selected = "Jul 4, 2019"
    assert calendar.value == dt.date(2019, 7, 4)

    calendar.value = dt.date(2020, 5, 3)
    assert calendar.selected == "May 3, 2020"

    calendar.firstdate = "Jul 14, 2019"
    assert calendar.start == dt.date(2019, 7, 14)

    calendar.start = dt.date(2020, 5, 13)
    assert calendar.firstdate == "May 13, 2020"

    calendar.lastdate = "May 31, 2021"
    assert calendar.end == dt.date(2021, 5, 31)

    calendar.end = dt.date(2021, 10, 28)
    assert calendar.lastdate == "Oct 28, 2021"


def test_checkbox():
    checkbox = wired.Checkbox(name="Test CheckBox")

    assert "disabled" in checkbox.attributes_to_watch
    assert checkbox.html.startswith("<wired-checkbox")
    assert checkbox.html.endswith("</wired-checkbox>")

    # When/Then
    checkbox.disabled = True
    assert checkbox.attributes_last_change == {"disabled": ""}
    checkbox.update_html_from_attributes_to_watch()
    assert "disabled" in checkbox.html

    # When/Then
    checkbox.disabled = False
    assert checkbox.attributes_last_change == {"disabled": None}
    checkbox.update_html_from_attributes_to_watch()
    assert "disabled" not in checkbox.html


def test_checkbox_constructor_checked():
    checkbox = wired.Checkbox(value=True)
    assert checkbox.properties_last_change == {"checked": True}


def test_checkbox_name():
    checkbox = wired.Checkbox()

    checkbox.name = "Testing"
    assert ">Testing<" in checkbox.html


def test_dialog():
    dialog = wired.Dialog(text="a")

    # When/ Then
    assert dialog.text == "a"
    assert dialog.html == "<wired-dialog>a</wired-dialog>"

    # When/ Then
    dialog.text = "b"
    assert dialog.html == "<wired-dialog>b</wired-dialog>"


def test_fab():
    fab = wired.Fab(icon="fast_rewind")

    # When/ Then
    assert fab.icon == "fast_rewind"
    assert fab.html == "<wired-fab><mwc-icon>fast_rewind</mwc-icon></wired-fab>"

    # When/ Then
    fab.icon = "favorite"
    assert fab.html == "<wired-fab><mwc-icon>favorite</mwc-icon></wired-fab>"


def test_icon_button():
    icon = wired.IconButton(icon="fast_rewind")

    # When/ Then
    assert icon.icon == "fast_rewind"
    assert icon.html == "<wired-icon-button><mwc-icon>fast_rewind</mwc-icon></wired-icon-button>"

    # When/ Then
    icon.icon = "favorite"
    assert icon.html == "<wired-icon-button><mwc-icon>favorite</mwc-icon></wired-icon-button>"


def test_float_slider():
    # When/ Then
    slider = wired.FloatSlider(attributes_to_watch={"value": "value"})
    slider.html = '<wired-slider id="slider" value="40.507407407407406" knobradius="15" class="wired-rendered" style="margin: 0px"></wired-slider>'
    assert slider.value == 40.507407407407406

def test_int_slider():
    # When/ Then
    slider = wired.IntSlider(attributes_to_watch={"value": "value"})
    slider.html = '<wired-slider id="slider" value="2" knobradius="15" class="wired-rendered" style="margin: 0px"></wired-slider>'
    assert slider.value == 2


def test_int_slider_properties_last_change():
    slider = wired.IntSlider()

    # When/ Then
    slider.properties_last_change = {"input.value": "13"}
    assert slider.value == 13

def test_float_slider_properties_last_change():
    slider = wired.FloatSlider()

    # When/ Then
    slider.properties_last_change = {"input.value": "13.7"}
    assert slider.value == 13.7


def test_input():
    # Given
    wired_input = wired.TextInput()

    # When/ Then
    wired_input.type_ = "password"
    assert wired_input.attributes_last_change == {"type": "password"}
    wired_input.update_html_from_attributes_to_watch()
    assert "password" in wired_input.html


def test_progress():
    progress = wired.Progress(value=4, max=9)

    # Then
    assert progress.value == 4
    assert progress.max == 9
    assert progress.param.value.bounds == (0, 9)

    # # When/ Then
    progress.max = 5
    assert progress.value == 4
    assert progress.max == 5
    assert progress.param.value.bounds == (0, 5)


def test_searchinput():
    # Given
    search = wired.SearchInput()
    # When/ Then
    search.placeholder = "New Search"
    assert search.attributes_last_change == {"placeholder": "New Search"}
    search.disabled = True
    assert search.attributes_last_change == {"disabled": ""}
    search.autocomplete = "on"
    assert search.attributes_last_change == {"autocomplete": "on"}
    search.update_html_from_attributes_to_watch()
    assert (
        search.html
        == '<wired-search-input placeholder="New Search" autocomplete="on" disabled></wired-search-input>'
    )

def test_select():
    """Supports dict."""
    options = OrderedDict([('red', 'red'), ('yellow', 'yellow'), ('green', 'green')])
    wired.Select(options=options)

def test_select_something():
    component = wired.Select(value="a", options=['a'])
    pn.Param(component, parameters=['options'])


def test_text_area():
    # When/ Then
    text_area = wired.TextAreaInput(placeholder="a", rows=3)
    assert text_area.html == '<wired-textarea placeholder="a"></wired-textarea>'

    # When/ Then
    text_area.placeholder = "b"
    assert text_area.attributes_last_change == {"placeholder": "b"}


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
    assert (
        wired_link.html
        == '<wired-link href="www.google.com" target="_blank">another link</wired-link>'
    )


def test_toggle():
    # When/ Then
    toggle = wired.Toggle()
    assert toggle.html == "<wired-toggle></wired-toggle>"
    assert toggle.disabled == False


def test_literal_input_value_from_client():
    # Given
    literal_input = wired.LiteralInput()
    # When
    literal_input.properties_last_change = {"textInput.value": "{'2': 2, 'b': 18}"}
    # Then
    assert literal_input.value == {"2": 2, "b": 18}


def test_literal_input_value_to_client():
    # Given
    literal_input = wired.LiteralInput()
    # When
    literal_input.value = {"2": 2, "b": 18}
    # Then
    assert literal_input.properties_last_change == {"textInput.value": "{'2': 2, 'b': 18}"}


def test_wired_view():
    js = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js"></script>
<script src="https://wiredjs.com/dist/showcase.min.js"></script>
"""
    show_html = True

    # https://wiredjs.com/dist/showcase.min.js
    # <script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.0.0/webcomponents-loader.js"></script>
    # https://wiredjs.com/dist/showcase.min.js
    # pn.config.js_files["webcomponents-loaded"]="https://unpkg.com/@webcomponents/webcomponentsjs@latest/webcomponents-loader.js"
    # pn.config.js_files["wired-button"]="https://unpkg.com/wired-button@1.0.0/lib/wired-button.js"

    js_pane = pn.pane.HTML(js)

    def section(component, message=None, show_html=show_html):
        title = "## " + str(type(component)).split(".")[3][:-2]

        parameterset = set(component._child_parameters())
        if show_html:
            parameterset.add("html")
        for parameter in component.parameters_to_watch:
            parameterset.add(parameter)

        parameters = list(parameterset)
        if message:
            return (
                title,
                component,
                pn.Param(component, parameters=parameters),
                pn.pane.Markdown(message),
                pn.layout.Divider(),
            )
        return (title, component, pn.Param(component, parameters=parameters), pn.layout.Divider())

    button = wired.Button()
    check_box = wired.Checkbox()
    check_box_checked = wired.Checkbox(value=True)
    date_picker = wired.DatePicker()
    dialog = wired.Dialog(text="Lorum Ipsum. Panel is awesome!")
    divider = wired.Divider()
    fab = wired.Fab()
    float_slider = wired.FloatSlider()
    icon_button = wired.IconButton()
    int_slider = wired.IntSlider()
    image = wired.Image(
        object="https://www.gstatic.com/webp/gallery/1.sm.jpg", height=200, width=300
    )
    link = wired.Link(href="https://panel.holoviz.org/", text="HoloViz", target="_blank")
    # literal_input = wired.LiteralInput(default={"a": 1, "b": "hello app world"})
    progress = wired.Progress(value=50)
    progress_spinner = wired.ProgressSpinner()
    radio_button = wired.RadioButton()
    search_input = wired.SearchInput()
    select = wired.Select(
        html="""<wired-combo id="colorCombo" selected="red" role="combobox" aria-haspopup="listbox" tabindex="0" class="wired-rendered" aria-expanded="false"><wired-item value="red" aria-selected="true" role="option" class="wired-rendered">Red</wired-item><wired-item value="green" role="option" class="wired-rendered">Green</wired-item><wired-item value="blue" role="option" class="wired-rendered">Blue</wired-item></wired-combo>"""
    )
    # @Philippfr: How do I avoid the the pn.Param(slider, parameters=["value"]) to turn red when
    # using the slider? It seems the value needs to be rounded?
    text_area = wired.TextAreaInput()
    text_input = wired.TextInput()
    toggle = wired.Toggle()
    video = wired.Video(
        autoplay=True,
        loop=True,
        object="https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4",
    )
    section(select)
    return pn.Column(
        js_pane,
        *section(button),
        *section(check_box),
        *section(check_box_checked),
        *section(date_picker, "@Philippfr: I get a ValueError: Parameter 'value' only takes numeric values when selecting a date"),
        *section(dialog, "@Philippfr: How do I add a close button and size the Dialog."),
        *section(divider),
        *section(fab),
        *section(
            float_slider,
            "@Philippfr: Currently an error is raised because the slider value is not rounded to 1 decimal",
        ),
        *section(icon_button),
        *section(image),
        *section(int_slider,),
        *section(
            link,
            "Normally you would just use the `<wired-link>` tag directly in your html or markdown text",
        ),
        # Todo: Fix AssertionError
        # *section(literal_input),
        *section(progress),
        *section(radio_button),
        *section(search_input, "@Philippfr. I cannot catch when the user clicks the x and clears the value"),
        *section(select),
        *section(progress_spinner),
        *section(text_area),
        *section(text_input),
        *section(toggle),
        *section(video),
        name = "Wired View",
    )


def test_param_view():
    js = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js"></script>
<script src="https://wiredjs.com/dist/showcase.min.js"></script>
"""
    js_pane = pn.pane.HTML(js)

    class BaseClass(param.Parameterized):
        x = param.Parameter(default=3.14, doc="X position")
        y = param.Parameter(default="Not editable", constant=True)
        string_value = param.String(default="str", doc="A string")
        num_int = param.Integer(50000, bounds=(-200, 100000))
        unbounded_int = param.Integer(23)
        float_with_hard_bounds = param.Number(8.2, bounds=(7.5, 10))
        float_with_soft_bounds = param.Number(0.5, bounds=(0, None), softbounds=(0, 2))
        unbounded_float = param.Number(30.01, precedence=0)
        hidden_parameter = param.Number(2.718, precedence=-1)
        integer_range = param.Range(default=(3, 7), bounds=(0, 10))
        float_range = param.Range(default=(0, 1.57), bounds=(0, 3.145))
        dictionary = param.Dict(default={"a": 2, "b": 9})

    class Example(BaseClass):
        """An example Parameterized class"""

        timestamps = []

        boolean = param.Boolean(True, doc="A sample Boolean parameter")
        color = param.Color(default="#FFFFFF")
        date = param.Date(
            dt.datetime(2017, 1, 1), bounds=(dt.datetime(2017, 1, 1), dt.datetime(2017, 2, 1))
        )
        dataframe = param.DataFrame(pd.util.testing.makeDataFrame().iloc[:3])
        select_string = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
        select_fn = param.ObjectSelector(default=list, objects=[list, set, dict])
        int_list = param.ListSelector(default=[3, 5], objects=[1, 3, 5, 7, 9], precedence=0.5)
        single_file = param.FileSelector(path="../../*/*.py*", precedence=0.5)
        multiple_files = param.MultiFileSelector(path="../../*/*.py?", precedence=0.5)
        record_timestamp = param.Action(
            lambda x: x.timestamps.append(dt.datetime.utcnow()),
            doc="""Record timestamp.""",
            precedence=0.7,
        )

    base = Example()
    parameters = [
        "x",
        "y",
        "string_value",
        "num_int",
        "unbounded_int", # Todo: Add Feature Request for unbounded int to Wired
        "float_with_hard_bounds",
        "float_with_soft_bounds",
        "unbounded_float", # Todo: Add Feature Request for unbounded int to
        "hidden_parameter",
        # "integer_range",  # Todo: Add Feature Request for Integer Range to Wired
        # "float_range",  # Todo: Add Feature Request for Float Range to Wired
        "dictionary",
        "boolean",
        # "color", # Todo: Add Feature Request for Color Picker to Wired
        "date",
        # "dataframe", # Todo: Add Feature Request for Table to Wired
        "select_string",
    ]
    widgets = {
        # Todo: Implement spinner to support Numbers
        # "x": wired.TextInput,  # Todo: Find out why value is not shown on construction
        "y": wired.TextInput,  # Todo: Find out why value is not shown on construction
        "string_value": wired.TextInput,  # Todo: Find out why value is not shown on construction
        "num_int": wired.IntSlider,  # Todo: Add value to label
        "unbounded_int": wired.TextInput,  # Todo: Find out why unbounded_int does not use TextInput
        "float_with_hard_bounds": wired.FloatSlider,  # Todo: Add value to label
        "float_with_soft_bounds": wired.FloatSlider,  # Todo: Add value to label
        "unbounded_float": wired.TextInput,  # Todo: Find out why unbounded_int does not use TextInput
        "dictionary": wired.LiteralInput,
        "boolean": wired.Checkbox,
        "date": wired.DatePicker,
        "select_string": wired.Select,
    }
    pn.Param(base, parameters=parameters, widgets=widgets)
    # @Philippfr: how do I get wired widgets to stretch_width automatically?
    return pn.Column(
        js_pane,
        pn.Row(
            pn.Param(base, parameters=parameters),
            pn.Param(base, parameters=parameters, widgets=widgets),
        ),
        name = "Param View",
    )


if __name__.startswith("bk"):
    # import ptvsd
    # ptvsd.enable_attach(address=('localhost', 5678))
    # print('Ready to attach the VS Code debugger')
    # ptvsd.wait_for_attach() # Only include this line if you always wan't to attach the debugger

    pn.config.sizing_mode = "stretch_width"
    wired_view = test_wired_view()
    param_view = test_param_view()
    app = pn.layout.Tabs(
        wired_view,
        param_view
        )
    app.servable()
