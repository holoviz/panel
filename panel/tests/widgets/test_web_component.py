from html import unescape 

import pandas as pd
import param
import pytest

from bokeh.models import ColumnDataSource

from panel.widgets.web_component import WebComponent, PARAMETER_TYPE


@pytest.fixture
def html():
    return '<wired-radio id="1" string="" integer="0" number="0.0">Radio Two</wired-radio>'

@pytest.fixture
def CustomWebComponent(html):
    html_value = html # Hack
    class CustomWebComponent_(WebComponent):
        """Mockup used for testing"""
        html = param.String(html_value)
        attributes_to_watch = param.Dict({"boolean": "boolean", "string": "string", "integer": "integer", "number": "number", "list": "list_", "dict": "dict_"})

        boolean = param.Boolean()
        string = param.String()
        integer = param.Integer()
        number = param.Number()
        list_ = param.List(default=None)
        dict_ = param.Dict(default=None)
        clicks = param.Integer()

    return CustomWebComponent_

@pytest.fixture
def attributes_to_watch():
    return {"boolean": "boolean"}

def test_constructor_base():
    # When
    component = WebComponent()
    # Then
    assert hasattr(component, "html")
    assert isinstance(component.attributes_to_watch, dict)
    assert hasattr(component, "attributes_last_change")
    assert isinstance(component.properties_to_watch, dict)
    assert hasattr(component, "properties_last_change")
    assert isinstance(component.events_to_watch, dict)
    assert hasattr(component, "column_data_source")
    assert component.column_data_source_orient == "dict"
    assert hasattr(component, "column_data_source_load_function")

def test_constructor(CustomWebComponent, html, attributes_to_watch):
    # When
    component = CustomWebComponent(html=html, attributes_to_watch=attributes_to_watch)

    # Then
    assert component.html == html
    assert component.attributes_to_watch == attributes_to_watch

def test_constructor_with_parameter_values(CustomWebComponent):
    """I think it most natural that the parameter values takes precedence over attribute values"""
    # Given
    html = '<a></a>'
    boolean= True
    string = "s"
    integer = 1
    number = 1.1

    # When
    component = CustomWebComponent(html=html, boolean=boolean, string=string, integer=integer, number=number)

    # Then
    assert component.string == string
    assert component.html == '<a boolean="" string="s" integer="1" number="1.1"></a>'

def test_bokeh_model(document, comm, html):
    # Given
    web_component = WebComponent(html=html, column_data_source_load_function="load")

    # When
    model = web_component.get_root(document, comm=comm)
    # Then
    assert web_component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert unescape(model.innerHTML) == html
    assert model.attributesToWatch == {}

    assert hasattr(model, "columnDataSource")
    assert model.columnDataSourceOrient == "dict"
    assert model.columnDataSourceLoadFunction == "load"
    # Cleanup
    web_component._cleanup(model)
    assert web_component._models == {}

def test_custom_web_component(document, comm, html, CustomWebComponent):
    """The custom parameter 'boolean' should not raise an
    `AttributeError: unexpected attribute 'boolean' to WebComponent, ...` exception"""
    web_component = CustomWebComponent()

    # Create pane
    model = web_component.get_root(document, comm=comm)
    assert web_component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert unescape(model.innerHTML) == html

    # Cleanup
    web_component._cleanup(model)
    assert web_component._models == {}

