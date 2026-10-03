import html
import json

import pytest

from panel.config import config
from panel.io.jupyter_server_extension import KERNEL_ERROR_TEMPLATE
from panel.io.pages import (
    _BASE_CSS, ROBOTO_URL, contrast_text, load_page_config, page_theme,
    theme_css,
)
from panel.io.resources import (
    BASIC_LOGIN_TEMPLATE, ERROR_TEMPLATE, INDEX_TEMPLATE, LOGOUT_TEMPLATE,
)
from panel.io.server import INDEX_HTML, render_auth_error, render_index_page

PIXEL_PNG = bytes.fromhex(
    '89504e470d0a1a0a0000000d4948445200000001000000010806000000'
    '1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082'
)


def _pages():
    return {
        'index': render_index_page(['/b', '/a'], '', index=INDEX_HTML),
        'convert_index': INDEX_TEMPLATE.render(items={'App': './app.html'}),
        'error': ERROR_TEMPLATE.render(error_type='Error', error='Oops'),
        'auth_error': render_auth_error('Denied'),
        'kernel_error': KERNEL_ERROR_TEMPLATE.render(kernels=['python3'], error_type='Kernel Error', error='No kernel'),
        'login': BASIC_LOGIN_TEMPLATE.render(errormessage=''),
        'logout': LOGOUT_TEMPLATE.render(LOGIN_ENDPOINT='/login'),
    }


PAGES = list(_pages())


@pytest.fixture
def page_config():
    def set_config(value):
        config.page_config = value
    yield set_config
    config.page_config = {}


# Loading and validation

def test_load_page_config_from_json_string():
    assert load_page_config('{"title": "Acme"}') == {'title': 'Acme'}


def test_load_page_config_normalizes_stylesheet_strings():
    cfg = load_page_config({'css_files': 'https://example.com/a.css', 'raw_css': '.x {}'})
    assert cfg == {'css_files': ['https://example.com/a.css'], 'raw_css': ['.x {}']}


def test_load_page_config_from_file_resolves_images_relative_to_file(tmp_path, monkeypatch):
    (tmp_path / 'logo.png').write_bytes(PIXEL_PNG)
    (tmp_path / 'page.json').write_text(json.dumps({
        'logo': {'light': 'logo.png', 'dark': 'https://example.com/dark.png'},
        'favicon': 'logo.png',
    }))
    monkeypatch.chdir(tmp_path.parent)
    cfg = load_page_config(str(tmp_path / 'page.json'))
    assert cfg['logo'] == {'light': str(tmp_path / 'logo.png'), 'dark': 'https://example.com/dark.png'}
    assert cfg['favicon'] == str(tmp_path / 'logo.png')


@pytest.mark.parametrize('value, match', [
    ({'colour': 'red'}, 'unknown keys'),
    ({'dark_theme': 'yes'}, 'dark_theme'),
    ({'logo': {'sm': 'logo.png'}}, "'light' and 'dark'"),
    ({'theme_config': 'dark'}, 'theme_config'),
    ('missing.json', 'neither'),
])
def test_load_page_config_rejects_invalid(value, match):
    with pytest.raises(ValueError, match=match):
        load_page_config(value)


def test_config_page_config_validates_on_set(page_config):
    with pytest.raises(ValueError, match='unknown keys'):
        page_config({'colour': 'red'})
    page_config('{"title": "Acme"}')
    assert config.page_config == {'title': 'Acme'}


def test_config_page_config_from_env(monkeypatch):
    monkeypatch.setenv('PANEL_PAGE_CONFIG', '{"title": "From env"}')
    assert config.page_config == {'title': 'From env'}


# theme_config translation

def test_theme_css_empty():
    assert theme_css(None) == ''
    assert theme_css({}) == ''


def test_theme_css_shared_config_derives_scheme_specific_values():
    css = theme_css({'palette': {'primary': {'main': '#ff5722'}}, 'shape': {'borderRadius': 12}})
    assert '--pn-primary: #ff5722;' in css
    assert '--pn-radius: 12px;' in css
    assert '--pn-primary-hover: color-mix(in srgb, #ff5722 80%, black);' in css
    # The hover surface is more opaque in dark mode, like MUI
    assert '--pn-primary-hover-surface: light-dark(' in css
    assert 'prefers-color-scheme' not in css


