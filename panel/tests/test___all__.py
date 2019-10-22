import os
import warnings

from pathlib import Path
from typing import Iterator
from importlib import import_module

from . import TOP_PATH

def scantree(path: os.PathLike) -> Iterator[os.DirEntry]:
    for entry in os.scandir(path):
        if entry.is_dir():
            if (Path(entry) / "__init__.py").is_file():
                yield from scantree(entry)
        else:
            yield entry

def collect_modules(path: os.PathLike) -> Iterator[str]:
    for entry in scantree(path):
        if not entry.name.endswith(".py"):
            continue
        if entry.name == "__main__.py":
            continue
        if entry.name == "__init__.py":
            continue
        if "tests" in entry.path:
            continue

        path = Path(entry.path).relative_to(TOP_PATH)
        yield str(path).replace(os.sep, ".")[:-3]

def missing__all__() -> Iterator[str]:
    for name in collect_modules(TOP_PATH / "panel"):
        try:
            module = import_module(name)
        except ImportError:
            warnings.warn(f"can't import {name} for testing")
        else:
            if not hasattr(module, "__all__"):
                yield name

def test___all__():
    assert list(missing__all__()) == []
