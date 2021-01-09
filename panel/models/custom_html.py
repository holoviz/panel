import html.parser
import re

from collections import defaultdict

from bokeh.core.properties import Instance, String, Dict, List, Tuple
from bokeh.models.layouts import HTMLBox
from bokeh.model import DataModel
from bokeh.events import ModelEvent


class CustomHTMLParser(html.parser.HTMLParser):
    
    def __init__(self):
        super().__init__()
        self.attrs = defaultdict(list)
        self._template_re = re.compile('^\$\{.+\}$')
    
    def handle_starttag(self, tags, attrs):
        attrs = dict(attrs)
        dom_id = attrs.pop('id', None)
        if not dom_id or not dom_id.endswith('-${id}'):
            return
        
        name = '-'.join(dom_id.split('-')[:-1])
        for attr, value in attrs.items():
            if self._template_re.match(value):
                self.attrs[name].append((attr, value[2:-1]))


def find_attrs(html):
    p = CustomHTMLParser()
    p.feed(html)
    return p.attrs


class CustomEvent(ModelEvent):

    event_name = 'custom'

    def __init__(self, model, event=None):
        self.event = event
        super().__init__(model=model)


class CustomHTML(HTMLBox):

    attrs = Dict(String, List(Tuple(String, String)))

    events = Dict(String, List(String))

    html = String()

    model = Instance(DataModel)

    def __init__(self, **props):
        if 'attrs' not in props and 'html' in props:
            props['attrs'] = find_attrs(props['html'])
        super().__init__(**props)

