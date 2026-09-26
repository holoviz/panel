"""Focused tests for the generated panel.ui component reference."""

import importlib.util
import io
import json
import tarfile
import zipfile

from pathlib import Path
from types import SimpleNamespace

import param
import pytest

import panel.io.convert
import panel.io.resources

from panel.config import config
from panel.io.convert import (
    BOKEH_VERSION, PANEL_LOCAL_WHL, collect_python_requirements, convert_app,
)
from panel.pane import HoloViews
from panel.param import Param

EXTENSION = Path(__file__).resolve().parents[2] / 'doc' / '_ext' / 'ui_reference.py'
spec = importlib.util.spec_from_file_location('ui_reference', EXTENSION)
assert spec is not None and spec.loader is not None
ui_reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui_reference)


def test_docs_panel_wheel_matches_checkout():
    """Non-release docs use a trimmed wheel for the checked-out Panel version."""
    if not PANEL_LOCAL_WHL.is_file():
        pytest.skip('Build the Panel Pyodide wheel before checking its contents')
    with zipfile.ZipFile(PANEL_LOCAL_WHL) as wheel:
        assert not any(name.startswith('panel/tests/') for name in wheel.namelist())
        assert not any(name.endswith('.whl') for name in wheel.namelist())
        metadata = next(name for name in wheel.namelist() if name.endswith('.dist-info/METADATA'))
        assert 'Requires-Dist: bokeh >=3.10.0,<3.11.0' in wheel.read(metadata).decode()


def test_docs_converted_apps_use_local_panel_wheel():
    """The converted Pyodide apps pack the same Panel wheel as the docs gallery."""
    if not PANEL_LOCAL_WHL.is_file():
        pytest.skip('Build the Panel Pyodide wheel before checking conversion')
    requirements = collect_python_requirements('examples/gallery/altair_brushing.ipynb', [], panel_version='local')
    assert f'file:{PANEL_LOCAL_WHL.resolve()}' in requirements
    assert f'bokeh=={BOKEH_VERSION}' in requirements


def test_local_panel_wheel_without_bokeh_wheel(tmp_path, monkeypatch):
    """A dev docs build uses the branch wheel without requiring a Bokeh wheel."""
    panel_wheel = tmp_path / 'panel-1.0-py3-none-any.whl'
    panel_wheel.touch()
    monkeypatch.setattr(panel.io.convert, 'PANEL_LOCAL_WHL', panel_wheel)
    monkeypatch.setattr(panel.io.convert, 'BOKEH_LOCAL_WHL', tmp_path / 'missing-bokeh.whl')

    requirements = collect_python_requirements('examples/gallery/altair_brushing.ipynb', [], panel_version='local')
    assert requirements == [f'bokeh=={BOKEH_VERSION}', f'file:{panel_wheel.resolve()}', 'pyodide-http']


def test_local_panel_wheel_missing(tmp_path, monkeypatch):
    """A missing branch wheel must fail before publishing released Panel code."""
    monkeypatch.setattr(panel.io.convert, 'PANEL_LOCAL_WHL', tmp_path / 'missing-panel.whl')

    with pytest.raises(FileNotFoundError, match='Panel Pyodide wheel not found'):
        collect_python_requirements('examples/gallery/altair_brushing.ipynb', [], panel_version='local')


def test_converted_app_packs_local_panel_wheel(tmp_path, monkeypatch):
    """Converted docs apps ship the built wheel instead of requesting the CDN release."""
    wheel = tmp_path / 'panel-1.0-py3-none-any.whl'
    wheel.write_bytes(b'branch wheel')
    monkeypatch.setattr(panel.io.convert, 'PANEL_LOCAL_WHL', wheel)
    monkeypatch.setattr(panel.io.convert, 'BOKEH_LOCAL_WHL', tmp_path / 'missing-bokeh.whl')
    requirements = []

    def render(app, **kwargs):
        requirements.extend(kwargs['requirements'])
        return '<html></html>', None

    monkeypatch.setattr(panel.io.convert, 'script_to_html', render)
    convert_app('examples/gallery/altair_brushing.ipynb', tmp_path, requirements=[], panel_version='local')

    assert 'emfs:packed_wheels/panel-1.0-py3-none-any.whl' in requirements
    with zipfile.ZipFile(tmp_path / 'altair_brushing.resources.zip') as resources:
        assert resources.read('packed_wheels/panel-1.0-py3-none-any.whl') == b'branch wheel'


