import builtins
import os
import sys

import numpy as np
import pandas as pd
import param

from bokeh.core.json_encoder import serialize_json
from bokeh.document import Document
from bokeh.models import ImportedStyleSheet
from bokeh.plotting import figure
from bokeh.protocol import Protocol

from panel.config import config
from panel.custom import PyComponent, ReactComponent, ReactiveESM
from panel.io.state import set_curdoc, state
from panel.layout import Row
from panel.pane import Bokeh, Markdown
from panel.util import edit_readonly
from panel.viewable import Child, Children


class SimplePyComponent(PyComponent):

    def __panel__(self):
        return Row(1, 2, 3, height=42)


def test_py_component_syncs(document, comm):
    spy = SimplePyComponent(width=42)

    spy.get_root(document, comm)

    assert isinstance(spy._view__, Row)
    assert spy._view__.width == 42
    assert spy.height == 42

    spy.width = 84

    assert spy._view__.width == 84

    spy._view__.width = 42

    assert spy._view__.width == 42


def test_py_component_cleanup(document, comm):
    spy = SimplePyComponent(width=42)

    model = spy.get_root(document, comm)

    assert model.ref['id'] in spy._models
    assert model.ref['id'] in spy._view__._models

    spy._cleanup(model)

    assert not spy._models
    assert not spy._view__._models


class ESMDataFrame(ReactiveESM):

    df = param.DataFrame(doc="""A DataFrame to be displayed in the ESM.""")


def test_reactive_esm_sync_dataframe(document, comm):
    esm_df = ESMDataFrame()

    model = esm_df.get_root(document, comm)

    esm_df.df = pd.DataFrame({"1": [2]})

    assert isinstance(model.data.df, dict)
    assert len(model.data.df) == 2
    expected = {"index": np.array([0]), "1": np.array([2])}
    for col, values in model.data.df.items():
        np.testing.assert_array_equal(values, expected.get(col))


def test_reactive_esm_dataframe_default_without_polars(monkeypatch):
    real_import = builtins.__import__

    def import_without_polars(name, *args, **kwargs):
        if name == 'polars':
            raise ModuleNotFoundError("No module named 'polars'")
        return real_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, 'polars', raising=False)
    monkeypatch.setattr(builtins, '__import__', import_without_polars)

    class ESMDataFrameDefault(ReactiveESM):

        df = param.DataFrame(default=pd.DataFrame({"1": [2]}))

    default = ESMDataFrameDefault._data_model.lookup('df').property._default
    assert isinstance(default, dict)
    expected = {"index": np.array([0]), "1": np.array([2])}
    assert set(default) == set(expected)
    for col, values in default.items():
        np.testing.assert_array_equal(values, expected[col])


def test_reactive_esm_stylesheet_updates_across_documents(document, comm):
    """A reused ESM component does not attach stylesheets to another document."""
    other_doc = Document()
    component = ReactiveESM(stylesheets=['https://example.com/first.css'])

    with set_curdoc(document):
        model1 = component.get_root(document, comm)
        document.add_root(model1)
        model2 = component.get_root(other_doc, comm)
        other_doc.add_root(model2)
        shared = ImportedStyleSheet(url='https://example.com/shared.css')
        process = component._process_param_change

        def add_shared(params):
            props = process(params)
            if 'stylesheets' in props:
                props['stylesheets'].append(shared)
            return props

        component._process_param_change = add_shared
        component.stylesheets = ['https://example.com/second.css']

    for model, doc in ((model1, document), (model2, other_doc)):
        assert all(sts.document is doc for sts in model.stylesheets if isinstance(sts, ImportedStyleSheet))
        assert any(
            isinstance(sts, ImportedStyleSheet) and sts.url == 'https://example.com/shared.css'
            for sts in model.stylesheets
        )
        doc.to_json()


class ESMBundle(ReactiveESM):

    _bundle_path = "esm.js"  # type: ignore[assignment]


def test_inline_bundle_serialized_once_per_document(tmp_path, monkeypatch):
    from bokeh.embed.bundle import extension_dirs

    bundle = tmp_path / 'shared.bundle.js'
    source = 'export function render() { /* shared bundle */ }'
    bundle.write_text(source)
    # The temporary directory may be on a different drive from this module.
    monkeypatch.setitem(extension_dirs, 'panel-test-ext', tmp_path)

    class BundledComponent(ReactiveESM):
        _bundle = bundle

    with config.set(inline=True):
        for doc in (Document(), Document()):
            components = Row(BundledComponent(), BundledComponent())
            doc.add_root(components.get_root(doc))
            assert serialize_json(doc.to_json()).count(source) == 1
            events = []
            doc.on_change(events.append)
            with set_curdoc(doc):
                components.append(BundledComponent())
            assert source not in Protocol().create('PATCH-DOC', events).content_json


