"""Implementation of the wired WebComponent"""
import param

from panel.models import WebComponent as _BkWebComponent
from panel.widgets.base import Widget
from typing import Set, Dict, Optional

from html.parser import HTMLParser
# Todo: For now i'm using lxml for . @Philipp should now if that is ok to add as a requirement
# or if we need to find another solution like regex or BeautifulSoup
import lxml.html as LH

# Todo: Systematically go through this parameter types and update this dictionary
PARAMETER_TYPE = {
    param.String: str,
    param.Integer: int,
    param.Number: float,
}


class AttributeParser(HTMLParser):
    first_tag: bool = True
    attr_dict: Optional[Dict] = None

    def handle_starttag(self, tag, attrs):
        if self.first_tag:
            for attr in attrs:
                self.attr_dict[attr[0]] = attr[1]
            self.first_tag = False


class WebComponent(Widget):
    """A Wired WebComponent

    Use the WebComponent by inheriting from it. An example would be

    ```
    class RadioButton(WebComponent):
    html = param.String('<wired-radio>Radio Two</wired-radio>')
    attributes_to_watch = param.Dict({"checked": "checked})

    checked = param.Boolean(default=False)
    ```

    - A Boolean parameter set to True like `checked=True` is in included as `checked` or `checked=""` in the html
    - A Boolean parameter set to False is not included in the html

    Please note

    - The html attributes in attributes_to_watch will be set to the corresponding parameter value
    on construction.
    """

    _rename = {"title": None, "html": "innerHTML", "attributes_to_watch": "attributesToWatch"}
    _widget_type = _BkWebComponent

    # Todo: Consider the right name: element, html, tag or ?
    # Todo: Right now a complex element like `<a><b></b></a><c></c>` is allowed and <a></a> is the component we observe changes to
    # consider if we should allow only simple/ single elements like `<a href="abcd"></a>`
    # Todo: Consider adding a regex
    html = param.String()
    # Todo: Consider the right name: attributes, attributes_to_watch, attributes_and_parameters
    attributes_to_watch = param.Dict(
        doc="""
    A dictionary of attributes and parameters

    - The attributes are the names of webcomponent to observe for changes on the client/ browser/ javascript side.
    - The parameters are the corresponding names of the parameters on the python side

    The attributes and parameters are automatically synchronized

    If an attribute key has a parameter value of None then the attribute is still observed and changes
    are update in the html parameter. But it is not synchronized to a parameter.

    Example:

    attributes_to_watch = {"checked": "checked", "value": None, "ballSize": "ball_size"}
    """
    )

    def __init__(self, **params):
        # Avoid AttributeError: unexpected attribute ...
        for parameter in self._child_parameters():
            self._rename[parameter] = None

        super().__init__(**params)

        self.parser: HTMLParser = AttributeParser()
        self.param.watch(self._update_parameters, ['html',])

        # Todo: Maybe setup watch of attributes_to_watch so that the below is updated if attributes_to_watch change
        # after construction
        if self.attributes_to_watch:
            parameters_to_watch = [value for value in self.attributes_to_watch.values() if value]
            self.param.watch(self._update_html, parameters_to_watch)

        self._update_html()

    def _child_parameters(self) -> Set:
        """Returns a set of any new parameters added on self compared to WebComponent.

        """
        return set(self.param.objects()) - set(WebComponent.param.objects())

    def parse_html_to_dict(self, html):
        self.parser.attr_dict = {}
        self.parser.first_tag = True
        self.parser.feed(html)
        return self.parser.attr_dict

    def _update_parameters(self, event):
        if not self.attributes_to_watch:
            return
        attr_dict = self.parse_html_to_dict(self.html)

        for attribute, parameter in self.attributes_to_watch.items():
            if parameter:
                self.update_parameter(parameter, attribute, attr_dict)

    def update_parameter(self, parameter: str, attribute: str, attr_dict: Dict):
        """Updates the parameter with the value of the html attribute

        Parameters
        ----------
        parameter : str
            A parameter name like 'checked' or 'ball_size'
        attribute : str
            An attribute name like 'checked' or 'ballSize'
        attr_dict : Dict
            A dictionary contained the parse attributes and attribute values of the html string

        Raises
        ------
        TypeError
            If we are trying to parse a non suppported type of parameter like param.Action.
            If this should be supported in your use case then you can define how by overriding
            this function
        """
        parameter_item = self.param[parameter]
        if isinstance(parameter_item, param.Boolean):
            self._update_boolean_parameter(attr_dict, attribute, parameter)
        elif type(parameter_item) in PARAMETER_TYPE:
            parameter_type = PARAMETER_TYPE[type(parameter_item)]
            self._update_parameter(attr_dict, attribute, parameter, parameter_type)
        else:
            # Todo: Find out if f strings are allowed in Panel
            raise TypeError(f"Parameter of type {type(parameter_item)} is not supported")

    def _update_boolean_parameter(self, attr_dict, attribute, parameter):
        parameter_value = getattr(self, parameter)
        if attribute in attr_dict:
            attr_value = attr_dict[attribute]
            # <a attribute=""></a> or <a attribute></a> is True
            if (attr_value=="" or not attr_value):
                new_parameter_value = True
            # <a></a> is False
            else:
                new_parameter_value = False
        else:
            new_parameter_value = False

        if new_parameter_value!=parameter_value:
            setattr(self, parameter, new_parameter_value)

    def _update_parameter(self, attr_dict, attribute, parameter, parameter_type):
        parameter_value = getattr(self, parameter)
        if attribute in attr_dict:
            attr_value = attr_dict[attribute]
            new_parameter_value = parameter_type(attr_value)
        else:
            new_parameter_value = self.param[parameter].default

        if new_parameter_value!=parameter_value:
            setattr(self, parameter, new_parameter_value)

    def _update_html(self, event=None):
        if not self.attributes_to_watch:
            return

        html = self.html
        root = LH.fromstring(html)
        for attribute, parameter in self.attributes_to_watch.items():
            if parameter:
                if event and event.name!=parameter:
                    next
                # if event and event.new == False:
                #     breakpoint()
                parameter_value = getattr(self, parameter)
                parameter_item = self.param[parameter]
                if isinstance(parameter_item, param.Boolean):
                    if parameter_value:
                        attribute_value = ""
                        root.set(attribute, attribute_value)
                    elif attribute in root.attrib:
                        del root.attrib[attribute]
                else:
                    attribute_value = str(parameter_value)
                    root.set(attribute, attribute_value)
        new_html = LH.tostring(root).decode("utf-8")
        # Todo: Find out if I need to check. I'm just afraid that this will trigger parameter update
        # and an infinite cycle will start
        if new_html != self.html:
            self.html = new_html
