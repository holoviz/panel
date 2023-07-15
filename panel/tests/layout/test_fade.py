from panel.layout import Fade, Spacer


def test_fade_construct(document, comm):
    before = Spacer(styles={"background": "red"}, height=400, width=800)
    after = Spacer(styles={"background": "green"}, height=400, width=800)
    swipe = Fade(
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