@pytest.fixture(autouse=True)
def restore_design():
    design = param.Parameterized.__getattribute__(config, 'design')
    globals_to_restore = (
        (Param, 'mapping'),
        (Param, 'input_widgets'),
        (HoloViews, 'default_widgets'),
        (panel.io.convert, 'loading_resources'),
        (panel.io.convert, 'BASE_TEMPLATE'),
        (panel.io.resources, 'BASE_TEMPLATE'),
    )
    prior = [
        (obj, attr, dict(value) if isinstance(value := getattr(obj, attr), dict) else value)
        for obj, attr in globals_to_restore
    ]
    yield
    for obj, attr, value in prior:
        setattr(obj, attr, value)
    param.Parameterized.__setattr__(config, 'design', design)


def notebook(path, *cells):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'cells': [
        {'cell_type': kind, 'source': text.splitlines(keepends=True)}
        for kind, text in cells
    ]}), encoding='utf-8')


@pytest.fixture
def gallery(tmp_path):
    examples = tmp_path / 'examples' / 'reference'
    examples.mkdir(parents=True)
    material = tmp_path / 'material' / 'examples' / 'reference'
    material.mkdir(parents=True)
    app = SimpleNamespace(
        builder=SimpleNamespace(srcdir=str(tmp_path / 'doc')),
        config=SimpleNamespace(ui_reference_pmui_source=str(material), nbsite_gallery_conf={
            'examples_dir': '../examples',
            'galleries': {
                'reference/classic': {'source': 'reference'},
                'reference': {'sections': []},
            },
        }),
    )
    yield app, examples
    ui_reference.cleanup_ui_gallery(app, None)


def test_material_notebook_preserves_narrative_and_rewrites_code(gallery):
    app, _ = gallery
    source = Path(app.config.ui_reference_pmui_source)
    notebook(source / 'widgets' / 'Button.ipynb',
        ('code', 'import panel as pn\nimport panel_material_ui as pmui\nfrom panel_material_ui import Button\npn.extension()'),
        ('markdown', 'A **material** button. See [next](TextInput.ipynb#usage) and [guide](../../how_to/index.md).'),
        ('code', 'label = "pmui.Button"\n# pmui.Button\npmui.Row(Button(label="Go"), pmui.Button())'),
    )
    notebook(source / 'widgets' / 'TextInput.ipynb',
             ('code', 'import panel as pn\nimport panel_material_ui as pmui\npmui.TextInput()'))
    ui_reference.generate_ui_reference(app)
    content = (Path(app.builder.srcdir) / 'reference/widgets/Button.md').read_text()
    assert 'A **material** button.' in content
    assert 'pn.ui.Row(pn.ui.Button(label="Go"), pn.ui.Button())' in content
    assert 'import panel_material_ui' not in content
    assert 'from panel_material_ui' not in content
    assert 'import panel.ui' in content
    assert '"pmui.Button"' in content
    assert '# pmui.Button' in content
    assert '(TextInput#usage)' in content
    assert '(../../how_to/index.md)' in content


def test_material_notebook_rejects_unsupported_api(gallery):
    import panel.ui as ui

    app, _ = gallery
    source = Path(app.config.ui_reference_pmui_source)
    path = source / 'widgets' / 'Button.ipynb'
    notebook(path, ('code', 'import panel as pn\nimport panel_material_ui as pmui\npmui.NotExported()\npmui.Button()'))
    with pytest.raises(ValueError, match='NotExported'):
        ui_reference._material_page(path, source, ui)
    notebook(path, ('code', 'import panel as pn\nfrom panel_material_ui import Button\nButton()'))
    content = ui_reference._material_page(path, source, ui)
    assert 'pn.ui.Button()' in content


