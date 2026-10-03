"""
In-process tests of the panel migrate codemod on small source
strings, covering each rewrite rule individually and in combination.
"""
import pytest

pytest.importorskip("libcst")

# The codemod introspects panel.ui.
pytestmark = pytest.mark.panel_ui


def migrate_source(source):
    # Not imported at collection time: the codemod imports panel.ui, which would
    # add the Material widgets to every test parametrized over Widget subclasses.
    from panel.command._migrate.codemod import migrate_source
    return migrate_source(source)


def _rules(result):
    return {r.rule for r in result.rewrites}


def test_import_path_rewrite_import_panel_as_pn():
    result = migrate_source("import panel as pn\npn.widgets.TextInput()\n")
    assert result.changed
    assert result.source.count('import panel as pn') == 1
    assert 'pn.ui.TextInput()' in result.source
    assert result.rewrites and result.rewrites[0].rule == 'import-path'


def test_import_path_rewrite_from_panel_import_widgets_as_alias():
    source = "from panel import widgets as w\nw.TextInput()\n"
    result = migrate_source(source)
    assert result.changed
    assert 'import panel as pn' in result.source
    assert 'pn.ui.TextInput()' in result.source


def test_import_path_rewrite_from_panel_widgets_import_button():
    source = "from panel.widgets import Button\nButton()\n"
    result = migrate_source(source)
    assert result.changed
    assert 'pn.ui.Button()' in result.source


def test_reassigned_import_is_not_rewritten():
    """A reassigned Panel import may refer to a different class at call time."""
    source = (
        'from panel.widgets import Button, TextInput\n'
        'Button()\n'
        'Button = MyButton\n'
        'Button()\n'
        'TextInput()\n'
    )
    result = migrate_source(source)
    assert 'pn.ui.Button()\nButton = MyButton\nButton()' in result.source
    assert 'pn.ui.TextInput()' in result.source


def test_annotated_reassignment_is_not_rewritten():
    """Annotated assignments can replace an imported component too."""
    source = 'from panel.widgets import Button\nButton: type = MyButton\nButton()\n'
    result = migrate_source(source)
    assert result.source == source


def test_unpacking_reassignment_is_not_rewritten():
    """Unpacking can also replace a Panel import."""
    source = 'from panel.widgets import Button\nButton, other = MyButton, None\nButton()\n'
    assert migrate_source(source).source == source


@pytest.mark.parametrize('source', [
    'from panel.widgets import Button\ndef make(Button):\n    return Button()\n',
    'from panel.widgets import Button\nf = lambda Button: Button()\n',
    'from panel.widgets import Button\nfor Button in factories:\n    Button()\n',
    'from panel.widgets import Button\nwidgets = [Button() for Button in factories]\n',
    'from panel.widgets import Button\nwith factory() as Button:\n    Button()\n',
    'from panel.widgets import Button\ndef f():\n    class Button: pass\n    Button()\n',
])
def test_locally_rebound_import_is_not_rewritten(source):
    assert migrate_source(source).source == source


def test_module_level_def_shadows_later_calls_only():
    source = 'from panel.widgets import Button\nButton()\ndef Button():\n    pass\nButton()\n'
    result = migrate_source(source)
    assert 'pn.ui.Button()\ndef Button():\n    pass\nButton()\n' in result.source


def test_reassigned_pn_is_not_used_for_new_rewrites():
    """Inserted imports cannot fix a name that the application rebinds."""
    source = 'from panel.widgets import TextInput\npn = other\nTextInput()\n'
    assert migrate_source(source).source == source


def test_import_path_rewrite_uses_existing_panel_import():
    source = 'import panel\npanel.widgets.Button()\n'
    result = migrate_source(source)
    assert result.source == 'import panel\nimport panel as pn\npn.ui.Button()\n'
    assert not migrate_source(result.source).changed