def test_esm_extension_can_select_bundle_url_after_model_creation(tmp_path, monkeypatch):
    from bokeh.embed.bundle import extension_dirs

    bundle = tmp_path / 'extension.bundle.js'
    bundle.write_text('export function render() {}')
    # The temporary directory may be on a different drive from this module.
    monkeypatch.setitem(extension_dirs, 'panel-test-ext', tmp_path)
    url = '/assets/extension.bundle.js'

    class ExtensionComponent(ReactiveESM):
        _bundle = bundle

        @classmethod
        def _render_esm(cls, compiled=True, server=False):
            return url

        def _get_model(self, *args, **kwargs):
            model = super()._get_model(*args, **kwargs)
            if model.esm is url:
                model.bundle = 'url'
            return model

    model = ExtensionComponent().get_root(Document())
    assert model.bundle == 'url'
    assert model.esm == url


def test_esm_bundle_resource_path():
    assert ESMBundle._render_esm(compiled=True, server=True) == "./components/panel.tests.test_custom/ESMBundle/_bundle_path/esm.js"


def test_esm_bundle_resource_rel_path():
    with edit_readonly(state):
        state.rel_path = ".."
    try:
        assert ESMBundle._render_esm(compiled=True, server=True) == "../components/panel.tests.test_custom/ESMBundle/_bundle_path/esm.js"
    finally:
        with edit_readonly(state):
            state.rel_path = None


def test_react_bundle_url_omits_importmap(tmp_path, monkeypatch, server_document):
    from bokeh.embed.bundle import extension_dirs

    bundle = tmp_path / 'mui.bundle.js'
    bundle.write_text('export default {}')
    # Served as an extension, since a url relative to the module cannot be
    # computed across drives, e.g. for tmp_path on Windows.
    monkeypatch.setitem(extension_dirs, 'panel-test-ext', tmp_path)

    class MuiBundle(ReactComponent):
        _bundle = bundle
        _importmap = {'imports': {'@mui/material': 'https://esm.sh/@mui/material@7.1.0'}}

    model = MuiBundle().get_root(server_document)

    assert model.bundle == 'url'
    assert model.importmap == {}


class ESMWithChildren(ReactiveESM):

    child = Child(doc="""A child Viewable to be displayed in the ESM.""")

    children = Children(doc="""Child Viewables to be displayed in the ESM.""")


class ReactWithChildren(ReactComponent):

    items = Children()

    _esm = "export function render({model}) { return null }"


def test_react_component_initial_data_serialization(document, comm):
    component = ReactWithChildren(items=[Markdown("foo")])

    model = component.get_root(document, comm)
    document.add_root(model)

    data = document.to_json(deferred=False)["roots"][0]["attributes"]["data"]
    assert [item["id"] for item in data["attributes"]["items"]] == [model.data.items[0].id]


def test_reactive_esm_model_cleanup(document, comm):
    esm = ReactiveESM()

    model = esm.get_root(document, comm)

    ref = model.ref['id']
    assert ref in esm._models
    assert esm._models[ref] == (model, None)

    esm._cleanup(model)
    assert esm._models == {}

def test_reactive_esm_child_model_cleanup(document, comm):
    md = Markdown('foo')
    esm = ESMWithChildren(child=md)

    model = esm.get_root(document, comm)

    ref = model.ref['id']
    assert ref in md._models

    md._cleanup(model)
    assert md._models == {}

def test_reactive_esm_child_model_cleanup_on_replace(document, comm):
    md1 = Markdown('foo')
    esm = ESMWithChildren(child=md1)

    model = esm.get_root(document, comm)

    ref = model.ref['id']
    assert ref in md1._models
    md1_model, _ = md1._models[ref]
    assert model.data.child is md1_model

    esm.child = md2 = Markdown('bar')

    assert md1._models == {}
    assert ref in md2._models
    md2_model, _ = md2._models[ref]
    assert model.data.child is md2_model

def test_reactive_esm_child_pane_replace(document, comm):
    fig1 = figure()
    bk = Bokeh(fig1)
    esm = ESMWithChildren(child=bk)

    model = esm.get_root(document, comm)

    ref = model.ref['id']
    assert ref in bk._models
    bk_model1, _ = bk._models[ref]
    assert bk_model1 is fig1
    assert model.data.child is fig1

    fig2 = figure()
    bk.object = fig2

    ref = model.ref['id']
    assert ref in bk._models
    bk_model2, _ = bk._models[ref]
    assert bk_model2 is fig2
    assert model.data.child is fig2

