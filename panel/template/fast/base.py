import pathlib

import param

from ...io.state import state
from ..base import BasicTemplate
from ..react import ReactTemplate
from ..theme import THEMES, DefaultTheme

_ROOT = pathlib.Path(__file__).parent


class FastBaseTemplate(BasicTemplate):

    theme_toggle = param.Boolean(default=True, doc="""
        If True a switch to toggle the Theme is shown.""")

    sidebar_footer = param.String("", doc="""
        A HTML string appended to the sidebar""")

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
            'fast-colors': 'https://unpkg.com/@microsoft/fast-colors@5.1.0',
            'fast': 'https://unpkg.com/@microsoft/fast-components@1.13.0'
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

        super().__init__(**params)
        theme = self._get_theme()
        if "header_color" not in params:
            self.header_color = theme.style.header_color
        if "header_background" not in params:
            self.header_background = theme.style.header_background

    @staticmethod
    def _get_theme_from_query_args():
        theme_arg = state.session_args.get("theme", None)
        if not theme_arg:
            return
        theme_arg = theme_arg[0].decode("utf-8")
        return theme_arg.strip("'").strip('"')

    def _update_vars(self):
        super()._update_vars()
        self._render_variables["style"] = self._get_theme().style
        self._render_variables["theme_toggle"] = self.theme_toggle
        self._render_variables["theme"] = self.theme.__name__[:-5].lower()
        self._render_variables["sidebar_footer"] = self.sidebar_footer


class FastGridBaseTemplate(FastBaseTemplate, ReactTemplate):
    """
    Combines the FastTemplate and the React template.
    """

    _resources = dict(FastBaseTemplate._resources, **ReactTemplate._resources)

    __abstract = True