def test_import_path_rewrite_bare_panel_layout_shortcut():
    source = "import panel as pn\npn.Row('a', 'b')\n"
    result = migrate_source(source)
    assert result.changed
    assert "pn.ui.Row('a', 'b')" in result.source


def test_import_path_rewrite_indicators_alias():
    source = "import panel as pn\npn.indicators.Number(value=1)\n"
    result = migrate_source(source)
    assert result.changed
    assert 'pn.ui.Number(value=1)' in result.source


def test_non_panel_call_is_left_alone():
    source = "import panel as pn\nsome_other_thing.Button(name='x')\n"
    result = migrate_source(source)
    assert not result.changed


def test_name_to_label_rewrite_on_widget():
    source = "import panel as pn\npn.widgets.Button(name='Click me')\n"
    result = migrate_source(source)
    assert result.changed
    assert "pn.ui.Button(label='Click me')" in result.source
    assert 'name-to-label' in _rules(result)


def test_name_is_not_touched_on_layouts():
    """
    Row(name=...) is left alone (the name= rename never fires): layout
    `name` is a distinct tab-title/hierarchy-name concept, not the widget
    `label`. The import path itself is still safe to unify, since it is a
    plain namespace change.
    """
    source = "import panel as pn\npn.Row(name='Tab 1')\n"
    result = migrate_source(source)
    assert "pn.ui.Row(name='Tab 1')" in result.source
    assert 'label' not in result.source
    assert 'name-to-label' not in _rules(result)


def test_button_widget_name_rewritten_but_row_name_is_not():
    source = (
        "import panel as pn\n"
        "pn.widgets.Button(name='Click me')\n"
        "pn.Row(name='Tab 1')\n"
    )
    result = migrate_source(source)
    assert "pn.ui.Button(label='Click me')" in result.source
    assert "pn.ui.Row(name='Tab 1')" in result.source


def test_button_type_rewrite():
    source = "import panel as pn\npn.widgets.Button(button_type='primary')\n"
    result = migrate_source(source)
    assert "pn.ui.Button(color='primary')" in result.source
    assert 'button-appearance' in _rules(result)


def test_button_style_rewrite():
    source = "import panel as pn\npn.widgets.Button(button_style='outline')\n"
    result = migrate_source(source)
    assert "pn.ui.Button(variant='outline')" in result.source


def test_button_type_and_style_together_with_name():
    source = "import panel as pn\npn.widgets.Button(name='Go', button_type='primary', button_style='outline')\n"
    result = migrate_source(source)
    assert "label='Go'" in result.source
    assert "color='primary'" in result.source
    assert "variant='outline'" in result.source
    assert 'pn.ui.Button(' in result.source


@pytest.mark.parametrize('group', ['RadioButtonGroup', 'CheckButtonGroup'])
@pytest.mark.parametrize('keyword', ['variant', 'button_style'])
@pytest.mark.parametrize(('classic', 'material'), [('solid', 'contained'), ('outline', 'outlined')])
def test_button_group_variant_migration(group, keyword, classic, material):
    source = f"import panel as pn\npn.widgets.{group}(button_type='primary', {keyword}='{classic}')\n"
    result = migrate_source(source)
    assert "color='primary'" in result.source
    assert f"variant='{material}'" in result.source
    assert 'button_style=' not in result.source
    assert 'button-appearance' in _rules(result)
    assert not result.manual_reviews


@pytest.mark.parametrize('keyword', ['variant', 'button_style'])
def test_dynamic_button_group_variant_requires_review(keyword):
    source = f'import panel as pn\npn.widgets.RadioButtonGroup({keyword}=style)\n'
    result = migrate_source(source)
    assert not result.changed
    assert result.manual_reviews


def test_menu_button_split_true_becomes_split_button():
    source = "import panel as pn\npn.widgets.MenuButton(name='Menu', items=[('A', 'a')], split=True)\n"
    result = migrate_source(source)
    assert 'pn.ui.SplitButton(' in result.source
    assert 'split=' not in result.source
    assert "label='Menu'" in result.source
    assert 'menu-button-split' in _rules(result)


