"""The FastTemplateSettings widget enables you to change the look and feel of the
FastListTemplate and FastGridTemplate dynamically on a live app.

Add it to the sidebar of your template to dynamically change the settings of the Template.

If you need more control you can add the `comms` and `editor` components individually
instead."""
import param

from ....layout import Column, Row
from ....pane import HTML, Markdown
from ....param import Param
from ....viewable import Viewer
from ....widgets import Button, ColorPicker, TextAreaInput
from ..base import FastBaseTemplate
from ..grid import FastGridTemplate
from ..list import FastListTemplate
from .fast_design_provider import FastDesignProvider

PALETTE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="1em" viewBox="0 0 512 512" ><path fill="var(--accent-fill-rest)" d="M 204.3 5 C 104.9 24.4 24.8 104.3 5.2 203.4 c -37 187 131.7 326.4 258.8 306.7 c 41.2 -6.4 61.4 -54.6 42.5 -91.7 c -23.1 -45.4 9.9 -98.4 60.9 -98.4 h 79.7 c 35.8 0 64.8 -29.6 64.9 -65.3 C 511.5 97.1 368.1 -26.9 204.3 5 Z M 96 320 c -17.7 0 -32 -14.3 -32 -32 s 14.3 -32 32 -32 s 32 14.3 32 32 s -14.3 32 -32 32 Z m 32 -128 c -17.7 0 -32 -14.3 -32 -32 s 14.3 -32 32 -32 s 32 14.3 32 32 s -14.3 32 -32 32 Z m 128 -64 c -17.7 0 -32 -14.3 -32 -32 s 14.3 -32 32 -32 s 32 14.3 32 32 s -14.3 32 -32 32 Z m 128 64 c -17.7 0 -32 -14.3 -32 -32 s 14.3 -32 32 -32 s 32 14.3 32 32 s -14.3 32 -32 32 Z" /></svg>
""" # noqa: E501

GEAR_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="1.3em" style="display: inline-block;vertical-align: middle;" fill="currentColor" class="bi bi-gear" viewBox="0 0 16 16">
  <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
  <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115l.094-.319z"/>
</svg>
""" # noqa: E501


