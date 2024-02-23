from __future__ import annotations

from typing import (
    TYPE_CHECKING, ClassVar, Optional, Type,
)

import param

from ..models.chatarea_input import (
    ChatAreaInput as _bkChatAreaInput, ShiftEnterKeyDown,
)
from ..widgets import TextAreaInput as _PnTextAreaInput

if TYPE_CHECKING:
    from bokeh.document import Document
    from pyviz_comms import Comm

from bokeh.model import Model


class ChatAreaInput(_PnTextAreaInput):
    """
    The `ChatAreaInput` allows entering any multiline string using a text input
    box.

    Lines are joined with the newline character `\n`.

    Reference: https://panel.holoviz.org/reference/widgets/TextAreaInput.html
    :Example:

    >>> ChatAreaInput(
    ...     name='Description', placeholder='Enter your description here...'
    ... )
    """

    resizable = param.ObjectSelector(
        objects=["both", "width", "height", False],
        doc="""
        Whether the layout is interactively resizable,
        and if so in which dimensions: `width`, `height`, or `both`.
        Can only be set during initialization.""",
    )

    _widget_type: ClassVar[Type[Model]] = _bkChatAreaInput

    def _get_model(
        self,
        doc: Document,
        root: Optional[Model] = None,
        parent: Optional[Model] = None,
        comm: Optional[Comm] = None,
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._register_events("shift_enter_key_down", model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event: ShiftEnterKeyDown) -> None:
        """
        Clear value on shift enter key down.
        """
        with param.parameterized.batch_call_watchers(self):
            self.value = self.value_input
        with param.discard_events(self):
            self.value = ""
        self.value_input = ""
