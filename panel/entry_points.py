""" This module defines a function for iterating over entry points
as well as for loading them.
It is copied almost entirely from the entrypoint handling in the excellent
Hypothesis package https://github.com/HypothesisWorks/hypothesis.
"""

import importlib.metadata

from collections.abc import Iterator


def entry_points_for(group: str) -> Iterator[importlib.metadata.EntryPoint]:
    yield from importlib.metadata.entry_points(group=group)


def load_entry_points(group: str) -> None:
    for entry in entry_points_for(group):  # pragma: no cover
        hook = entry.load()
        if callable(hook):
            hook()