def test_material_source_takes_precedence_over_classic(gallery):
    app, examples = gallery
    source = Path(app.config.ui_reference_pmui_source)
    notebook(examples / 'widgets' / 'Button.ipynb',
             ('code', 'import panel as pn\npn.widgets.Button(name="Classic")'))
    notebook(source / 'widgets' / 'Button.ipynb',
             ('markdown', 'Material button examples.'),
             ('code', 'import panel as pn\nimport panel_material_ui as pmui\npmui.Button(label="Modern")'))
    ui_reference.generate_ui_reference(app)
    content = (Path(app.builder.srcdir) / 'reference/widgets/Button.md').read_text()
    assert 'Material button examples.' in content
    assert 'pn.ui.Button(label="Modern")' in content
    assert 'Classic' not in content


def test_nbsite_generates_ui_gallery_cards(gallery, monkeypatch):
    from nbsite.gallery import gen

    app, _ = gallery
    source = Path(app.config.ui_reference_pmui_source)
    notebook(source / 'widgets' / 'Button.ipynb',
             ('code', 'import panel as pn\nimport panel_material_ui as pmui\npmui.Button()'))
    app.config.nbsite_gallery_conf = dict(gen.DEFAULT_GALLERY_CONF, **app.config.nbsite_gallery_conf)
    app.config.nbsite_gallery_conf['galleries']['reference']['title'] = 'Component Gallery'
    app.config.nbsite_gallery_conf['only_use_existing'] = True
    app.config.html_static_path = ['_static']
    app.config.html_theme_options = {}
    monkeypatch.setattr(gen, '_resolve_thumbnail', lambda *args, **kwargs: (1, '', 'png', 'Unavailable'))

    ui_reference.prepare_ui_gallery(app)
    gen.generate_gallery(app, 'reference')
    ui_reference.generate_ui_reference(app)

    index = (Path(app.builder.srcdir) / 'reference/index.rst').read_text()
    assert '.. grid-item-card:: Button' in index
    assert ':link: widgets/Button\n        :link-type: doc' in index
    assert index.index('Templates') < index.index('Classic Reference')
    assert '.. grid-item-card:: Classic Component Gallery' in index
    assert not (Path(app.builder.srcdir) / 'reference/index.md').exists()


def test_renamed_and_menu_notebooks_use_ui_exports(gallery):
    app, _ = gallery
    source = Path(app.config.ui_reference_pmui_source)
    notebook(source / 'widgets' / 'IconButton.ipynb',
             ('code', 'import panel as pn\nimport panel_material_ui as pmui\npmui.IconButton(icon="star")'))
    notebook(source / 'menus' / 'MenuButton.ipynb',
             ('code', 'import panel as pn\nimport panel_material_ui as pmui\npmui.MenuButton()'))
    ui_reference.generate_ui_reference(app)
    output = Path(app.builder.srcdir) / 'reference/widgets'
    assert 'pn.ui.IconButton(icon="star")' in (output / 'ButtonIcon.md').read_text()
    assert 'pn.ui.MenuButton()' in (output / 'MenuButton.md').read_text()


def test_missing_material_source_fails_with_instruction(gallery, monkeypatch):
    app, _ = gallery
    del app.config.ui_reference_pmui_source
    monkeypatch.delenv('PANEL_UI_REFERENCE_PMUI_SOURCE', raising=False)
    monkeypatch.setattr(ui_reference, 'find_spec', lambda name: None)
    with pytest.raises(FileNotFoundError, match='PANEL_UI_REFERENCE_PMUI_SOURCE'):
        ui_reference.generate_ui_reference(app)


def test_installed_material_source_archive_fallback(gallery, monkeypatch):
    app, _ = gallery
    del app.config.ui_reference_pmui_source
    package = Path(app.builder.srcdir).parent / 'installed' / 'panel_material_ui'
    package.mkdir(parents=True)
    (package / '__init__.py').write_text('')
    monkeypatch.setattr(ui_reference, 'find_spec', lambda name: SimpleNamespace(origin=str(package / '__init__.py')))
    monkeypatch.setattr(ui_reference, 'version', lambda name: '0.15.0')
    contents = json.dumps({'cells': [{'cell_type': 'code', 'source': ['import panel_material_ui as pmui\npmui.Button()']}]})
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode='w:gz') as tar:
        payload = contents.encode()
        member = tarfile.TarInfo('panel-material-ui-0.15.0/examples/reference/widgets/Button.ipynb')
        member.size = len(payload)
        tar.addfile(member, io.BytesIO(payload))
        stray = tarfile.TarInfo('panel-material-ui-0.15.0/README.md')
        stray.size = 0
        tar.addfile(stray, io.BytesIO())
    requested = []

    def fetch(url, timeout):
        requested.append((url, timeout))
        return io.BytesIO(archive.getvalue())

    monkeypatch.setattr(ui_reference, 'urlopen', fetch)
    source = ui_reference._material_examples(app)
    assert requested == [('https://github.com/panel-extensions/panel-material-ui/archive/refs/tags/v0.15.0.tar.gz', 30)]
    assert (source / 'widgets/Button.ipynb').read_text() == contents
    assert not (source / 'README.md').exists()
    app._pmui_reference_dir.cleanup()


