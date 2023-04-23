from panel.layout import Spacer, Swipe


def test_swip_construct(document, comm):
    before = Spacer(background="red", height=400, width=800)
    after = Spacer(background="green", height=400, width=800)
    swipe = Swipe(
        before,
        after,
        value=20,
        height=800,
        slider_width=15,
        slider_color="lightgray"
    )

    model = swipe.get_root(document, comm)

    assert model.children == {
        'before-inner': [before._models[model.ref['id']][0]],
        'after-inner': [after._models[model.ref['id']][0]]
    }
