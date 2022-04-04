import pathlib

import param

from ...io.state import state
from ..base import BasicTemplate
from ..react import ReactTemplate
from ..theme import THEMES, DefaultTheme

_ROOT = pathlib.Path(__file__).parent


class FastBaseTemplate(BasicTemplate):

    accent_base_color = param.String(default="#0072B5", doc="""
        Optional body accent color override.""")

    background_color = param.String(doc="""
        Optional body background color override.""")

    corner_radius = param.Integer(default=3, bounds=(0,25), doc="""
        The corner radius applied to controls.""")

    font = param.String(doc="""
        The font to use.""")

    font_url = param.String(doc="""
        A font url to import.""")

    header_neutral_color = param.String(doc="""
        Optional header neutral color override.""")

    header_accent_base_color = param.String(doc="""
        Optional header accent color override.""")

    neutral_color = param.String(doc="""
        Optional body neutral color override.""")

    theme_toggle = param.Boolean(default=True, doc="""
        If True a switch to toggle the Theme is shown.""")

    shadow = param.Boolean(doc="""
        Optional shadow override. Whether or not to apply shadow.""")

    sidebar_footer = param.String("", doc="""
        A HTML string appended to the sidebar""")

    # Might be extended to accordion or tabs in the future
    main_layout = param.Selector(default="card", label="Layout", objects=["", "card"], doc="""
        What to wrap the main components into. Options are '' (i.e. none) and 'card' (Default).
        Could be extended to Accordion, Tab etc. in the future.""")

    _css = [
        _ROOT / "css/fast_root.css",
        _ROOT / "css/fast_bokeh.css",
        _ROOT / "css/fast_bokeh_slickgrid.css",
        _ROOT / "css/fast_panel.css",
        _ROOT / "css/fast_panel_dataframe.css",
        _ROOT / "css/fast_panel_widgets.css",
        _ROOT / "css/fast_panel_markdown.css",
        _ROOT / "css/fast_awesome.css"
    ]

    _js = _ROOT / "js/fast_template.js"

    _resources = {
        'js_modules': {
            'fast-colors': 'https://unpkg.com/@microsoft/fast-colors@5.1.4',
            'fast': 'https://unpkg.com/@microsoft/fast-components@1.21.8'
        },
        'bundle': False
    }

    __abstract = True

    def __init__(self, **params):
        query_theme = self._get_theme_from_query_args()
        if query_theme:
            params['theme'] = THEMES[query_theme]
        elif "theme" not in params:
            params['theme'] = DefaultTheme
        elif isinstance(params['theme'], str):
            params['theme'] = THEMES[params['theme']]
        if "accent" in params:
            accent = params.pop("accent")
            if not "accent_base_color" in params:
                params["accent_base_color"]=accent
            if not "header_background" in params:
                params["header_background"]=accent

        super().__init__(**params)
        theme = self._get_theme()
        if "background_color" not in params:
            self.background_color = theme.style.background_color
        if "accent_base_color" not in params:
            self.accent_base_color = theme.style.accent_base_color
        if "header_color" not in params:
            self.header_color = theme.style.header_color
        if "header_accent_base_color" not in params:
            self.header_accent_base_color = theme.style.header_accent_base_color
        if "header_background" not in params:
            self.header_background = theme.style.header_background
        if "neutral_color" not in params:
            self.neutral_color = theme.style.neutral_color
        if "header_neutral_color" not in params:
            self.header_neutral_color = theme.style.header_neutral_color
        if "corner_radius" not in params:
            self.corner_radius = theme.style.corner_radius
        if "font" not in params:
            self.font = theme.style.font
        if "font_url" not in params:
            self.font_url = theme.style.font_url
        if "shadow" not in params:
            self.shadow = theme.style.shadow

    @staticmethod
    def _get_theme_from_query_args():
        theme_arg = state.session_args.get("theme", None)
        if not theme_arg:
            return
        theme_arg = theme_arg[0].decode("utf-8")
        return theme_arg.strip("'").strip('"')

    def _update_vars(self):
        super()._update_vars()
        style = self._get_theme().style
        style.background_color = self.background_color
        style.accent_base_color = self.accent_base_color
        style.header_color = self.header_color
        style.header_background = self.header_background
        style.header_accent_base_color = self.header_accent_base_color
        style.neutral_color = self.neutral_color
        style.header_neutral_color = self.header_neutral_color
        style.corner_radius = self.corner_radius
        style.font = self.font
        style.font_url = self.font_url
        style.shadow = self.shadow
        self._render_variables["style"] = style
        self._render_variables["theme_toggle"] = self.theme_toggle
        self._render_variables["theme"] = self.theme.__name__[:-5].lower()
        self._render_variables["sidebar_footer"] = self.sidebar_footer
        self._render_variables["main_layout"] = self.main_layout


class FastGridBaseTemplate(FastBaseTemplate, ReactTemplate):
    """
    Combines the FastTemplate and the React template.
    """

    _resources = dict(FastBaseTemplate._resources, js=ReactTemplate._resources['js'])

    __abstract = True