def test_menu_button_without_split_stays_menu_button():
    source = "import panel as pn\npn.widgets.MenuButton(name='Menu', items=[('A', 'a')])\n"
    result = migrate_source(source)
    assert 'pn.ui.MenuButton(' in result.source
    assert 'menu-button-split' not in _rules(result)


def test_menu_button_split_false_is_unsafe_to_rewrite():
    """
    panel.ui.MenuButton has no `split` parameter at all (only SplitButton
    does), so `split=False` is a genuine dropped-parameter conflict, not the
    split=True special case: leaving `split=False` on a rewritten
    panel.ui.MenuButton call would break at runtime.
    """
    source = "import panel as pn\npn.widgets.MenuButton(items=[], split=False)\n"
    result = migrate_source(source)
    assert not result.changed
    assert result.manual_reviews
    assert 'split' in result.manual_reviews[0].message


def test_template_rewritten_to_page_when_kwargs_are_safe():
    source = (
        "import panel as pn\n"
        "pn.template.BootstrapTemplate(title='App', sidebar_width=350)\n"
    )
    result = migrate_source(source)
    assert result.changed
    assert "pn.ui.Page(title='App', sidebar_width=350)" in result.source
    assert 'template-to-page' in _rules(result)


def test_template_with_meta_kwargs_rewritten_to_page():
    """
    `Page` forwards `meta_<suffix>` kwargs into a nested `Meta` object rather
    than declaring them as `Page.param` members (see
    `panel_material_ui.template.base.Page.__init__`), but the classic
    templates and `Page` still accept the identical call-site spelling, so
    these must be carried over unchanged like any other safe kwarg.
    """
    source = (
        "import panel as pn\n"
        "pn.template.BootstrapTemplate(title='App', meta_description='desc', meta_keywords='a,b')\n"
    )
    result = migrate_source(source)
    assert result.changed
    assert not result.manual_reviews
    assert (
        "pn.ui.Page(title='App', meta_description='desc', meta_keywords='a,b')" in result.source
    )
    assert 'template-to-page' in _rules(result)


def test_template_with_unsafe_kwarg_is_not_rewritten():
    source = (
        "import panel as pn\n"
        "pn.template.BootstrapTemplate(title='App', accent_base_color='#ff0000')\n"
    )
    result = migrate_source(source)
    assert not result.changed
    assert 'pn.ui' not in result.source
    assert result.manual_reviews
    assert 'accent_base_color' in result.manual_reviews[0].message


def test_template_with_positional_args_is_not_rewritten():
    source = "from panel.template import VanillaTemplate\nVanillaTemplate('positional')\n"
    result = migrate_source(source)
    assert not result.changed
    assert result.manual_reviews


def test_progress_max_is_rewritten():
    """Progress max is supported by the Material component."""
    source = "import panel as pn\npn.widgets.Progress(value=1, max=100)\n"
    result = migrate_source(source)
    assert result.changed
    assert 'pn.ui.Progress(value=1, max=100)' in result.source
    assert not result.manual_reviews


def test_progress_without_dropped_param_is_rewritten():
    source = "import panel as pn\npn.widgets.Progress(value=50)\n"
    result = migrate_source(source)
    assert result.changed
    assert 'pn.ui.Progress(value=50)' in result.source


def test_identical_component_is_still_namespace_unified():
    """Tabulator has no Material counterpart; the rewrite still happens (it's
    a safe namespace unification), just noted informationally."""
    source = "import panel as pn\npn.widgets.Tabulator()\n"
    result = migrate_source(source)
    assert result.changed
    assert 'pn.ui.Tabulator()' in result.source
    rewrite = next(r for r in result.rewrites if r.rule == 'import-path')
    assert 'namespace unification only' in rewrite.message


def test_star_args_are_left_alone_and_reported():
    source = "import panel as pn\nkwargs = {'value': 1}\npn.widgets.Progress(**kwargs)\n"
    result = migrate_source(source)
    assert not result.changed
    assert result.manual_reviews


