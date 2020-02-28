from panel.pane import HTML
import param


class WebComponent(HTML):
    tag = param.String("vaadin-checkbox", constant=True)
    js = param.List(constant=True)
    attributes = param.List(constant=True)