def test_web_component_parameter_attribute_change(document, comm, CustomWebComponent):
    # Given
    component = CustomWebComponent(
        html = "<div></div>",
        attributes_to_watch = {"boolean": "boolean", "string": "string", "integer": "integer", "number": "number", "list": "list_"},
    )

    # When/ Then
    model = component.get_root(document, comm=comm)
    assert component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert unescape(model.innerHTML) == '<div string="" integer="0" number="0.0"></div>'
    assert model.attributesToWatch == {"boolean": "boolean", "string": "string", "integer": "integer", "number": "number", "list": "list_"}
    assert model.attributesLastChange == {}

    # When/ Then
    component.boolean = True
    assert model.attributesLastChange == {"boolean": ""}
    assert component.boolean == True

    component.boolean = False
    assert model.attributesLastChange == {"boolean": None}
    assert component.boolean == False

    component.string = "a"
    assert model.attributesLastChange == {"string": "a"}
    assert component.string == "a"

    component.integer = 1
    assert model.attributesLastChange == {"integer": "1"}
    assert component.integer == 1

    component.number = 2.1
    assert model.attributesLastChange == {"number": "2.1"}
    assert component.number == 2.1

    component.list_ = ["x", "y"]
    assert model.attributesLastChange == {"list": '["x","y"]'} # Note compact json dump
    assert component.list_ == ["x", "y"]

    component.list_ = []
    assert model.attributesLastChange == {"list": "[]"}
    assert component.list_ == []

    component.list_ = None
    assert model.attributesLastChange == {"list": None}
    assert component.list_ == None

    # Cleanup
    component._cleanup(model)
    assert component._models == {}

def test_custom_web_component_attributes_comm(document, comm):
    # Given
    class Component(WebComponent):
        """Mockup used for testing"""
        html = param.String("<div></div>")
        attributes_to_watch = param.Dict({"baram1": "param1"})

        param1 = param.String("")
    component = Component()

    # When/ Then
    model = component.get_root(document, comm=comm)
    assert component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert unescape(model.innerHTML) == '<div baram1=""></div>'
    assert model.attributesToWatch == {"baram1": "param1"}
    assert model.attributesLastChange == {}

    # When/ Then
    component.attributes_last_change = {"param1": "a"}
    assert model.attributesLastChange == {"param1": "a"}

    # When/ Then
    # @Philippfr: I would like to test communication from Bokeh model to Panel model
    # How do I do that? An example test is the below that fails.
    model.attributesLastChange = {"param1": "b"}
    assert component.attributes_last_change == {"param1": "b"}

    # Cleanup
    component._cleanup(model)
    assert component._models == {}

def test_attributes_last_change_change_to_none(document, comm, CustomWebComponent):
    # Given
    component = CustomWebComponent(
        html = "<div></div>",
    )

    component.param.boolean.default=True
    component.param.boolean.allow_None=False
    component.param.string.default="a"
    component.param.string.allow_None=False
    component.param.integer.default=10
    component.param.integer.allow_None=False
    component.param.number.default=12.1
    component.param.number.allow_None=False
    component.param.list_.default=["x"]
    component.param.list_.allow_None=False
    component.param.dict_.default={"x": "y"}
    component.param.dict_.allow_None=False

    assert component.boolean !=  component.param.boolean.default
    assert component.string !=  component.param.string.default
    assert component.integer !=  component.param.integer.default
    assert component.number !=  component.param.number.default
    assert component.list_ !=  component.param.list_.default
    assert component.dict_ !=  component.param.dict_.default

    # When
    component._process_events({'attributes_last_change': {
        "boolean": None,
        "string": None,
        "integer": None,
        "number": None,
        "list": None,
        "dict": None,
    }})
    # Then
    assert component.boolean ==  True
    assert component.string ==  component.param.string.default
    assert component.integer ==  component.param.integer.default
    assert component.number ==  component.param.number.default
    assert component.list_ ==  component.param.list_.default
    assert component.dict_ ==  component.param.dict_.default


def test_custom_web_component_properties_comm(document, comm):
    # Given
    class Component(WebComponent):
        """Mockup used for testing"""
        html = param.String("<div></div>")
        properties_to_watch = param.Dict({"baram1": "param1"})

        param1 = param.String()
    component = Component()

    # When/ Then
    model = component.get_root(document, comm=comm)
    assert component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert unescape(model.innerHTML) == '<div></div>'
    assert model.propertiesToWatch == {"baram1": "param1"}
    assert model.propertiesLastChange == {"baram1": ""}

    # When/ Then
    component.properties_last_change = {"param1": "a"}
    assert model.propertiesLastChange == {"param1": "a"}

    # When/ Then
    model.propertiesLastChange = {"param1": "a"}
    assert component.properties_last_change == {"param1": "a"}

    # Cleanup
    component._cleanup(model)
    assert component._models == {}

