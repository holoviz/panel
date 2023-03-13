from panel.layout import BeforeAfterSlider, Spacer


def test_can_construct():
    before = Spacer(background="red", sizing_mode="stretch_both", height=800)
    after = Spacer(background="green", sizing_mode="stretch_both", height=800)
    return BeforeAfterSlider(
        before, after,
        value=20,
        height=800,
        slider_width=15,
        slider_color="lightgray"
    )
