import panel as pn
from holoviews import opts
from panel.template.fast.list import FastListDarkTheme, FastListTemplate
from panel.tests.template.fast.test_fast_grid_template import (
    INFO, _create_hvplot, _fast_button_card, _sidebar_items)

ACCENT_COLOR = "#4099da"

opts.defaults(opts.Ellipse(line_width=3, color=ACCENT_COLOR))

def test_template_theme_parameter():
    template = FastListTemplate(title="Fast", theme="dark")
    # Not '#3f3f3f' which is for the Vanilla theme

    doc = template.server_doc()
    assert doc.theme._json['attrs']['Figure']['background_fill_color']=="#181818"

    assert isinstance(template._get_theme(), FastListDarkTheme)


#Todo: header_color must be rgb or #

def test_app():
    pn.config.sizing_mode = "stretch_width"
    app = FastListTemplate(
        title="FastListTemplate w. #ORSOME colors",
        site="Panel",
        accent_base_color=ACCENT_COLOR,
        header_background=ACCENT_COLOR,
        header_color="#FFFFFF",
        header_accent_base_color="#FFFFFF",
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
