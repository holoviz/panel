"""
Introspects the installed ``panel`` and ``panel.ui`` namespaces to build the
lookup data the ``panel migrate`` codemod and its report need.

Everything here is derived at import time by walking ``param.Parameterized``
subclasses and comparing their ``.param`` members, the same technique used by
``plans/scripts/panel_ui_api_audit.py``. Keeping it data-driven means this
module can't silently drift from ``panel.ui`` as components are added,
dropped parameters are restored, etc.

The only genuinely hardcoded pieces are the handful of rules that cannot be
derived generically: the ``MenuButton`` -> ``SplitButton`` special case, the
``button_type``/``button_style`` rename pair, and the *candidate* keyword
arguments for the classic-template -> ``Page`` allowlist (which is still
verified against the live classes rather than trusted blindly). The
allowlist also covers ``meta_<suffix>`` keywords, which ``Page.__init__``
strips and forwards into a nested ``Meta`` object rather than declaring as
``Page.param`` members directly; membership for those is derived entirely
from introspecting the nested ``Meta`` class, not hardcoded.

This module does not import ``libcst``, so it can be imported (and tested)
without the optional ``migrate`` dependency installed.
"""
from __future__ import annotations

import dataclasses
import typing as t

import param

import panel as pn
import panel.chat as pn_chat
import panel.io.convert as pn_convert
import panel.io.resources as pn_resources
import panel.layout as pn_layout
import panel.pane as pn_pane
import panel.template as pn_template
import panel.widgets as pn_widgets
import panel.widgets.indicators as pn_indicators

# Introspection must not select a design or patch classic components for an app.
_prior_design = param.Parameterized.__getattribute__(pn.config, 'design')
_patched_globals = (
    (pn.param.Param, 'mapping'),
    (pn.param.Param, 'input_widgets'),
    (pn.pane.HoloViews, 'default_widgets'),
    (pn_convert, 'loading_resources'),
    (pn_convert, 'BASE_TEMPLATE'),
    (pn_resources, 'BASE_TEMPLATE'),
)
_prior_globals = [
    (obj, attr, dict(value) if isinstance(value := getattr(obj, attr), dict) else value)
    for obj, attr in _patched_globals
]
try:
    import panel.ui as pn_ui
finally:
    for obj, attr, value in _prior_globals:
        setattr(obj, attr, value)
    param.Parameterized.__setattr__(pn.config, 'design', _prior_design)

# 'name' is structural (every Parameterized has it) rather than meaningful API
# surface, and it is handled by the dedicated name->label rule, not treated as
# a generic dropped/available parameter.
_IGNORED_PARAMS = frozenset({'name'})

# Classic submodules the codemod resolves component access through, keyed by
# the dotted path a user's source spells them with. `panel.indicators` and
# `panel.widgets.indicators` are the same module under two access paths.
_CLASSIC_MODULES: dict[str, t.Any] = {
    'panel.widgets': pn_widgets,
    'panel.pane': pn_pane,
    'panel.layout': pn_layout,
    'panel.chat': pn_chat,
    'panel.widgets.indicators': pn_indicators,
    'panel.indicators': pn_indicators,
}

# panel/__init__.py re-exports these as bare `panel.Row`-style shortcuts, on
# top of `panel.layout.Row`.
_TOP_LEVEL_MODULE = 'panel'
_TOP_LEVEL_NAMES: frozenset[str] = frozenset(pn.__all__)


def _public_components(mod: t.Any) -> dict[str, type]:
    out: dict[str, type] = {}
    for name in dir(mod):
        if name.startswith('_'):
            continue
        obj = getattr(mod, name)
        if isinstance(obj, type) and issubclass(obj, param.Parameterized):
            out[name] = obj
    return out


def _public_params(cls: type) -> set[str]:
    return {n for n in cls.param if not n.startswith('_')} - _IGNORED_PARAMS


@dataclasses.dataclass(frozen=True)
class ComponentMatch:
    """
    Everything the codemod needs to know about rewriting one classic component
    access path (e.g. ``panel.widgets.Button``) to ``panel.ui``.
    """

    #: The classic dotted access path, e.g. ``'panel.widgets.Button'``.
    classic_path: str
    #: The classic class object.
    classic_cls: type
    #: The name it is exported under in ``panel.ui`` (currently always the
    #: same name as the classic class, but kept explicit rather than assumed).
    ui_name: str
    #: The `panel.ui` class object.
    ui_cls: type
    #: True if `ui_cls is classic_cls` (a plain re-export; no behavior change).
    identical: bool
    #: Parameters on the classic class that don't exist on the `panel.ui`
    #: counterpart; using one of these in a call is unsafe to auto-migrate.
    dropped_params: frozenset[str]
    #: True if the classic class has a `label` parameter, i.e. `name=` can be
    #: safely rewritten to `label=`.
    has_label: bool
    #: True if the classic class has both `button_type` and `color`.
    has_color_alias: bool
    #: True if the classic class has both `button_style` and `variant`.
    has_variant_alias: bool