def test_existing_panel_ui_import_alias_is_preserved():
    source = (
        "import panel.ui as ui\n"
        "import panel as pn\n"
        "pn.widgets.Button(name='Click me')\n"
    )
    result = migrate_source(source)
    assert result.source.count('import panel.ui') == 1
    assert 'pn.ui.Button(' in result.source
    assert result.source.count('import panel as pn') == 1


def test_plain_panel_ui_import_does_not_reuse_panel_name():
    source = 'import panel.ui\nimport panel as pn\npn.widgets.Button()\n'
    result = migrate_source(source)
    assert 'import panel as pn\n' in result.source
    assert 'pn.ui.Button()' in result.source
    assert 'panel.Button()' not in result.source
    assert not migrate_source(result.source).changed


def test_from_panel_import_ui_still_uses_canonical_pn_ui():
    source = 'from panel import ui\nfrom panel.widgets import Button\nButton()\n'
    result = migrate_source(source)
    assert result.source == 'from panel import ui\nfrom panel.widgets import Button\nimport panel as pn\npn.ui.Button()\n'
    assert not migrate_source(result.source).changed


def test_no_rewrite_needed_produces_no_import():
    source = "import panel as pn\nprint('hello')\n"
    result = migrate_source(source)
    assert not result.changed
    assert 'panel.ui' not in result.source


@pytest.mark.parametrize('design', ["'fast'", "'material'", 'pn.theme.Fast'])
def test_explicit_design_settings_removed(design):
    source = (
        'import panel as pn\n'
        f'pn.config.design = {design}\n'
        f'pn.extension(design={design}, sizing_mode="stretch_width")\n'
        'pn.widgets.Button()\n'
    )
    result = migrate_source(source)
    assert 'config.design' not in result.source
    assert 'design=' not in result.source
    assert 'pn.extension(sizing_mode="stretch_width")' in result.source
    assert 'pn.ui.Button()' in result.source
    assert sum(rewrite.rule == 'remove-design' for rewrite in result.rewrites) == 2
    assert not result.manual_reviews


def test_design_only_extension_call_is_kept_without_design():
    result = migrate_source('import panel as pn\npn.extension(design="fast")\npn.widgets.Button()\n')
    assert 'pn.extension()' in result.source
    assert 'import panel.ui' not in result.source


def test_design_is_kept_when_nothing_is_migrated():
    """Without panel.ui components the app would lose its design, not switch to Material."""
    source = (
        'import panel as pn\n'
        'pn.config.design = "fast"\n'
        'pn.extension(design="fast")\n'
        'pn.widgets.Button(**kwargs)\n'
    )
    result = migrate_source(source)
    assert result.source == source
    assert not [r for r in result.rewrites if r.rule == 'remove-design']


def test_template_migration_removes_design():
    source = 'import panel as pn\npn.extension(design="fast")\npn.template.BootstrapTemplate(title="App")\n'
    result = migrate_source(source)
    assert 'pn.extension()' in result.source
    assert 'pn.ui.Page(title="App")' in result.source


def test_user_defined_design_is_reported_not_removed():
    source = (
        'import panel as pn\n'
        'from corporate import CorporateDesign\n'
        'pn.config.design = CorporateDesign\n'
        'pn.extension(design=CorporateDesign)\n'
        'pn.widgets.Button()\n'
    )
    result = migrate_source(source)
    assert 'pn.config.design = CorporateDesign' in result.source
    assert 'pn.extension(design=CorporateDesign)' in result.source
    assert 'pn.ui.Button()' in result.source
    assert len(result.manual_reviews) == 2


def test_design_setting_aliases_and_semicolon_siblings():
    source = (
        'import panel as pn\n'
        'from panel import config as settings, extension as init\n'
        'settings.design = "fast"; print("keep")\n'
        'init(sizing_mode="stretch_width", design="fast")\n'
        'pn.widgets.Button()\n'
    )
    result = migrate_source(source)
    assert 'settings.design' not in result.source
    assert 'print("keep")' in result.source
    assert 'init(sizing_mode="stretch_width")' in result.source