def test_theme_css_split_config_uses_media_queries():
    css = theme_css({
        'light': {'palette': {'primary': {'main': '#ff5722'}}},
        'dark': {'palette': {'background': {'default': '#000000'}}},
    })
    light, dark = css.split('@media (prefers-color-scheme: dark)')
    assert '@media (prefers-color-scheme: light)' in light
    assert '--pn-primary: #ff5722;' in light
    assert '--pn-background: #000000;' in dark
    assert '--pn-primary' not in dark


@pytest.mark.parametrize('dark_theme, scheme, color', [(True, 'dark', '#111111'), (False, 'light', '#eeeeee')])
def test_theme_css_forced_scheme(dark_theme, scheme, color):
    css = theme_css({
        'light': {'palette': {'background': {'default': '#eeeeee'}}},
        'dark': {'palette': {'background': {'default': '#111111'}}},
    }, dark_theme=dark_theme)
    assert f'color-scheme: {scheme};' in css
    assert f'--pn-background: {color};' in css
    assert 'prefers-color-scheme' not in css


def test_theme_css_typography():
    css = theme_css({'typography': {'fontFamily': ['Inter', 'sans-serif'], 'fontSize': 16}})
    assert '--pn-font: Inter, sans-serif;' in css
    assert 'html { font-size: 114.286%; }' in css


def test_theme_css_rejects_unsafe_values():
    with pytest.raises(ValueError, match='invalid CSS value'):
        theme_css({'palette': {'primary': {'main': 'red; } body { display: none'}}})


@pytest.mark.parametrize('color, text', [
    ('#0072b5', '#ffffff'),
    ('#ffeb3b', 'rgba(0, 0, 0, 0.87)'),
    ('rgb(255, 255, 255)', 'rgba(0, 0, 0, 0.87)'),
    ('rebeccapurple', '#ffffff'),
])
def test_contrast_text(color, text):
    assert contrast_text(color) == text


def test_primary_contrast_text_override():
    css = theme_css({'palette': {'primary': {'main': '#ffeb3b', 'contrastText': '#222'}}})
    assert '--pn-on-primary: #222;' in css


# Page theme

def test_page_theme_follows_global_dark_theme(page_config):
    with config.set(theme='dark'):
        assert page_theme.dark_theme is True
        page_config({'dark_theme': False})
        assert page_theme.dark_theme is False


def test_page_theme_head_loads_roboto_only_without_custom_font(page_config):
    roboto = html.escape(ROBOTO_URL)
    assert roboto in page_theme.head
    page_config({'theme_config': {'typography': {'fontFamily': 'Inter'}}, 'css_files': ['https://example.com/inter.css']})
    assert roboto not in page_theme.head
    assert '<link rel="stylesheet" href="https://example.com/inter.css">' in page_theme.head


def test_page_theme_head_appends_raw_css(page_config):
    page_config({'raw_css': ['.pn-card { border: 1px solid red; }']})
    head = page_theme.head
    assert head.index(_BASE_CSS) < head.index('.pn-card { border: 1px solid red; }')


def test_page_theme_brand_default():
    brand = page_theme.brand('Panel <Apps>', 'h1', 'https://panel.holoviz.org')
    assert brand == (
        '<a class="pn-brand" href="https://panel.holoviz.org"><span class="pn-mark" aria-hidden="true"></span>'
        '<h1 class="pn-appbar-title">Panel &lt;Apps&gt;</h1></a>'
    )


def test_page_theme_brand_custom_logo_drops_panel_link(page_config):
    page_config({'logo': 'https://example.com/logo.svg'})
    brand = page_theme.brand('Acme', 'span', 'https://panel.holoviz.org')
    assert brand.startswith('<div class="pn-brand"><img class="pn-logo" src="https://example.com/logo.svg"')
    page_config({'logo': 'https://example.com/logo.svg', 'site_url': '/home'})
    assert page_theme.brand('Acme').startswith('<a class="pn-brand" href="/home">')


