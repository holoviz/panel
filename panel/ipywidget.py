"""Functionality to enable easily interacting with ipywidgets via familiar APIs like pn.bind,
@pn.depends and pn.rx"""

from typing import TYPE_CHECKING, Iterable

import param

from .viewable import Viewer

if TYPE_CHECKING:
    try:
        from traitlets import HasTraits
    except ModuleNotFoundError:

        class HasTraits:  # type: ignore
            """Mock class"""

else:

    class HasTraits:  # type: ignore
        """Mock class"""


def to_viewer(widget: HasTraits, parameters: Iterable | None = None) -> Viewer:
    """Returns a Viewer object with parameters synced to the ipywidget widget parameters

    Args:
        widget (HasTraits): The ipywidget to create the Viewer from.
        parameters (Iterable | None): The parameters to add to the Viewer and to sync.
            If no parameters are specified all parameters on the widget will be added
            and synced.

    """
    raise NotImplementedError()


def to_rx(
    widget: HasTraits, parameters: Iterable | None = None
) -> tuple[param.rx, ...]:
    """Returns a tuple of `rx` parameters. Each one synced to a parameter of the ipywidget widget.

    Args:
        widget (HasTraits): The ipywidget to create the `rx` parameters from.
        parameters (Iterable): The parameters to create `rx` parameters from and to sync.
            If no parameters are specified all parameters on the widget will be added
            and synced.
    """
    raise NotImplementedError()
