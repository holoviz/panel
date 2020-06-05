"""Implementation of Material Components"""
import panel as pn
import param

from panel.widgets import WebComponent

from .config import FONTS_HTML, MWC_ICONS, MWC_JS

# pylint: disable=abstract-method

MWC_SLIDER_HTML = """
<mwc-slider
    step="5"
    pin
    markers
    max="50"
    value="10">
</mwc-slider>
"""


def fonts_pane():
    """HTML pane containing the `link` imports for the Roboto font and the Material Icons"""
    return pn.pane.HTML(FONTS_HTML, width=0, height=0, margin=0, sizing_mode="fixed")


class MWCButton(WebComponent):
    """Implementation of mwc-button

    Set the `name` to set the text shown to the user
    Set the `icon` to set the icon shown to the user

    Set `unelevated` or `raised` to change the style
    """

    html = param.String("<mwc-button style='width:100%'></mwc-button")
    attributes_to_watch = param.Dict(
        {"label": "name", "icon": "icon", "raised": "raised", "unelevated": "unelevated"}
    )

    unelevated = param.Boolean(default=True)
    raised = param.Boolean(default=False)
    icon = param.ObjectSelector(default=None, objects=MWC_ICONS, allow_None=True)

    height = param.Integer(default=30)

    # NEW IN THIS EXAMPLE
    events_to_watch = param.Dict({"click": "clicks"})
    clicks = param.Integer()


class MWCSelect(WebComponent):
    """Implementation of the mwc-select component

    The `value` is the value selected by the user. Can be None.
    The `options` are the options that can be selected by the user

    Set `outlined` to change the style
    """

    html = param.String("""<mwc-select style="width:100%"></mwc-select>""")
    attributes_to_watch = param.Dict({"label": "name", "outlined": "outlined"})
    properties_to_watch = param.Dict({"value": "_index"})
    events_to_watch = param.Dict(default={"selected": "selects"})
    parameters_to_watch = param.List(["options"])

    outlined = param.Boolean(default=False)

    def __init__(self, min_height=60, **params):
        super().__init__(min_height=min_height, **params)

        self._set_class_()

    value = param.Parameter()
    selects = param.Integer()
    options = param.ClassSelector(default=[], class_=(dict, list))
    _index = param.String()

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        options = params["options"]
        if not options:
            return """<mwc-select></mwc-select>"""

        innerhtml = []
        if isinstance(options, list):
            for index, obj in enumerate(options):
                if hasattr(obj, "name"):
                    value = obj.name
                else:
                    value = str(obj)
                item = f'<mwc-list-item value="{index}">{value}</mwc-list-item>'
                innerhtml.append(item)
        if isinstance(options, dict):
            for index, value in enumerate(options.values()):
                item = f'<mwc-list-item value="{index}">{str(value)}</mwc-list-item>'
                innerhtml.append(item)

        return f"""<mwc-select>{"".join(innerhtml)}</mwc-select>"""

    @param.depends("options", watch=True)
    def _set_class_(self):
        if isinstance(self.options, list):
            self.param.options.class_ = list
        if isinstance(self.options, dict):
            self.param.options.class_ = dict

    @param.depends("value", watch=True)
    def _update_index(self):
        # pylint: disable=unsupported-membership-test
        if isinstance(self.options, list) and self.value in self.options:
            self._index = str(self.options.index(self.value))
        elif isinstance(self.options, dict) and self.value in self.options:
            self._index = str(list(self.options).index(self.value))
        else:
            self._index = ""

    @param.depends("_index", watch=True)
    def _update_value(self):
        if self._index == "":
            self.value = None
        elif isinstance(self.options, list):
            self.value = self.options[int(self._index)]  # pylint: disable=unsubscriptable-object
        elif isinstance(self.options, dict):
            self.value = list(self.options)[int(self._index)]
        else:
            self.value = None


class MWCSlider(WebComponent):
    """Implementation of mwc-slider

    You can change the behaviour by changning the `bounds` and `step` value.
    """

    html = param.String(MWC_SLIDER_HTML)
    properties_to_watch = param.Dict({"value": "value"})

    value = param.Integer(default=10, bounds=(0, 50), step=5)
    height = param.Integer(default=50)
