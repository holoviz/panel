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


def get_watchers(reactive):
    return [w for pwatchers in reactive._param_watchers.values()
            for awatchers in pwatchers.values() for w in awatchers]


def param_to_jslink(model, widget):
    """
    Converts Param pane widget links into JS links if possible.
    """
    from ..links import Link, JSLinkCallbackGenerator
    from ..viewable import Reactive

    param_pane = widget._param_pane
    pobj = param_pane.object
    pname = [k for k, v in param_pane._widgets.items() if v is widget]
    watchers = [w for w in get_watchers(widget) if w not in widget._callbacks
                and w not in param_pane._callbacks]

    if (not pname or not isinstance(pobj, Reactive) or watchers or
        pname[0] not in pobj._linkable_params):
        return
    pname = pname[0]
    kwargs = {}
    if 'value' in widget._embed_transforms:
        src_attr = widget._rename.get('value', 'value')
        tgt_attr = pobj._rename.get(pname, pname)
        src_transform = "target['{spec}'] = ({transform})".format(
            spec=tgt_attr, transform=widget._embed_transforms['value']
        )
        kwargs['code'] = {'value': src_transform}
        tgt_transform = "value = source['{attr}']; target['{spec}'] = ({transform})".format(
            attr=tgt_attr, spec=src_attr,
            transform=widget._reverse_transforms['value']
        )
        link = Link(pobj, widget, code={pname: tgt_transform})
        JSLinkCallbackGenerator(model, link, pobj, widget)
    else:
        kwargs['bidirectional'] = True
        kwargs['properties'] = dict(value=pobj._rename.get(pname, pname))
    link = Link(widget, pobj, **kwargs)
    JSLinkCallbackGenerator(model, link, widget, pobj)
    return link

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def embed_state(panel, model, doc, max_states=1000, max_opts=3,
                json=False, json_prefix='', save_path='./', load_path=None):
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
    from ..layout import Panel
    from ..links import Link
    from ..models.state import State
    from ..pane import PaneBase
    from ..widgets import Widget, DiscreteSlider

    target = model.ref['id']
    if isinstance(panel, PaneBase) and target in panel.layout._models:
        panel = panel.layout

    if not isinstance(panel, Panel):
        add_to_doc(model, doc)
        return
    _, _, _, comm = state._views[target]

    model.tags.append('embedded')

    widgets = [w for w in panel.select(Widget) if w not in Link.registry]
    state_model = State()

    widget_data, ignore = [], []
    for widget in widgets:
        if widget._param_pane is not None:
            # Replace parameter links with JS links
            link = param_to_jslink(model, widget)
            if link is not None:
                continue # Skip if we were able to attach JS link
            pobj = widget._param_pane.object
            if isinstance(pobj, Widget):
                watchers = [w for w in get_watchers(pobj) if widget not in pobj._callbacks
                            and widget not in widget._param_pane._callbacks]
                if not watchers:
                    # If underlying parameterized object is a widget
                    # which has no other links ensure it is skipped later
                    ignore.append(pobj) 

        if widget._links:
            # TODO: Implement JS linking for .link calls
            pass

        # If the widget does not support embedding or has no external callback skip it
        if not widget._supports_embed or all(w in widget._callbacks for w in get_watchers(widget)):
            continue

        # Get data which will let us record the changes on widget events 
        widget, w_model, vals, getter, on_change, js_getter = widget._get_embed_state(model, max_opts)
        w_type = widget._widget_type
        if isinstance(widget, DiscreteSlider):
            w_model = widget._composite[1]._models[target][0].select_one({'type': w_type})
        else:
            w_model = widget._models[target][0].select_one({'type': w_type})
        js_callback = CustomJS(code=STATE_JS.format(
            id=state_model.ref['id'], js_getter=js_getter))
        widget_data.append((widget, w_model, vals, getter, js_callback, on_change))

    # Ensure we recording state for widgets which could be JS linked
    values = []
    for (w, w_model, vals, getter, js_callback, on_change) in values:
        if w in ignore:
            continue
        w_model.js_on_change(on_change, js_callback)
        values.append((w, w_model, vals, getter))

    add_to_doc(model, doc, True)
    doc._held_events = []

    if not values:
        return

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
    changes = False
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
        changes |= events['content'] == '{}'
        if events:
            sub_dict.update(events)

    if not changes:
        return

    for (w, _, _, _), v in zip(values, restore):
        try:
            w.param.set_param(value=v)
        except:
            pass

    if json:
        random_dir = '_'.join([json_prefix, uuid.uuid4().hex])
        save_path = os.path.join(save_path, random_dir)
        if load_path is not None:
            load_path = os.path.join(load_path, random_dir)
        state_dict = save_dict(state_dict, max_depth=len(values)-1,
                               save_path=save_path, load_path=load_path)

    state_model.update(json=json, state=state_dict, values=init_vals,
                       widgets={m.ref['id']: i for i, (_, m, _, _) in enumerate(values)})
    doc.add_root(state_model)