@pytest.mark.parametrize(["html", "expected"], [
    ('<wired-radio boolean id="1">Radio Two</wired-radio>', {"boolean": None, "id": "1"}),
    ('<wired-radio id="2">Radio Two</wired-radio>', {"id": "2"}),
    ('<wired-radio boolean id="3" boolean>Radio Two</wired-radio>', {"boolean": None, "id": "3"}),
    ('<wired-radio boolean="" id="4">Radio Two</wired-radio>', {"boolean": "", "id": "4"}),
    ('<a id="5"><b src="x"></b></a>', {"id": "5"}),
    ('<a id="6"></a><b src="y"></b>', {"id": "6"}),
])
def test_parse_html_to_dict(html, expected):
    # When
    result = WebComponent().parse_html_to_dict(html)
    # Then
    assert result == expected

# @pytest.mark.parametrize(["value", "parameter", "expected"], [
#     (None, param.Boolean(), True),
#     ("", param.Boolean(), True),
# ])

def test_update_parameters_boolean(CustomWebComponent):
    # When/ Then
    custom_web_component = CustomWebComponent(attributes_to_watch={"boolean": "boolean"})
    custom_web_component._process_events({'html': '<wired-radio>Radio Two</wired-radio>'})
    assert custom_web_component.boolean == False
    custom_web_component._process_events({'html': '<wired-radio boolean>Radio Two</wired-radio>'})
    assert custom_web_component.boolean == True
    custom_web_component._process_events({'html': '<wired-radio>Radio Two</wired-radio>'})
    assert custom_web_component.boolean == False
    custom_web_component._process_events({'html': '<wired-radio boolean="">Radio Two</wired-radio>'})
    assert custom_web_component.boolean == True

def test_update_parameters_string(CustomWebComponent):
    # When/ Then
    custom_web_component = CustomWebComponent(attributes_to_watch={"string": "string"})
    custom_web_component._process_events({"html": '<a></a>'})
    assert custom_web_component.string == ""
    custom_web_component._process_events({"html": '<a string=""></a>'})
    assert custom_web_component.string == ""
    custom_web_component._process_events({"html": '<a string="b"></a>'})
    assert custom_web_component.string == "b"
    custom_web_component._process_events({"html": '<a></a>'})
    assert custom_web_component.string == ""

def test_update_parameters_integer(CustomWebComponent):
    # When/ Then
    custom_web_component = CustomWebComponent(attributes_to_watch={"integer": "integer"})
    custom_web_component._process_events({"html": '<a></a>'})
    assert custom_web_component.integer == custom_web_component.param.integer.default
    custom_web_component._process_events({"html": '<a integer=4></a>'})
    assert custom_web_component.integer == 4
    custom_web_component._process_events({"html": '<a></a>'})
    assert custom_web_component.integer == custom_web_component.param.integer.default

def test_update_parameters_number(CustomWebComponent):
    # When/ Then
    custom_web_component = CustomWebComponent(attributes_to_watch={"number": "number"})
    custom_web_component.html = '<a></a>'
    assert custom_web_component.number == custom_web_component.param.integer.default
    custom_web_component._process_events({"html": '<a number="4.1"></a>'}) 
    assert custom_web_component.number == 4.1
    custom_web_component._process_events({"html": '<a"></a>'})
    assert custom_web_component.number == custom_web_component.param.integer.default
    custom_web_component._process_events({"html": '<a number="40.507407407407406"></a>'})
    assert custom_web_component.number == 40.507407407407406

