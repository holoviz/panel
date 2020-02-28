from panel.pane import HTML
import param


class WebComponent(HTML):
    html = param.String("<wired-radio checked>Radio Two</wired-radio>")