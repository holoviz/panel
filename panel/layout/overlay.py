"""
Defines the Overlay layout, which floats one or more panels at
anchored positions on top of a base component without the panels
consuming layout space or displacing the base.
"""
from __future__ import annotations

import typing as t

import param

from .._param import Margin
from ..custom import Child, JSComponent
from .base import NamedListLike

if t.TYPE_CHECKING:
    from typing_extensions import Self

    from ..viewable import Viewable

ANCHORS = {
    "top-left", "top-center", "top-right",
    "center-left", "center", "center-right",
    "bottom-left", "bottom-center", "bottom-right",
}


def _valid_where(where: t.Any) -> bool:
    """
    Whether `where` is a valid Overlay placement: one of the nine
    named anchors or an (x, y) coordinate of ints, floats and/or
    percentage strings.
    """
    if where in ANCHORS:
        return True
    return (
        isinstance(where, (tuple, list)) and len(where) == 2 and
        all(isinstance(v, (int, float, str)) for v in where)
    )


class Overlay(NamedListLike, JSComponent):
    """
    The `Overlay` layout floats one or more panels at anchored
    positions on top of a `base` component (e.g. a map, plot, image
    or video) without the panels consuming layout space or
    displacing the base. Unlike a covering layer, each floating panel
    is only as large as its own footprint, so the base remains
    interactive (pan/zoom/click) everywhere else.

    Each panel is declared as a `(where, obj)` tuple where `where` is
    either a named anchor (one of the nine points of a 3x3 grid, e.g.
    `"top-left"` or `"center"`) or an explicit `(x, y)` coordinate
    (in pixels or as a percentage string) measured from the top-left
    of `base`. To place more than one thing at a single anchor,
    compose them first with `Row`, `Column` or `FlexBox`.

    A named anchor may only be used once; reusing one raises a
    `ValueError`. Coordinates may be reused freely. Every item must
    declare a placement explicitly -- a bare object (with no `where`)
    also raises a `ValueError`.

    `sizing_mode` and `margin` default to whatever `base` declares, so
    a responsive `base` (e.g. `sizing_mode="stretch_both"`) makes the
    Overlay responsive too without repeating yourself. Pass either
    explicitly to opt out of the inheritance for that parameter.

    Reference: https://panel.holoviz.org/reference/layouts/Overlay.html

    :Example:

    >>> pn.layout.Overlay(
    ...     ("top-left", legend),
    ...     ("top-right", pn.Column(search, layers)),
    ...     ("bottom-right", guide),
    ...     base=deckgl_map,  # e.g. sizing_mode="stretch_both"
    ... )
    """

    base = Child(default=None, doc="""
        The underlay component that the panels float on top of.
        Determines the size of the Overlay unless overridden by
        sizing_mode, width and/or height. Unless explicitly set,
        sizing_mode and margin are inherited from base.""")

    margin = Margin(default=0, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left). Defaults to 0,
        unlike most other layouts, so that a full-bleed base has no
        stray outer gap -- unless `base` is set and declares its own
        margin, which then takes precedence over this default.""")

    # Index-aligned with `objects`. Mirrors each panel's anchor or
    # coordinate so the frontend can position it; read (read-only)
    # from Python via the `anchors` property.
    _anchors = param.List(default=[], doc="""
        Read-only, index-aligned with `objects`.""")

    _esm = "overlay.js"

    def __init__(self, *objects: t.Any, **params: t.Any):
        # sizing_mode/margin default to whatever `base` declares,
        # unless the caller passed them explicitly -- checked against
        # the raw incoming kwargs, before any class defaults apply.
        self._inherit_sizing_mode = 'sizing_mode' not in params
        self._inherit_margin = 'margin' not in params
        self._updating_from_base = False
        base = params.get('base')
        if base is not None:
            if self._inherit_sizing_mode and base.sizing_mode is not None:
                params['sizing_mode'] = base.sizing_mode
            if self._inherit_margin:
                params['margin'] = base.margin
        super().__init__(*objects, **params)
        # NamedListLike.__init__ sets the initial `_names` directly
        # (bypassing the 'objects' watcher below), so the first sync
        # has to happen explicitly here.
        self._sync_anchors()
        self.param.watch(self._inherit_from_base, 'base')
        self.param.watch(self._track_explicit_sizing, ['sizing_mode', 'margin'])

    #----------------------------------------------------------------
    # Sizing inheritance
    #----------------------------------------------------------------

    def _track_explicit_sizing(self, *events: param.parameterized.Event) -> None:
        # Once the user sets sizing_mode/margin themselves -- whether
        # at construction or later -- stop overriding that parameter
        # on future base changes. Ignore changes we made ourselves in
        # _inherit_from_base below.
        if self._updating_from_base:
            return
        for event in events:
            if event.name == 'sizing_mode':
                self._inherit_sizing_mode = False
            elif event.name == 'margin':
                self._inherit_margin = False

    def _inherit_from_base(self, event: param.parameterized.Event) -> None:
        base = self.base
        if base is None or not (self._inherit_sizing_mode or self._inherit_margin):
            return
        updates: dict[str, t.Any] = {}
        if self._inherit_sizing_mode and base.sizing_mode is not None:
            updates['sizing_mode'] = base.sizing_mode
        if self._inherit_margin:
            updates['margin'] = base.margin
        if not updates:
            return
        self._updating_from_base = True
        try:
            self.param.update(**updates)
        finally:
            self._updating_from_base = False

    #----------------------------------------------------------------
    # NamedListLike API
    #----------------------------------------------------------------

    def _to_object_and_name(self, item: t.Any) -> tuple[Viewable, t.Any]:
        if not (isinstance(item, tuple) and len(item) == 2):
            raise ValueError(
                "Overlay items must be (anchor, object) tuples, e.g. "
                "('top-left', widget) or ((x, y), widget); got "
                f"{item!r}."
            )
        where, obj = item
        if not _valid_where(where):
            raise ValueError(f"invalid anchor: {where!r}")
        from ..pane import panel
        return panel(obj), where

    def _update_names(self, event: param.parameterized.Event) -> None:
        super()._update_names(event)
        self._sync_anchors()

    def _sync_anchors(self) -> None:
        """
        Validates the current `_names` (anchors, aligned with
        `objects`) and mirrors them onto `_anchors` for the frontend.
        Runs after every mutation, whether via the constructor, the
        list-like methods (append/insert/extend/__setitem__), or a
        direct assignment to `.objects`.
        """
        seen = set()
        for where in self._names:
            if not _valid_where(where):
                raise ValueError(f"invalid anchor: {where!r}; must be one of {sorted(ANCHORS)} or an (x, y) coordinate")
            if where in ANCHORS:
                if where in seen:
                    raise ValueError(f"duplicate anchor: {where!r}")
                seen.add(where)
        self._anchors = list(self._names)

    def clone(self, *objects: t.Any, **params: t.Any) -> Self:
        """
        Makes a copy of the Overlay sharing the same parameters.

        Parameters
        ----------
        objects: (anchor, object) tuples to add to the cloned Overlay.
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned Overlay object
        """
        if objects:
            overrides = objects
            if 'objects' in params:
                raise ValueError(
                    "Overlay objects should be supplied either as "
                    "positional arguments or as a keyword, not both."
                )
        elif 'objects' in params:
            overrides = params.pop('objects')
        else:
            overrides = tuple(zip(self._names, self.objects))
        p = dict(self.param.values(), **params)
        del p['objects']
        return type(self)(*overrides, **p)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @property
    def anchors(self) -> list[t.Any]:
        """
        Read-only list of each panel's anchor or coordinate, aligned
        with `objects`.
        """
        return list(self._anchors)
