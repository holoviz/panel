import os
import re

from functools import partial
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import pandas as pd
import param

from ..custom import PyComponent
from ..layout import Column, FlexBox, ListPanel
from ..layout.base import NamedListLike
from ..pane import panel
from ..pane.image import Image
from ..pane.markup import Markdown
from ..widgets import Button, WidgetBase

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".tiff")


def _is_equal(value, other_value):
    if value is other_value:
        return True
    elif isinstance(value, pd.DataFrame):
        try:
            pd.testing.assert_frame_equal(value, other_value)
            return True
        except Exception:
            return False
    elif isinstance(value, pd.Series):
        try:
            pd.testing.assert_series_equal(value, other_value)
            return True
        except Exception:
            return False
    else:
        return value == other_value

class ExampleMixin(param.Parameterized):
    targets = param.Parameter(
        allow_refs=False,
        doc="""An Optional object or list of objects. The individual object can
        be a class with a `.value` or `.object` attribute - for example a widget or pane.
        Can also be a callable taking a single argument. Will be updated or called
        when the `value` is updated or triggered. Default is None.""",
    )
    # Todo: Figure out how to make classselector of class_=ListPanel

    layout: ListPanel | None = param.Parameter(
        default=None,
        allow_None=True,
        doc="""An optional list-like layout to hold the values in""",
    )
    button_kwargs: dict = param.Dict(
        {},
        allow_None=False,
        doc="""An optional dictionary of `Button` keyword arguments like `button_type` or `height`.""",
    )

class Example(ExampleMixin, PyComponent):
    value: Any = param.Parameter(
        constant=True,
        doc="""The example value. Either a single value or an iterable of values to assign to a single or an iterable of `targets` when updated or triggered.""",
        allow_None=False,
    )
    thumbnail: str = param.String(
        constant=True,
        doc="""A thumbnail image. If specified as a local file will be embedded as a *data url*.""",
        allow_None=False,
    )


    click = param.Event()

    def __init__(
        self,
        value: Any,
        name: str = "",
        thumbnail: str | Path = "",
        *,
        targets=None,
        layout: ListPanel | None = None,
        button_kwargs: dict | None = None,
        **params,
    ):
        if not name:
            name = self._get_name(value)

        if not thumbnail:
            thumbnail = self._get_thumbnail_from_value(value)
        else:
            thumbnail = self._get_thumbnail_from_thumbnail(thumbnail)

        if not button_kwargs:
            button_kwargs = {}

        super().__init__(
            name=name,
            value=value,
            thumbnail=thumbnail,
            targets=targets,
            layout=layout,
            button_kwargs=button_kwargs,
            **params,
        )

        self.param.watch(self._update_value, "click")
        self.param.watch(self._update_targets, "value")

        button_defaults = {
            "margin": (10, 5, 10, 5),
            "stylesheets": self._button_stylesheets,
            "align": ("start", "center"),
            "sizing_mode": "fixed",
            "name": self._button_name,
        }
        button_values = button_defaults | self.button_kwargs
        self._button = Button.from_param(self.param.click, **button_values)

    @param.depends("name", "layout", "thumbnail")
    def _button_name(self):
        if self.thumbnail:
            return "Select"
        if self.layout:
            return self.name
        return self.name

    @param.depends("thumbnail")
    def _button_stylesheets(self):
        if self.thumbnail:
            CSS = f"""button {{
                background-image: url("{self.thumbnail}");
                background-size: 100% 100%;
                background-position: center;
                background-repeat: no-repeat;
                color: transparent !important;
            }}"""
            return [CSS]
        return []

    @staticmethod
    def _get_name(value) -> str:
        name = "Example"

        try:
            if isinstance(value, (pd.DataFrame, pd.Series)):
                return name
            if isinstance(value, (type(None), int, float)):
                return str(value)
            if hasattr(value, "name"):
                return value.name
            if value and isinstance(value, str) and len(value) <= 10:
                return value
            if value and isinstance(value, str):
                parsed_url = urlparse(value)
                return os.path.basename(parsed_url.path)
        except Exception:
            pass

        return name

    @staticmethod
    def _get_thumbnail_from_value(value) -> str:
        if isinstance(value, (str, Path)) and Image.applies(value):
            html_string = Image(value)._transform_object(value)["object"]
            decoded_string = (
                html_string.replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&quot;", '"')
            )
            match = re.search(r'src="([^"]+)"', decoded_string)

            if match:
                return match.group(1)
        return ""

    @classmethod
    def _get_thumbnail_from_thumbnail(cls, thumbnail) -> str:
        if isinstance(thumbnail, str) and thumbnail.startswith("http"):
            return thumbnail
        return cls._get_thumbnail_from_value(thumbnail)

    def __eq__(self, other):
        try:
            return (
                _is_equal(self.value, other.value)
                and self.name == other.name
                and self.thumbnail == other.thumbnail
            )
        except Exception:
            return False

    def __hash__(self):
        return id(self)

    @param.depends("value", "layout")
    def _get_layout(self):
        if self.layout:
            if isinstance(self.targets, list):
                values = (panel(item, align="center") for item in self.value)
            else:
                values = (panel(str(self.value), align="center"),)
            return self.layout(
                self._button, *values, styles={"border-bottom": "1px solid black"},
            )

        return self._button

    def __repr__(self):
        return f"Example({self.name})"

    def _clean_name(self: Any, index: int) -> int:
        if not self.name or self.name.lower() == "example":
            with param.edit_constant(self):
                self.name = f"Example {index}"
            index += 1
        return index

    @classmethod
    def _clean_examples(cls, examples: list) -> list["Example"]:
        result = []
        index = 0
        for example in examples:
            if not isinstance(example, Example):
                example = Example(example)
            index = example._clean_name(index)
            result.append(example)
        return result

    def to_dict(self):
        return {"name": self.name, "value": self.value, "thumbnail": self.thumbnail}

    def __panel__(self):
        return self._get_layout()

    def _set_value(self, item, value):
        if hasattr(item, "value"):
            item.value = value
        elif hasattr(item, "object"):
            item.object = value
        elif isinstance(item, Callable):
            item(value)
        else:
            msg = f"Cannot update {item}"
            raise ValueError(msg)

    def _update_targets(self, event):
        if not self.targets:
            return

        if not isinstance(self.targets, list):
            self._set_value(self.targets, self.value)
        else:
            for target, value in zip(self.targets, self.value):
                self._set_value(target, value)

    def _update_value(self, event):
        self.param.trigger("value")


class Examples(ExampleMixin, NamedListLike, PyComponent, WidgetBase):
    # Todo: Figure out `value` should be Example or Example.value
    value = param.Parameter()
    name = param.String(default="📝 Examples", constant=True)

    def __init__(self,
        *examples: list,
        targets=None,
        layout: ListPanel | None = None,
        button_kwargs: dict | None = None,
        **params: Any
    ):
        if button_kwargs is None:
            button_kwargs={}
        examples = Example._clean_examples(examples)
        for example in examples:
            example.param.update(targets=targets, layout=layout, button_kwargs=button_kwargs)

        super().__init__(*examples, targets=targets, layout=layout, button_kwargs=button_kwargs, **params)

        for example in examples:
            example.param.watch(partial(self._update_self_value, example), "click")

    def _update_self_value(self, example, event):
        self.value = example.value

    def __panel__(self):
        return Column(
            Markdown(self.name, margin=(0, 5, 0, 5)),
            # Todo: FlexBox if button layout and Feed otherwise
            FlexBox(*self, margin=(-10, 0, 0, 0)),
            margin=(0,5)
        )
