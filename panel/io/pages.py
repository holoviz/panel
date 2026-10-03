"""
Theming of the pages Panel serves outside of applications, i.e. the index,
login, logout and error pages.

The pages are configured with ``config.page_config``, which mirrors the
theming parameters of ``panel.ui.Page`` so that the same ``theme_config``,
logo and title can be shared between the server pages and the applications.
"""
from __future__ import annotations

import base64
import functools
import html
import json
import mimetypes
import os
import pathlib
import re
import sys
import typing as t

from ..config import config

PAGE_CONFIG_KEYS = (
    'css_files', 'dark_theme', 'favicon', 'logo', 'raw_css', 'site_url',
    'theme_config', 'title',
)

ROBOTO_URL = "https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap"

_BASE_CSS = (pathlib.Path(__file__).parent.parent / '_templates' / 'page.css').read_text(encoding='utf-8')

# Characters that would let a value escape its CSS declaration or the
# enclosing <style> element.
_UNSAFE_CSS = re.compile(r'[;{}<>]')

_HEX = re.compile(r'^#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$', re.IGNORECASE)
_RGB = re.compile(r'^rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)', re.IGNORECASE)


def load_page_config(value: t.Any) -> dict[str, t.Any]:
    """
    Normalize a page configuration given as a dict, a JSON string or a path
    to a JSON file, and validate its keys.
    """
    if value is None:
        return {}
    root = None
    if isinstance(value, (str, os.PathLike)):
        text = str(value)
        if not text.lstrip().startswith('{'):
            path = pathlib.Path(text)
            if not path.is_file():
                raise ValueError(
                    f"page_config must be a dict, a JSON string or the path "
                    f"to a JSON file, {text!r} is neither."
                )
            text = path.read_text(encoding='utf-8')
            root = path.absolute().parent
        value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError(f"page_config must be a dict, got {type(value).__name__}.")
    unknown = set(value) - set(PAGE_CONFIG_KEYS)
    if unknown:
        raise ValueError(
            f"page_config got unknown keys {sorted(unknown)}, the supported "
            f"keys are {list(PAGE_CONFIG_KEYS)}."
        )
    dark_theme = value.get('dark_theme')
    if dark_theme not in (None, True, False):
        raise ValueError(f"page_config 'dark_theme' must be True, False or None, got {dark_theme!r}.")
    logo = value.get('logo')
    if isinstance(logo, dict) and set(logo) - {'light', 'dark'}:
        raise ValueError("page_config 'logo' dict may only define 'light' and 'dark' logos.")
    theme_config = value.get('theme_config')
    if theme_config is not None and not isinstance(theme_config, dict):
        raise ValueError("page_config 'theme_config' must be a dict.")
    value = dict(value)
    for key in ('css_files', 'raw_css'):
        if isinstance(value.get(key), str):
            value[key] = [value[key]]
    if root is not None:
        # Images in a config file are relative to the file, not the server.
        for key in ('logo', 'favicon'):
            image = value.get(key)
            if isinstance(image, dict):
                value[key] = {k: _relative_to(root, v) for k, v in image.items()}
            elif image:
                value[key] = _relative_to(root, image)
    return value


def _relative_to(root: pathlib.Path, image: str) -> str:
    path = root / image
    return str(path) if path.is_file() else image


def _css_value(value: t.Any, key: str) -> str:
    if isinstance(value, (list, tuple)):
        value = ', '.join(str(v) for v in value)
    value = str(value).strip()
    if _UNSAFE_CSS.search(value):
        raise ValueError(f"theme_config {key!r} has an invalid CSS value {value!r}.")
    return value


