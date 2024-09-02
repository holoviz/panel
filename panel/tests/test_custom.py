import param

from panel.custom import ReactiveESM
from panel.pane import Markdown
from panel.viewable import Viewable


class ESMWithChildren(ReactiveESM):

    child = param.ClassSelector(class_=Viewable)

    children = param.List(item_type=Viewable)


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
