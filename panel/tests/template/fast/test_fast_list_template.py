import panel as pn

from panel.template.fast.list import FastListTemplate, FastListDarkTheme

from panel.tests.template.fast.test_fast_grid_template import (
    _create_hvplot,
    _fast_button_card,
    _sidebar_items,
    INFO,
)

def test_template_theme_parameter():
    template = FastListTemplate(title="Fast", theme="dark")
    # Not '#3f3f3f' which is for the Vanilla theme

    doc = template.server_doc()
    assert doc.theme._json['attrs']['Figure']['background_fill_color']=="#181818"

    assert isinstance(template._get_theme(), FastListDarkTheme)

    
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