def test_reuses_classic_notebook_without_copying_source(gallery):
    """Identity-compatible code renders the UI component and retains classic links."""
    import panel as pn
    import panel.ui as ui

    app, examples = gallery
    path = examples / 'widgets' / 'Tabulator.ipynb'
    notebook(path,
        ('markdown', 'See [Table](./Other.ipynb) and [guide](../../how_to/index.md).'),
        ('code', 'import panel as pn\npn.extension()\nwidget = pn.widgets.Tabulator()\nwidget'),
    )
    content = ui_reference._notebook_page(path, examples, pn, ui)
    assert 'pn.ui.Tabulator()' in content
    assert 'import panel.ui' in content
    assert '(./Other.ipynb)' in content
    assert '(../../how_to/index.md)' in content
    ui_reference.generate_ui_reference(app)
    generated = Path(app.builder.srcdir) / 'reference/widgets/Tabulator.md'
    assert 'pn.ui.Tabulator()' in generated.read_text()
    ui_reference.prepare_ui_gallery(app)
    gallery_conf = app.config.nbsite_gallery_conf['galleries']['reference']
    assert gallery_conf['thumbnail_source'] == 'reference/ui'
    assert (Path(gallery_conf['source']) / 'widgets/Tabulator.ipynb').is_symlink()
    assert not (Path(app.builder.srcdir) / 'reference/ui/index.md').exists()
    assert len(list(examples.rglob('Tabulator.ipynb'))) == 1


def test_different_class_falls_back_to_api(gallery):
    """Material replacements must not display a classic widget as their demo."""
    app, examples = gallery
    notebook(examples / 'widgets' / 'Button.ipynb',
             ('code', 'import panel as pn\npn.widgets.Button(name="Classic")'))
    ui_reference.generate_ui_reference(app)
    content = (Path(app.builder.srcdir) / 'reference/widgets/Button.md').read_text()
    assert "pn.ui.Button(label='Click me')" in content
    assert 'pn.widgets.Button(name=' not in content
    assert '{autoclass} panel_material_ui.' in content


def test_ui_only_exports_and_manual_page(gallery):
    """Every UI-only category is included and authored pages remain untouched."""
    app, _ = gallery
    page = Path(app.builder.srcdir) / 'reference/wrappers/Tooltip.md'
    page.parent.mkdir(parents=True)
    page.write_text('# Handwritten\n')
    ui_reference.generate_ui_reference(app)
    assert page.read_text() == '# Handwritten\n'
    for section, name in [('widgets', 'Fab'), ('layouts', 'Paper'),
                          ('chat', 'ChatMessage'), ('indicators', 'String'),
                          ('templates', 'Page'), ('wrappers', 'Badge')]:
        assert (Path(app.builder.srcdir) / f'reference/{section}/{name}.md').exists()


def test_classic_gallery_follows_templates(gallery):
    app, examples = gallery
    notebook(examples / 'templates' / 'FastListTemplate.ipynb',
             ('code', 'import panel as pn\npn.template.FastListTemplate()'))
    ui_reference.prepare_ui_gallery(app)
    sections = app.config.nbsite_gallery_conf['galleries']['reference']['sections']
    assert sections[-2]['title'] == 'Templates'
    assert 'pn.ui.Page' in sections[-2]['description']
    assert sections[-1]['title'] == 'Classic Reference'
    assert sections[-1]['items'][0]['url'] == 'classic/index.html'


