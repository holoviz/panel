"""The Label visualizes the `labels` of a classification

- It automatically determines the `theme` from the query args
- It allows you to change the color
"""
import panel as pn

ACCENT_COLOR = "#0072B5"

def test_label(height=800):
    """Test the Label constructor"""
    labels = {"egyptian": 0.22, "tabby cat": 0.18, "tiger cat": 0.13, "lynx": 0.09, "Siamese cat": 0.04}
    # labels = [{"label": key, "score": value} for key, value in labels.items()]
    plot = pn.indicators.Label(
        value=labels,
        color=ACCENT_COLOR,
        height=height,
        sizing_mode="stretch_width",
    )
    return plot


if __name__.startswith("bokeh"):
    pn.extension(sizing_mode="stretch_width")
    labels = test_label()
    labels_small = test_label(height=300)
    
    pn.template.FastListTemplate(
        title="ClassificationPlot",
        sidebar=[labels.controls(jslink=True)],
        main=[labels, labels_small],
        accent_base_color=ACCENT_COLOR, header_background=ACCENT_COLOR
    ).servable()
