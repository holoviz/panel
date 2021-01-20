"""In this module we define the BaseModel.

The BaseModel adds ordering by the name parameter to a Class"""
import pathlib
from typing import Callable, Dict

import param
import toml


class BaseModel(param.Parameterized):
    """The BaseModel adds ordering by the name parameter to a Class"""

    uid = param.String(doc="A unique id identifying the model.")

    def __lt__(self, other):
        if hasattr(other, "name"):
            return self.name.casefold() < other.name.casefold()
        return True

    def __eq__(self, other):
        if hasattr(other, "name"):
            return self.name == other.name
        return False

    def __str__(
        self,
    ):
        return self.name

    def __repr__(
        self,
    ):
        return self.name

    @classmethod
    def create_from_toml(cls, path: pathlib.Path, clean_func: Callable = None) -> Dict:
        """Returns a list of Models from the toml file specified by the path"""
        config = toml.load(path)
        if not clean_func:
            clean_func = lambda x: x
        return {key: cls(uid=key, **clean_func(value)) for key, value in config.items()}