def test_update_parameters_list():
    class Component(WebComponent):
        html = param.String("<a></a>")
        attributes_to_watch = param.Dict({"attrib1": "param1"})

        param1 = param.List(None)

    # When/ Then
    component = Component()
    assert component.html == '<a></a>'

    component.param1 = ["x"]
    assert component.html == '<a></a>' # We don't update the html because it would send it to client

    component.param1 = []
    assert component.html == '<a></a>' # We don't update the html because it would send it to client


def test_parameter_change_to_attribute_change(CustomWebComponent):
    component = CustomWebComponent()
    html = component.html

    component.boolean=True
    assert component.html == html
    assert component.attributes_last_change == {"boolean": ""}
    component.update_html_from_attributes_to_watch()
    html = '<wired-radio id="1" string="" integer="0" number="0.0" boolean="">Radio Two</wired-radio>'
    assert component.html == html


    component.boolean=False
    assert component.html == html
    assert component.attributes_last_change == {"boolean": None}
    component.update_html_from_attributes_to_watch()
    html = '<wired-radio id="1" string="" integer="0" number="0.0">Radio Two</wired-radio>'
    assert component.html == html

    component.boolean=True
    component.string="a"
    component.integer=1
    component.number=1.1
    assert component.html == html
    assert component.attributes_last_change == {"number": "1.1"}
    component.update_html_from_attributes_to_watch()
    html = '<wired-radio id="1" string="a" integer="1" number="1.1" boolean="">Radio Two</wired-radio>'
    assert component.html == html

def test_property_change_triggers_parameter_change(CustomWebComponent):
    # Given
    component = CustomWebComponent(attributes_to_watch={}, properties_to_watch={"boolean": "boolean"})

    # When/ Then
    component._process_events({"boolean": True})
    assert component.boolean == True
    component._process_events({"boolean": False})
    assert component.boolean == False
    component._process_events({"boolean": True})
    assert component.boolean == True

def test_parameter_change_triggers_property_change(CustomWebComponent):
    # Given
    component = CustomWebComponent(
        attributes_to_watch={},
        properties_to_watch={"boolean": "boolean", "string": "string", "integer": "integer", "number": "number"})

    # When/ Then
    component.boolean = True
    assert component.properties_last_change == {"boolean": True}
    component.boolean = False
    assert component.properties_last_change == {"boolean": False}
    component.boolean = True
    assert component.properties_last_change == {"boolean": True}
    component.string = "a"
    assert component.properties_last_change == {"string": "a"}
    component.integer = 1
    assert component.properties_last_change == {"integer": 1}
    component.number = 1.1
    assert component.properties_last_change == {"number": 1.1}

def test_events_count_last_change_triggers_parameter_update(CustomWebComponent):
    # Given
    web_component = CustomWebComponent(events_to_watch={"click": "clicks"})
    # When
    web_component._process_events({"clicks": 2})
    # Then
    assert web_component.clicks == 2

def test_parameters_to_watch():
    # Given
    class CustomComponent(WebComponent):
        parameters_to_watch = param.List(["param1", "param2"])
        param1 = param.String()
        param2 = param.String()

        def _get_html_from_parameters_to_watch(self, **params) -> str:
            return f"<span>{params['param1']},{params['param2']}</span>"

    # When/ Then
    component = CustomComponent(param1="a", param2="b")
    assert component.param1=="a"
    assert component.param2=="b"
    assert component.html=="<span>a,b</span>"

    # When/ Then
    component.param1 = "c"
    assert component.html=="<span>c,b</span>"

    # When/ Then
    component = CustomComponent(param1="d")
    assert component.html=="<span>d,</span>"

