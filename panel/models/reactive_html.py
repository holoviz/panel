import difflib
import re

from collections import defaultdict
from html.parser import HTMLParser

import bokeh.core.properties as bp
import param as pm

from bokeh.models import HTMLBox, LayoutDOM
from bokeh.model import DataModel
from bokeh.events import ModelEvent


class ReactiveHTMLParser(HTMLParser):

    def __init__(self, cls):
        super().__init__()
        self.cls = cls
        self.attrs = defaultdict(list)
        self.children = {}
        self.nodes = []
        self.looped = []
        self._template_re = re.compile('\$\{[^}]+\}')
        self._current_node = None
        self._node_stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        dom_id = attrs.pop('id', None)
        self._current_node = None
        self._node_stack.append((tag, dom_id))

        if not dom_id:
            return

        if dom_id in self.nodes:
            raise ValueError(f'Multiple DOM nodes with id="{dom_id}" found.')
        self._current_node = dom_id
        self.nodes.append(dom_id)
        for attr, value in attrs.items():
            if value is None:
                continue
            matches = []
            for match in self._template_re.findall(value):
                if not match[2:-1].startswith('model.'):
                    matches.append(match[2:-1])
            if matches:
                self.attrs[dom_id].append((attr, matches, value.replace('${', '{')))

    def handle_endtag(self, tag):
        self._node_stack.pop()
        self._current_node = self._node_stack[-1][1] if self._node_stack else None

    def handle_data(self, data):
        dom_id = self._current_node
        matches = [
            '%s}]}' % match if match.endswith('.index0 }') else match
            for match in self._template_re.findall(data)
        ]
        if not (self._current_node and matches):
            return
        if len(matches) == 1:
            match = matches[0][2:-1]
        else:
            for match in matches:
                mode = self.cls._child_config.get(match, 'model')
                if mode != 'template':
                    raise ValueError(f"Cannot match multiple variables in '{mode}' mode.")
            match = None
        if match and '[' in match:
            match, num = match.split('[')
            dom_id = dom_id.replace('-{{ loop.index0 }}', '')
            num = num.rstrip(']')
            self.looped.append((dom_id, match))
        else:
            num = None
        mode = self.cls._child_config.get(match, 'model')
        if match in self.cls.param and mode != 'template':
            self.children[dom_id] = match
            return

        templates = []
        for match in matches:
            match = match[2:-1]
            if match.startswith('model.'):
                continue
            if match not in self.cls.param:
                params = difflib.get_close_matches(match, list(self.cls.param))
                raise ValueError("HTML template references unknown parameter "
                                 f"'{match}', similar parameters include "
                                 f"{params}.")
            templates.append(match)
        self.attrs[dom_id].append(('children', templates, data.replace('${', '{')))



def find_attrs(html):
    p = ReactiveHTMLParser()
    p.feed(html)
    return p.attrs


PARAM_MAPPING = {
    pm.Boolean: lambda p, kwargs: bp.Bool(**kwargs),
    pm.CalendarDate: lambda p, kwargs: bp.Date(**kwargs),
    pm.CalendarDateRange: lambda p, kwargs: bp.Tuple(bp.Date, bp.Date, **kwargs),
    pm.Color: lambda p, kwargs: bp.Color(**kwargs),
    pm.DateRange: lambda p, kwargs: bp.Tuple(bp.Datetime, bp.Datetime, **kwargs),
    pm.Date: lambda p, kwargs: bp.Datetime(**kwargs),
    pm.Dict: lambda p, kwargs: bp.Dict(bp.String, bp.Any, **kwargs),
    pm.Event: lambda p, kwargs: bp.Bool(**kwargs),
    pm.Integer: lambda p, kwargs: bp.Int(**kwargs),
    pm.List: lambda p, kwargs: bp.List(bp.Any, **kwargs),
    pm.Number: lambda p, kwargs: bp.Float(**kwargs),
    pm.NumericTuple: lambda p, kwargs: bp.Tuple(*(bp.Float for p in p.length), **kwargs),
    pm.Range: lambda p, kwargs: bp.Tuple(bp.Float, bp.Float, **kwargs),
    pm.String: lambda p, kwargs: bp.String(**kwargs),
    pm.Tuple: lambda p, kwargs: bp.Tuple(*(bp.Any for p in p.length), **kwargs),
}


def construct_data_model(parameterized, name=None, ignore=[]):
    properties = {}
    for pname in parameterized.param:
        if pname in ignore:
            continue
        p = parameterized.param[pname]
        if p.precedence and p.precedence < 0:
            continue
        prop = PARAM_MAPPING.get(type(p))
        pname = parameterized._rename.get(pname, pname)
        if pname == 'name':
            continue
        kwargs = {'default': p.default, 'help': p.doc}
        if prop is None:
            properties[pname] = bp.Any(**kwargs)
        else:
            properties[pname] = prop(p, kwargs)
    name = name or parameterized.name
    return type(name, (DataModel,), properties)


class DOMEvent(ModelEvent):

    event_name = 'dom_event'

    def __init__(self, model, node=None, data=None):
        self.data = data
        self.node = node
        super().__init__(model=model)


class ReactiveHTML(HTMLBox):

    attrs = bp.Dict(bp.String, bp.List(bp.Tuple(bp.String, bp.List(bp.String), bp.String)))

    callbacks = bp.Dict(bp.String, bp.List(bp.Tuple(bp.String, bp.String)))

    children = bp.Dict(bp.String, bp.List(bp.Either(bp.Instance(LayoutDOM), bp.String)))

    data = bp.Instance(DataModel)

    events = bp.Dict(bp.String, bp.Dict(bp.String, bp.Bool))

    html = bp.String()

    looped = bp.List(bp.String)

    nodes = bp.List(bp.String)

    scripts = bp.Dict(bp.String, bp.List(bp.String))

    def __init__(self, **props):
        if 'attrs' not in props and 'html' in props:
            props['attrs'] = find_attrs(props['html'])
        super().__init__(**props)
