"""Implementation of the wired WebComponent"""
import param

from panel.models import WebComponent as _BkWebComponent
from panel.widgets.base import Widget
from typing import Set, Dict, Optional
import json
from html.parser import HTMLParser
from bokeh.models import ColumnDataSource

# Todo: For now i'm using lxml for . @Philipp should now if that is ok to add as a requirement
# or if we need to find another solution like regex or similar
import lxml.html as LH
import ast

# Defines how to convert from attribute string value to parameter value
PARAMETER_TYPE = {
    param.String: str,
    param.Integer: int,
    param.Number: float,
    param.ObjectSelector: str,
    param.List: ast.literal_eval,
    param.Dict: ast.literal_eval,
}


class AttributeParser(HTMLParser):
    """Used to parse a the WebComponent html string to a dictionary of attribute keys and
    their values"""
    first_tag: bool = True
    attr_dict: Optional[Dict] = None

    def handle_starttag(self, tag, attrs):
        if self.first_tag:
            for attr in attrs:
                self.attr_dict[attr[0]] = attr[1]
            self.first_tag = False


class WebComponent(Widget):
    """
    WebComponent
    ============

    Use the WebComponent to quickly plugin webcomponents and/ or Javascript libraries not already
    supported in Panel.

    You can use it by instantiating an instance or inheriting from it.

    Parameters
    ----------

    - The parameters listed in `attributes_to_watch` will be used to set the corresponding
    `html` element attributes on construction.
    - The parameters listed in `properties_to_watch` will be used to set the corresponding
    `html` element properties on construction.

    Example
    -------

    ```
    class RadioButton(WebComponent):
        html = param.String('<wired-radio>Radio Two</wired-radio>')
        attributes_to_watch = param.Dict({"checked": "checked})

        checked = param.Boolean(default=False)
    ```

    - A Boolean parameter set to True like `checked=True` is in included as `checked=""` in the html
    - A Boolean parameter set to False is not included in the html

    Additional Resources
    --------------------

    - Examples in the Panel Reference Gallery
    - Source code for Wired widgets
    - Source code for Perspective widgets
    """

    _rename = {
        "title": None,
        "html": "innerHTML",
        "attributes_to_watch": "attributesToWatch",
        "attributes_last_change": "attributesLastChange",
        "properties_to_watch": "propertiesToWatch",
        "properties_last_change": "propertiesLastChange",
        "events_to_watch": "eventsToWatch",
        "events_count_last_change": "eventsCountLastChange",
        "parameters_to_watch": None,
        "column_data_source": "columnDataSource",
        "column_data_source_orient": "columnDataSourceOrient",
        "column_data_source_load_function": "columnDataSourceLoadFunction",

    }
    _widget_type = _BkWebComponent

    # Todo: Consider adding a regex
    html = param.String()
    # Todo: Can we enforce that this is Dict[str, Optional[str]]?
    attributes_to_watch = param.Dict(
        doc="""
    A dictionary of attributes and parameters

    - The attributes are the names of webcomponent to observe for changes on the client/ browser/ javascript side.
    - The parameters are the corresponding names of the parameters on the python side

    The attributes and parameters are automatically synchronized

    If an attribute key has a parameter value of None then the attribute is still observed and changes
    are update in the html parameter. But it is not synchronized to a parameter.

    DO NOT CHANGE AFTER CONSTRUCTION OF THE OBJECT!

    Example
    ~~~~~~~

    `attributes_to_watch = {"checked": "checked", "value": None, "ballSize": "ball_size"}`
    """
    )
    # Todo: Can we enforce that this is Dict[str, Optional[str]]?
    attributes_last_change = param.Dict(
        doc="""

    The key is the name of the attribute changed. The value is the new value of the attribute.

    Please note that the value is a string or None

    Examples
    ~~~~~~~~

    ```
    attributes_last_change = {"checked": ""}
    attributes_last_change = {"value": None}
    attributes_last_change = {"ballSize": "2"}
    ```
    """
    )
    # Todo: Can we enforce that this is Dict[str, Optional[anything]?
    properties_to_watch = param.Dict(
        doc="""
    The key is the name of the js property. The value is the name of the python parameter

    DO NOT CHANGE AFTER CONSTRUCTION OF THE OBJECT!

    Example
    ~~~~~~~

    `properties_to_watch = {"checked": "checked", "value": None, "ballSize": "ball_size"}`
    """
    )
    # Todo: Can we enforce that this is Dict[str, Optional[anything]?
    properties_last_change = param.Dict(
        doc="""

    The key is the name of the property changed. The value is the new value of the property

     Examples
    ~~~~~~~~

    ```
    properties_last_change = {"checked": True}
    properties_last_change = {"value": None}
    properties_last_change = {"ballSize": 2}
    ```
    """
    )
    parameters_to_watch = param.List(
        doc="""
        A list of parameters that do not correspond to attributes but that the value of `html`
        depends on. For example parameters that define the `innerHTML` of the `html` string.

        In order for this to take effect you also need to do a custom implementation of
        `_get_html_from_parameters_to_watch`.

        DO NOT CHANGE AFTER CONSTRUCTION OF THE OBJECT!

        Example
        ~~~~~~~

        The Wired `Fab` has an `icon` parameter that defines the `html` of the web component
        as `<wired-fab><mwc-icon>{self.icon}</mwc-icon></wired-fab>`.
        """
    )
    events_to_watch = param.Dict(
        doc="""
    The key is the name of the js event. The value is the name of a python parameter to increment
    or None.

    Use this if you want to support button clicks, mouseups etc.

    Example Button
    ~~~~~~~~~~~~~~

    class Button(WebComponent):
        html = param.String('<wired-button>Button</wired-radio>')
        events_to_watch = param.Dict(default={"click": "clicks"})

        clicks = param.Integer()


    Example Combobox
    ~~~~~~~~~~~~~~~~

    The Wired `ComboBox` does not run the `onchange` event handler when the selection changes. I.e.
    adding "selected" to the `parameters_to_watch` does not work as expected.

    But the `select` event is fired by the `ComboBox`. So if we also add `select`to
    `events_to_watch` list, then the synchronization from js `selection` property to python
    `selection` property works
    """
    )
    events_count_last_change = param.Dict(
        doc="""
        Key is the name of the event, Value is the number of times it has fired in total

        Please note that the communication goes from client to server and not the other way around.

        Example
        ~~~~~~~

        events_count_last_change = {"click": 2}
        """
    )
    column_data_source = param.Parameter(
        doc="""
    The ColumnDataSource containing is used to efficiently transfer columnar data to the client

    Example
    ~~~~~~~

    PerspectiveWidget
    """
    )
    column_data_source_orient = param.ObjectSelector(
        "dict",
        objects=["dict", "records"],
        doc="""
    The orientation of the data when provided to the web component.

    - dict: {"x": [1,2], "y": [3,4]}
    - records: [{"x": 1, "y": 3}, {"x": 2, "y": 4}]

    Example
    ~~~~~~~

    The `perspective-viewer`'s `load`s data in the `records` format.
    """,
    )
    column_data_source_load_function = param.String(doc="""
    The name of the web component function or property used to load the data

    Example
    ~~~~~~

    The `perspective-viewer` component uses the `load` function to load data.
    """)

    def __init__(self, **params):
        # Avoid AttributeError: unexpected attribute ...
        for parameter in self._child_parameters():
            self._rename[parameter] = None

        if not self.param.attributes_to_watch.default:
            self.param.attributes_to_watch.default = {}
        if not self.param.properties_to_watch.default:
            self.param.properties_to_watch.default = {}
        if not self.param.events_to_watch.default:
            self.param.events_to_watch.default = {}
        if not self.param.parameters_to_watch.default:
            self.param.parameters_to_watch.default = {}
        else:
            params["html"] = self._get_initial_html_from_parameters_to_watch(**params)

        super().__init__(**params)

        self.parser: HTMLParser = AttributeParser()
        self.param.watch(self._update_parameters, ["html",])
        self.param.watch(self._handle_attributes_last_change, ["attributes_last_change",])
        self.param.watch(self._handle_properties_last_change, ["properties_last_change",])
        self.param.watch(self._handle_events_count_last_change, ["events_count_last_change",])

        if self.attributes_to_watch:
            parameters_to_watch = [value for value in self.attributes_to_watch.values() if value]
            self.param.watch(self._handle_parameter_attribute_change, parameters_to_watch)

        if self.properties_to_watch:
            parameters_to_watch = list(self.properties_to_watch.values())
            self.param.watch(self._handle_parameter_property_change, parameters_to_watch)

        if self.parameters_to_watch:
            self.param.watch(
                self._handle_parameters_to_watch_change, list(self.parameters_to_watch)
            )

        self.update_html_from_attributes_to_watch()
        self._update_properties()

    def _handle_parameters_to_watch_change(self, event):
        params = {parameter: getattr(self, parameter) for parameter in self.parameters_to_watch}
        html = self._get_html_from_parameters_to_watch(**params)
        html = self._update_html_from_attributes_to_watch(html)
        if html != self.html:
            self.html = html

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
                init_params[parameter] = params[parameter]
            else:
                init_params[parameter] = self.param[parameter].default
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
        raise NotImplementedError(
            "You need to do a custom implementation of this because the parameters_to_watch list is not empty"
        )

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
        """Updates the parameter with the value of a html attribute

        Parameters
        ----------
        parameter : str
            A parameter name like 'checked' or 'ball_size' to update
        attribute : str
            An attribute name like 'checked' or 'ballSize' to update from
        attr_dict : Dict
            A dictionary containing attribute keys and their values

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

    def update_html_from_attributes_to_watch(self):
        if not self.attributes_to_watch or not self.html:
            return
        html = self.html

        new_html = self._update_html_from_attributes_to_watch(html)

        if new_html != self.html:
            self.html = new_html

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
        html = f"<span>{html}</span>"  # Workaround to handle both single tags and multiple tags
        root = LH.fromstring(html)
        iterchildren = [item for item in root.iterchildren()]
        first_child = iterchildren[0]

        for attribute, parameter in self.attributes_to_watch.items():
            if parameter:
                parameter_value = getattr(self, parameter)
                parameter_item = self.param[parameter]
                if isinstance(parameter_item, param.Boolean):
                    if parameter_value:
                        attribute_value = ""
                        first_child.set(attribute, attribute_value)
                    elif attribute in first_child.attrib:
                        del first_child.attrib[attribute]
                else:
                    if parameter_value is not None:
                        attribute_value = str(parameter_value)
                        first_child.set(attribute, attribute_value)
                    else:
                        if attribute in first_child.attrib:
                            first_child.attrib.pop(attribute)
        new_html = LH.tostring(first_child).decode("utf-8")
        if len(iterchildren) > 1:
            new_html = new_html + "".join(
                LH.tostring(item).decode("utf-8") for item in iterchildren[1:]
            )
        return new_html

    def _handle_parameter_attribute_change(self, event=None):
        if not self.attributes_to_watch:
            return

        parameters_to_attributes = {v: k for k, v in self.attributes_to_watch.items()}
        parameter_name= event.name
        value = event.new

        value = self.parse_parameter_value_to_attribute_value(parameter_name, value)

        attribute_name = parameters_to_attributes[parameter_name]
        change = {attribute_name: value}
        if self.attributes_last_change != change:
            self.attributes_last_change = change

    def parse_parameter_value_to_attribute_value(self, parameter: str, value) -> Optional[str]:
        """Returns the value to input to the setAttribute method of a JS HTML Element

        Parameters
        ----------
        parameter : str
            The name of the parameter. For example "columns"
        value : [type]
            The value of the parameter. For example None, [] or ["x","y"]

        Returns
        -------
        Optional[str]
            The attribute value. For example None, "[]" or '["x", "y"]'
        """
        parameter_item = self.param[parameter]

        if value is None:
            return value
        if isinstance(parameter_item, param.Boolean):
            if value == True:
                return ""
            else:
                return None
        elif isinstance(parameter_item, (param.String, param.Integer, param.ObjectSelector)):
            if value:
                return str(value)
        else:
            return json.dumps(value, separators=(',',':'))
        return value

    def _handle_attributes_last_change(self, event):
        if not self.attributes_to_watch or not event.new or event.old == event.new:
            return

        # Todo: If we can skip the check below at all or just put in try/ catch to speed up
        for attribute_, new_value in event.new.items():
            if not attribute_ in self.attributes_to_watch:
                continue

            parameter_name = self.attributes_to_watch[attribute_]
            parameter_item = self.param[parameter_name]

            if isinstance(parameter_item, param.Boolean):
                if new_value == "":
                    new_value = True
                else:
                    new_value = False
            elif isinstance(parameter_item, param.Integer):
                if not new_value is None:
                    new_value = int(new_value)
                elif parameter_item.allow_None:
                    new_value = None
                else:
                    new_value = parameter_item.default
            elif isinstance(parameter_item, param.Number):
                if not new_value is None:
                    new_value = float(new_value)
                elif parameter_item.allow_None:
                    new_value = None
                else:
                    new_value = parameter_item.default
            elif isinstance(parameter_item, (param.String, param.ObjectSelector)):
                if not new_value is None:
                    new_value = str(new_value)
                elif parameter_item.allow_None:
                    new_value = None
                else:
                    new_value = parameter_item.default
            elif isinstance(parameter_item, (param.List, param.Dict)):
                if not new_value is None:
                    new_value = json.loads(new_value)
                elif parameter_item.allow_None:
                    new_value = None
                else:
                    new_value = parameter_item.default

            old_value = getattr(self, parameter_name)
            if old_value != new_value:
                setattr(self, parameter_name, new_value)

    def _handle_properties_last_change(self, event):
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

            old_value = getattr(self, parameter)
            if old_value != new_value:
                setattr(self, parameter, new_value)

    def _handle_parameter_property_change(self, event):
        if not self.properties_to_watch:
            return

        parameters_to_properties = {v: k for k, v in self.properties_to_watch.items()}
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
