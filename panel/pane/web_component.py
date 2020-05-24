"""Implementation of a generic WebComponent pane"""

import json

from html.parser import HTMLParser

import lxml.html as LH
import param

from bokeh.models import ColumnDataSource

from ..models import WebComponent as _BkWebComponent
from ..util import escape
from ..viewable import Layoutable
from ..widgets.base import Widget


# Defines how to convert from attribute string value to parameter value
PARAMETER_TYPE = {
    param.String: str,
    param.Integer: int,
    param.Number: float,
    param.ObjectSelector: str,
    param.Parameter: str,
    param.List: json.loads,
    param.Dict: json.loads,
    param.Boolean: lambda value: value == "" or value is None
}


class AttributeParser(HTMLParser):
    """Used to parse a the WebComponent html string to a dictionary of attribute keys and
    their values"""

    first_tag = True
    attr_dict = None

    def handle_starttag(self, tag, attrs):
        if self.first_tag:
            for attr in attrs:
                self.attr_dict[attr[0]] = attr[1]
            self.first_tag = False


class WebComponent(Widget):
    """
    A WebComponent allows wrapping webcomponents and/ or Javascript
    libraries not already supported in Panel.

    You can use it by instantiating an instance or inheriting from it.

    Parameters
    ----------

    - The parameter values listed in `attributes_to_watch` will be used to set the `html` parameter
    attributes on construction. Further more the the key attributes of the Javascript
    WebComponent and the value parameters of the Python WebComponent will be kept in sync.
    - The value parameters listed in `properties_to_watch` will be used to set the Javascript Web
    Component key properties on construction and kept in sync after construction.
    - The parameters listed in `parameters_to_watch` will be used to set the `html` parameter on
    construction and when changed.
    - The event keys listed in `events_to_watch` will be watched on the JavaScript side. When fired
    the javascript code will check whether any properties_to_watch have changed and if yes then they
    will be synced to Python. If a Python value parameter is specified it will be
    incremented by +1 for each event.

    Other
    -----

    - If the JavaScript WebComponent contains an `after_layout` function this can be used to
    resize the JS WebComponent. An example is the ECharts web component.
    - You can specify nested JS properties as values in properties_to_watch
    - Please note that you will propably have to experiment a bit in order to determine which
    javascript files to import and what combination of attributes, properties, events and/ or
    parameters to watch.

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

    attributes_to_watch = param.Dict(default={}, constant=True, doc="""
        A dictionary of attributes and parameters
  
          - The attributes are the names of webcomponent to observe
            for changes on the client/ browser/ javascript side.
          - The parameters are the corresponding names of the
            parameters on the python side

        The attributes and parameters are automatically synchronized

        If an attribute key has a parameter value of None then the
        attribute is still observed and changes are update in the html
        parameter. But it is not synchronized to a parameter.""")

    attributes_last_change = param.Dict(doc="""
        Mapping where the key is the name of the attribute changed and
        the value is the new value of the attribute.

        Please note that the value is a string or None.""")

    column_data_source = param.ClassSelector(class_=ColumnDataSource, doc="""
        The ColumnDataSource is used to efficiently transfer columnar
        data to the client.""")

    column_data_source_orient = param.ObjectSelector("dict", objects=["dict", "records"],
                                                     doc="""
        The orientation of the data when provided to the web component.

          - dict: {"x": [1,2], "y": [3,4]}
          - records: [{"x": 1, "y": 3}, {"x": 2, "y": 4}]
    """)

    column_data_source_load_function = param.String(doc="""
        The name of the web component function or property used to load the data""")

    component_type = param.ObjectSelector(default="htmlbox",
                                          objects=["htmlbox", "inputgroup"])

    events_count_last_change = param.Dict(doc="""
        Mapping where the key is the name of the event, and the value
        is the number of times it has fired in total.

        Please note that the communication goes from client to server
        and not the other way around.""")

    events_to_watch = param.Dict(default={}, doc="""
        Mapping where the keys are the name of the js events to watch
        and the value is the name of a python parameter to increment
        or None.

        Use this if you want to support button clicks, mouseups etc.

          class Button(WebComponent):
              html = param.String('<wired-button>Button</wired-radio>')
              events_to_watch = param.Dict(default={"click": "clicks"})
              clicks = param.Integer()
        """)

    html = param.String()

    properties_to_watch = param.Dict(default={}, constant=True, doc="""
        Mapping where the key is the name of the js property and the value
        is the name of the python parameter.""")

    properties_last_change = param.Dict(doc="""
        Mapping where the key is the name of the changed property and
        the value is the new value of the property.""")

    parameters_to_watch = param.List(default=[], constant=True, doc="""
        A list of parameters that do not correspond to attributes but 
        that the value of `html` depends on. For example parameters
        that define the `innerHTML` of the `html` string.

        In order for this to take effect you also need to do a custom
        implementation of `_get_html_from_parameters_to_watch`.
        """)

    _rename_dict = {
        "title": None,
        "component_type": "componentType",
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

    @property
    def _rename(self):
        """Returns a set of any new parameters added on self compared to WebComponent.
        """
        params = (
            list(self.attributes_to_watch.values()) +
            list(self.properties_to_watch.values()) +
            list(self.events_to_watch.values())
        )
        return dict(self._rename_dict, **{p: None for p in self.param
                                          if p not in params and p not in self._rename_dict
                                          and p not in Layoutable.param})

    def __init__(self, **params):
        if 'html' not in params:
            params["html"] = self._get_initial_html_from_parameters_to_watch(**params)
        super(WebComponent, self).__init__(**params)
        self.parser: HTMLParser = AttributeParser()
        self.update_html_from_attributes_to_watch()
        self.properties_last_change = {
            prop: getattr(self, pname) for prop, pname in self.properties_to_watch.items()
        }

    def _process_param_change(self, msg):
        msg = super(WebComponent, self)._process_param_change(msg)
        if 'innerHTML' in msg:
            msg['innerHTML'] = escape(msg['innerHTML'])
        for attr, pname in self.attributes_to_watch.items():
            if pname not in msg:
                continue
            value = self.parse_parameter_value_to_attribute_value(pname, msg.pop(pname))
            if msg.get('attributesLastChange') is None:
                msg['attributesLastChange'] = {}
            msg['attributesLastChange'][attr] = value
        for prop, pname in self.properties_to_watch.items():
            if pname not in msg:
                continue
            value = msg.pop(pname)
            if msg.get('propertiesLastChange') is None:
                msg['propertiesLastChange'] = {}
            msg['propertiesLastChange'][prop] = value
        for pname in self.events_to_watch.values():
            if pname in msg:
                del msg[pname]
        html_change = any(pname in msg for pname in self.parameters_to_watch)
        if html_change:
            msg = {k: v for k, v in msg.items() if k not in self.parameters_to_watch}
            params = {parameter: getattr(self, parameter) for parameter in self.parameters_to_watch}
            html = self._get_html_from_parameters_to_watch(**params)
            self.html = html

        return msg

    def _process_property_change(self, msg):
        msg = super(WebComponent, self)._process_property_change(msg)
        if 'html' in msg:
            attr_dict = self.parse_html_to_dict(msg['html'])
            for attribute, parameter in self.attributes_to_watch.items():
                if not parameter:
                    continue
                ptype = type(self.param[parameter])
                if ptype not in PARAMETER_TYPE:
                    raise TypeError("Parameter of type '%s' is not supported." % ptype)
                if attribute in attr_dict:
                    attr_value = attr_dict[attribute]
                    value = PARAMETER_TYPE[ptype](attr_value)
                else:
                    value = self.param[parameter].default
                msg[attribute] = value
        if 'attributes_last_change' in msg:
            for attr, new_value in msg['attributes_last_change'].items():
                pname = self.attributes_to_watch.get(attr)
                if pname is None:
                    continue
                pobj = self.param[pname]
                ptype = type(pobj)
                msg[pname] = PARAMETER_TYPE[ptype](new_value)
        if 'events_count_last_change' in msg:
            for prop, new_value in msg['events_count_last_change'].items():
                pname = self.events_to_watch.get(prop)
                if pname is None:
                    continue
                pobj = self.param[pname]
                ptype = type(pobj)
                msg[pname] = PARAMETER_TYPE[ptype](new_value)
        if 'properties_last_change' in msg:            
            for prop, new_value in msg['properties_last_change'].items():
                pname = self.properties_to_watch.get(prop)
                if pname is None:
                    continue
                pobj = self.param[pname]
                ptype = type(pobj)
                if isinstance(new_value, str) and ptype in PARAMETER_TYPE:
                    new_value = PARAMETER_TYPE[ptype](new_value)
                msg[pname] = new_value            
        return msg

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
            """You need to do a custom implementation of this because the parameters_to_watch list
            is not empty"""
        )

    def parse_html_to_dict(self, html):
        self.parser.attr_dict = {}
        self.parser.first_tag = True
        self.parser.feed(html)
        return self.parser.attr_dict

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

    def parse_parameter_value_to_attribute_value(self, parameter, value):
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

        if value is None or value=="":
            return value
        if isinstance(parameter_item, param.Boolean):
            if value == True:
                return ""
            return None
        elif isinstance(parameter_item, (param.String, param.Integer, param.ObjectSelector)):
            return str(value)
        return json.dumps(value, separators=(",", ":"))