def _parse_rgb(color: str) -> tuple[float, float, float] | None:
    if match := _HEX.match(color):
        digits = match.group(1)
        if len(digits) in (3, 4):
            digits = ''.join(c * 2 for c in digits)
        return tuple(int(digits[i:i+2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    if match := _RGB.match(color):
        return tuple(float(c) for c in match.groups())  # type: ignore[return-value]
    return None


def _luminance(rgb: tuple[float, float, float]) -> float:
    channels = []
    for c in rgb:
        c /= 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_text(color: str) -> str:
    """
    The text color MUI's ``getContrastText`` picks for the given background.
    Colors that cannot be parsed are assumed to be dark.
    """
    rgb = _parse_rgb(color)
    if rgb is None:
        return '#ffffff'
    ratio = 1.05 / (_luminance(rgb) + 0.05)
    return '#ffffff' if ratio >= 3 else 'rgba(0, 0, 0, 0.87)'


def _mix(color: str, other: str, amount: float) -> str:
    # Mixing in sRGB with black or white is exactly MUI's darken and lighten.
    return f"color-mix(in srgb, {color} {round((1 - amount) * 100)}%, {other})"


def _theme_for(theme_config: dict | None, dark: bool) -> dict:
    """
    Picks the configuration for one color scheme. Like ``panel.ui``, a
    ``theme_config`` with ``light`` and ``dark`` keys configures each scheme
    separately, otherwise it applies to both.
    """
    if not theme_config:
        return {}
    if 'light' in theme_config or 'dark' in theme_config:
        return theme_config.get('dark' if dark else 'light') or {}
    return theme_config


def _theme_variables(theme: dict, dark: bool) -> dict[str, str]:
    palette = theme.get('palette') or {}
    variables: dict[str, str] = {}

    primary = palette.get('primary') or {}
    if main := primary.get('main'):
        main = _css_value(main, 'palette.primary.main')
        variables['--pn-primary'] = main
        variables['--pn-primary-text'] = _css_value(primary.get('light', main), 'palette.primary.light') if dark else main
        variables['--pn-primary-hover'] = _css_value(primary['dark'], 'palette.primary.dark') if 'dark' in primary else _mix(main, 'black', 0.2)
        variables['--pn-on-primary'] = _css_value(primary.get('contrastText') or contrast_text(main), 'palette.primary.contrastText')
        variables['--pn-focus-ring'] = _mix(main, 'transparent', 0.5)
        variables['--pn-primary-hover-surface'] = _mix(main, 'transparent', 0.92 if dark else 0.96)
        variables['--pn-media'] = _mix(main, 'var(--pn-paper)', 0.88 if dark else 0.92)

    for name in ('error', 'success'):
        color = (palette.get(name) or {}).get('main')
        if not color:
            continue
        color = _css_value(color, f'palette.{name}.main')
        variables[f'--pn-{name}'] = color
        variables[f'--pn-{name}-surface'] = _mix(color, 'black' if dark else 'white', 0.85 if dark else 0.9)
        if name == 'error':
            variables['--pn-error-text'] = _mix(color, 'white' if dark else 'black', 0.6)

    background = palette.get('background') or {}
    if 'default' in background:
        variables['--pn-background'] = _css_value(background['default'], 'palette.background.default')
    if 'paper' in background:
        paper = _css_value(background['paper'], 'palette.background.paper')
        variables['--pn-paper'] = paper
        variables['--pn-paper-raised'] = _mix(paper, 'white', 0.06) if dark else paper

    text = palette.get('text') or {}
    if 'primary' in text:
        variables['--pn-text'] = variables['--pn-border-hover'] = _css_value(text['primary'], 'palette.text.primary')
    if 'secondary' in text:
        variables['--pn-text-secondary'] = _css_value(text['secondary'], 'palette.text.secondary')
    if 'divider' in palette:
        variables['--pn-divider'] = _css_value(palette['divider'], 'palette.divider')

    typography = theme.get('typography') or {}
    if 'fontFamily' in typography:
        variables['--pn-font'] = _css_value(typography['fontFamily'], 'typography.fontFamily')

    shape = theme.get('shape') or {}
    if 'borderRadius' in shape:
        radius = shape['borderRadius']
        variables['--pn-radius'] = f'{radius}px' if isinstance(radius, (int, float)) else _css_value(radius, 'shape.borderRadius')
    return variables


def theme_css(theme_config: dict | None, dark_theme: bool | None = None) -> str:
    """
    Translates a MUI ``theme_config`` into overrides of the page stylesheet
    variables. With ``dark_theme=None`` the pages follow the color scheme of
    the operating system, otherwise the given scheme is forced.
    """
    rules = []
    split = bool(theme_config) and ('light' in theme_config or 'dark' in theme_config)
    if dark_theme is not None:
        variables = {
            'color-scheme': 'dark' if dark_theme else 'light',
            **_theme_variables(_theme_for(theme_config, dark_theme), dark_theme),
        }
        rules.append(_rule(':root', variables))
    elif split:
        # Variables a scheme does not set keep the stylesheet defaults.
        for scheme in ('light', 'dark'):
            if variables := _theme_variables(_theme_for(theme_config, scheme == 'dark'), scheme == 'dark'):
                rules.append(f'@media (prefers-color-scheme: {scheme}) {{\n{_rule(":root", variables)}}}\n')
    else:
        light = _theme_variables(_theme_for(theme_config, False), False)
        dark = _theme_variables(_theme_for(theme_config, True), True)
        variables = {
            var: value if value == dark[var] else f'light-dark({value}, {dark[var]})'
            for var, value in light.items()
        }
        if variables:
            rules.append(_rule(':root', variables))

    themes = [_theme_for(theme_config, False), _theme_for(theme_config, True)]
    font_size = next((th['typography']['fontSize'] for th in themes if 'fontSize' in th.get('typography', {})), None)
    if font_size:
        # MUI sizes body text at fontSize / 14 rem.
        rules.append(f'html {{ font-size: {float(font_size) / 14 * 100:g}%; }}\n')
    return ''.join(rules)


def _rule(selector: str, declarations: dict[str, str]) -> str:
    body = ''.join(f'  {k}: {v};\n' for k, v in declarations.items())
    return f'{selector} {{\n{body}}}\n'


@functools.lru_cache(maxsize=32)
def _read_image(path: str) -> str:
    mime = mimetypes.guess_type(path)[0] or 'image/png'
    if path.endswith('.ico'):
        mime = 'image/x-icon'
    data = base64.b64encode(pathlib.Path(path).read_bytes()).decode('ascii')
    return f'data:{mime};base64,{data}'


def resolve_image(image: str | os.PathLike | None) -> str | None:
    """
    Embeds local image files as data URIs so the pages do not depend on
    static routes, and passes URLs through unchanged.
    """
    if image is None:
        return None
    image = str(image)
    if os.path.isfile(image):
        return _read_image(os.path.abspath(image))
    return image


def page_defaults() -> dict[str, t.Any]:
    """
    The branding configured as class defaults of ``panel.ui.Page``, e.g. by
    a ``--setup`` script, so that applications and server pages share one
    brand configuration. Only consulted once panel-material-ui is imported,
    since importing it replaces the global design.
    """
    pmui = sys.modules.get('panel_material_ui')
    page = getattr(pmui, 'Page', None)
    if page is None:
        return {}
    defaults: dict[str, t.Any] = {}
    for key in ('theme_config', 'logo', 'favicon', 'title'):
        if value := getattr(page, key, None):
            defaults[key] = value
    # '/' is the Page default, which would replace the link to the Panel site.
    if (site_url := getattr(page, 'site_url', None)) not in (None, '', '/'):
        defaults['site_url'] = site_url
    # Fonts loaded for the Page apply here too, its raw CSS targets the Page.
    page_config = getattr(page, 'config', None)
    if css_files := list(getattr(page_config, 'css_files', None) or []):
        defaults['css_files'] = [str(f) for f in css_files]
    return defaults


def _pick_logo(logo: t.Any) -> t.Any:
    """
    Reduces a Page logo keyed by breakpoints to a single (possibly
    per-scheme) logo, since the server pages have one app bar layout.
    """
    if not isinstance(logo, dict) or set(logo) <= {'light', 'dark'}:
        return logo
    for key in ('md', 'lg', 'xl', 'sm', 'xs', 'default'):
        if key in logo:
            return _pick_logo(logo[key])
    return _pick_logo(next(iter(logo.values()), None))


class PageTheme:
    """
    Exposes ``config.page_config`` to the page templates as ``page``. It is
    resolved on every access, so changes to the config apply without a
    restart and no stale state is captured at import time.
    """

    @property
    def config(self) -> dict[str, t.Any]:
        return {**page_defaults(), **config.page_config}

    @property
    def dark_theme(self) -> bool | None:
        dark = self.config.get('dark_theme')
        if dark is None and config.theme == 'dark':
            return True
        return dark

    @property
    def title(self) -> str | None:
        return self.config.get('title') or None

    @property
    def favicon(self) -> str | None:
        return resolve_image(self.config.get('favicon'))

    @property
    def site_url(self) -> str | None:
        return self.config.get('site_url') or None

    @property
    def logo(self) -> dict[str, str] | None:
        logo = _pick_logo(self.config.get('logo'))
        if not logo:
            return None
        if isinstance(logo, dict):
            logos = {k: resolve_image(v) for k, v in logo.items() if v}
        else:
            logos = {'light': resolve_image(logo)}
        logos.setdefault('light', logos.get('dark'))
        logos.setdefault('dark', logos['light'])
        return logos  # type: ignore[return-value]

    @property
    def css(self) -> str:
        theme_config = self.config.get('theme_config')
        raw = '\n'.join(self.config.get('raw_css') or [])
        return '\n'.join(filter(None, [_BASE_CSS, theme_css(theme_config, self.dark_theme), raw]))

    @property
    def head(self) -> str:
        """
        The stylesheets of the page, to be inserted unescaped into ``<head>``.
        """
        theme_config = self.config.get('theme_config') or {}
        fonts = [
            _theme_for(theme_config, dark).get('typography', {}).get('fontFamily')
            for dark in (False, True)
        ]
        links = [] if all(fonts) else [ROBOTO_URL]
        links += list(self.config.get('css_files') or [])
        tags = [f'<style>\n{self.css}</style>']
        tags += [f'<link rel="stylesheet" href="{html.escape(url)}">' for url in links]
        return '\n'.join(tags)

    def brand(self, title: str, tag: str = 'span', href: str | None = None) -> str:
        """
        Renders the logo and title of the app bar, to be inserted unescaped.

        Arguments
        ---------
        title: str
            The title to display, already resolved by the template.
        tag: str
            The element wrapping the title, e.g. ``h1`` on the index page.
        href: str | None
            Link for the Panel logo, only used without a custom logo or
            ``site_url``.
        """
        logos = self.logo
        if logos is None:
            mark = '<span class="pn-mark" aria-hidden="true"></span>'
        else:
            light, dark = (html.escape(logos[k]) for k in ('light', 'dark'))
            if self.dark_theme is None and light != dark:
                mark = (
                    f'<picture><source srcset="{dark}" media="(prefers-color-scheme: dark)">'
                    f'<img class="pn-logo" src="{light}" alt=""></picture>'
                )
            else:
                mark = f'<img class="pn-logo" src="{dark if self.dark_theme else light}" alt="">'
        content = f'{mark}<{tag} class="pn-appbar-title">{html.escape(title)}</{tag}>'
        link = self.site_url or (href if logos is None else None)
        if link:
            return f'<a class="pn-brand" href="{html.escape(link)}">{content}</a>'
        return f'<div class="pn-brand">{content}</div>'


page_theme = PageTheme()