class FastTemplateSettings(Viewer):
    template = param.ClassSelector(
        class_=FastBaseTemplate,
        constant=True,
        doc="""
        The Fast Template to edit""",
    )
    template_constructor = param.String(
        constant=True,
        doc="""
        The Python code needed to construct a Template with the same parameter settings""",
    )
    editor = param.ClassSelector(
        class_=Column,
        constant=True,
        doc="""
        A Column containing the settings editor. You would need to also include the `comms` in
        your app to enable bidirectional communication.
        """,
    )
    comms = param.ClassSelector(
        class_=Column,
        constant=True,
        doc="""The component that provides bidirectional communication to set and get the style
        values. Include this in your app if you want to enable changing Template settings
        dynamically.""",
    )

    def __init__(self, template):
        """The FastTemplateSettings component enables you to change the look and feel of the
        FastListTemplate and FastGridTemplate dynamically on a live app.

        Add it to the sidebar of your template to dynamically change the settings of the Template.

        If you need more control you can add the `comms` and `editor` components individually
        instead."""

        params = {}
        params["template"] = template
        params["editor"] = Column(sizing_mode="stretch_width", margin=0)
        params["comms"] = Column(
            sizing_mode="fixed",
            height=0,
            width=0,
            margin=0,
        )

        super().__init__(**params)

        self._create_layout()
        self._update_template_constructor()

    @param.depends("template.background_color", watch=True)
    def _sync_background_color(self):
        self._body_provider.background_color = self.template.background_color

    @param.depends("template.accent_base_color", watch=True)
    def _sync_accent_base_color(self):
        self._body_provider.accent_base_color = self.template.accent_base_color

    @param.depends("template.neutral_color", watch=True)
    def _sync_neutral_color(self):
        self._body_provider.neutral_color = self.template.neutral_color

    @param.depends("template.corner_radius", watch=True)
    def _sync_corner_radius(self):
        self._body_provider.corner_radius = self.template.corner_radius

    @param.depends("template.header_background", watch=True)
    def _sync_header_background_color(self):
        self._header_provider.background_color = self.template.header_background

    @param.depends("template.header_accent_base_color", watch=True)
    def _sync_header_accent_base_color(self):
        self._header_provider.accent_base_color = self.template.header_accent_base_color

    def _create_layout(self):
        self._body_settings = Param(
            self.template,
            parameters=[
                "background_color",
                "neutral_color",
                "accent_base_color",
                "corner_radius",
                "font",
                "shadow",
                "main_layout",
            ],
            widgets={
                "background_color": ColorPicker,
                "neutral_color": ColorPicker,
                "accent_base_color": ColorPicker,
            },
            name="Body",
            sizing_mode="stretch_width",
        )
        self._header_settings = Param(
            self.template,
            parameters=[
                "header_background",
                "header_color",
                "header_accent_base_color",
            ],
            widgets={
                "header_background": ColorPicker,
                "header_color": ColorPicker,
                "header_accent_base_color": ColorPicker,
            },
            name="Header",
            sizing_mode="stretch_width",
        )
        self.editor[:] = [self._body_settings, self._header_settings]

        self._body_provider = FastDesignProvider(provider="body-design-provider")
        self._header_provider = FastDesignProvider(provider="header-design-provider")
        self._styles = HTML(width=0, height=0, sizing_mode="fixed", margin=0)
        self.comms[:] = [self._body_provider, self._header_provider, self._styles]

        self.layout = Column(
            HTML(f"<h3>{GEAR_SVG} Template Settings</h3>", margin=(0, 10, 0, 10)),
            self._body_settings,
            self._header_settings,
            self._body_provider,
            self._header_provider,
            self._styles,
            sizing_mode="stretch_width",
            margin=0,
        )

    @param.depends(
        "template.background_color",
        "template.shadow",
        "template.font",
        "template.main_layout",
        "template.header_color",
        watch=True,
    )
    def _update_styles(self):
        html = f"""<style>
body {{
    background: {self.template.background_color}
}}
"""
        if self.template.shadow:
            html += """
        #sidebar, #header {
            box-shadow: 2px 2px 10px silver;
        }
        """
        else:
            html += """
        #sidebar, #header {
            box-shadow: none;
        }
        """

        if self.template.font:
            html += f""":root {{
    --body-font: { self.template.font };
}}"""

        if self.template.main_layout == "":
            html += ".pn-wrapper {display: contents;}"

        if self.template.header_color:
            html += f"""
#header-design-provider {{
    --neutral-foreground-rest: { self.template.header_color };
}}
"""

        html += "</style>"
        self._styles.object = html

    @param.depends(
        "template.background_color",
        "template.neutral_color",
        "template.accent_base_color",
        "template.corner_radius",
        "template.font",
        "template.main_layout",
        "template.shadow",
        "template.header_background",
        "template.header_color",
        "template.header_accent_base_color",
        watch=True,
    )
    def _update_template_constructor(self):
        tmp = self.template
        with param.edit_constant(self):
            self.template_constructor = f"""template={type(tmp).name}(
    site='{tmp.site}',
    title='{tmp.title}',
    background_color='{tmp.background_color}',
    neutral_color='{tmp.neutral_color}',
    accent_base_color='{tmp.accent_base_color}',
    corner_radius={tmp.corner_radius},
    font='{tmp.font}',
    main_layout='{tmp.main_layout}',
    shadow={tmp.shadow},
    header_background='{tmp.header_background}',
    header_color='{tmp.header_color}',
    header_accent_base_color='{tmp.header_accent_base_color}',
)"""

    def __panel__(self):
        return self.layout

    @classmethod
    def create_list_designer(cls):
        template = FastListTemplate(
            site="Panel",
            title="FastListTemplate Designer",
            font="Comic Sans MS",
        )
        fast_template_settings = cls(template)

        template.sidebar[:] = [
            fast_template_settings,
        ]

        (
            body_colors_panel,
            header_colors_panel,
            panel_buttons_panel,
            template_constructor_panel,
        ) = FastTemplateSettings._create_main_app_components(fast_template_settings)
        template.main[:] = [
            body_colors_panel,
            header_colors_panel,
            panel_buttons_panel,
            template_constructor_panel,
        ]
        return template

    @classmethod
    def create_grid_designer(cls):
        template = FastGridTemplate(
            site="Panel",
            title="FastGridTemplate Designer",
            font="Comic Sans MS",
            row_height=10,
            prevent_collision=True,
            save_layout=True,
        )
        fast_template_settings = cls(template)

        template.sidebar[:] = [
            fast_template_settings,
        ]

        (
            body_colors_panel,
            header_colors_panel,
            panel_buttons_panel,
            template_constructor_panel,
        ) = FastTemplateSettings._create_main_app_components(fast_template_settings)
        template.main[0:9, :] = body_colors_panel
        template.main[9:17, :] = header_colors_panel
        template.main[17:25, :] = panel_buttons_panel
        template.main[25:45, :] = template_constructor_panel
        return template

    @staticmethod
    def _create_main_app_components(fast_template_settings):
        body_colors_panel = HTML(sizing_mode="stretch_width", height=130)
        header_colors_panel = HTML(sizing_mode="stretch_width", height=130)
        panel_buttons_panel = Column(
            Markdown("## Panel Buttons"),
            Row(
                Button(name="DEFAULT", button_type="default"),
                Button(name="PRIMARY", button_type="primary"),
                Button(name="SUCCESS", button_type="success"),
                Button(name="WARNING", button_type="warning"),
                Button(name="DANGER", button_type="danger"),
            ),
            name="Panel Widgets",
        )

        @param.depends(fast_template_settings._body_provider.param.updates, watch=True)
        def _update_body_html(*_):
            body_colors_panel.object = (
                f"<h2>{PALETTE_SVG} Body Colors </h2>\n\n"
                + fast_template_settings._body_provider.to_html()
            )

        _update_body_html()

        @param.depends(fast_template_settings._header_provider.param.updates, watch=True)
        def _update_header_html(*_):
            header_colors_panel.object = (
                f"<h2>{PALETTE_SVG} Header Colors </h2>\n\n"
                + fast_template_settings._header_provider.to_html()
            )

        _update_header_html()

        template_constructor_panel = Param(
            fast_template_settings,
            parameters=["template_constructor"],
            widgets={
                "template_constructor": {
                    "type": TextAreaInput,
                    "sizing_mode": "stretch_width",
                    "height": 300,
                    "disabled": True,
                    "name": "",
                }
            },
            name="Template Constructor",
        )
        return (
            body_colors_panel,
            header_colors_panel,
            panel_buttons_panel,
            template_constructor_panel,
        )
