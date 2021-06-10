from panel.template.fast import FastStyle
from panel.template import FastListTemplate
import panel as pn


def test_constructor():
    FastStyle(
        background="#000000",
        neutral_color="#ffffff",
        accent_color="#aabbcc",
    )


PALETTE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="1em" viewBox="0 0 512 512" ><path fill="var(--accent-fill-rest)" d="M 204.3 5 C 104.9 24.4 24.8 104.3 5.2 203.4 c -37 187 131.7 326.4 258.8 306.7 c 41.2 -6.4 61.4 -54.6 42.5 -91.7 c -23.1 -45.4 9.9 -98.4 60.9 -98.4 h 79.7 c 35.8 0 64.8 -29.6 64.9 -65.3 C 511.5 97.1 368.1 -26.9 204.3 5 Z M 96 320 c -17.7 0 -32 -14.3 -32 -32 s 14.3 -32 32 -32 s 32 14.3 32 32 s -14.3 32 -32 32 Z m 32 -128 c -17.7 0 -32 -14.3 -32 -32 s 14.3 -32 32 -32 s 32 14.3 32 32 s -14.3 32 -32 32 Z m 128 -64 c -17.7 0 -32 -14.3 -32 -32 s 14.3 -32 32 -32 s 32 14.3 32 32 s -14.3 32 -32 32 Z m 128 64 c -17.7 0 -32 -14.3 -32 -32 s 14.3 -32 32 -32 s 32 14.3 32 32 s -14.3 32 -32 32 Z" /></svg>
"""

GEAR_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="1em" fill="currentColor" class="bi bi-gear" viewBox="0 0 16 16">
  <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
  <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115l.094-.319z"/>
</svg>
"""


def test_styler_app():
    template = FastListTemplate(
        site="Awesome Panel",
        title="Fast Template Style")
    style = FastStyle()
    html_pane = pn.pane.HTML(sizing_mode="stretch_width", height=200)
    panel_widgets_panel = pn.Column(
        pn.pane.Markdown("## Panel Buttons"),
        pn.Row(
            pn.widgets.Button(name="DEFAULT", button_type="default"),
            pn.widgets.Button(name="PRIMARY", button_type="primary"),
            pn.widgets.Button(name="SUCCESS", button_type="success"),
            pn.widgets.Button(name="WARNING", button_type="warning"),
            pn.widgets.Button(name="DANGER", button_type="danger"),
        ),
        name="Panel Widgets",
    )

    @pn.depends(style.param.updates, watch=True)
    def _update_html(*_):
        print("update html")
        html_pane.object = f"<h2>{PALETTE_SVG} Colors </h2>\n\n" + style.to_html()

    _update_html()
    styler_settings = pn.Param(
        style,
        parameters=[
            "provider",
            "background_color",
            "neutral_color",
            "accent_base_color",
            "corner_radius",
            "body_font",
        ],
        sizing_mode="stretch_width",
        margin=0,
    )
    template.sidebar[:] = [
        pn.pane.HTML(f"<h2>{GEAR_SVG} Settings</h2>", margin=(0, 10, 0, 10)),
        styler_settings,
        style,
    ]
    template.main[:] = [
        html_pane,
        panel_widgets_panel,
    ]
    return template


if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"
    test_styler_app().servable()
