import difflib
import re

from collections import defaultdict
from html.parser import HTMLParser

import bokeh.core.properties as bp

from bokeh.models import HTMLBox, LayoutDOM
from bokeh.model import DataModel
from bokeh.events import ModelEvent


endfor = '{%-? endfor -?%}'
list_iter_re = r'{%-? for (\s*[A-Za-z_]\w*\s*) in (\s*[A-Za-z_]\w*\s*) -?%}'
items_iter_re = r'{%-? for \s*[A-Za-z_]\w*\s*, (\s*[A-Za-z_]\w*\s*) in (\s*[A-Za-z_]\w*\s*)\.items\(\) -?%}'
values_iter_re = r'{%-? for (\s*[A-Za-z_]\w*\s*) in (\s*[A-Za-z_]\w*\s*)\.values\(\) -?%}'


class ReactiveHTMLParser(HTMLParser):

    def __init__(self, cls, template=True):
        super().__init__()
        self.template = template
        self.cls = cls
        self.attrs = defaultdict(list)
        self.children = {}
        self.nodes = []
        self.looped = []
        self._template_re = re.compile(r'\$\{[^}]+\}')
        self._current_node = None
        self._node_stack = []
        self._open_for = False
        self.loop_map = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        dom_id = attrs.pop('id', None)
        self._current_node = None
        self._node_stack.append((tag, dom_id))

        if not dom_id:
            for attr, value in attrs.items():
                if value is None:
                    continue
                params, methods = [], []
                for match in self._template_re.findall(value):
                    match = match[2:-1]
                    if match.startswith('model.'):
                        continue
                    if match in self.cls.param:
                        params.append(match)
                    elif hasattr(self.cls, match):
                        methods.append(match)
                if methods:
                    raise ValueError(
                        "DOM nodes with an attached callback must declare "
                        f"an id. Found <{tag}> node with the `{attr}` callback "
                        f"referencing the `{methods[0]}` method. Add an id "
                        "attribute like this: "
                        f"<{tag} id=\"{tag}\" {attr}=\"${{{methods[0]}}}>...</{tag}>."
                    )
                elif params:
                    literal = value.replace(f'${{{params[0]}}}', f'{{{{{params[0]}}}}}')
                    raise ValueError(
                        "DOM node with a linked parameter declaration "
                        f"must declare an id. Found <{tag}> node with "
                        f"the `{attr}` attribute referencing the `{params[0]}` "
                        "parameter. Either declare an id on the node, "
                        f"i.e. <{tag} id=\"{tag}\" {attr}=\"{value}\">...</{tag}>, "
                        "or insert the value as a literal: "
                        f"<{tag} {attr}=\"{literal}\">...</{tag}>."
                    )
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
        if not self.template:
            return

        dom_id = self._current_node
        matches = [
            '%s}]}' % match if match.endswith('.index0 }') else match
            for match in self._template_re.findall(data)
        ]

        # Detect templating for loops
        list_loop = re.findall(list_iter_re, data)
        values_loop = re.findall(values_iter_re, data)
        items_loop = re.findall(items_iter_re, data)
        nloops = len(list_loop) + len(values_loop) + len(items_loop)
        if nloops > 1 and nloops and self._open_for:
            raise ValueError('Nested for loops currently not supported in templates.')
        elif nloops:
            loop = [loop for loop in (list_loop, values_loop, items_loop) if loop][0]
            var, obj = loop[0]
            if var in self.cls.param:
                raise ValueError(f'Loop variable {var} clashes with parameter name. '
                                 'Ensure loop variables have a unique name. Relevant '
                                 f'template section:\n\n{data}')
            self.loop_map[var] = obj

        open_for = re.search(r'{%-? for', data)
        end_for = re.search(endfor, data)
        if open_for:
            self._open_for = True
        if end_for and (not nloops or end_for.start() > open_for.start()):
            self._open_for = False

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

        # Handle looped variables
        if match and (match in self.loop_map or '[' in match) and self._open_for:
            if match in self.loop_map:
                matches[matches.index('${%s}' % match)] = '${%s}' % self.loop_map[match]
                match = self.loop_map[match]
            elif '[' in match:
                match, _ = match.split('[')
            dom_id = dom_id.replace('-{{ loop.index0 }}', '')
            self.looped.append((dom_id, match))

        mode = self.cls._child_config.get(match, 'model')
        if match in self.cls.param and mode != 'template':
            self.children[dom_id] = match
            return

        templates = []
        for match in matches:
            match = match[2:-1]
            if match.startswith('model.'):
                continue
            if match not in self.cls.param and '.' not in match:
                params = difflib.get_close_matches(match, list(self.cls.param))
                raise ValueError(f"{self.cls.__name__} HTML template references "
                                 f"unknown parameter '{match}', similar parameters "
                                 f"include {params}.")
            templates.append(match)
        self.attrs[dom_id].append(('children', templates, data.replace('${', '{')))



def find_attrs(html):
    p = ReactiveHTMLParser()
    p.feed(html)
    return p.attrs



class DOMEvent(ModelEvent):

    event_name = 'dom_event'

    def __init__(self, model, node=None, data=None):
        self.data = data
        self.node = node
        super().__init__(model=model)


class ReactiveHTML(HTMLBox):

    attrs = bp.Dict(bp.String, bp.List(bp.Tuple(bp.String, bp.List(bp.String), bp.String)))

    callbacks = bp.Dict(bp.String, bp.List(bp.Tuple(bp.String, bp.String)))

    children = bp.Dict(bp.String, bp.Either(bp.List(bp.Either(bp.Instance(LayoutDOM), bp.String)), bp.String))

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
