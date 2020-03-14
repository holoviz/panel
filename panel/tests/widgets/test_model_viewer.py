from panel.widgets.model_viewer import ModelViewer, JAVASCRIPT

# @philippfr: How do I change or set the height and width?
# @Philippfr: Why does Test 2 not show up. Its not in the HTML code either.
if __name__.startswith("bk"):
    import panel as pn
    js_pane = pn.pane.HTML(JAVASCRIPT)
    model_viewer = ModelViewer(height=300, width=300)

    pn.Column(
        js_pane,
        "# Test",
        pn.Row(model_viewer, height=500, width=300),
        "# Test 2",
        # pn.Param(model_viewer, parameters=["html"]),
        height=600, width=600, background="blue"
    ).servable()