def test_reactive_esm_children_models_cleanup(document, comm):
    md = Markdown('foo')
    esm = ESMWithChildren(children=[md])

    model = esm.get_root(document, comm)

    ref = model.ref['id']
    assert ref in md._models

    md._cleanup(model)
    assert md._models == {}

def test_reactive_esm_children_models_cleanup_on_replace(document, comm):
    md1 = Markdown('foo')
    esm = ESMWithChildren(children=[md1])

    model = esm.get_root(document, comm)

    ref = model.ref['id']
    assert ref in md1._models
    md1_model, _ = md1._models[ref]
    assert model.data.children == [md1_model]

    esm.children = [md2] = [Markdown('bar')]

    assert md1._models == {}
    assert ref in md2._models
    md2_model, _ = md2._models[ref]
    assert model.data.children == [md2_model]

def test_reactive_esm_children_pane_replace(document, comm):
    fig1 = figure()
    bk = Bokeh(fig1)
    esm = ESMWithChildren(children=[bk])

    model = esm.get_root(document, comm)

    ref = model.ref['id']
    assert ref in bk._models
    bk_model1, _ = bk._models[ref]
    assert bk_model1 is fig1
    assert model.data.children == [fig1]

    fig2 = figure()
    bk.object = fig2

    ref = model.ref['id']
    assert ref in bk._models
    bk_model2, _ = bk._models[ref]
    assert bk_model2 is fig2
    assert model.data.children == [fig2]

class ESMOverride(ReactiveESM):

    width = param.Integer(default=42, allow_None=True)

def test_esm_parameter_override(document, comm):
    esm = ESMOverride()

    model = esm.get_root(document, comm)

    assert model.width == 42

    esm.width = 84

    assert model.width == 84


class ESMWithValue(ReactiveESM):

    value = param.String(default='A', doc="Test value")


def test_esm_python_update_not_suppressed_by_stale_frontend_event(document, comm):
    esm = ESMWithValue(value='A')

    model = esm.get_root(document, comm)

    # Simulate a frontend event setting value to 'B'
    with set_curdoc(document):
        esm._process_events({'value': 'B'})

    assert esm.value == 'B'

    # Now a Python-side update sets a different value
    esm.value = 'C'

    # The model must reflect the Python update
    assert model.data.value == 'C'


def test_esm_model_only_update_does_not_read_data_model(document, comm):
    esm = ESMWithValue()
    model = esm.get_root(document, comm)
    model.destroy()

    esm.width = 300

    assert model.width == 300


def test_esm_boomerang_suppresses_model_update(document, comm):
    esm = ESMWithValue(value='A')

    model = esm.get_root(document, comm)

    with set_curdoc(document):
        esm._process_events({'value': 'B'})

    assert esm.value == 'B'
    assert model.data.value == 'A'


def test_esm_python_update_different_from_frontend_is_applied(document, comm):
    esm = ESMWithValue(value='A')

    model = esm.get_root(document, comm)

    # Frontend sends 'B'
    with set_curdoc(document):
        esm._process_events({'value': 'B'})

    assert esm.value == 'B'

    # Python sets a different value from what the frontend sent
    esm.value = 'C'

    # The model must reflect the Python update since 'C' != 'B'
    assert model.data.value == 'C'


class ESMWithEvent(ReactiveESM):

    clicks = param.Integer(default=0)

    value = param.Event()


def test_esm_event_reset_does_not_retrigger_watchers(document, comm):
    esm = ESMWithEvent()

    model = esm.get_root(document, comm)

    values = []
    esm.param.watch(lambda e: values.append(e.new), 'value')

    with set_curdoc(document):
        esm.param.update(clicks=1, value=True)

    assert values == [True]
    assert model.data.value is False


def test_reactive_esm_children_preprocess_jslink(document, comm):
    from panel.widgets import IntSlider

    container = ESMWithChildren()
    container.get_root(document, comm)

    w1 = IntSlider(value=1)
    w2 = IntSlider(value=2)
    w1.jslink(w2, value='value', bidirectional=True)
    with set_curdoc(document):
        container.children = [w1, w2]

    ref = list(container._models.keys())[0]
    m1 = w1._models[ref][0]
    m2 = w2._models[ref][0]
    assert 'change:value' in m1.js_property_callbacks
    assert 'change:value' in m2.js_property_callbacks


class Inner(param.Parameterized):

    text = param.String(default='a')


