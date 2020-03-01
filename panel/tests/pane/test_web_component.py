from panel.pane import WebComponent
import param
import pytest

@pytest.fixture
def html():
    return '<wired-radio boolean id="1">Radio Two</wired-radio>'

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

    return CustomWebComponent_

@pytest.fixture
def attributes_to_watch():
    return {"boolean": "boolean"}


def test_constructor(html, attributes_to_watch):
    # When
    web_component = WebComponent(html=html, attributes_to_watch=attributes_to_watch)

    # Then
    web_component.html == html
    web_component.attributes_to_watch == attributes_to_watch

def test_web_component(document, comm, html, attributes_to_watch):
    web_component = WebComponent(html=html, attributes_to_watch = attributes_to_watch)

    # Create pane
    model = web_component.get_root(document, comm=comm)
    assert web_component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert model.innerHTML == html
    assert model.attributesToWatch == attributes_to_watch

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

def test_update_not_supported_parameter_type():
    """updating an unsupported type of parameter should raise an TypeError"""
    class Component(WebComponent):
        """Mockup used for testing"""
        html = param.String("<a></a>")
        attributes_to_watch = param.Dict({"attribute": "parameter"})

        parameter = param.Action()

    component = Component()
    with pytest.raises(TypeError):
        component.html = "<a attribute=""></a>"
