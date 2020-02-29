from panel.pane import WebComponent
import param
import pytest

@pytest.fixture
def html():
    return '<wired-radio checked id="1" checked>Radio Two</wired-radio>'

@pytest.fixture
def custom_web_component(html):
    html_value = html # Hack
    class RadioButton(WebComponent):
        """Mockup used for testing"""
        html = param.String(html_value)

        checked = param.Boolean(default=True)
    return RadioButton

@pytest.fixture
def attributes_to_sync():
    return {"checked": "checked"}


def test_constructor(html, attributes_to_sync):
    # When
    web_component = WebComponent(html=html, attributes_to_sync=attributes_to_sync)

    # Then
    web_component.html == html
    web_component.attributes_to_sync == attributes_to_sync

def test_web_component(document, comm, html, attributes_to_sync):
    web_component = WebComponent(html=html, attributes_to_sync = attributes_to_sync)

    # Create pane
    model = web_component.get_root(document, comm=comm)
    assert web_component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert model.innerHTML == html
    assert model.attributesTosync == attributes_to_sync

    # Cleanup
    web_component._cleanup(model)
    assert web_component._models == {}

def test_custom_web_component(document, comm, html, custom_web_component):
    """The custom parameter 'checked' should not raise an
    `AttributeError: unexpected attribute 'checked' to WebComponent, ...` exception"""
    web_component = custom_web_component()

    # Create pane
    model = web_component.get_root(document, comm=comm)
    assert web_component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert model.innerHTML == html

    # Cleanup
    web_component._cleanup(model)
    assert web_component._models == {}

@pytest.mark.parametrize(["html", "expected"], [
    ('<wired-radio checked id="1">Radio Two</wired-radio>', {"checked": None, "id": "1"}),
    ('<wired-radio id="2">Radio Two</wired-radio>', {"id": "2"}),
    ('<wired-radio checked id="3" checked>Radio Two</wired-radio>', {"checked": None, "id": "3"}),
    ('<wired-radio checked="" id="4">Radio Two</wired-radio>', {"checked": "", "id": "4"}),
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



