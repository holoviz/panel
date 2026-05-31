import numpy as np
import pandas as pd
import param

from bokeh.plotting import figure

from panel.custom import PyComponent, ReactiveESM
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


class ESMBundle(ReactiveESM):

    _bundle_path = "esm.js"  # type: ignore[assignment]


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


class ESMWithChildren(ReactiveESM):

    child = Child(doc="""A child Viewable to be displayed in the ESM.""")

    children = Children(doc="""Child Viewables to be displayed in the ESM.""")


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
