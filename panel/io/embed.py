"""
Various utilities for recording and embedding state in a rendered app.
"""
import os
import json
import uuid
import param
import sys

from collections import defaultdict
from contextlib import contextmanager
from itertools import product

from bokeh.core.property.bases import Property
from bokeh.models import CustomJS
from param.parameterized import Watcher

from .model import add_to_doc, diff
from .state import state

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

STATE_JS = """
var state = null
for (var root of cb_obj.document.roots()) {{
  if (root.id == '{id}') {{
    state = root;
    break;
  }}
}}
if (!state) {{ return; }}
state.set_state(cb_obj, {js_getter})
"""


@contextmanager
def always_changed(enable):
    def matches(self, new, old):
        return False
    if enable:
        backup = Property.matches
        Property.matches = matches
    try:
        yield
    finally:
        if enable:
            Property.matches = backup


def record_events(doc):
    msg = diff(doc, False)
    if msg is None:
        return {'header': '{}', 'metadata': '{}', 'content': '{}'}
    return {'header': msg.header_json, 'metadata': msg.metadata_json,
            'content': msg.content_json}


def save_dict(state, key=(), depth=0, max_depth=None, save_path='', load_path=None):
    filename_dict = {}
    for k, v in state.items():
        curkey = key+(k,)
        if depth < max_depth:
            filename_dict[k] = save_dict(v, curkey, depth+1, max_depth,
                                         save_path, load_path)
        else:
            filename = '_'.join([str(i) for i in curkey]) +'.json'
            filepath = os.path.join(save_path, filename)
            directory = os.path.dirname(filepath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(filepath, 'w') as f:
                json.dump(v, f)
            refpath = filepath
            if load_path:
                refpath = os.path.join(load_path, filename)
            filename_dict[k] = refpath
    return filename_dict


def get_watchers(reactive):
    return [w for pwatchers in reactive._param_watchers.values()
            for awatchers in pwatchers.values() for w in awatchers]


def param_to_jslink(model, widget):
    """
    Converts Param pane widget links into JS links if possible.
    """
    from ..reactive import Reactive
    from ..widgets import Widget, LiteralInput

    param_pane = widget._param_pane
    pobj = param_pane.object
    pname = [k for k, v in param_pane._widgets.items() if v is widget]
    watchers = [w for w in get_watchers(widget) if w not in widget._callbacks
                and w not in param_pane._callbacks]

    if isinstance(pobj, Reactive):
        tgt_links = [Watcher(*l[:-4]) for l in pobj._links]
        tgt_watchers = [w for w in get_watchers(pobj) if w not in pobj._callbacks
                        and w not in tgt_links and w not in param_pane._callbacks]
    else:
        tgt_watchers = []

    for widget in param_pane._widgets.values():
        if isinstance(widget, LiteralInput):
            widget.serializer = 'json'

    if (not pname or not isinstance(pobj, Reactive) or watchers or
        pname[0] not in pobj._linkable_params or
        (not isinstance(pobj, Widget) and tgt_watchers)):
        return
    return link_to_jslink(model, widget, 'value', pobj, pname[0])


def link_to_jslink(model, source, src_spec, target, tgt_spec):
    """
    Converts links declared in Python into JS Links by using the
    declared forward and reverse JS transforms on the source and target.
    """
    ref = model.ref['id']

    if ((source._source_transforms.get(src_spec, False) is None) or
        (target._target_transforms.get(tgt_spec, False) is None) or
        ref not in source._models or ref not in target._models):
        # We cannot jslink if either source or target declare
        # that they apply Python transforms
        return

    from ..links import Link, JSLinkCallbackGenerator
    properties = dict(value=target._rename.get(tgt_spec, tgt_spec))
    link = Link(source, target, bidirectional=True, properties=properties)
    JSLinkCallbackGenerator(model, link, source, target)
    return link


def links_to_jslinks(model, widget):
    from ..widgets import Widget

    src_links = [Watcher(*l[:-4]) for l in widget._links]
    if any(w not in widget._callbacks and w not in src_links for w in get_watchers(widget)):
        return

    links = []
    for link in widget._links:
        target = link.target
        tgt_watchers = [w for w in get_watchers(target) if w not in target._callbacks]
        if link.transformed or (tgt_watchers and not isinstance(target, Widget)):
            return

        mappings = []
        for pname, tgt_spec in link.links.items():
            if Watcher(*link[:-4]) in widget._param_watchers[pname]['value']:
                mappings.append((pname, tgt_spec))

        if mappings:
            links.append((link, mappings))
    jslinks = []
    for link, mapping in links:
        for src_spec, tgt_spec in mapping:
            jslink = link_to_jslink(model, widget, src_spec, link.target, tgt_spec)
            if jslink is None:
                return
            widget.param.trigger(src_spec)
            jslinks.append(jslink)
    return jslinks


#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def embed_state(panel, model, doc, max_states=1000, max_opts=3,
                json=False, json_prefix='', save_path='./',
                load_path=None, progress=True, states={}):
    """
    Embeds the state of the application on a State model which allows
    exporting a static version of an app. This works by finding all
    widgets with a predefined set of options and evaluating the cross
    product of the widget values and recording the resulting events to
    be replayed when exported. The state is recorded on a State model
    which is attached as an additional root on the Document.

    Arguments
    ---------
    panel: panel.reactive.Reactive
      The Reactive component being exported
    model: bokeh.model.Model
      The bokeh model being exported
    doc: bokeh.document.Document
      The bokeh Document being exported
    max_states: int (default=1000)
      The maximum number of states to export
    max_opts: int (default=3)
      The max number of ticks sampled in a continuous widget like a slider
    json: boolean (default=True)
      Whether to export the data to json files
    json_prefix: str (default='')
      Prefix for JSON filename
    save_path: str (default='./')
      The path to save json files to
    load_path: str (default=None)
      The path or URL the json files will be loaded from.
    progress: boolean (default=True)
      Whether to report progress
    states: dict (default={})
      A dictionary specifying the widget values to embed for each widget
    """
    from tqdm import tqdm

    from ..config import config
    from ..layout import Panel
    from ..links import Link
    from ..models.state import State
    from ..pane import PaneBase
    from ..widgets import Widget, DiscreteSlider

    ref = model.ref['id']
    if isinstance(panel, PaneBase) and ref in panel.layout._models:
        panel = panel.layout

    if not isinstance(panel, Panel):
        add_to_doc(model, doc)
        return
    _, _, _, comm = state._views[ref]

    model.tags.append('embedded')

    def is_embeddable(object):
        if not isinstance(object, Widget):
            return False
        if isinstance(object, DiscreteSlider):
            return ref in object._composite[1]._models
        return ref in object._models

    widgets = [w for w in panel.select(is_embeddable)
               if w not in Link.registry]
    state_model = State()

    widget_data, merged, ignore = [], {}, []
    for widget in widgets:
        if widget._param_pane is not None:
            # Replace parameter links with JS links
            link = param_to_jslink(model, widget)
            if link is not None:
                pobj = widget._param_pane.object
                if isinstance(pobj, Widget):
                    if not any(w not in pobj._callbacks and w not in widget._param_pane._callbacks
                               for w in get_watchers(pobj)):
                        ignore.append(pobj)
                continue # Skip if we were able to attach JS link

        if widget._links:
            jslinks = links_to_jslinks(model, widget)
            if jslinks:
                continue

        # If the widget does not support embedding or has no external callback skip it
        if not widget._supports_embed or all(w in widget._callbacks for w in get_watchers(widget)):
            continue

        # Get data which will let us record the changes on widget events
        w, w_model, vals, getter, on_change, js_getter = widget._get_embed_state(
            model, states.get(widget), max_opts)
        w_type = w._widget_type
        if isinstance(w, DiscreteSlider):
            w_model = w._composite[1]._models[ref][0].select_one({'type': w_type})
        else:
            w_model = w._models[ref][0]
            if not isinstance(w_model, w_type):
                w_model = w_model.select_one({'type': w_type})

        # If there is a widget with the same name, merge with it
        if widget.name and widget.name in merged:
            merged[widget.name][0].append(w)
            merged[widget.name][1].append(w_model)
            continue

        js_callback = CustomJS(code=STATE_JS.format(
            id=state_model.ref['id'], js_getter=js_getter))
        widget_data.append(([w], [w_model], vals, getter, js_callback, on_change))
        merged[widget.name] = widget_data[-1]

    # Ensure we recording state for widgets which could be JS linked
    values = []
    for (ws, w_models, vals, getter, js_callback, on_change) in widget_data:
        if ws[0] in ignore:
            continue
        for w_model in w_models:
            w_model.js_on_change(on_change, js_callback)

        # Bidirectionally link models with same name
        wm = w_models[0]
        for wmo in w_models[1:]:
            attr = ws[0]._rename.get('value', 'value')
            wm.js_link(attr, wmo, attr)
            wmo.js_link(attr, wm, attr)

        values.append((ws, w_models, vals, getter))

    add_to_doc(model, doc, True)
    doc.callbacks._held_events = []

    if not widget_data:
        return

    restore = [ws[0].value for ws, _, _, _ in values]
    init_vals = [g(ms[0]) for _, ms, _, g in values]
    cross_product = list(product(*[vals[::-1] for _, _, vals, _ in values]))
    if len(cross_product) > max_states:
        if config._doc_build:
            return
        param.main.warning('The cross product of different application '
                           'states is very large to explore (N=%d), consider '
                           'reducing the number of options on the widgets or '
                           'increase the max_states specified in the function '
                           'to remove this warning' %
                           len(cross_product))

    nested_dict = lambda: defaultdict(nested_dict)
    state_dict = nested_dict()
    changes = False
    for key in (tqdm(cross_product, leave=False, file=sys.stdout) if progress else cross_product):
        sub_dict = state_dict
        skip = False
        for i, k in enumerate(key):
            ws, m, _, g = values[i]
            try:
                with always_changed(config.safe_embed):
                    for w in ws:
                        w.value = k
            except Exception:
                skip = True
                break
            sub_dict = sub_dict[g(m[0])]
        if skip:
            doc.callbacks._held_events = []
            continue

        # Drop events originating from widgets being varied
        models = [m for v in values for m in v[1]]
        doc.callbacks._held_events = [e for e in doc.callbacks._held_events if e.model not in models]
        events = record_events(doc)
        changes |= events['content'] != '{}'
        if events:
            sub_dict.update(events)

    if not changes:
        return

    for (ws, _, _, _), v in zip(values, restore):
        try:
            for w in ws:
                w.param.set_param(value=v)
        except Exception:
            pass

    if json:
        random_dir = '_'.join([json_prefix, uuid.uuid4().hex])
        save_path = os.path.join(save_path, random_dir)
        if load_path is not None:
            load_path = os.path.join(load_path, random_dir)
        state_dict = save_dict(state_dict, max_depth=len(values)-1,
                               save_path=save_path, load_path=load_path)

    state_model.update(json=json, state=state_dict, values=init_vals,
                       widgets={m[0].ref['id']: i for i, (_, m, _, _) in enumerate(values)})
    doc.add_root(state_model)
    return state_model
