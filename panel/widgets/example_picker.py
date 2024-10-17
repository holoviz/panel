import os
import re

from functools import partial
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import pandas as pd
import param

from ..custom import PyComponent
from ..layout import Column, FlexBox, Row
from ..layout.base import NamedListLike
from ..pane.image import Image
from ..pane.markup import Markdown
from ..widgets import Button, WidgetBase

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.tiff')

class Example(PyComponent):
    value: Any = param.Parameter(constant=True)
    thumbnail: str = param.String(constant=True)

    click = param.Event()

    def __init__(self, value: Any, name: str="", thumbnail: str | Path=""):
        if not name:
            name = self._get_name(value)

        if not thumbnail:
            thumbnail = self._get_thumbnail(value)

        super().__init__(name=name, value=value, thumbnail=thumbnail)

    @staticmethod
    def _get_name(value)->str:
        name = "Example"

        try:
            if isinstance(value, (pd.DataFrame, pd.Series)):
                return name
            if isinstance(value, (type(None), int, float)):
                return str(value)
            if hasattr(value, 'name'):
                return value.name
            if value and isinstance(value, str) and len(value)<=10:
                return value
            if value and isinstance(value, str):
                parsed_url = urlparse(value)
                return os.path.basename(parsed_url.path)
        except Exception:
            pass

        return name

    @staticmethod
    def _get_thumbnail(value)->str:
        if isinstance(value, str) and Image.applies(value):
            html_string=Image(value)._transform_object(value)["object"]
            decoded_string = html_string.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
            match = re.search(r'src="([^"]+)"', decoded_string)

            if match:
                return match.group(1)
        return ""

    def __eq__(self, other):
        try:
            return (self.value==other.value and self.name==other.name and self.thumbnail==other.thumbnail)
        except Exception:
            return False

    def as_button(self)->Button:
        return Button.from_param(self.param.click, name=self.name, margin=(10, 5, 10, 5))

    def as_row(self)->Row:
        select_button = Button.from_param(self.param.click, name="Select")
        return Row(select_button, str(self.value))

    def __repr__(self):
        return f"Example({self.name})"

    def _clean_name(self: Any, index: int)->int:
        if not self.name or self.name.lower()=="example":
            with param.edit_constant(self):
                self.name = f"Example {index}"
            index+=1
        return index

    @classmethod
    def _clean_examples(cls, examples: list)->list['Example']:
        result = []
        index = 0
        for example in examples:
            if not isinstance(example, Example):
                example = Example(example)
            index = example._clean_name(index)
            result.append(example)
        return result

    def __panel__(self):
        return self.as_button()

class ExamplePicker(NamedListLike, PyComponent, WidgetBase):
    value = param.Parameter()
    name = param.String(default="📝 Examples", constant=True)

    def __init__(self, *examples: list, targets: Any | list = None, **params: Any):
        examples = Example._clean_examples(examples)

        super().__init__(*examples, **params)

        for example in examples:
            example.param.watch(partial(self._update_self_value, example), 'click')

        if targets:
            if isinstance(targets, list):
                self.bind(*targets)
            else:
                self.bind(targets)

    def _update_self_value(self, example, event):
        self.value = example.value

    def _update_item(self, item, index, length, event):
        if length==1:
            value = self.value
        else:
            value = self.value[index]

        if hasattr(item, 'value'):
            item.value = value
        elif hasattr(item, 'object'):
            item.object = value
        elif isinstance(item, Callable):
            item(value)
        else:
            msg = f"Cannot update {item}"
            raise ValueError(msg)

    def bind(self, *targets: list[WidgetBase]):
        length = len(targets)
        for index, item in enumerate(targets):
            self.param.watch(partial(self._update_item, item, index, length), 'value')

    def __panel__(self):
        return Column(Markdown(self.name, margin=(0,5,0,5)), FlexBox(*self, margin=(-10, 0, 0,0)))
