from bokeh.models import Div

from panel.layout import Card
from panel.models import Card as CardModel
from panel.pane import HTML


def test_card_model_cache_cleanup(document, comm):
    html = HTML()
    l = Card(header=html)

    model = l.get_root(document, comm)
    ref = model.ref['id']
    
    assert ref in l._models
    assert l._models[ref] == (model, None)
    assert ref in html._models

    l._cleanup(model)
    assert l._models == {}
    assert html._models == {}


def test_card_get_root(document, comm):
    div1 = Div()
    div2 = Div()
    layout = Card(div1, div2)

    model = layout.get_root(document, comm=comm)
    ref = model.ref['id']
    header = layout._header_layout._models[ref][0]

    assert isinstance(model, CardModel)
    assert model.children == [header, div1, div2]
    assert header.children[0].text == "&amp;#8203;"


def test_card_get_root_title(document, comm):
    div1 = Div()
    div2 = Div()
    layout = Card(div1, div2, title='Test')

    model = layout.get_root(document, comm=comm)
    ref = model.ref['id']
    header = layout._header_layout._models[ref][0]

    assert isinstance(model, CardModel)
    assert model.children == [header, div1, div2]
    assert header.children[0].text == "Test"

    div3 = Div()
    layout.header = div3
    assert header.children[0] is div3

    layout.header = None
    assert header.children[0].text == "Test"


def test_card_get_root_header(document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = Card(div1, div2, header=div3)

    model = layout.get_root(document, comm=comm)
    ref = model.ref['id']
    header = layout._header_layout._models[ref][0]

    assert isinstance(model, CardModel)
    assert model.children == [header, div1, div2]
    assert header.children[0] is div3
