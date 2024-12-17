import pathlib

import param

from ...io.state import state
from ...theme import THEMES, DefaultTheme
from ...theme.fast import Design, Fast
from ..base import BasicTemplate
from ..react import ReactTemplate

_ROOT = pathlib.Path(__file__).parent


class FastBaseTemplate(BasicTemplate):

    accent_base_color = param.Color(default="#0072B5", doc="""
        Optional body accent color override.""")

    background_color = param.Color(doc="""
        Optional body background color override.""")

    corner_radius = param.Integer(default=3, bounds=(0,25), doc="""
        The corner radius applied to controls.""")

    font = param.String(doc="""
        The font name(s) to apply.""")

    font_url = param.String(doc="""
        A font url to import.""")

    header_neutral_color = param.Color(doc="""
        Optional header neutral color override.""")

    header_accent_base_color = param.Color(doc="""
        Optional header accent color override.""")

    neutral_color = param.Color(doc="""
        Optional body neutral color override.""")

    theme_toggle = param.Boolean(default=True, doc="""
        If True a switch to toggle the Theme is shown.""")

    shadow = param.Boolean(doc="""
        Optional shadow override. Whether or not to apply shadow.""")

    sidebar_footer = param.String("", doc="""
        A HTML string appended to the sidebar""")

    # Might be extended to accordion or tabs in the future
    main_layout = param.Selector(default="card", label="Layout", objects=[None, "card"], doc="""
        What to wrap the main components into. Options are '' (i.e. none) and 'card' (Default).
        Could be extended to Accordion, Tab etc. in the future.""")

    design = param.ClassSelector(class_=Design, default=Fast,
                                 is_instance=False, instantiate=False, doc="""
        A Design applies a specific design system to a template.""")

    _css = [_ROOT / "fast.css"]

    _js = _ROOT / "js/fast_template.js"

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
            if "accent_base_color" not in params:
                params["accent_base_color"] = accent
            if "header_background" not in params:
                params["header_background"] = accent

        super().__init__(**params)
        self.param.update({
            p: v for p, v in self._design.theme.style.param.values().items()
            if p != 'name' and p in self.param and p not in params
        })

    @staticmethod
    def _get_theme_from_query_args():
        theme_arg = state.session_args.get("theme", None)
        if not theme_arg:
            return
        theme_arg = theme_arg[0].decode("utf-8")
        return theme_arg.strip("'").strip('"')

    def _update_vars(self):
        super()._update_vars()
        style = self._design.theme.style
        style.param.update({
            p: getattr(self, p) for p in style.param
            if p != 'name' and p in self.param
        })
        self._render_variables["style"] = style
        self._render_variables["theme_toggle"] = self.theme_toggle
        self._render_variables["theme"] = self.theme.__name__[:-5].lower()
        self._render_variables["sidebar_footer"] = self.sidebar_footer
        self._render_variables["main_layout"] = self.main_layout


class FastGridBaseTemplate(FastBaseTemplate, ReactTemplate):
    """
    Combines the FastTemplate and the React template.
    """

    _resources = dict(js=ReactTemplate._resources['js'])

    __abstract = True