class ESMWithNested(ReactiveESM):

    child = param.ClassSelector(class_=Inner)

    children = param.List(item_type=Inner)


def test_reactive_esm_tags_nested_datamodels(document, comm):
    esm = ESMWithNested(child=Inner(), children=[Inner()])

    model = esm.get_root(document, comm)

    ref = f"__ref:{model.ref['id']}"
    assert ref in model.data.tags
    assert ref in model.data.child.tags
    assert ref in model.data.children[0].tags

    esm.child = Inner(text='b')
    esm.children = [Inner(text='c')]

    assert model.data.child.text == 'b'
    assert ref in model.data.child.tags
    assert model.data.children[0].text == 'c'
    assert ref in model.data.children[0].tags


def test_reactive_esm_tags_nested_datamodels_without_query(document, comm, monkeypatch):
    from bokeh.model import DataModel

    def query(*args, **kwargs):
        raise AssertionError('DataModel properties should not be queried')

    monkeypatch.setattr(DataModel, 'properties_with_values', query)
    esm = ESMWithNested(child=Inner(), children=[Inner(), Inner()])

    model = esm.get_root(document, comm)

    ref = f"__ref:{model.ref['id']}"
    assert ref in model.data.tags
    assert ref in model.data.child.tags
    assert all(ref in child.tags for child in model.data.children)


def test_reactive_esm_ref_properties():
    from panel.reactive import _ref_properties

    class ESMWithScalars(ESMWithNested):

        value = param.Integer(default=1)

        label = param.String(default='a')

    ref_props = _ref_properties(ESMWithScalars._data_model)
    assert 'child' in ref_props
    assert 'children' in ref_props
    assert 'value' not in ref_props
    assert 'label' not in ref_props


class ESMWithDefaults(ReactiveESM):

    value = param.Integer(default=1)

    _esm = 'export function render() {}'


def test_reactive_esm_get_model_drops_default_properties(document, comm, monkeypatch):
    from panel.models import ReactiveESM as BkReactiveESM

    kwargs = {}
    init = BkReactiveESM.__init__

    def spy(self, *args, **kw):
        kwargs.update(kw)
        init(self, *args, **kw)

    monkeypatch.setattr(BkReactiveESM, '__init__', spy)
    esm = ESMWithDefaults(value=2)
    model = esm.get_root(document, comm)
    monkeypatch.undo()

    for prop in ('css_classes', 'dev', 'events', 'styles', 'tags', 'use_shadow_dom', 'visible'):
        assert prop not in kwargs
    # Even a None spec must be passed so the model does not resolve its own
    assert 'external_resources' in kwargs
    assert model.data.value == 2
    assert model.class_name == 'ESMWithDefaults'
    assert model.esm == esm._render_esm(not config.autoreload)

    # Defaults are not filtered from updates, they must reach the frontend
    esm.visible = False
    assert model.visible is False
    esm.visible = True
    assert model.visible is True


def test_reactive_esm_get_model_matches_unfiltered_model(document, comm):
    from panel.io.resource_spec import resource_spec

    esm = ESMWithDefaults(value=2, css_classes=['foo'])
    model = esm.get_root(document, comm)

    props = esm._get_properties(document)
    props['external_resources'] = resource_spec(ESMWithDefaults)
    full = type(model)(**props)
    # Events are subscribed to after the model is constructed
    values = {k: v for k, v in model._property_values.items() if k != 'subscribed_events'}
    assert set(values) == set(full._property_values)
    for name, value in values.items():
        if name == 'data':
            data = value.properties_with_values()
            full_data = full.data.properties_with_values()
            assert data.pop('tags') == [f"__ref:{model.ref['id']}"]
            assert full_data.pop('tags') == []
            assert data == full_data
        else:
            assert value == full._property_values[name]


class ESMWithDataDefaults(ReactiveESM):

    count = param.Integer(default=1)

    direction: param.Selector[str] = param.Selector(default='ltr', objects=['ltr', 'rtl'])

    disabled = param.Boolean(default=False)

    label = param.String(default=None, allow_None=True)

    items = param.List(default=[])

    number = param.Number(default=0.5)

    options = param.Dict(default={})

    _esm = 'export function render() {}'


class ESMWithDataDefaultsSubclass(ESMWithDataDefaults):

    count = param.Integer(default=5)


def _spy_data_model_kwargs(monkeypatch, cls):
    kwargs = {}
    init = cls._data_model.__init__

    def spy(self, *args, **kw):
        kwargs.update(kw)
        init(self, *args, **kw)

    monkeypatch.setattr(cls._data_model, '__init__', spy)
    return kwargs


