"""
Structural tests for panel.command._migrate.compat.

These assert properties of the *introspected* data rather than hardcoding
names or counts from the plan doc, which predate panel.ui existing and would
go stale as panel.ui grows. See plan §10.1 / §2.
"""
import param
import pytest

pytest.importorskip("libcst")

from panel.command._migrate import compat


def test_component_matches_ui_name_gettable():
    import panel.ui as pn_ui
    for match in compat.COMPONENT_MATCHES.values():
        ui_cls = getattr(pn_ui, match.ui_name, None)
        assert ui_cls is match.ui_cls
        assert isinstance(ui_cls, type) and issubclass(ui_cls, param.Parameterized)


def test_component_matches_classic_cls_resolves_to_its_own_path():
    for classic_path, match in compat.COMPONENT_MATCHES.items():
        assert classic_path == match.classic_path
        assert classic_path.rsplit('.', 1)[-1] == match.ui_name


def test_identical_components_really_are_identical():
    """
    Every component we claim has no Material counterpart (a plain re-export)
    must actually resolve to the identical class object in panel.ui, not
    merely a same-named one.
    """
    identical = [m for m in compat.COMPONENT_MATCHES.values() if m.identical]
    assert identical, 'expected at least one classic-only, re-exported component'
    for match in identical:
        assert match.ui_cls is match.classic_cls


def test_non_identical_components_are_distinct_classes():
    for match in compat.COMPONENT_MATCHES.values():
        if not match.identical:
            assert match.ui_cls is not match.classic_cls


def test_dropped_params_are_really_dropped():
    for match in compat.COMPONENT_MATCHES.values():
        classic_params = {n for n in match.classic_cls.param if not n.startswith('_')}
        ui_params = {n for n in match.ui_cls.param if not n.startswith('_')}
        assert match.dropped_params <= classic_params
        assert match.dropped_params.isdisjoint(ui_params)


def test_progress_max_is_a_dropped_param():
    """The flagship dropped-parameter example from plan §8.1/§10.1."""
    match = compat.COMPONENT_MATCHES['panel.widgets.Progress']
    assert 'max' in match.dropped_params


def test_has_label_matches_live_param():
    for match in compat.COMPONENT_MATCHES.values():
        assert match.has_label == ('label' in match.classic_cls.param)


def test_has_button_appearance_aliases_match_live_params():
    """
    Gated on both sides: the classic class must have the classic/modern pair,
    *and* the panel.ui counterpart must still have the modern name (it isn't
    one of the params dropped relative to classic -- see
    test_check_button_group_variant_alias_is_gated_by_dropped_param below for
    the case where it is).
    """
    for match in compat.COMPONENT_MATCHES.values():
        classic_has_color_pair = 'button_type' in match.classic_cls.param and 'color' in match.classic_cls.param
        classic_has_variant_pair = 'button_style' in match.classic_cls.param and 'variant' in match.classic_cls.param
        assert match.has_color_alias == (classic_has_color_pair and 'color' not in match.dropped_params)
        assert match.has_variant_alias == (classic_has_variant_pair and 'variant' not in match.dropped_params)


def test_check_button_group_variant_alias_is_gated_by_dropped_param():
    """
    plan §8.2: classic `variant` means something different from Material
    `variant` for these two classes, and panel.ui drops it outright, so the
    codemod must not treat `button_style=` as safely renameable to
    `variant=` for them even though the classic class has both params.
    """
    for name in ('CheckButtonGroup', 'RadioButtonGroup'):
        match = compat.COMPONENT_MATCHES[f'panel.widgets.{name}']
        assert 'button_style' in match.classic_cls.param
        assert 'variant' in match.classic_cls.param
        assert 'variant' in match.dropped_params
        assert not match.has_variant_alias
        assert match.has_color_alias


def test_row_and_other_layouts_have_no_label():
    """
    Layouts have a distinct `name` concept (tab titles etc.) rather than a
    `label`, so the name->label rule must never fire for them.
    """
    for name in ('panel.Row', 'panel.Column', 'panel.Tabs'):
        match = compat.COMPONENT_MATCHES.get(name)
        if match is not None:
            assert not match.has_label


