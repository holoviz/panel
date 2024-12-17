"""
Vanilla template
"""
import pathlib

import param

from ...config import config as pn_config
from ..vanilla import VanillaTemplate

REVEAL_THEMES = ['black', 'white', 'league', 'beige', 'night', 'solarized', 'simple']

REVEAL_CSS = f"{pn_config.npm_cdn}/reveal.js@4.5.0/dist/reveal.min.css"
FONT_CSS = f"{pn_config.npm_cdn}/reveal.js@4.5.0/dist/theme/fonts/source-sans-pro/source-sans-pro.css"
REVEAL_THEME_CSS = {
    f'reveal-{theme}': f'{pn_config.npm_cdn}/reveal.js@4.5.0/dist/theme/{theme}.css'
    for theme in REVEAL_THEMES
}

class SlidesTemplate(VanillaTemplate):
    """
    SlidesTemplate is built on top of Vanilla web components.
    """

    collapsed_sidebar = param.Selector(default=True, constant=True, doc="""
        Whether the sidebar (if present) is initially collapsed.""")

    reveal_config = param.Dict(default={}, doc="""
        Configuration parameters for reveal.js""")

    reveal_theme = param.Selector(default=None, objects=REVEAL_THEMES, doc="""
        The reveal.js theme to load.""")

    show_header = param.Boolean(default=False, doc="""
        Whether to show the header component.""")

    _css = VanillaTemplate._css + [pathlib.Path(__file__).parent / 'slides.css']

    _template = pathlib.Path(__file__).parent / 'slides.html'

    _resources = {
        'js': {
            'reveal': f"{pn_config.npm_cdn}/reveal.js@4.5.0/dist/reveal.min.js",
        },
        'css': dict(REVEAL_THEME_CSS, reveal=REVEAL_CSS, font=FONT_CSS),
        'bundle': True,
        'tarball': {
            'reveal': {
                'tar': 'https://registry.npmjs.org/reveal.js/-/reveal.js-4.5.0.tgz',
                'src': 'package/',
                'dest': 'reveal.js@4.5.0',
                'exclude': ['*.d.ts', '*.json', '*.md', '*.html', '*esm*', '*js*', '*/css/*', '*/plugin/*', '*reveal.js']
            }
        }
    }

    def __init__(self, **params):
        super().__init__(**params)
        if 'reveal_theme' not in params:
            self.reveal_theme = 'black' if self._design.theme._name == 'dark' else 'white'
        self._update_render_vars()

    @param.depends('reveal_config', 'reveal_theme', 'show_header', watch=True)
    def _update_render_vars(self):
        self._resources['css'] = {
            'font': FONT_CSS,
            'reveal': REVEAL_CSS,
            'reveal-theme': REVEAL_THEME_CSS[f'reveal-{self.reveal_theme}']
        }
        self._render_variables['show_header'] = self.show_header
        self._render_variables['reveal_config'] = self.reveal_config
