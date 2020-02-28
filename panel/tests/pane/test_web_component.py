from panel.pane import WebComponent
import param


def test_constructor():
    # When
    WebComponent()


def test_custom_web_component():
    class VaadinCheckBox(WebComponent):
        tag = param.String("vaadin-checkbox", constant=True)
        js = param.List(
            ["https://unpkg.com/@vaadin/vaadin-checkbox@2.2.2/vaadin-checkbox.js"], constant=True
        )

        attributes = param.List(["value", "checked"], constant=True)

        value = param.String("1")
        checked = param.Boolean(True)

