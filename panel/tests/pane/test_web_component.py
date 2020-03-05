from panel.pane import WebComponent
import param
import pytest

@pytest.fixture
def html():
    return '<wired-radio id="1" string="" integer="0" number="0.0">Radio Two</wired-radio>'

@pytest.fixture
def CustomWebComponent(html):
    html_value = html # Hack
    class CustomWebComponent_(WebComponent):
        """Mockup used for testing"""
        html = param.String(html_value)
        attributes_to_watch = param.Dict({"boolean": "boolean", "string": "string", "integer": "integer", "number": "number"})

        boolean = param.Boolean()
        string = param.String()
        integer = param.Integer()
        number = param.Number()
        clicks = param.Integer()

    return CustomWebComponent_

@pytest.fixture
def attributes_to_watch():
    return {"boolean": "boolean"}

def test_constructor_base():
    # When
    component = WebComponent()
    # Then
    assert isinstance(component.attributes_to_watch, dict)
    assert isinstance(component.properties_to_watch, dict)
    assert isinstance(component.events_to_watch, dict)

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

def test_web_component(document, comm, html):
    web_component = WebComponent(html=html)

    # Create pane
    model = web_component.get_root(document, comm=comm)
    assert web_component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert model.innerHTML == html
    assert model.attributesToWatch == {}
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
    assert model.innerHTML == html

    # Cleanup
    web_component._cleanup(model)
    assert web_component._models == {}

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
    custom_web_component.html = '<wired-radio>Radio Two</wired-radio>'
    assert custom_web_component.boolean == False
    custom_web_component.html = '<wired-radio boolean>Radio Two</wired-radio>'
    assert custom_web_component.boolean == True
    custom_web_component.html = '<wired-radio>Radio Two</wired-radio>'
    assert custom_web_component.boolean == False
    custom_web_component.html = '<wired-radio boolean="">Radio Two</wired-radio>'
    assert custom_web_component.boolean == True

def test_update_parameters_string(CustomWebComponent):
    # When/ Then
    custom_web_component = CustomWebComponent(attributes_to_watch={"string": "string"})
    custom_web_component.html = '<a></a>'
    assert custom_web_component.string == ""
    custom_web_component.html = '<a string=""></a>'
    assert custom_web_component.string == ""
    custom_web_component.html = '<a string="b"></a>'
    assert custom_web_component.string == "b"
    custom_web_component.html = '<a></a>'
    assert custom_web_component.string == ""

def test_update_parameters_integer(CustomWebComponent):
    # When/ Then
    custom_web_component = CustomWebComponent(attributes_to_watch={"integer": "integer"})
    custom_web_component.html = '<a></a>'
    assert custom_web_component.integer == custom_web_component.param.integer.default
    custom_web_component.html = '<a integer=4></a>'
    assert custom_web_component.integer == 4
    custom_web_component.html = '<a></a>'
    assert custom_web_component.integer == custom_web_component.param.integer.default

def test_update_parameters_number(CustomWebComponent):
    # When/ Then
    custom_web_component = CustomWebComponent(attributes_to_watch={"number": "number"})
    custom_web_component.html = '<a></a>'
    assert custom_web_component.number == custom_web_component.param.integer.default
    custom_web_component.html = '<a number="4.1"></a>'
    assert custom_web_component.number == 4.1
    custom_web_component.html = '<a></a>'
    assert custom_web_component.number == custom_web_component.param.integer.default
    custom_web_component.html = '<a number="40.507407407407406"></a>'
    assert custom_web_component.number == 40.507407407407406

def test_update_not_supported_parameter_type():
    """watching a type of parameter that is not supported should raise n TypeError"""
    class Component(WebComponent):
        html = param.String("<a></a>")
        attributes_to_watch = param.Dict({"attribute": "parameter"})

        parameter = param.Action()

    with pytest.raises(TypeError):
        Component()

def test_parameter_change_triggers_attribute_change(CustomWebComponent):
    component = CustomWebComponent()

    component.boolean=True
    assert component.boolean==True
    assert component.html == '<wired-radio id="1" string="" integer="0" number="0.0" boolean="">Radio Two</wired-radio>'

    component.boolean=False
    assert component.boolean==False
    assert component.html == '<wired-radio id="1" string="" integer="0" number="0.0">Radio Two</wired-radio>'

    component.boolean=True
    component.string="a"
    component.integer=1
    component.number=1.1
    assert component.html == '<wired-radio id="1" string="a" integer="1" number="1.1" boolean="">Radio Two</wired-radio>'

def test_property_change_triggers_parameter_change(CustomWebComponent):
    # Given
    component = CustomWebComponent(attributes_to_watch={}, properties_to_watch={"boolean": "boolean"})

    # When/ Then
    component.properties_last_change = {"boolean": True}
    assert component.boolean == True
    component.properties_last_change = {"boolean": False}
    assert component.boolean == False
    component.properties_last_change = {"boolean": True}
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
    web_component.events_count_last_change = {"click": 2}
    # Then
    assert web_component.clicks == 2




