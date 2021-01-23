"""The GridBaseTemplate is a copy of the ReactTemplate"""
import pathlib

import panel as pn
import param
from panel.depends import depends
from panel.layout import Card, GridSpec
from panel.template.base import BasicTemplate as _PnBasicTemplate


# pylint: disable=unused-variable, invalid-name, line-too-long
class TemplateConfig(param.Parameterized):
    """Configuration similar to panel.config"""

    css_files = param.Dict(constant=True)

    def __init__(self, **params):
        params["css_files"] = params.get("css_files", {})
        super().__init__(**params)


class BasicTemplate(_PnBasicTemplate):
    """Improvement of Panel BasicTemplate"""

    _theme = "default"

    sidebar_footer = param.String("", doc="""A HTML string appended to the sidebar""")
    enable_theme_toggle = param.Boolean(
        default=True, doc="If True a switch to toggle the Theme is shown. Default is True"
    )
    config = param.ClassSelector(class_=TemplateConfig, doc="Similar to panel.config")

    def __init__(self, **params):
        if "theme" not in params:
            if params.get("enable_theme_toggle", self.param.enable_theme_toggle.default):
                self._theme = self._get_theme_from_query_args(default=self._theme)
            params["theme"] = self._get_theme(self._theme)
        else:
            if isinstance(params["theme"], str):
                params["theme"] = self._get_theme(params["theme"])
            if "dark" in str(params["theme"]).lower():
                self._theme = "dark"
            else:
                self._theme = "default"
        params["config"] = params.get("config", TemplateConfig())
        super().__init__(**params)

        if "header_color" not in params:
            self.header_color = self.theme.style.header_color
        if "header_background" not in params:
            self.header_background = self.theme.style.header_background
        self._update_special_render_vars()

    @staticmethod
    def _get_theme_from_query_args(default: str = "default") -> str:
        theme_arg = pn.state.session_args.get("theme", default)
        if isinstance(theme_arg, list):
            theme_arg = theme_arg[0].decode("utf-8")
            theme_arg = theme_arg.strip("'").strip('"')
        return theme_arg

    def _get_theme(self, name: str = "default"):
        """Should be implemented in child classes"""
        raise NotImplementedError()

    def _update_special_render_vars(self):
        self._render_variables["css_base"] = pathlib.Path(self._css).read_text()
        self._render_variables["css_theme"] = pathlib.Path(self.theme.css).read_text()
        self._render_variables["js"] = pathlib.Path(self._js).read_text()
        self._render_variables["theme"] = self._theme
        self._render_variables["style"] = self.theme.style
        self._render_variables["enable_theme_toggle"] = self.enable_theme_toggle
        self._render_variables["sidebar_footer"] = self.sidebar_footer
        self._render_variables["config"] = self.config


class GridBasicTemplate(BasicTemplate):
    """The GridBaseTemplate is an improvement of the ReactTemplate"""

    compact = param.ObjectSelector(default=None, objects=[None, "vertical", "horizontal", "both"])

    cols = param.Dict(default={"lg": 12, "md": 10, "sm": 6, "xs": 4, "xxs": 2})

    breakpoints = param.Dict(default={"lg": 1200, "md": 996, "sm": 768, "xs": 480, "xxs": 0})

    main = param.ClassSelector(
        class_=GridSpec,
        constant=True,
        doc="""
        A list-like container which populates the main area.""",
    )

    row_height = param.Integer(default=50)

    enable_theme_selection = param.Boolean(
        default=True,
        doc="""If True it will be possible for the
    user to toggle between the 'default' and 'dark' theme. Default""",
    )

    _modifiers = {Card: {"children": {"margin": (20, 20)}, "margin": (10, 5)}}

    _resources = {
        "js": {
            "react": "https://unpkg.com/react@16/umd/react.development.js",
            "react-dom": "https://unpkg.com/react-dom@16/umd/react-dom.development.js",
            "babel": "https://unpkg.com/babel-standalone@latest/babel.min.js",
            "react-grid": "https://cdnjs.cloudflare.com/ajax/libs/react-grid-layout/1.1.1/react-grid-layout.min.js",
        },
        "css": {},
    }

    def __init__(self, **params):
        if "main" not in params:
            params["main"] = GridSpec(ncols=12, mode="override")
        super().__init__(**params)
        self._update_render_vars()

    def _get_theme(self, name: str = "default"):
        """Should be implemented in child classes"""
        raise NotImplementedError()

    def _update_render_items(self, event):
        super()._update_render_items(event)
        if event.obj is not self.main:
            return
        layouts = []
        for i, ((y0, x0, y1, x1), v) in enumerate(self.main.objects.items()):
            if x0 is None:
                x0 = 0
            if x1 is None:
                x1 = 12
            if y0 is None:
                y0 = 0
            if y1 is None:
                y1 = self.main.nrows
            layouts.append({"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0, "i": str(i + 1)})
        self._render_variables["layouts"] = {"lg": layouts, "md": layouts}

    @depends("cols", "breakpoints", "row_height", "compact", watch=True)
    def _update_render_vars(self):
        self._render_variables["breakpoints"] = self.breakpoints
        self._render_variables["cols"] = self.cols
        self._render_variables["rowHeight"] = self.row_height
        self._render_variables["compact"] = self.compact
