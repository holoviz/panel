"""
Various utilities for recording and embedding state in a rendered app.
"""
from __future__ import absolute_import, division, unicode_literals

import os
import json
import uuid

from collections import defaultdict
from itertools import product

from bokeh.models import CustomJS

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

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def embed_state(panel, model, doc, max_states=1000, max_opts=3,
                json=False, save_path='./', load_path=None):
    """
    Embeds the state of the application on a State model which allows
    exporting a static version of an app. This works by finding all
    widgets with a predefined set of options and evaluating the cross
    product of the widget values and recording the resulting events to
    be replayed when exported. The state is recorded on a State model
    which is attached as an additional root on the Document.

    Arguments
    ---------
    panel: panel.viewable.Reactive
      The Reactive component being exported
    model: bokeh.model.Model
      The bokeh model being exported
    doc: bokeh.document.Document
      The bokeh Document being exported
    max_states: int (default=1000)
      The maximum number of states to export
    max_opts: int (default=3)
      The maximum number of options for a single widget
    json: boolean (default=True)
      Whether to export the data to json files
    save_path: str (default='./')
      The path to save json files to
    load_path: str (default=None)
      The path or URL the json files will be loaded from.
    """
    from ..links import Link
    from ..models.state import State
    from ..widgets import Widget, DiscreteSlider

    target = model.ref['id']
    _, _, _, comm = state._views[target]

    model.tags.append('embedded')
    widgets = [w for w in panel.select(Widget) if w._supports_embed
               and w not in Link.registry]
    state_model = State()

    values = []
    for w in widgets:
        w, w_model, vals, getter, on_change, js_getter = w._get_embed_state(model, max_opts)
        if isinstance(w, DiscreteSlider):
            w_model = w._composite[1]._models[target][0].select_one({'type': w._widget_type})
        else:
            w_model = w._models[target][0].select_one({'type': w._widget_type})
        js_callback = CustomJS(code=STATE_JS.format(
            id=state_model.ref['id'], js_getter=js_getter))
        w_model.js_on_change(on_change, js_callback)
        values.append((w, w_model, vals, getter))

    add_to_doc(model, doc, True)
    doc._held_events = []

    restore = [w.value for w, _, _, _ in values]
    init_vals = [g(m) for _, m, _, g in values]
    cross_product = list(product(*[vals[::-1] for _, _, vals, _ in values]))

    if len(cross_product) > max_states:
        raise RuntimeError('The cross product of different application '
                           'states is too large to explore (N=%d), either reduce '
                           'the number of options on the widgets or increase '
                           'the max_states specified on static export.' %
                           len(cross_product))

    nested_dict = lambda: defaultdict(nested_dict)
    state_dict = nested_dict()
    for key in cross_product:
        sub_dict = state_dict
        skip = False
        for i, k in enumerate(key):
            w, m, _, g = values[i]
            try:
                w.value = k
            except:
                skip = True
                break
            sub_dict = sub_dict[g(m)]
        if skip:
            doc._held_events = []

        # Drop events originating from widgets being varied
        models = [v[1] for v in values]
        doc._held_events = [e for e in doc._held_events if e.model not in models]
        events = record_events(doc)
        if events:
            sub_dict.update(events)

    for (w, _, _, _), v in zip(values, restore):
        try:
            w.set_param(value=v)
        except:
            pass

    if json:
        random_dir = uuid.uuid4().hex
        save_path = os.path.join(save_path, random_dir)
        if load_path is not None:
            load_path = os.path.join(load_path, random_dir)
        state_dict = save_dict(state_dict, max_depth=len(widgets)-1,
                               save_path=save_path, load_path=load_path)

    state_model.update(json=json, state=state_dict, values=init_vals,
                       widgets={m.ref['id']: i for i, (_, m, _, _) in enumerate(values)})
    doc.add_root(state_model)
