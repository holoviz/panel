"""
Tests the shape of the panel.ui namespace: that it is complete with respect to
the classic namespaces, that the flat and structured forms agree, and that
importing it has no side effect other than selecting the design.

panel.ui is imported through a fixture rather than at module scope. Importing it
imports panel-material-ui, which until 0.12 patches Panel and assigns
config.design, and doing that during collection would change what the rest of
the suite collects. The fixture also undoes those patches, since they otherwise
leak into every test that runs after this module.
"""
import inspect
import sys

from subprocess import check_output
from textwrap import dedent

import param
import pytest

import panel as pn

CLASSIC_MODULES = {
    'widgets': pn.widgets,
    'layout': pn.layout,
    'pane': pn.pane,
    'chat': pn.chat,
    'indicators': pn.indicators,
}

SUBMODULES = (
    'base', 'chat', 'designs', 'indicators', 'layout', 'notifications', 'pane',
    'template', 'theme', 'widgets', 'wrappers'
)

COMPONENT_SUBMODULES = (
    'chat', 'indicators', 'layout', 'pane', 'template', 'widgets', 'wrappers'
)

# Classic names panel.ui deliberately does not re-export, keyed by the classic
# module they come from. Adding to this list is an API decision, which is why
# the test asserts against it.
OMITTED = {
    'widgets.Spinner': 'deprecated alias of NumberInput',
    'widgets.DataFrame': 'deprecated in favour of Tabulator',
    'pane.Alert': 'superseded by the Material panel.ui.Alert',
    'pane.panel': 'a function, reachable as panel.panel',
}

# Reachable through the submodules but kept out of the flat namespace, matching
# panel's own flat namespace which exports neither bases nor helper classes.
NOT_FLAT = {
    'Widget', 'WidgetBase', 'CompositeWidget', 'Panel', 'ListLike', 'ListPanel',
    'Pane', 'PaneBase', 'BooleanIndicator', 'ValueIndicator',
    'MaterialComponent', 'MaterialUIComponent', 'MaterialWidget',
    'MaterialLayout', 'MaterialListLike', 'MaterialNamedListLike',
    'MaterialPaneBase',
    'Grammar', 'GrammarList', 'Utterance', 'Voice',
}


def patched_globals():
    """
    The globals panel-material-ui replaces at import time until 0.12, which the
    ui fixture restores so that the patches do not reach the rest of the suite.
    Leaving Param.mapping patched, for instance, makes Widget.controls(jslink=True)
    raise for every classic widget with an Action or Event parameter.
    """
    import panel.io.convert
    import panel.io.resources

    from panel.pane import HoloViews
    from panel.param import Param

    return (
        (Param, 'mapping'),
        (Param, 'input_widgets'),
        (HoloViews, 'default_widgets'),
        (panel.io.convert, 'loading_resources'),
        (panel.io.convert, 'BASE_TEMPLATE'),
        (panel.io.resources, 'BASE_TEMPLATE'),
    )


def snapshot(obj, attr):
    value = getattr(obj, attr)
    # The mappings are patched in place, the rest are rebound, and the templates
    # are jinja2 Templates which cannot be copied.
    return dict(value) if isinstance(value, dict) else value


# Filled in by the ui fixture with the globals the import actually patched.
PATCHED: list[str] = []


@pytest.fixture(scope='module')
def ui():
    prior = [(obj, attr, snapshot(obj, attr)) for obj, attr in patched_globals()]
    prior_design = param.Parameterized.__getattribute__(pn.config, 'design')
    try:
        import panel.ui
    finally:
        for obj, attr, value in prior:
            if getattr(obj, attr) != value:
                PATCHED.append(f'{obj.__name__}.{attr}')
            setattr(obj, attr, value)
        # Selecting the design is the one intended side effect of the import,
        # but it must not leak out of this module either.
        param.Parameterized.__setattr__(pn.config, 'design', prior_design)
    return panel.ui


@pytest.fixture(scope='module')
def pmui(ui):
    import panel_material_ui
    return panel_material_ui


def material_components(module):
    """The public components panel_material_ui itself defines in a module."""
    return {
        name: obj for name in dir(module)
        if not name.startswith('_')
        and inspect.isclass(obj := getattr(module, name))
        and issubclass(obj, param.Parameterized)
        and obj.__module__.startswith('panel_material_ui')
    }


def run_check(check):
    return check_output([sys.executable, '-c', dedent(check)]).decode().strip()


@pytest.mark.parametrize('module', CLASSIC_MODULES)
def test_classic_components_reachable_from_submodule(ui, module):
    classic, ui_module = CLASSIC_MODULES[module], getattr(ui, module)
    missing = [
        name for name in classic.__all__
        if f'{module}.{name}' not in OMITTED and not hasattr(ui_module, name)
    ]
    assert not missing, f'panel.ui.{module} is missing {missing}'


@pytest.mark.parametrize('module', CLASSIC_MODULES)
def test_classic_components_reachable_flat(ui, module):
    classic = CLASSIC_MODULES[module]
    missing = [
        name for name in classic.__all__
        if f'{module}.{name}' not in OMITTED and name not in NOT_FLAT
        and name not in ui.__all__
    ]
    assert not missing, f'panel.ui does not export {missing} flat'


