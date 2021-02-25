import panel as pn

from panel.template.fast import FastListTemplate

from panel.tests.template.fast.test_fast_grid_template import (
    _create_hvplot,
    _fast_button_card,
    _sidebar_items,
    INFO,
)


def test_app():
    pn.config.sizing_mode = "stretch_width"
    app = FastListTemplate(
        title="FastListTemplate",
    )
    app.main[:] = [
        pn.pane.Markdown(INFO, sizing_mode="stretch_both"),
        pn.pane.HoloViews(_create_hvplot(), sizing_mode="stretch_both"),
        _fast_button_card(),
        pn.pane.HoloViews(_create_hvplot(), sizing_mode="stretch_both"),
    ]
    app.sidebar.extend(_sidebar_items())

    return app


if __name__.startswith("bokeh"):
    test_app().servable()
