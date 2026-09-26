"""
The ``libcst`` codemod implementing the migration rewrite rules:

1. Rewrite classic import/access paths (``panel.widgets.X``, ``panel.pane.X``,
   ``panel.layout.X``, bare ``panel.X`` layout shortcuts, ``panel.chat.X``,
    ``panel.indicators.X``) to the ``panel.ui`` equivalent, inserting
   ``import panel.ui as pnui`` once per file.
2. ``name=`` to ``label=`` on calls resolved to a class with a ``label`` param.
3. ``button_type=``/``button_style=`` to ``color=``/``variant=``.
4. ``MenuButton(split=True)`` to ``SplitButton(...)``.
5. Classic template instantiation to ``panel.ui.Page(...)`` when every keyword
   used is confirmed compatible.
6. Remove explicit design selections so migrated apps use the ``panel.ui``
   default, reporting expressions with side effects for manual review.

Resolution of a call's callee back to its classic dotted path (through
``import panel as pn``, ``from panel import widgets as w``,
``from panel.widgets import Button``, etc.) is done with a small hand-rolled
import-alias tracker rather than ``FullyQualifiedNameProvider``: the aliasing
forms this codemod has to support are a small, fixed set, and a tracker scoped
to exactly those forms is easier to reason about and keep correct than
adapting a general-purpose provider to this problem.

The component rules that touch a call (1-4) are applied together, in a single pass
over each ``Call`` node, once that node's callee has been resolved to a
classic dotted path: rule 1's path rewrite and rules 2-4's keyword rewrites
all rewrite the *same* node, so doing them as one atomic operation avoids
having to re-resolve an already-rewritten node in a second pass. Classic
template calls (rule 5) never resolve to a name in ``panel.ui`` in the first
place (there is no ``panel.ui.BootstrapTemplate``), so they cannot collide
with rules 1-4 and are handled as an independent branch. Explicit design
arguments (rule 6) are handled separately from component and template calls.

Running the codemod on already-migrated code is a no-op: every rewrite target
lives under the inserted ``panel.ui`` alias, whose dotted path (``panel.ui``)
never matches a classic access path in :mod:`.compat`, so a second pass finds
nothing left to resolve.
"""
from __future__ import annotations

import dataclasses

import libcst as cst

from libcst.metadata import MetadataWrapper, PositionProvider

from . import compat
from .report import ManualReview, Rewrite

RULE_IMPORT_PATH = 'import-path'
RULE_NAME_TO_LABEL = 'name-to-label'
RULE_BUTTON_APPEARANCE = 'button-appearance'
RULE_MENU_BUTTON_SPLIT = 'menu-button-split'
RULE_TEMPLATE_TO_PAGE = 'template-to-page'
RULE_REMOVE_DESIGN = 'remove-design'

DEFAULT_PANEL_UI_ALIAS = 'pnui'


@dataclasses.dataclass
class MigrationResult:
    """The outcome of running the codemod on one file's source."""

    source: str
    changed: bool
    rewrites: list[Rewrite]
    manual_reviews: list[ManualReview]
    parse_error: str | None = None


def _dotted_name_to_str(node: cst.BaseExpression) -> str | None:
    """``Attribute``/``Name`` chain -> dotted string, e.g. ``panel.widgets``."""
    parts: list[str] = []
    cur: cst.BaseExpression = node
    while isinstance(cur, cst.Attribute):
        parts.append(cur.attr.value)
        cur = cur.value
    if isinstance(cur, cst.Name):
        parts.append(cur.value)
    else:
        return None
    return '.'.join(reversed(parts))


