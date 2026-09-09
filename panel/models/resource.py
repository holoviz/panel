"""
Declares the property that carries a component's resource specification.

The resource bearing models do not share a single base: ``HTMLBox`` covers
most of them, but ``KaTeX`` derives from Bokeh's ``Markup``,
``FileDropper`` from ``InputWidget``, ``Modal`` from ``Column`` and the
plot models from ``LayoutDOM``. The property is therefore declared through
a mixin, the same pattern Bokeh uses for ``FillProps`` and friends.
"""
from __future__ import annotations

import typing as t

from bokeh.core.has_props import HasProps
from bokeh.core.properties import (
    Any, Dict, Nullable, String,
)


class ExternalResourcesMixin(HasProps):
    """
    Mixin declaring the ``external_resources`` property.

    Bokeh only serializes properties that were explicitly set, so the
    specification is derived and assigned at construction time. It can be
    passed explicitly instead, which is what the ``ReactiveHTML`` and
    ``ReactiveESM`` models do: their resources are declared on the *Panel*
    class while the Bokeh model class is shared.
    """

    external_resources = Nullable(Dict(String, Any), help="""
    Client-side specification of the external libraries and stylesheets
    this component needs, resolved by the resource registry in panel.js
    when the component is rendered.""")

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        if 'external_resources' not in kwargs:
            from ..io.resource_spec import resource_spec
            spec = resource_spec(type(self))
            if spec is not None:
                kwargs['external_resources'] = spec
        super().__init__(*args, **kwargs)


__all__ = (
    "ExternalResourcesMixin",
)