def test_reactive_esm_data_model_drops_default_properties(document, comm, monkeypatch):
    from bokeh.core.serialization import Serializer

    kwargs = _spy_data_model_kwargs(monkeypatch, ESMWithDataDefaults)
    esm = ESMWithDataDefaults(count=2, direction='ltr', disabled=False, number=0.5)
    model = esm.get_root(document, comm)

    assert set(kwargs) == {'count', 'esm_constants', 'name'}
    assert model.data.count == 2

    # The frontend DataModel is generated from the serialized definition,
    # so omitted properties must resolve to the same defaults there.
    serializer = Serializer()
    modeldef = serializer.encode(ESMWithDataDefaults._data_model)
    defaults = {prop['name']: prop.get('default') for prop in modeldef['properties']}
    for name in ('direction', 'disabled', 'label', 'items', 'number', 'options'):
        assert defaults[name] == serializer.encode(getattr(esm, name))
        assert getattr(model.data, name) == getattr(esm, name)


def test_reactive_esm_data_model_respects_subclass_defaults(document, comm, monkeypatch):
    kwargs = _spy_data_model_kwargs(monkeypatch, ESMWithDataDefaultsSubclass)
    esm = ESMWithDataDefaultsSubclass(count=1)
    model = esm.get_root(document, comm)

    assert kwargs['count'] == 1
    assert model.data.count == 1

    kwargs.clear()
    model = ESMWithDataDefaultsSubclass().get_root(Document(), comm)

    assert 'count' not in kwargs
    assert model.data.count == 5


def test_reactive_esm_data_model_matches_unfiltered_model(document, comm, monkeypatch):
    from bokeh.model import DataModel

    import panel.custom

    esm = ESMWithDataDefaults(count=2, label='foo', items=[1], options={})
    data = esm.get_root(document, comm).data

    drop = panel.custom.drop_default_properties
    monkeypatch.setattr(
        panel.custom, 'drop_default_properties',
        lambda model_type, props: props if issubclass(model_type, DataModel) else drop(model_type, props)
    )
    kwargs = _spy_data_model_kwargs(monkeypatch, ESMWithDataDefaults)
    full = esm.get_root(Document(), comm).data

    assert {'direction', 'disabled', 'number'} <= set(kwargs)
    assert data.properties_with_values(include_defaults=False).keys() == full.properties_with_values(include_defaults=False).keys()
    values, full_values = data.properties_with_values(), full.properties_with_values()
    assert values.pop('tags') != full_values.pop('tags')
    assert values == full_values


def test_reactive_esm_data_model_syncs_reset_to_default(document, comm):
    esm = ESMWithDataDefaults(count=2, disabled=True, label='foo')
    model = esm.get_root(document, comm)

    esm.param.update(count=1, disabled=False, label=None)

    assert model.data.count == 1
    assert model.data.disabled is False
    assert model.data.label is None
    assert {'count', 'disabled', 'label'} <= set(model.data._property_values)


def test_reactive_esm_children_append_attaches_without_recompute(document, comm, monkeypatch):
    from bokeh.document.models import DocumentModelManager

    from panel.config import config

    # Inlining the stylesheets of new children in a notebook replaces
    # models, which does require a recompute.
    monkeypatch.setattr(config, 'inline', False)
    md1 = Markdown('foo')
    esm = ESMWithChildren(children=[md1])

    model = esm.get_root(document, comm)
    document.add_root(model)

    recomputes = []
    recompute = DocumentModelManager.recompute
    monkeypatch.setattr(
        DocumentModelManager, 'recompute', lambda self: recomputes.append(1) or recompute(self)
    )

    md2 = Markdown('bar')
    esm.children = [md1, md2]

    ref = model.ref['id']
    assert ref in md1._models and ref in md2._models
    md2_model, _ = md2._models[ref]
    assert model.data.children == [md1._models[ref][0], md2_model]
    assert md2_model.document is document
    assert md2_model.id in document.models._models
    assert not recomputes

    monkeypatch.undo()
    attached = set(document.models._models)
    document.models.recompute()
    assert set(document.models._models) == attached


def test_render_esm_reflects_file_changes(tmp_path):
    esm_file = tmp_path / 'component.js'
    esm_file.write_text('export function render() { return "a" }')

    class ESMFromFile(ReactiveESM):
        _esm = esm_file

    assert 'return "a"' in ESMFromFile._render_esm()

    esm_file.write_text('export function render() { return "b" }')
    stat = esm_file.stat()
    os.utime(esm_file, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))

    assert 'return "b"' in ESMFromFile._render_esm()
