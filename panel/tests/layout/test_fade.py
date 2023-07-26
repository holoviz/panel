from panel.layout import Fade, Spacer


def test_fade_construct(document, comm):
    obj_0 = Spacer(styles={"background": "red"}, height=400, width=800)
    obj_1 = Spacer(styles={"background": "green"}, height=400, width=800)
    obj_2 = Spacer(styles={"background": "yellow"}, height=400, width=800)
    swipe = Fade(
        obj_0,
        obj_1,
        obj_2,
        value=20,
        height=800,
        slider_width=15,
        slider_color="lightgray"
    )

    model = swipe.get_root(document, comm)
    assert model.children == {
        'object-inner': [
            obj_0._models[model.ref['id']][0],
            obj_1._models[model.ref['id']][0],
            obj_2._models[model.ref['id']][0]
        ]
    }