def test_page_theme_brand_logo_per_scheme(page_config):
    page_config({'logo': {'light': 'light.svg', 'dark': 'dark.svg'}})
    brand = page_theme.brand('Acme')
    assert '<source srcset="dark.svg" media="(prefers-color-scheme: dark)">' in brand
    assert 'src="light.svg"' in brand
    page_config({'logo': {'light': 'light.svg', 'dark': 'dark.svg'}, 'dark_theme': True})
    brand = page_theme.brand('Acme')
    assert '<picture>' not in brand
    assert 'src="dark.svg"' in brand


def test_page_theme_embeds_local_images(page_config, tmp_path):
    logo = tmp_path / 'logo.png'
    logo.write_bytes(PIXEL_PNG)
    page_config({'logo': str(logo), 'favicon': str(logo)})
    assert page_theme.logo['light'].startswith('data:image/png;base64,')
    assert page_theme.favicon.startswith('data:image/png;base64,')


# Templates

@pytest.mark.parametrize('name', PAGES)
def test_pages_include_base_css(name):
    html = _pages()[name]
    assert _BASE_CSS in html
    assert 'class="pn-mark"' in html


@pytest.mark.parametrize('name', PAGES)
def test_pages_apply_page_config(name, page_config):
    page_config({
        'title': 'Acme Analytics',
        'logo': 'https://example.com/logo.svg',
        'favicon': 'https://example.com/favicon.png',
        'theme_config': {'palette': {'primary': {'main': '#ff5722'}}},
    })
    html = _pages()[name]
    assert '--pn-primary: #ff5722;' in html
    assert 'Acme Analytics</' in html
    assert '<link rel="icon" href="https://example.com/favicon.png">' in html
    assert 'src="https://example.com/logo.svg"' in html
    assert 'class="pn-mark' not in html


def test_index_page_links_and_count():
    html = render_index_page(['/b', '/a'], '', index=INDEX_HTML)
    assert 'href="./a"' in html
    assert '2 applications' in html
    assert '<title>Panel Applications</title>' in html


def test_convert_index_explicit_title_wins(page_config):
    page_config({'title': 'Acme'})
    html = INDEX_TEMPLATE.render(items={'App': './app.html'}, title='Gallery')
    assert '<title>Gallery</title>' in html


def test_login_template_renders_error_alert_only_on_error():
    assert 'role="alert"' not in BASIC_LOGIN_TEMPLATE.render(errormessage='')
    html = BASIC_LOGIN_TEMPLATE.render(errormessage='Invalid <b>password</b>')
    assert 'role="alert"' in html
    assert 'Invalid &lt;b&gt;password&lt;/b&gt;' in html


def test_auth_page_titles_default_and_override(page_config):
    assert '<title>Panel App | Logout</title>' in LOGOUT_TEMPLATE.render()
    page_config({'title': 'Acme'})
    assert '<title>Acme | Login</title>' in BASIC_LOGIN_TEMPLATE.render(errormessage='')


def test_page_theme_falls_back_to_panel_ui_page_defaults(panel_ui, page_config):
    Page = panel_ui.Page
    theme = {'palette': {'primary': {'main': '#ff5722'}}}
    originals = {p: Page.param[p].default for p in ('theme_config', 'logo', 'site_url')}
    css_files = list(Page.config.css_files)
    try:
        Page.param.theme_config.default = theme
        Page.param.logo.default = {'sm': 'mobile.svg', 'md': {'light': 'light.svg', 'dark': 'dark.svg'}}
        Page.config.css_files.append('https://example.com/font.css')
        assert '--pn-primary: #ff5722;' in page_theme.head
        assert 'https://example.com/font.css' in page_theme.head
        assert page_theme.logo == {'light': 'light.svg', 'dark': 'dark.svg'}
        # The Page default site_url does not replace the link to the Panel site
        assert page_theme.site_url is None
        # Explicit page_config takes precedence over the Page defaults
        page_config({'theme_config': {'palette': {'primary': {'main': '#00695c'}}}})
        assert '--pn-primary: #00695c;' in page_theme.head
    finally:
        for p, default in originals.items():
            Page.param[p].default = default
        Page.config.css_files[:] = css_files