class _ImportAliasCollector(cst.CSTVisitor):
    """
    Builds a map of local names to the fully-dotted ``panel`` path they refer
    to, covering ``import panel as pn``, ``import panel.widgets as pnw``,
    plain ``import panel``/``import panel.widgets``, ``from panel import
    widgets as w``, and ``from panel.widgets import Button as B``. Only names
    rooted at ``panel`` are tracked; everything else is irrelevant to this
    codemod.

    Also records the local alias already bound to ``panel.ui`` (if any), so
    the codemod reuses an existing ``import panel.ui as pnui``-style import
    instead of inserting a second one.
    """

    def __init__(self) -> None:
        self.aliases: dict[str, str] = {}
        self.panel_ui_alias: str | None = None

    def visit_Import(self, node: cst.Import) -> None:
        for alias in node.names:
            dotted = _dotted_name_to_str(alias.name)
            if dotted is None or not (dotted == 'panel' or dotted.startswith('panel.')):
                continue
            if alias.asname is not None and isinstance(alias.asname.name, cst.Name):
                bound = alias.asname.name.value
                self.aliases[bound] = dotted
            else:
                # `import panel` / `import panel.widgets` both bind the
                # top-level name `panel`.
                bound = dotted.split('.')[0]
                self.aliases[bound] = bound
            if dotted == 'panel.ui' and alias.asname is not None:
                self.panel_ui_alias = bound

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if node.module is None or node.relative:
            return
        module_dotted = _dotted_name_to_str(node.module)
        if module_dotted is None or not (module_dotted == 'panel' or module_dotted.startswith('panel.')):
            return
        if isinstance(node.names, cst.ImportStar):
            return
        for alias in node.names:
            if not isinstance(alias.name, cst.Name):
                continue
            imported_name = alias.name.value
            if alias.asname is not None and isinstance(alias.asname.name, cst.Name):
                bound = alias.asname.name.value
            else:
                bound = imported_name
            self.aliases[bound] = f'{module_dotted}.{imported_name}'
            if module_dotted == 'panel' and imported_name == 'ui':
                self.panel_ui_alias = bound


def _resolve_dotted(expr: cst.BaseExpression, aliases: dict[str, str]) -> str | None:
    """
    Resolve a ``Call.func``-style ``Name``/``Attribute`` chain to its
    fully-dotted classic path, e.g. ``pn.widgets.Button`` -> ``panel.widgets.Button``,
    given the alias table built by :class:`_ImportAliasCollector`.
    """
    parts: list[str] = []
    cur: cst.BaseExpression = expr
    while isinstance(cur, cst.Attribute):
        parts.append(cur.attr.value)
        cur = cur.value
    if not isinstance(cur, cst.Name):
        return None
    parts.append(cur.value)
    parts.reverse()

    base, rest = parts[0], parts[1:]
    if base not in aliases:
        return None
    resolved_base = aliases[base]
    if not rest:
        return resolved_base
    return resolved_base + '.' + '.'.join(rest)


def _attribute(alias: str, name: str) -> cst.Attribute:
    return cst.Attribute(value=cst.Name(alias), attr=cst.Name(name))


def _is_true(expr: cst.BaseExpression) -> bool:
    return isinstance(expr, cst.Name) and expr.value == 'True'


def _safe_design_value(expr: cst.BaseExpression) -> bool:
    return isinstance(expr, (cst.SimpleString, cst.Name)) or (
        isinstance(expr, cst.Attribute) and _dotted_name_to_str(expr) is not None
    )


def _rename_kwarg(args: list[cst.Arg], old: str, new: str) -> tuple[list[cst.Arg], bool]:
    changed = False
    new_args = []
    for arg in args:
        if arg.keyword is not None and arg.keyword.value == old:
            new_args.append(arg.with_changes(keyword=cst.Name(new)))
            changed = True
        else:
            new_args.append(arg)
    return new_args, changed


def _drop_kwarg(args: list[cst.Arg], name: str) -> list[cst.Arg]:
    dropped_last = bool(args) and args[-1].keyword is not None and args[-1].keyword.value == name
    new_args = [arg for arg in args if not (arg.keyword is not None and arg.keyword.value == name)]
    if dropped_last and new_args:
        # The dropped argument was the last one, so its predecessor is now
        # the last argument in the call and must not keep a trailing comma.
        new_args[-1] = new_args[-1].with_changes(comma=cst.MaybeSentinel.DEFAULT)
    return new_args