def test_parameters_and_attributes_to_watch():
    # Given
    class CustomComponent(WebComponent):
        attributes_to_watch = param.Dict({"attrib1": "attrib1"})
        parameters_to_watch = param.List(["param1"])
        attrib1 = param.String()
        param1 = param.String()

        def _get_html_from_parameters_to_watch(self, **params) -> str:
            return f"<span>{params['param1']}</span>"

    # When/ Then
    component = CustomComponent(attrib1="a", param1="b")
    assert component.attrib1=="a"
    assert component.param1=="b"
    assert component.html=='<span attrib1="a">b</span>'

    # When/ Then
    component.param1 = "c"
    assert component.attrib1=="a"
    assert component.param1=="c"
    assert component.html=='<span attrib1="a">c</span>'

    # When/ Then
    component.attrib1 = "d"
    assert component.attrib1=="d"
    assert component.attributes_last_change == {"attrib1": "d"}
    assert component.html=='<span attrib1="a">c</span>'
    component.update_html_from_attributes_to_watch()
    assert component.html=='<span attrib1="d">c</span>'

def test_handle_attributes_to_watch_change_on_html_with_leading_new_line_and_spaces():
    # Given
    class Custom(WebComponent):
        html = param.String(
            """
        <perspective-viewer id="view1" class='perspective-viewer-material-dark' style="height:100%;width:100%"></perspective-viewer>
        <script>
        var data = [
            { x: 1, y: "a", z: true },
            { x: 2, y: "b", z: false },
            { x: 3, y: "c", z: true },
            { x: 4, y: "d", z: false }
        ];

        console.log(document.currentScript);
        var viewer = document.getElementById("view1");
        viewer.load(data);

        </script>
        """
        )
        attributes_to_watch = param.Dict({"class": "theme"})

        theme = param.String("perspective-viewer-material")
    # When
    component = Custom()
    # Then
    assert component.html.startswith("""<perspective-viewer id="view1" class="perspective-viewer-material" style="height:100%;width:100%"></perspective-viewer>""")

def test_handle_attributes_to_watch_change_simple():
    # Given
    class Custom(WebComponent):
        html = param.String(
            """
            <perspective-viewer id="view1" class="perspective-viewer-material-dark" style="height:100%;width:100%"></perspective-viewer>
            """
        )
        attributes_to_watch = param.Dict({"class": "theme"})

        theme = param.String("perspective-viewer-material")
    # When
    component = Custom()
    # Then
    assert component.html.startswith('<perspective-viewer id="view1" class="perspective-viewer-material" style="height:100%;width:100%"></perspective-viewer>')

def test_data():
    # Given
    data = [
        { "x": 1, "y": "a", "z": True },
        { "x": 2, "y": "b", "z": False },
        { "x": 3, "y": "c", "z": True },
        { "x": 4, "y": "d", "z": False }
    ]
    dataframe = pd.DataFrame(data)
    cds = ColumnDataSource(dataframe)
    # When
    component = WebComponent(html="<div></div>", column_data_source=cds)
    # Then
    assert component.column_data_source == cds
def test_parameter_type_dict():
    perspective_columns_attribute = "['x']"
    assert ["x"]==PARAMETER_TYPE[param.List](perspective_columns_attribute)


if __name__.startswith("bk"):
    import panel as pn
    class Component_(WebComponent):
        """Mockup used for testing"""
        html = param.String("<span>My Component</span>")
        attributes_to_watch = param.Dict({"boolean": "boolean", "string": "string", "integer": "integer", "number": "number", "list": "list_"})

        boolean = param.Boolean()
        string = param.String()
        integer = param.Integer()
        number = param.Number()
        list_ = param.List()

    def section(component, message=None, show_html=True):
        title = "## " + str(type(component))

        parameters = list(component._child_parameters())
        if show_html:
            parameters = ["html"] + parameters

        if message:
            return (
                title,
                component,
                pn.Param(component, parameters=parameters),
                pn.pane.Markdown(message),
                pn.layout.Divider(),
            )
        return (title, component, pn.Param(component, parameters=parameters), pn.layout.Divider())

    component=Component_()
    pn.Column(*section(component)).servable()
