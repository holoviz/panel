import param
import pytest

from bokeh.models import Div

from panel.custom import Child, JSComponent
from panel.layout import (
    Column, GridSpec, Row, Tabs,
)
from panel.pane import Bokeh
from panel.reactive import ReactiveHTML
from panel.viewable import Viewable
from panel.widgets import TextInput


class ESMChild(JSComponent):

    child = Child()

    _esm = "export function render({ model }) {}"


class HTMLChild(ReactiveHTML):

    child = param.ClassSelector(class_=Viewable, allow_refs=False)

    _template = "<div id='container'>${child}</div>"


def _render_shared(container, document, comm):
    widget = TextInput(value='A')
    if container is Tabs:
        other = Tabs(('A', widget))
    elif container is GridSpec:
        other = GridSpec()
        other[0, 0] = widget
    elif container is ESMChild:
        other = ESMChild(child=widget)
    elif container is HTMLChild:
        other = HTMLChild(child=widget)
    else:
        other = container(widget)
    row = Row(widget)
    layout = Column(row, other)
    root = layout.get_root(document, comm)
    return widget, row, other, layout, root


containers = [Row, Tabs, GridSpec, ESMChild, HTMLChild]


@pytest.mark.parametrize('container', containers)
def test_shared_object_reuses_model(container, document, comm):
    widget, row, other, _, root = _render_shared(container, document, comm)
    ref = root.ref['id']

    model = widget._models[ref][0]
    assert row._models[ref][0].children[0] is model
    assert other._models[ref][0] in widget._model_parents[ref]
    assert len(widget._model_parents[ref]) == 2

    widget.value = 'B'
    assert model.value == 'B'


@pytest.mark.parametrize('container', containers)
def test_shared_object_removed_from_one_parent(container, document, comm):
    widget, row, other, _, root = _render_shared(container, document, comm)
    ref = root.ref['id']
    model = widget._models[ref][0]

    row.objects = []

    assert widget._models[ref][0] is model
    assert model._callbacks
    widget.value = 'B'
    assert model.value == 'B'


@pytest.mark.parametrize('container', containers)
def test_shared_object_removed_from_all_parents(container, document, comm):
    widget, row, other, layout, root = _render_shared(container, document, comm)
    ref = root.ref['id']

    layout.objects = []

    assert ref not in widget._models
    assert ref not in widget._model_parents


@pytest.mark.parametrize('container', containers)
def test_shared_object_root_cleanup(container, document, comm):
    widget, _, _, layout, root = _render_shared(container, document, comm)

    layout._cleanup(root)

    assert widget._models == {}
    assert widget._model_parents == {}


def test_shared_object_readded_to_parent(document, comm):
    widget, row, _, _, root = _render_shared(Row, document, comm)
    ref = root.ref['id']
    model = widget._models[ref][0]

    row.objects = []
    row.objects = [widget]

    assert row._models[ref][0].children[0] is model
    assert len(widget._model_parents[ref]) == 2


def test_shared_pane_rerender_replaces_model_in_all_parents(document, comm):
    pane = Bokeh(Div(text='A'))
    row1, row2 = Row(pane), Row(pane)
    layout = Column(row1, row2)
    root = layout.get_root(document, comm)
    ref = root.ref['id']

    div = Div(text='B')
    pane.object = div

    assert pane._models[ref][0] is div
    assert row1._models[ref][0].children[0] is div
    assert row2._models[ref][0].children[0] is div