class _PanelMigrateTransformer(cst.CSTTransformer):
    """
    Applies rules 1-5 to every ``Call`` node whose callee resolves to a
    classic Panel component or template access path.
    """

    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, aliases: dict[str, str], existing_pnui_alias: str | None) -> None:
        super().__init__()
        self._aliases = aliases
        self.pnui_alias = existing_pnui_alias or DEFAULT_PANEL_UI_ALIAS
        self.needs_pnui_import = False
        self.rewrites: list[Rewrite] = []
        self.manual_reviews: list[ManualReview] = []

    def _line(self, node: cst.CSTNode) -> int:
        return self.get_metadata(PositionProvider, node).start.line

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:
        dotted = _resolve_dotted(original_node.func, self._aliases)
        if dotted is None:
            return updated_node

        if dotted == 'panel.extension':
            design_args = [
                arg for arg in original_node.args
                if arg.keyword is not None and arg.keyword.value == 'design'
            ]
            if design_args:
                line = self._line(original_node)
                if not all(_safe_design_value(arg.value) for arg in design_args):
                    self.manual_reviews.append(ManualReview(
                        line, 'panel.extension(design=...) uses an expression; remove the design '
                        'setting manually to preserve its side effects.'
                    ))
                else:
                    self.rewrites.append(Rewrite(line, RULE_REMOVE_DESIGN, 'removed panel.extension(design=...)'))
                    return updated_node.with_changes(args=_drop_kwarg(list(updated_node.args), 'design'))
            return updated_node

        template_match = compat.TEMPLATE_MATCHES.get(dotted)
        match = compat.COMPONENT_MATCHES.get(dotted) if template_match is None else None
        if template_match is None and match is None:
            return updated_node

        line = self._line(original_node)
        used_kwargs = {arg.keyword.value for arg in original_node.args if arg.keyword is not None}
        has_star = any(arg.star for arg in original_node.args)
        has_positional = any(arg.keyword is None and not arg.star for arg in original_node.args)

        if has_star:
            self.manual_reviews.append(ManualReview(
                line=line,
                message=(
                    f'{dotted}(...) uses * or ** argument unpacking; the keyword arguments in use '
                    'cannot be determined statically, left unmigrated for manual review.'
                ),
            ))
            return updated_node

        if template_match is not None:
            return self._handle_template(updated_node, template_match, used_kwargs, has_positional, line)

        assert match is not None
        # `split=True` on MenuButton is handled by the dedicated rule 4
        # (MenuButton(split=True) -> SplitButton), not treated as a generic
        # unsafe-to-migrate dropped parameter. Any other use of `split`
        # (False, or a non-literal value) is genuinely unsafe: panel.ui's
        # MenuButton has no `split` parameter at all, so it falls through to
        # the ordinary dropped-parameter conflict check below.
        menu_button_split_true = False
        if dotted == compat.MENU_BUTTON_CLASSIC_PATH and compat.MENU_BUTTON_SPLIT_KWARG in used_kwargs:
            split_arg = next(
                a for a in original_node.args
                if a.keyword is not None and a.keyword.value == compat.MENU_BUTTON_SPLIT_KWARG
            )
            menu_button_split_true = _is_true(split_arg.value)

        button_group = dotted in ('panel.widgets.RadioButtonGroup', 'panel.widgets.CheckButtonGroup')
        dropped_for_conflict_check = match.dropped_params - {'variant'} if button_group else match.dropped_params
        if menu_button_split_true:
            dropped_for_conflict_check = dropped_for_conflict_check - {compat.MENU_BUTTON_SPLIT_KWARG}

        conflicting = used_kwargs & dropped_for_conflict_check
        if conflicting:
            self.manual_reviews.append(ManualReview(
                line=line,
                message=(
                    f"{dotted}(...) uses {', '.join(sorted(conflicting))}, which panel.ui.{match.ui_name} "
                    'does not support; left unmigrated for manual review.'
                ),
            ))
            return updated_node

        if button_group:
            for arg in original_node.args:
                if arg.keyword is None or arg.keyword.value not in ('variant', 'button_style'):
                    continue
                if not isinstance(arg.value, cst.SimpleString) or arg.value.evaluated_value not in ('solid', 'outline'):
                    self.manual_reviews.append(ManualReview(
                        line, f'{dotted} uses a dynamic {arg.keyword.value}; left unmigrated for manual review.'
                    ))
                    return updated_node

        return self._rewrite_component_call(updated_node, match, dotted, used_kwargs, line)

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine,
    ) -> cst.BaseStatement | cst.RemovalSentinel:
        body = []
        for stmt in original_node.body:
            if not isinstance(stmt, cst.Assign) or len(stmt.targets) != 1 or (
                _resolve_dotted(stmt.targets[0].target, self._aliases)
                not in ('panel.config.design', 'panel.config.config.design')
            ):
                body.append(stmt)
                continue
            line = self._line(stmt)
            if not _safe_design_value(stmt.value):
                self.manual_reviews.append(ManualReview(
                    line, 'panel.config.design uses an expression; remove the design '
                    'setting manually to preserve its side effects.'
                ))
                body.append(stmt)
                continue
            self.rewrites.append(Rewrite(line, RULE_REMOVE_DESIGN, 'removed panel.config.design assignment'))
        if len(body) == len(original_node.body):
            return updated_node
        if not body:
            return cst.RemoveFromParent()
        return updated_node.with_changes(body=body)

    def _rewrite_component_call(
        self, node: cst.Call, match: compat.ComponentMatch, dotted: str, used_kwargs: set[str], line: int
    ) -> cst.Call:
        new_args = list(node.args)
        final_ui_name = match.ui_name

        # Rule 4: MenuButton(split=True) -> SplitButton(...)
        if dotted == compat.MENU_BUTTON_CLASSIC_PATH and compat.MENU_BUTTON_SPLIT_KWARG in used_kwargs:
            split_arg = next(
                a for a in new_args
                if a.keyword is not None and a.keyword.value == compat.MENU_BUTTON_SPLIT_KWARG
            )
            if _is_true(split_arg.value):
                new_args = _drop_kwarg(new_args, compat.MENU_BUTTON_SPLIT_KWARG)
                final_ui_name = compat.SPLIT_BUTTON_UI_NAME
                self.rewrites.append(Rewrite(
                    line, RULE_MENU_BUTTON_SPLIT,
                    f'{dotted}(split=True, ...) -> panel.ui.{final_ui_name}(...); '
                    "review 'clicked'/callback semantics by hand (plan §8.2)",
                ))

        # Rule 2: name= -> label=
        if match.has_label and 'name' in used_kwargs and 'label' not in used_kwargs:
            new_args, renamed = _rename_kwarg(new_args, 'name', 'label')
            if renamed:
                self.rewrites.append(Rewrite(line, RULE_NAME_TO_LABEL, f'{dotted}: name= -> label='))

        # Rule 3: button_type=/button_style= -> color=/variant=
        for classic_kw, modern_kw in compat.BUTTON_APPEARANCE_RENAMES.items():
            supported = match.has_color_alias if modern_kw == 'color' else (
                match.has_variant_alias or dotted in ('panel.widgets.RadioButtonGroup', 'panel.widgets.CheckButtonGroup')
            )
            if not supported or classic_kw not in used_kwargs or modern_kw in used_kwargs:
                continue
            new_args, renamed = _rename_kwarg(new_args, classic_kw, modern_kw)
            if renamed:
                self.rewrites.append(Rewrite(
                    line, RULE_BUTTON_APPEARANCE, f'{dotted}: {classic_kw}= -> {modern_kw}='
                ))

        if dotted in ('panel.widgets.RadioButtonGroup', 'panel.widgets.CheckButtonGroup'):
            for index, arg in enumerate(new_args):
                if arg.keyword is not None and arg.keyword.value == 'variant' and isinstance(arg.value, cst.SimpleString):
                    value = arg.value.evaluated_value
                    assert isinstance(value, str)
                    new_args[index] = arg.with_changes(value=cst.SimpleString(repr({
                        'solid': 'contained', 'outline': 'outlined'
                    }[value])))

        # Rule 1: rewrite the access path itself.
        self.needs_pnui_import = True
        note = (
            f' (panel.ui.{final_ui_name} is the same class; namespace unification only, no behavior change)'
            if match.identical else ''
        )
        self.rewrites.append(Rewrite(
            line, RULE_IMPORT_PATH, f'{dotted} -> panel.ui.{final_ui_name}{note}'
        ))
        return node.with_changes(func=_attribute(self.pnui_alias, final_ui_name), args=new_args)

    def _handle_template(
        self, node: cst.Call, template_match: compat.TemplateMatch,
        used_kwargs: set[str], has_positional: bool, line: int,
    ) -> cst.Call:
        unsafe_kwargs = used_kwargs - template_match.allowed_kwargs
        if unsafe_kwargs or has_positional:
            reasons = sorted(unsafe_kwargs)
            if has_positional:
                reasons = ['positional arguments'] + reasons
            self.manual_reviews.append(ManualReview(
                line=line,
                message=(
                    f'{template_match.classic_path}(...) uses {", ".join(reasons)}, which are not '
                    'confirmed compatible with panel.ui.Page; left unmigrated for manual review.'
                ),
            ))
            return node

        self.needs_pnui_import = True
        self.rewrites.append(Rewrite(
            line, RULE_TEMPLATE_TO_PAGE, f'{template_match.classic_path} -> panel.ui.{compat.PAGE_UI_NAME}'
        ))
        return node.with_changes(func=_attribute(self.pnui_alias, compat.PAGE_UI_NAME))


