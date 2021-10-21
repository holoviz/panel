from panel.layout import Spacer


def test_spacer(document, comm):
    spacer = Spacer(width=400, height=300)

    model = spacer.get_root(document, comm=comm)

    assert isinstance(model, spacer._bokeh_model)
    assert model.width == 400
    assert model.height == 300

    spacer.height = 400
    assert model.height == 400


def test_spacer_clone():
    spacer = Spacer(width=400, height=300)
    clone = spacer.clone()
    assert ({k: v for k, v in spacer.param.values().items() if k != 'name'} ==
            {k: v for k, v in clone.param.values().items() if k != 'name'})
