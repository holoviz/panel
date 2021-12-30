"""The Label visualizes the `labels` of a classification

- It automatically determines the `theme` from the query args
- It allows you to change the color
"""
import panel as pn

ACCENT_COLOR = "#0072B5"

def test_scores(height=600, sizing_mode="stretch_width", name="Large"):
    """Test the Label constructor"""
    labels = {"egyptian": 0.22, "tabby cat": 0.18, "tiger cat": 0.13, "lynx": 0.09, "Siamese cat": 0.04, "aaa": 0.01, "bbb": 0.01, "ccc": 0.01, "ddd": 0.01, "eee": 0.01}
    # labels = [{"label": key, "score": value} for key, value in labels.items()]
    label = pn.indicators.Scores(
        value=labels,
        color=ACCENT_COLOR,
        height=height,
        sizing_mode=sizing_mode,
        name=name
    )
    return label

def test_indicator_change():
    value = {"egyptian": 0.22, "tabby cat": 0.18, "tiger cat": 0.13, "lynx": 0.09, "Siamese cat": 0.04}    
    label = pn.indicators.Scores(value=value)
    assert len(label.top_value)==5
    assert label.top_value[0]=={"label": "egyptian", "score": 0.22}
    
    # When/ Then
    label.value = {"egyptian": 0.22, "tabby cat": 0.28, "tiger cat": 0.13, "lynx": 0.09, "Siamese cat": 0.04}
    assert len(label.top_value)==5
    assert label.top_value[0]=={"label": "tabby cat", "score": 0.28}

    # When/ Then
    label.top=3
    assert len(label.top_value)==3
    

if __name__.startswith("bokeh"):
    pn.extension()
    labels = test_scores(height=600)
    labels_small = test_scores(height=300, sizing_mode="stretch_width", name="Small")
    
    pn.template.FastListTemplate(
        title="Scores",
        sidebar=[pn.Param(labels, parameters=["top", "color", "value", "sizing_mode", "width", "height"]), pn.Param(labels_small, parameters=["top", "color", "value", "sizing_mode", "width", "height"])],
        main=[pn.Column(labels, sizing_mode="stretch_both"), pn.Column(labels_small, sizing_mode="stretch_both")],
        accent_base_color=ACCENT_COLOR, header_background=ACCENT_COLOR
    ).servable()
