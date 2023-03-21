""" This module defines a function for iterating over entry points
as well as for loading them.
It is copied almost entirely from the entrypoint handling in the excellent
Hypothesis package https://github.com/HypothesisWorks/hypothesis.
"""

import importlib.metadata

from typing import Iterator


def entry_points_for(group: str) -> Iterator[importlib.metadata.EntryPoint]:
    try:
        eps = importlib.metadata.entry_points(group=group)
    except TypeError:
        # Load-time selection requires Python >= 3.10 or importlib_metadata >= 3.6,
        # so we'll retain this fallback logic for some time to come.  See also
        # https://importlib-metadata.readthedocs.io/en/latest/using.html
        eps = importlib.metadata.entry_points().get(group, [])
    yield from eps


def load_entry_points(group: str) -> None:
    for entry in entry_points_for(group):  # pragma: no cover
        hook = entry.load()
        if callable(hook):
            hook()