def _build_component_matches() -> dict[str, ComponentMatch]:
    matches: dict[str, ComponentMatch] = {}

    def add(module_path: str, name: str, cls: type) -> None:
        classic_path = f'{module_path}.{name}'
        if classic_path in matches:
            return
        ui_cls = getattr(pn_ui, name, None)
        if not (isinstance(ui_cls, type) and issubclass(ui_cls, param.Parameterized)):
            return
        classic_params = _public_params(cls)
        ui_params = _public_params(ui_cls)
        matches[classic_path] = ComponentMatch(
            classic_path=classic_path,
            classic_cls=cls,
            ui_name=name,
            ui_cls=ui_cls,
            identical=ui_cls is cls,
            dropped_params=frozenset(classic_params - ui_params),
            has_label='label' in cls.param,
            # Check both sides before renaming an appearance alias.
            has_color_alias=(
                'button_type' in cls.param and 'color' in cls.param and 'color' in ui_params
            ),
            has_variant_alias=(
                'button_style' in cls.param and 'variant' in cls.param and 'variant' in ui_params
            ),
        )

    for module_path, mod in _CLASSIC_MODULES.items():
        for name, cls in _public_components(mod).items():
            add(module_path, name, cls)

    for name in _TOP_LEVEL_NAMES:
        obj = getattr(pn, name, None)
        if isinstance(obj, type) and issubclass(obj, param.Parameterized):
            add(_TOP_LEVEL_MODULE, name, obj)

    return matches


#: Maps a classic dotted access path to its `panel.ui` rewrite data. Built
#: once at import time.
COMPONENT_MATCHES: dict[str, ComponentMatch] = _build_component_matches()

#: Every name importable from `panel.ui`, i.e. `panel.ui.__all__`.
UI_ALL: frozenset[str] = frozenset(pn_ui.__all__)


# ---------------------------------------------------------------------------
# MenuButton(split=True) -> SplitButton(...)
# ---------------------------------------------------------------------------
# Not derivable from parameter introspection alone: `split=True` selects a
# different, purpose-built class rather than toggling a parameter that exists
# on both sides (`SplitButton` has no `split` parameter of its own).

MENU_BUTTON_CLASSIC_PATH = 'panel.widgets.MenuButton'
MENU_BUTTON_SPLIT_KWARG = 'split'
SPLIT_BUTTON_UI_NAME = 'SplitButton'


# ---------------------------------------------------------------------------
# button_type/button_style -> color/variant
# ---------------------------------------------------------------------------
# The rename pair itself is a naming convention decision, not something that
# can be derived from introspection; whether it applies to a given class is
# still gated dynamically via `ComponentMatch.has_color_alias`/
# `has_variant_alias` above.

BUTTON_APPEARANCE_RENAMES: dict[str, str] = {
    'button_type': 'color',
    'button_style': 'variant',
}


# ---------------------------------------------------------------------------
# Classic templates -> panel.ui.Page
# ---------------------------------------------------------------------------

_TEMPLATE_CLASS_NAMES = (
    'BootstrapTemplate', 'EditableTemplate', 'FastGridTemplate',
    'FastListTemplate', 'GoldenTemplate', 'MaterialTemplate', 'ReactTemplate',
    'SlidesTemplate', 'VanillaTemplate',
)

#: Candidate keywords confirmed by hand to be directly analogous between a
#: classic template and `Page` (plan §10.1). Membership here is necessary but
#: not sufficient: `_build_template_matches` re-verifies that each name is
#: actually present on both the specific template class and `Page` before
#: allowing it, so a template missing one of these still gets the rest.
_TEMPLATE_KWARG_CANDIDATES = (
    'main', 'sidebar', 'header', 'title', 'sidebar_width', 'favicon', 'site_url',
)

#: Prefix `Page.__init__` strips from any `meta_<suffix>` keyword before
#: forwarding it into the nested `Meta` object it constructs (see
#: `panel_material_ui.template.base.Page.__init__`). Classic templates accept
#: the same `meta_<suffix>` spelling as real top-level params, so the two
#: call-site spellings match even though `Page` doesn't declare them as
#: `Page.param` members.
_META_KWARG_PREFIX = 'meta_'

PAGE_UI_NAME = 'Page'
#: Name of the `Page` param holding the nested `Meta` instance.
PAGE_META_PARAM = 'meta'


@dataclasses.dataclass(frozen=True)
class TemplateMatch:
    """
    A classic template access path and the keyword arguments that are safe to
    carry over to `panel.ui.Page` unchanged.
    """

    classic_path: str
    classic_cls: type
    allowed_kwargs: frozenset[str]


def _meta_params(page_cls: type) -> set[str]:
    """
    `Page` doesn't declare `meta_description`, `meta_keywords`, etc. as
    `Page.param` members; `Page.__init__` instead catches any `meta_<suffix>`
    keyword, strips the prefix, and forwards it into a nested
    `Meta(param.Parameterized)` instance. Introspect that nested class's
    public params the same way `_public_params` does for everything else in
    this module, so membership stays derived rather than hardcoded.
    """
    meta_cls = page_cls.param[PAGE_META_PARAM].class_
    return _public_params(meta_cls)


def _build_template_matches() -> dict[str, TemplateMatch]:
    page_cls = getattr(pn_ui, PAGE_UI_NAME)
    page_params = _public_params(page_cls)
    meta_params = _meta_params(page_cls)
    matches: dict[str, TemplateMatch] = {}
    for name in _TEMPLATE_CLASS_NAMES:
        cls = getattr(pn_template, name, None)
        if cls is None:
            continue
        template_params = _public_params(cls)
        allowed = {
            kw for kw in _TEMPLATE_KWARG_CANDIDATES
            if kw in template_params and kw in page_params
        }
        allowed.update(
            kw for kw in template_params
            if kw.startswith(_META_KWARG_PREFIX)
            and kw[len(_META_KWARG_PREFIX):] in meta_params
        )
        classic_path = f'panel.template.{name}'
        matches[classic_path] = TemplateMatch(
            classic_path=classic_path,
            classic_cls=cls,
            allowed_kwargs=frozenset(allowed),
        )
    return matches


#: Maps a classic template's dotted access path (`panel.template.<Name>`) to
#: the keyword arguments that are safe to carry over to `panel.ui.Page`.
TEMPLATE_MATCHES: dict[str, TemplateMatch] = _build_template_matches()
