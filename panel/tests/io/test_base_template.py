from io import StringIO

from bokeh.core.templates import MACROS

from panel.config import config
from panel.io.resources import _env
from panel.layout import Column
from panel.theme import Design
from panel.widgets import TextInput


def render(**context):
    context = dict(docs=[], macros=MACROS, plot_script='', **context)
    return _env.get_template('base.html').render(**context)


def test_base_template_default_icons():
    html = render(dist_url='https://cdn.example.org/dist/')
    assert '<link rel="apple-touch-icon" sizes="180x180" href="https://cdn.example.org/dist/images/apple-touch-icon.png">' in html
    assert '<link rel="icon" type="image/png" sizes="32x32" href="https://cdn.example.org/dist/images/favicon.ico">' in html
    assert 'href=""' not in html


def test_base_template_custom_icons():
    html = render(apple_icon='/custom-apple.png', app_favicon='/custom.ico')
    assert '<link rel="apple-touch-icon" href="/custom-apple.png">' in html
    assert '<link rel="icon" href="/custom.ico">' in html
    assert 'apple-touch-icon.png' not in html
    assert 'favicon.ico' not in html


def test_base_template_theme_managed():
    assert 'data-theme-managed="false"' in render()
    assert 'data-theme-managed="true"' in render(theme_managed=True)


def test_base_template_meta():
    html = render(meta={
        'title': 'Meta Title',
        'name': 'Meta Name',
        'description': 'Meta Description',
        'keywords': 'panel, meta',
        'author': 'Panel',
        'refresh': '30',
        'viewport': 'width=device-width, initial-scale=1',
    })
    assert '<meta name="title" content="Meta Title">' in html
    assert '<meta name="name" content="Meta Name">' in html
    assert '<meta name="description" content="Meta Description">' in html
    assert '<meta name="keywords" content="panel, meta">' in html
    assert '<meta name="author" content="Panel">' in html
    assert '<meta http-equiv="refresh" content="30">' in html
    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html


def test_base_template_no_meta():
    html = render()
    assert '<meta charset="utf-8">' in html
    assert html.count('<meta ') == 1


def test_base_template_partial_meta():
    html = render(meta={'description': 'Only a description'})
    assert '<meta name="description" content="Only a description">' in html
    assert '<meta name="title"' not in html
    assert '<meta name="viewport"' not in html


def test_base_template_extension_blocks():
    template = _env.from_string("""
    {% extends "base.html" %}
    {% block loader_css %}.loader { color: red }{% endblock %}
    {% block loader %}<div id="loader"></div>{% endblock %}
    {% block loader_script %}<script>hide_loader()</script>{% endblock %}
    {% block postamble %}<link rel="stylesheet" href="/extra.css">{% endblock %}
    """)
    html = template.render(docs=[], macros=MACROS, plot_script='')
    assert '.loader { color: red }' in html
    assert '<div id="loader"></div>' in html
    assert '<script>hide_loader()</script>' in html
    assert '<link rel="stylesheet" href="/extra.css">' in html


def test_base_template_meta_block_overridable():
    template = _env.from_string("""
    {% extends "base.html" %}
    {% block meta %}<meta name="custom" content="1">{% endblock %}
    """)
    html = template.render(docs=[], macros=MACROS, plot_script='', meta={'title': 'Ignored'})
    assert '<meta name="custom" content="1">' in html
    assert 'Ignored' not in html


def test_save_does_not_emit_empty_icon_href():
    sio = StringIO()
    Column('# Test', TextInput()).save(sio, resources='cdn')
    sio.seek(0)
    html = sio.read()
    assert 'href=""' not in html
    assert html.count('rel="apple-touch-icon"') == 1


def test_base_template_pmui_aliases():
    html = render(apple_touch_icon='/custom-apple.png', favicon='/custom.ico', is_page=True)
    assert '<link rel="apple-touch-icon" href="/custom-apple.png">' in html
    assert '<link rel="icon" href="/custom.ico">' in html
    assert 'apple-touch-icon.png' not in html
    assert 'favicon.ico' not in html
    assert 'data-theme-managed="true"' in html


def test_base_template_explicit_favicon_wins_over_server_default():
    # The server always supplies app_favicon, a component's favicon must win.
    html = render(app_favicon='./favicon.ico', favicon='/custom.ico')
    assert '<link rel="icon" href="/custom.ico">' in html
    assert './favicon.ico' not in html


def test_base_template_loader():
    html = render()
    assert '<div id="loader" style="display: none;">' in html
    assert 'window._panelConnectionError' in html
    assert html.index('TrackedWebSocket') < html.index("getElementById('loader')")


def test_base_template_pyodide_loader():
    html = render(pyodide=True)
    assert '<div id="loader" style="display: flex;">' in html
    assert '<div id="loader-msg"></div>' in html
    assert 'window.panelLoader' in html


def test_base_template_dark_theme():
    html = render(theme_name='dark')
    assert 'body { background-color: #121212; color: #fff }' in html
    assert 'body { background-color: #121212' not in render(theme_name='default')


def test_base_template_material_ui_styles():
    html = render(material_ui=True, theme_name='default', dist_url='/dist/')
    assert '<style id="template-styles">' in html
    assert '<link rel="stylesheet" href="/dist/bundled/theme/default.css">' in html

    managed = render(material_ui=True, theme_managed=True, theme_name='default', dist_url='/dist/')
    assert '<style id="template-styles">' in managed
    assert 'bundled/theme/default.css' not in managed

    classic = render(theme_name='default', dist_url='/dist/')
    assert 'template-styles' not in classic
    assert 'bundled/theme/default.css' not in classic


def test_base_template_page_resources():
    html = render(resources={
        'css': {'page': '/page.css'}, 'raw_css': ['.page { color: red }'],
        'js': {'page': '/page.js'}, 'js_modules': {'mod': '/page.mjs'},
    })
    assert '<link rel="stylesheet" href="/page.css">' in html
    assert '.page { color: red }' in html
    assert '<script src="/page.js"></script>' in html
    assert '<script src="/page.mjs" type="module"></script>' in html


class MaterialUITestDesign(Design):

    _template_variables = {'material_ui': True}


def test_save_renders_design_template_variables():
    sio = StringIO()
    with config.set(design=MaterialUITestDesign):
        Column('# Test').save(sio, resources='cdn')
    assert '<style id="template-styles">' in sio.getvalue()

    sio = StringIO()
    Column('# Test').save(sio, resources='cdn')
    assert 'template-styles' not in sio.getvalue()