def test_button_appearance_renames_pair_is_bidirectional_over_known_classes():
    button_match = compat.COMPONENT_MATCHES['panel.widgets.Button']
    assert button_match.has_color_alias
    assert button_match.has_variant_alias
    assert compat.BUTTON_APPEARANCE_RENAMES == {'button_type': 'color', 'button_style': 'variant'}


def test_menu_button_split_rule_points_at_real_classes():
    import panel.ui as pn_ui
    match = compat.COMPONENT_MATCHES[compat.MENU_BUTTON_CLASSIC_PATH]
    assert match.classic_cls.__name__ == 'MenuButton'
    split_button_cls = getattr(pn_ui, compat.SPLIT_BUTTON_UI_NAME)
    assert issubclass(split_button_cls, param.Parameterized)
    assert compat.MENU_BUTTON_SPLIT_KWARG in match.classic_cls.param


def test_every_ui_all_name_is_gettable_from_panel_ui():
    import panel.ui as pn_ui
    for name in compat.UI_ALL:
        assert hasattr(pn_ui, name), f'panel.ui.__all__ claims {name!r} but it is not an attribute'


def test_template_matches_allowed_kwargs_are_verified_live():
    import panel.ui as pn_ui
    page_params = {n for n in pn_ui.Page.param if not n.startswith('_')}
    meta_params = compat._meta_params(pn_ui.Page)
    assert compat.TEMPLATE_MATCHES, 'expected at least one classic template to be tracked'
    for match in compat.TEMPLATE_MATCHES.values():
        template_params = {n for n in match.classic_cls.param if not n.startswith('_')}
        for kwarg in match.allowed_kwargs:
            assert kwarg in template_params
            if kwarg in compat._TEMPLATE_KWARG_CANDIDATES:
                assert kwarg in page_params
            else:
                # A `meta_<suffix>` kwarg: not a `Page.param` member itself,
                # but forwarded by `Page.__init__` into the nested `Meta`
                # object it builds -- see `compat._meta_params`.
                assert kwarg.startswith(compat._META_KWARG_PREFIX)
                assert kwarg[len(compat._META_KWARG_PREFIX):] in meta_params


def test_template_matches_include_meta_kwargs():
    """
    `Page` doesn't declare `meta_description`/`meta_keywords`/etc. as
    `Page.param` members -- `Page.__init__` forwards any `meta_<suffix>`
    keyword into a nested `Meta` object instead (see
    `panel_material_ui.template.base.Page.__init__`). Classic templates use
    the identical `meta_<suffix>` spelling, so these must still be allowed.
    """
    for template_name in ('FastListTemplate', 'BootstrapTemplate'):
        match = compat.TEMPLATE_MATCHES[f'panel.template.{template_name}']
        template_params = {n for n in match.classic_cls.param if not n.startswith('_')}
        expected = {
            n for n in template_params
            if n.startswith(compat._META_KWARG_PREFIX)
        }
        assert expected, f'{template_name} is expected to declare meta_* params'
        assert expected <= match.allowed_kwargs
        # Sanity-check against the specific names the bug report called out,
        # without assuming every one of them exists on every template.
        for name in ('meta_description', 'meta_keywords', 'meta_author', 'meta_refresh', 'meta_viewport'):
            if name in template_params:
                assert name in match.allowed_kwargs


def test_page_is_the_template_rewrite_target():
    import panel.ui as pn_ui
    assert hasattr(pn_ui, compat.PAGE_UI_NAME)


def test_template_matches_cover_the_documented_classic_templates():
    import panel.template as pn_template
    for name in compat._TEMPLATE_CLASS_NAMES:
        assert hasattr(pn_template, name), f'{name} is expected to exist in panel.template'
        assert f'panel.template.{name}' in compat.TEMPLATE_MATCHES