def _is_docstring(stmt: cst.BaseStatement) -> bool:
    if not (isinstance(stmt, cst.SimpleStatementLine) and stmt.body):
        return False
    expr = stmt.body[0]
    return isinstance(expr, cst.Expr) and isinstance(expr.value, cst.SimpleString)


def _is_import(stmt: cst.BaseStatement) -> bool:
    return (
        isinstance(stmt, cst.SimpleStatementLine)
        and bool(stmt.body)
        and isinstance(stmt.body[0], (cst.Import, cst.ImportFrom))
    )


def _insert_pnui_import(module: cst.Module, alias: str) -> cst.Module:
    """
    Insert ``import panel.ui as pnui`` after the module docstring (if any) and
    the contiguous block of leading imports, so it lands with the rest of the
    file's imports rather than at the very top or in the middle of the code.
    """
    import_stmt = cst.SimpleStatementLine(body=[
        cst.Import(names=[cst.ImportAlias(
            name=cst.Attribute(value=cst.Name('panel'), attr=cst.Name('ui')),
            asname=cst.AsName(name=cst.Name(alias)),
        )])
    ])
    body = list(module.body)
    insert_at = 0
    for i, stmt in enumerate(body):
        if _is_import(stmt) or (i == 0 and _is_docstring(stmt)):
            insert_at = i + 1
        else:
            break
    body.insert(insert_at, import_stmt)
    return module.with_changes(body=body)


def migrate_source(source: str) -> MigrationResult:
    """
    Run the ``panel migrate`` codemod over one file's source and return the
    rewritten source plus a report of what was (and wasn't) changed.
    """
    try:
        module = cst.parse_module(source)
    except cst.ParserSyntaxError as exc:
        return MigrationResult(
            source=source, changed=False, rewrites=[], manual_reviews=[], parse_error=str(exc),
        )

    alias_collector = _ImportAliasCollector()
    module.visit(alias_collector)

    wrapper = MetadataWrapper(module)
    transformer = _PanelMigrateTransformer(alias_collector.aliases, alias_collector.panel_ui_alias)
    new_module = wrapper.visit(transformer)

    if transformer.needs_pnui_import and alias_collector.panel_ui_alias is None:
        new_module = _insert_pnui_import(new_module, transformer.pnui_alias)

    new_source = new_module.code
    return MigrationResult(
        source=new_source,
        changed=new_source != source,
        rewrites=transformer.rewrites,
        manual_reviews=transformer.manual_reviews,
    )