def test_unsafe_code_is_not_rewritten(gallery):
    """Non-UI components or explicit classic imports require an API page."""
    import panel as pn
    import panel.ui as ui

    _, examples = gallery
    path = examples / 'widgets' / 'Button.ipynb'
    notebook(path, ('code', 'import panel as pn\npn.widgets.Button()'))
    assert ui_reference._notebook_page(path, examples, pn, ui) is None
    notebook(path, ('code', 'from panel.widgets import Tabulator\nTabulator()'))
    assert ui_reference._notebook_page(path, examples, pn, ui) is None
    notebook(path, ('code', 'import panel as pn\npn.ui.Button()'),
             ('markdown', 'See pn.widgets.Button for details.'))
    assert ui_reference._notebook_page(path, examples, pn, ui) is None


def test_links_route_to_ui_or_classic_and_leave_other_urls_alone(gallery):
    """Only real notebook targets are rerouted; ordinary links stay relative."""
    import panel as pn
    import panel.ui as ui

    _, examples = gallery
    notebook(examples / 'widgets' / 'ColorMap.ipynb',
             ('code', 'import panel as pn\npn.widgets.ColorMap()'))
    notebook(examples / 'widgets' / 'Button.ipynb',
             ('code', 'import panel as pn\npn.widgets.Button()'))
    path = examples / 'widgets' / 'Tabulator.ipynb'
    notebook(path, ('code', 'import panel as pn\npn.widgets.Tabulator()'),
             ('markdown', '[same](ColorMap.ipynb#part) [classic](Button.ipynb) '
              '[guide](../../how_to/layout/index.md) [external](https://example.com/x) '
              '[missing](Missing.ipynb) ![image](../image.png)'))
    content = ui_reference._notebook_page(path, examples, pn, ui)
    assert '(../classic/widgets/ColorMap#part)' in content
    assert '(../classic/widgets/Button)' in content
    assert '(../../how_to/layout/index.md)' in content
    assert '(https://example.com/x)' in content
    assert '(Missing.ipynb)' in content
    assert '![image](../image.png)' in content


def test_flat_and_alias_references_fall_back(gallery):
    """Classic flat layouts and module aliases cannot masquerade as UI components."""
    import panel as pn
    import panel.ui as ui

    _, examples = gallery
    path = examples / 'widgets' / 'Tabulator.ipynb'
    for code in ('import panel as pn\npn.Column(pn.widgets.Tabulator())',
                 'import panel as pn\nwidgets = pn.widgets\nwidgets.Tabulator()',
                 'import panel as pn\npn = object()\npn.widgets.Tabulator()',
                 'import panel as other\nother.widgets.Tabulator()'):
        notebook(path, ('code', code))
        assert ui_reference._notebook_page(path, examples, pn, ui) is None


def test_code_strings_comments_and_unicode_are_preserved(gallery):
    """AST rewriting changes only real class references, not quoted text."""
    import panel as pn
    import panel.ui as ui

    _, examples = gallery
    path = examples / 'widgets' / 'Tabulator.ipynb'
    notebook(path, ('code', 'import panel as pn\ntext = "pn.widgets.Button"\n'
             '# pn.widgets.Button\nlabel = "calf\u00e9"; pn.widgets.Tabulator()'))
    content = ui_reference._notebook_page(path, examples, pn, ui)
    assert 'pn.ui.Tabulator()' in content
    assert '"pn.widgets.Button"' in content
    assert '# pn.widgets.Button' in content
    assert 'calf\u00e9' in content


def test_generation_order_and_nonexecuting_fallback(gallery):
    """nbsite runs first and unsupported constructors are shown without execution."""
    callbacks = []
    ui_reference.setup(SimpleNamespace(connect=lambda *args, **kwargs: callbacks.append((args, kwargs))))
    assert callbacks[0][0][0] == 'builder-inited'
    assert callbacks[0][1]['priority'] < 500
    assert callbacks[1][1]['priority'] > 500
    app, _ = gallery
    ui_reference.generate_ui_reference(app)
    content = (Path(app.builder.srcdir) / 'reference/panes/ParamMethod.md').read_text()
    assert 'Use `pn.ui.ParamMethod`' in content
    assert '```{pyodide}' not in content