def test_config_module_import_design_assignment_removed():
    source = 'from panel.config import config\nfrom panel.widgets import Button\nconfig.design = "fast"\nButton()\n'
    result = migrate_source(source)
    assert 'config.design' not in result.source
    assert [rewrite.rule for rewrite in result.rewrites] == ['remove-design', 'import-path']


def test_dynamic_design_settings_are_reported_not_removed():
    source = (
        'import panel as pn\n'
        'pn.config.design = select_design()\n'
        'pn.extension(design=select_design())\n'
        'pn.widgets.Button()\n'
    )
    result = migrate_source(source)
    assert result.source == source.replace('pn.widgets.Button', 'pn.ui.Button')
    assert len(result.manual_reviews) == 2


def test_unrelated_design_settings_are_preserved():
    source = 'import panel as pn\nother.config.design = "fast"\nother.extension(design="fast")\n'
    result = migrate_source(source)
    assert not result.changed
    assert result.source == source


def test_idempotent_second_pass_is_a_no_op():
    source = (
        "import panel as pn\n"
        "pn.widgets.Button(name='Click me', button_type='primary')\n"
        "pn.widgets.MenuButton(name='Menu', items=[], split=True)\n"
        "pn.template.BootstrapTemplate(title='App')\n"
    )
    first = migrate_source(source)
    assert first.changed
    second = migrate_source(first.source)
    assert not second.changed
    assert second.source == first.source
    assert not second.rewrites


def test_syntax_error_is_reported_as_parse_error_not_silently_skipped():
    """
    A file that fails to parse must not look identical to a clean file with
    nothing to change: `parse_error` is populated with a clear message so
    the CLI layer can surface it instead of silently skipping the file.
    """
    source = "def broken(:\n    pass\n"
    result = migrate_source(source)
    assert not result.changed
    assert result.source == source
    assert not result.rewrites
    assert not result.manual_reviews
    assert result.parse_error is not None
    assert result.parse_error.strip()


def test_pmui_module_alias_rewritten_and_import_removed():
    result = migrate_source("import panel_material_ui as pmu\npmu.DatePicker(label='Date')\n")
    assert result.source == "import panel as pn\npn.ui.DatePicker(label='Date')\n"
    assert _rules(result) == {'pmui-import-path'}


def test_pmui_submodule_access_rewritten():
    result = migrate_source("import panel as pn\nimport panel_material_ui as pmu\npmu.widgets.Button()\n")
    assert result.source == "import panel as pn\npn.ui.Button()\n"


def test_pmui_from_import_rewritten_and_import_removed():
    source = "import panel as pn\nfrom panel_material_ui import Button as B, Page\nB(label='a')\nPage(main=[])\n"
    result = migrate_source(source)
    assert result.source == "import panel as pn\npn.ui.Button(label='a')\npn.ui.Page(main=[])\n"


def test_pmui_import_kept_while_still_referenced():
    source = (
        "import panel as pn\n"
        "from panel_material_ui import Button, ThemeToggle\n"
        "Button()\n"
        "isinstance(obj, ThemeToggle)\n"
    )
    result = migrate_source(source)
    assert 'from panel_material_ui import ThemeToggle\n' in result.source
    assert 'pn.ui.Button()' in result.source


def test_pmui_keywords_are_not_rewritten():
    # panel.ui re-exports the same class, so keywords are already correct.
    result = migrate_source("import panel_material_ui as pmu\npmu.Button(name='x', button_type='primary')\n")
    assert "pn.ui.Button(name='x', button_type='primary')" in result.source
    assert _rules(result) == {'pmui-import-path'}


def test_pmui_migration_is_idempotent():
    first = migrate_source("import panel_material_ui as pmu\npmu.Button()\n")
    assert not migrate_source(first.source).changed
