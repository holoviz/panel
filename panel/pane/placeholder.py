"""
Defines the Placeholder pane which serves as a placeholder for other Panel components.
"""

from __future__ import annotations

import param

from ..pane.base import ReplacementPane


class Placeholder(ReplacementPane):
    """
    The `Placeholder` pane serves as a placeholder for other Panel components.
    It can be used to display a message while a computation is running, for
    example.

    Reference: https://panel.holoviz.org/reference/panes/Placeholder.html

    :Example:

    >>> with Placeholder("⏳ Idle"):
    ...     placeholder.object = "🏃 Running..."
    """

    def __init__(self, object=None, **params):
        super().__init__(object=object, **params)
        self._past_object = object  # used to restore object when Placeholder is exited
        self._temporary = False
        if object is not None:
            self._replace_panel()

    @param.depends("object", watch=True)
    def _replace_panel(self):
        if not self._temporary:
            self._past_object = self.object
        self._update_inner(self.object)

    def __enter__(self):
        self._temporary = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.object = self._past_object
        finally:
            self._temporary = False
        return False

    def update(self, object):
        """
        Updates the object on the Placeholder.

        Parameters
        ----------
        object: The object to update the Placeholder with.
        """
        self.object = object