@pytest.mark.parametrize('module', COMPONENT_SUBMODULES)
def test_material_components_reachable_flat(ui, pmui, module):
    missing = [
        name for name in material_components(getattr(pmui, module))
        if name not in NOT_FLAT and name not in ui.__all__
    ]
    assert not missing, f'panel.ui does not export {missing} flat'


def test_classic_components_are_not_wrapped(ui):
    assert ui.Tabulator is pn.widgets.Tabulator
    assert ui.widgets.Tabulator is pn.widgets.Tabulator
    assert ui.Matplotlib is pn.pane.Matplotlib
    assert ui.GridStack is pn.layout.GridStack


def test_material_components_come_from_panel_material_ui(ui, pmui):
    # True only while panel.ui is a composition layer over the dependency; when
    # the implementation is vendored the identity flips (plan section 7.5).
    assert ui.Button is pmui.Button
    assert ui.widgets.Button is pmui.Button
    assert ui.MaterialUIDesign is pmui.MaterialDesign


@pytest.mark.parametrize('module', (None, *SUBMODULES))
def test_all_names_resolve(ui, module):
    obj = ui if module is None else getattr(ui, module)
    assert not [name for name in obj.__all__ if not hasattr(obj, name)]


@pytest.mark.parametrize('module', (None, *SUBMODULES))
def test_all_is_sorted_and_unique(ui, module):
    obj = ui if module is None else getattr(ui, module)
    assert len(set(obj.__all__)) == len(obj.__all__)
    assert list(obj.__all__) == sorted(obj.__all__, key=str.lower)


@pytest.mark.parametrize('module', (None, *SUBMODULES))
def test_no_module_getattr(ui, module):
    # Every export is a real import, so that type checkers and language
    # servers resolve them (plan section 3.2).
    obj = ui if module is None else getattr(ui, module)
    assert '__getattr__' not in vars(obj)


def test_flat_names_are_the_submodule_components(ui):
    submodules = [getattr(ui, module) for module in SUBMODULES]
    mismatched = [
        name for name in ui.__all__
        if not any(getattr(sub, name, None) is getattr(ui, name) for sub in submodules)
    ]
    assert not mismatched


def test_flat_namespace_exports_only_components(ui):
    assert not [name for name in ui.__all__ if inspect.ismodule(getattr(ui, name))]


def test_submodules_are_not_exported_flat(ui):
    # Otherwise `from panel.ui import *` rebinds names like `widgets`.
    assert not [name for name in SUBMODULES if name in ui.__all__]


def test_no_ambiguous_flat_names(ui):
    # A flat name that resolves to different classes in different submodules
    # cannot be exported flat; one of them has to be omitted instead.
    submodules = [getattr(ui, module) for module in SUBMODULES]
    ambiguous = [
        name for name in ui.__all__
        if len({
            id(getattr(sub, name)) for sub in submodules if hasattr(sub, name)
        }) > 1
    ]
    assert not ambiguous


def test_deprecated_dataframe_widget_is_not_exported(ui):
    # panel.widgets.DataFrame is deprecated in favour of Tabulator, so only the
    # rendering pane claims the name in panel.ui.
    assert ui.DataFrame is pn.pane.DataFrame
    assert ui.pane.DataFrame is pn.pane.DataFrame
    assert not hasattr(ui.widgets, 'DataFrame')


def test_design_alias_resolves(ui):
    from panel.theme import resolve_design
    from panel.theme.base import DESIGN_ALIASES

    assert 'material-ui' in DESIGN_ALIASES
    assert resolve_design('material-ui') is ui.MaterialUIDesign
    assert resolve_design('Material-UI') is ui.MaterialUIDesign


def test_importing_panel_ui_selects_the_material_design():
    output = run_check("""\
    import panel as pn

    import panel.ui

    print(pn.config.design is pn.ui.MaterialUIDesign, end='')
    """)
    assert output == 'True'


def test_explicit_design_survives_importing_panel_ui():
    # panel-material-ui assigns config.design unconditionally at import time;
    # panel.ui has to undo that.
    output = run_check("""\
    import panel as pn

    pn.extension(design='fast')

    import panel.ui

    print(pn.config.design.__name__, end='')
    """)
    assert output == 'Fast'


@pytest.mark.xfail(
    reason='panel-material-ui patches Panel at import time until 0.12',
    strict=False
)
def test_importing_panel_ui_does_not_patch_core(ui):
    # The patches are replaced by the extension points added in Phase 1, in the
    # upstream closeout window (plan section 6.3). This starts passing then, at
    # which point the restore in the ui fixture can go too.
    assert PATCHED == []


def test_panel_ui_has_no_config_side_effects():
    output = run_check("""\
    import panel as pn
    from panel.config import _config

    before = {p: getattr(pn.config, p) for p in _config.param if p != 'design'}

    import panel.ui

    after = {p: getattr(pn.config, p) for p in _config.param if p != 'design'}
    print(sorted(p for p in before if before[p] is not after[p]), end='')
    """)
    assert output == '[]'
