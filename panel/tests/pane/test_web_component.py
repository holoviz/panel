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


def test_constructor(html):
    # When
    web_component = WebComponent(html=html)

    # Then
    web_component.html == html

def test_web_component(document, comm, html):
    web_component = WebComponent(html=html)

    # Create pane
    model = web_component.get_root(document, comm=comm)
    assert web_component._models[model.ref['id']][0] is model
    assert type(model).__name__ == 'WebComponent'
    assert model.innerHTML == html

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


