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
    param.ObjectSelector: str,
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

    _rename = {
        "title": None,
        "html": "innerHTML",
        "attributes_to_watch": "attributesToWatch",
        "properties_to_watch": "propertiesToWatch",
        "properties_last_change": "propertiesLastChange",
        "events_to_watch": "eventsToWatch",
        "events_count_last_change": "eventsCountLastChange",
        "parameters_to_watch": None,
    }
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
    properties_to_watch = param.Dict(
        doc="""
    The key is the name of the js property. The value is the name of the python parameter
    """
    )
    properties_last_change = param.Dict(
        doc="""

    The key is the name of the property changed. The value is the new value of the property
    """
    )
    parameters_to_watch = param.List(
        doc="""
        A list of parameters that the value of `html` depends before the value of the attributes
        specified in `attributes_to_watch` are applied.

        Only relevant for custom implementations that inherit from WebComponent.

        For example the wired.Fab has an `icon` parameter that defines the html of the web component as
        `<wired-fab><mwc-icon>{self.icon}</mwc-icon></wired-fab>`

        In order for this to work you need to define a custom implementation of
        `_get_html_from_parameters_to_watch`.
        """
    )
    events_to_watch = param.Dict(
        doc="""
    The key is the name of the js event. The value is the name of a python parameter to increment or None

    Use this if you want to support button clicks, mouseups etc.

    # Below is not implemented yet
    When the event is fired on the js side any changes to the html or properties_to_change will
    also be sent. Use this if you webcomponent don't fire the onchange event when your property changes
    """
    )
    events_count_last_change = param.Dict(
        doc="""
        Key is the name of the event, Value is the number of times it has fired in total
        """
    )

    def __init__(self, **params):
        # Avoid AttributeError: unexpected attribute ...
        for parameter in self._child_parameters():
            self._rename[parameter] = None

        # Todo: Could not get instantiate=False, constant=False working on parameters.
        # So I added the below
        if not self.param.attributes_to_watch.default:
            self.param.attributes_to_watch.default = {}
        if not self.param.properties_to_watch.default:
            self.param.properties_to_watch.default = {}
        if not self.param.events_to_watch.default:
            self.param.events_to_watch.default = {}
        if not self.param.parameters_to_watch.default:
            self.param.parameters_to_watch.default = {}
        else:
            params["html"]=self._get_initial_html_from_parameters_to_watch(**params)

        super().__init__(**params)

        self.parser: HTMLParser = AttributeParser()
        self.param.watch(self._update_parameters, ["html",])
        self.param.watch(self._handle_properties_last_change, ["properties_last_change",])
        self.param.watch(self._handle_events_count_last_change, ["events_count_last_change",])

        # Todo: Maybe setup watch of attributes_to_watch so that the below is updated if attributes_to_watch change
        # after construction
        if self.attributes_to_watch:
            parameters_to_watch = [value for value in self.attributes_to_watch.values() if value]
            self.param.watch(self._handle_attributes_to_watch_change, parameters_to_watch)

        if self.properties_to_watch:
            parameters_to_watch = list(self.properties_to_watch.values())
            self.param.watch(self._handle_parameter_property_change, parameters_to_watch)

        if self.parameters_to_watch:
            self.param.watch(self._handle_parameters_to_watch_change, list(self.parameters_to_watch))

        self._handle_attributes_to_watch_change()
        self._update_properties()

    def _handle_parameters_to_watch_change(self, event):
        params = {parameter: getattr(self, parameter) for parameter in self.parameters_to_watch}
        html = self._get_html_from_parameters_to_watch(**params)
        html = self._update_html_from_attributes_to_watch(html)
        if html!=self.html:
            self.html=html

    def _get_initial_html_from_parameters_to_watch(self, **params) -> str:
        """Returns the initial html value based on the specified params and
        paramaters_to_watch.

        Returns
        -------
        str
            The initial html to use
        """
        if "html" in params:
            return params["html"]
        if not self.parameters_to_watch:
            return self.param.html.default

        init_params = {}
        for parameter in self.parameters_to_watch:
            if params and parameter in params:
                init_params[parameter]=params[parameter]
            else:
                init_params[parameter]=self.param[parameter].default
        return self._get_html_from_parameters_to_watch(**init_params)

    def _get_html_from_parameters_to_watch(self, **params) -> str:
        """Returns the html value to use based on values of the parameters_to_watch specified

        This function should be overridden when implementing a child/ custom WebComponent class
        with non-empty list of paramaters_to_watch.

        For example the `wired.Fab` would
        return f"<wired-fab><mwc-icon>{params['icon']}</mwc-icon></wired-fab>"

        Returns
        -------
        str
            A html string like "<wired-fab><mwc-icon>favorite</mwc-icon></wired-fab>"

        Parameters
        ----------
            The parameter name is a parameter_to_watch and the value is its value
            for example icon="favorite"

        """
        raise NotImplementedError("You need to do a custom implementation of this because the parameters_to_watch list is not empty")

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
            if attr_value == "" or not attr_value:
                new_parameter_value = True
            # <a></a> is False
            else:
                new_parameter_value = False
        else:
            new_parameter_value = False

        if new_parameter_value != parameter_value:
            setattr(self, parameter, new_parameter_value)

    def _update_parameter(self, attr_dict, attribute, parameter, parameter_type):
        parameter_value = getattr(self, parameter)
        if attribute in attr_dict:
            attr_value = attr_dict[attribute]
            new_parameter_value = parameter_type(attr_value)
        else:
            new_parameter_value = self.param[parameter].default

        if new_parameter_value != parameter_value:
            setattr(self, parameter, new_parameter_value)

    def _update_html_from_attributes_to_watch(self, html: str) -> str:
        """Returns a html string with the attributes updated

        Parameters
        ----------
        html : str
            A html string like `<wired-link>link</wired-link>`

        Returns
        -------
        str
            A html string like `<wired-link href="www.google.com" target="_blank">link</wired-link>`
            based on the values of the attributes_to_watch
        """
        root = LH.fromstring(html)
        for attribute, parameter in self.attributes_to_watch.items():
            if parameter:
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
        html_update = LH.tostring(root).decode("utf-8")
        return html_update

    def _handle_attributes_to_watch_change(self, event=None):
        if not self.attributes_to_watch or not self.html:
            return

        html = self.html
        root = LH.fromstring(html)
        for attribute, parameter in self.attributes_to_watch.items():
            if parameter:
                if event and event.name != parameter:
                    continue
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

    def _handle_properties_last_change(self, event):
        print("_handle_properties_last_change")
        print(event)
        if not self.properties_to_watch or not event.new:  # or not isinstance(event.new, dict):
            return

        # Todo: If we can skip the check below at all or just put in try/ catch to speed up
        for property_, new_value in event.new.items():
            if not property_ in self.properties_to_watch:
                continue

            parameter = self.properties_to_watch[property_]

            parameter_item = self.param[parameter]
            if type(parameter_item) in PARAMETER_TYPE:
                parameter_type = PARAMETER_TYPE[type(parameter_item)]
                new_value = parameter_type(new_value)

            old_value = getattr(self, parameter)
            if old_value != new_value:
                setattr(self, parameter, new_value)

    def _handle_events_count_last_change(self, event):
        if not self.events_to_watch or not event.new:  # or not isinstance(event.new, dict):
            return

        # Todo: If we can skip the check below at all or just put in try/ catch to speed up
        for property_, new_value in event.new.items():
            if not property_ in self.events_to_watch:
                continue

            parameter = self.events_to_watch[property_]
            if not parameter:
                continue

            print(parameter)
            old_value = getattr(self, parameter)
            if old_value != new_value:
                setattr(self, parameter, new_value)

    def _handle_parameter_property_change(self, event):
        if not self.properties_to_watch:
            return

        parameters_to_properties = {v:k for k, v in self.properties_to_watch.items()}
        property_name = parameters_to_properties[event.name]

        change = {property_name: event.new}
        self.properties_last_change = change

    def _update_properties(self):
        if not self.properties_to_watch or not isinstance(self.properties_to_watch, dict):
            return

        change = {}
        for property_, parameter in self.properties_to_watch.items():
            value = getattr(self, parameter)
            change[property_] = value
        self.properties_last_change = change
