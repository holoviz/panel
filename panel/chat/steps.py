from __future__ import annotations

import param

from ..io.resources import CDN_DIST
from ..layout import Column
from ..pane.markup import Markdown
from .step import ChatStep
from .utils import serialize_recursively


class ChatSteps(Column):

    step_params = param.Dict(
        default={},
        doc="Parameters to pass to the ChatStep constructor.",
    )

    active = param.Boolean(
        default=True,
        doc="Whether additional steps can be automatically appended to the ChatSteps.",
    )

    css_classes = param.List(
        default=["chat-steps"],
        doc="CSS classes to apply to the component.",
    )

    _rename = {"step_params": None, "active": None, **Column._rename}

    _stylesheets = [f"{CDN_DIST}css/chat_steps.css"]

    @param.depends("objects", watch=True, on_init=True)
    def _validate_steps(self):
        for step in self.objects:
            if not isinstance(step, ChatStep):
                raise ValueError(f"Expected ChatStep, got {step.__class__.__name__}")

    def create_step(self, objects: str | list[str] | None = None, **step_params):
        """
        Create a new ChatStep and append it to the ChatSteps.

        Arguments
        ---------
        objects : str | list[str] | None
            The initial object or objects to append to the ChatStep.
        **step_params : dict
            Parameters to pass to the ChatStep constructor.

        Returns
        -------
        ChatStep
            The newly created ChatStep.
        """
        merged_step_params = self.step_params.copy()
        if objects is not None:
            if not isinstance(objects, list):
                objects = [objects]
            objects = [
                (
                    Markdown(obj, css_classes=["step-message"])
                    if isinstance(obj, str)
                    else obj
                )
                for obj in objects
            ]
            step_params["objects"] = objects
        merged_step_params.update(step_params)
        step = ChatStep(**merged_step_params)
        self.append(step)
        return step

    def serialize(
        self,
        prefix_with_viewable_label: bool = True,
        prefix_with_container_label: bool = True,
    ) -> str:
        """
        Format the objects to a string.

        Arguments
        ---------
        prefix_with_viewable_label : bool
            Whether to include the name of the Viewable, or type
            of the viewable if no name is specified.
        prefix_with_container_label : bool
            Whether to include the name of the container, or type
            of the container if no name is specified.

        Returns
        -------
        str
            The serialized string.
        """
        return serialize_recursively(
            self,
            prefix_with_viewable_label=prefix_with_viewable_label,
            prefix_with_container_label=prefix_with_container_label,
        )

    def __enter__(self):
        self.active = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.active = False
