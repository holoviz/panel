from panel.layout import BeforeAfterSlider
import panel as pn

def test_can_construct():

    before = pn.Spacer(background="red", sizing_mode="stretch_both", height=800)
    after = pn.Spacer(background="green", sizing_mode="stretch_both", height=800)

    return BeforeAfterSlider(
        value=20,
        before=before,
        after=after,
        height=800,
        slider_width=15,
        slider_color="lightgray"
    )

if __name__.startswith("bokeh"):
    import hvplot.pandas
    import pandas as pd
    pn.extension(sizing_mode="stretch_width")

    ACCENT_COLOR = "#D2386C"

    data = pd.DataFrame({"y": range(10)})
    before = data.hvplot().opts(color="green", line_width=6, responsive=True, height=700)
    after = data.hvplot().opts(color="red", line_width=6, responsive=True, height=700)

    before = pn.Spacer(background="red", sizing_mode="stretch_both")
    after = pn.Spacer(background="green", sizing_mode="stretch_both")

    before_after = BeforeAfterSlider(value=20, before=before, after=after, height=600)
    controls = pn.Param(before_after, parameters=["value", "slider_width", "slider_color"])
    pn.template.FastListTemplate(
        site="Awesome Panel",
        title="Before After Slider",
        sidebar=[controls],
        main=[before_after],
        accent_base_color=ACCENT_COLOR,
        header_background=ACCENT_COLOR,
    ).servable()