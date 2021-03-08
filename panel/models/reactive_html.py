import re

from collections import defaultdict
from html.parser import HTMLParser

import bokeh.core.properties as bp
import param as pm

from bokeh.models import HTMLBox, LayoutDOM
from bokeh.model import DataModel
from bokeh.events import ModelEvent


class ReactiveHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.attrs = defaultdict(list)
        self.children = {}
        self.nodes = []
        self._template_re = re.compile('\$\{[^}]+\}')
        self._current_node = None

    def handle_starttag(self, tags, attrs):
        attrs = dict(attrs)
        dom_id = attrs.pop('id', None)
        self._current_node = None
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
            self.attrs[dom_id].append((attr, matches, value.replace('${', '{')))

    def handle_endtag(self, tag):
        self._current_node = None

    def handle_data(self, data):
        if self._current_node and self._template_re.match(data):
            self.children[self._current_node] = data[2:-1]


def find_attrs(html):
    p = ReactiveHTMLParser()
    p.feed(html)
    return p.attrs


PARAM_MAPPING = {
    pm.String: lambda p, kwargs: bp.String(**kwargs),
    pm.Boolean: lambda p, kwargs: bp.Bool(**kwargs),
    pm.Integer: lambda p, kwargs: bp.Int(**kwargs),
    pm.Number: lambda p, kwargs: bp.Float(**kwargs),
    pm.List: lambda p, kwargs: bp.List(bp.Any, **kwargs),
    pm.Dict: lambda p, kwargs: bp.Dict(bp.String, bp.Any, **kwargs),
    pm.Tuple: lambda p, kwargs: bp.Tuple(*(bp.Any for p in p.length), **kwargs)
}


def construct_data_model(parameterized, name=None, ignore=['name']):
    properties = {}
    for pname in parameterized.param:
        if pname in ignore:
            continue
        p = parameterized.param[pname]
        prop = PARAM_MAPPING.get(type(p))
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

    children = bp.Dict(bp.String, bp.List(bp.Instance(LayoutDOM)))

    data = bp.Instance(DataModel)

    events = bp.Dict(bp.String, bp.List(bp.String))

    html = bp.String()

    scripts = bp.Dict(bp.String, bp.Dict(bp.String, bp.List(bp.String)))

    def __init__(self, **props):
        if 'attrs' not in props and 'html' in props:
            props['attrs'] = find_attrs(props['html'])
        super().__init__(**props)