def test_gallery_index_is_owned_by_nbsite(gallery):
    """nbsite owns the landing, while authored pages remain untouched."""
    app, _ = gallery
    index = Path(app.builder.srcdir) / 'reference/index.rst'
    index.parent.mkdir(parents=True)
    ui_reference.generate_ui_reference(app)
    assert not index.exists()
    assert not (index.parent / 'index.md').exists()
    authored = index.parent / 'widgets/Button.md'
    authored.write_text('# Custom button\n')
    ui_reference.generate_ui_reference(app)
    assert authored.read_text() == '# Custom button\n'


def test_reuse_requires_target_component(gallery):
    """A notebook without a target demo falls back rather than showing other widgets."""
    import panel as pn
    import panel.ui as ui

    _, examples = gallery
    path = examples / 'widgets' / 'Tabulator.ipynb'
    notebook(path, ('code', 'import panel as pn\npn.widgets.ColorMap()'))
    assert ui_reference._notebook_page(path, examples, pn, ui) is None


def test_relocated_classic_page_links(gallery):
    """nbsite's doc links escape classic; sibling and download links do not."""
    app, _ = gallery
    page = Path(app.builder.srcdir) / 'reference/classic/widgets/Tabulator.md'
    page.parent.mkdir(parents=True)
    page.write_text('# Tabulator\n')
    source = [
        '[widget](../widgets/Select.ipynb) [pane](../panes/Markdown) '
        '[guide](../../how_to/index.md#start) [tutorial](../../tutorials/index.md)\n'
        '[back](../../reference/index.md) '
        '[external](https://example.com/x) [root](/how_to/index.md) '
        '[anchor](#parameters) [download](</assets/reference/widgets/Tabulator.ipynb>)\n'
    ]
    ui_reference.relocate_classic_links(app, 'reference/classic/widgets/Tabulator', source)
    assert '(../widgets/Select.ipynb)' in source[0]
    assert '(../panes/Markdown)' in source[0]
    assert '(../../../how_to/index.md#start)' in source[0]
    assert '(../../../tutorials/index.md)' in source[0]
    assert '(../../../reference/index.md)' in source[0]
    assert '(https://example.com/x)' in source[0]
    assert '(/how_to/index.md)' in source[0]
    assert '(#parameters)' in source[0]
    assert '(</assets/reference/widgets/Tabulator.ipynb>)' in source[0]


def test_classic_source_read_skips_fences_and_nonclassic_pages(gallery):
    """Source-read changes only classic Markdown prose, not executable cells."""
    app, _ = gallery
    page = Path(app.builder.srcdir) / 'reference/classic/widgets/Tabulator.md'
    page.parent.mkdir(parents=True)
    page.write_text('# Tabulator\n')
    text = (
        '```{pyodide}\nlink = "[guide](../../how_to/index.md)"\n```\n'
        '~~~python\n# [guide](../../how_to/index.md)\n~~~\n'
        '[guide](../../how_to/index.md)\n'
    )
    source = [text]
    ui_reference.relocate_classic_links(app, 'reference/classic/widgets/Tabulator', source)
    assert source[0].count('(../../how_to/index.md)') == 2
    assert source[0].count('(../../../how_to/index.md)') == 1
    unchanged = [text]
    ui_reference.relocate_classic_links(app, 'reference/widgets/Tabulator', unchanged)
    assert unchanged == [text]
    ui_reference.relocate_classic_links(app, 'reference/classic/widgets/Missing', unchanged)
    assert unchanged == [text]


def test_source_read_hook_registered(gallery):
    """Relocation runs when Sphinx reads nbsite's generated classic Markdown."""
    callbacks = []
    ui_reference.setup(SimpleNamespace(connect=lambda *args, **kwargs: callbacks.append((args, kwargs))))
    assert callbacks[2][0] == ('source-read', ui_reference.relocate_classic_links)
    assert callbacks[3][0] == ('source-read', ui_reference.resolve_gallery_index_links)
    assert callbacks[4][0] == ('build-finished', ui_reference.cleanup_ui_gallery)


def test_existing_gallery_index_links_resolve_to_nbsite(gallery):
    app, _ = gallery
    source = ['[Gallery](../../reference/index.md#widgets) [Page](../reference/index.md)']
    ui_reference.resolve_gallery_index_links(app, 'tutorials/basic/widgets', source)
    assert source[0] == '[Gallery](../../reference/index.rst#widgets) [Page](../reference/index.rst)'
