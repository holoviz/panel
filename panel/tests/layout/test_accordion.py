import pytest

from bokeh.models import Column as BkColumn, Div

from panel.layout import Accordion
from panel.models import Card
from panel.pane import Pane


@pytest.fixture
def accordion(document, comm):
    """Set up a accordion instance"""
    div1, div2 = Div(), Div()

    return Accordion(('Tab1', div1), ('Tab2', div2))


def assert_tab_is_similar(tab1, tab2):
    """Helper function to check tab match"""
    assert tab1.child is tab2.child
    assert tab1.name == tab2.name
    assert tab1.title == tab2.title


def test_accordion_basic_constructor(document, comm):
    accordion = Accordion('plain', 'text')

    model = accordion.get_root(document, comm=comm)

    assert isinstance(model, BkColumn)
    assert len(model.children) == 2
    assert all(isinstance(c, Card) for c in model.children)
    card1, card2 = model.children

    assert 'plain' in card1.children[1].text
    assert 'text' in card2.children[1].text


def test_accordion_constructor(document, comm):
    div1 = Div()
    div2 = Div()
    accordion = Accordion(('Div1', div1), ('Div2', div2))
    p1, p2 = accordion.objects

    model = accordion.get_root(document, comm=comm)

    assert isinstance(model, BkColumn)
    assert len(model.children) == 2
    assert all(isinstance(c, Card) for c in model.children)
    card1, card2 = model.children

    assert card1.children[0].children[0].text == 'Div1'
    assert card1.children[1] is div1
    assert card2.children[0].children[0].text == 'Div2'
    assert card2.children[1] is div2


def test_accordion_implicit_constructor(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    accordion = Accordion(p1, p2)

    model = accordion.get_root(document, comm=comm)

    assert isinstance(model, BkColumn)
    assert len(model.children) == 2
    assert all(isinstance(c, Card) for c in model.children)
    card1, card2 = model.children

    assert card1.children[0].children[0].text == p1.name == 'Div1'
    assert card1.children[1] is div1
    assert card2.children[0].children[0].text == p2.name == 'Div2'
    assert card2.children[1] is div2


def test_accordion_constructor_with_named_objects(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    accordion = Accordion(('Tab1', p1), ('Tab2', p2))

    model = accordion.get_root(document, comm=comm)

    assert isinstance(model, BkColumn)
    assert len(model.children) == 2
    assert all(isinstance(c, Card) for c in model.children)
    card1, card2 = model.children

    assert card1.children[0].children[0].text == 'Tab1'
    assert card1.children[1] is div1
    assert card2.children[0].children[0].text == 'Tab2'
    assert card2.children[1] is div2


def test_accordion_cleanup_panels(document, comm, accordion):
    model = accordion.get_root(document, comm=comm)
    card1, card2 = accordion._panels.values()

    assert model.ref['id'] in card1._models
    assert model.ref['id'] in card2._models
    accordion._cleanup(model)
    assert model.ref['id'] not in card1._models
    assert model.ref['id'] not in card2._models


def test_accordion_active(document, comm, accordion):
    model = accordion.get_root(document, comm=comm)

    assert model.children[0].collapsed
    assert model.children[1].collapsed
    accordion.active = [1]
    assert model.children[0].collapsed
    assert not model.children[1].collapsed
    accordion.active = [0]
    assert not model.children[0].collapsed
    assert model.children[1].collapsed
    accordion.active = []
    assert model.children[0].collapsed
    assert model.children[1].collapsed
    accordion.active = [0, 1]
    assert not model.children[0].collapsed
    assert not model.children[1].collapsed


def test_accordion_set_card_collapsed(document, comm, accordion):
    accordion.get_root(document, comm=comm)

    events = []

    accordion.param.watch(lambda e: events.append(e), 'active')

    c1, c2 = accordion._panels.values()

    c1.collapsed = False
    assert accordion.active == [0]

    assert len(events) == 1

    c2.collapsed = False
    assert accordion.active == [0, 1]

    assert len(events) == 2

    c1.collapsed = True
    c2.collapsed = True
    assert accordion.active == []

    assert len(events) == 4


def test_accordion_set_card_collapsed_toggle(document, comm, accordion):
    accordion.toggle = True
    accordion.get_root(document, comm=comm)

    events = []

    accordion.param.watch(lambda e: events.append(e), 'active')

    c1, c2 = accordion._panels.values()

    c1.collapsed = False
    assert accordion.active == [0]

    assert len(events) == 1

    c2.collapsed = False
    assert accordion.active == [1]

    assert len(events) == 2
