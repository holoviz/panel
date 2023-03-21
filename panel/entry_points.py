""" This module defines a function for iterating over entry points
as well as for loading them.
It is copied almost entirely from the entrypoint handling in the excellent
Hypothesis package https://github.com/HypothesisWorks/hypothesis.
"""

try:
    from importlib import metadata as importlib_metadata
except ImportError:
    import importlib_metadata  # type: ignore  # mypy thinks this is a redefinition

def entry_points_for(group):
    try:
        eps = importlib_metadata.entry_points(group=group)
    except TypeError:
        # Load-time selection requires Python >= 3.10 or importlib_metadata >= 3.6,
        # so we'll retain this fallback logic for some time to come.  See also
        # https://importlib-metadata.readthedocs.io/en/latest/using.html
        eps = importlib_metadata.entry_points().get(group, [])
    yield from eps


def load_entry_points(group):
    for entry in entry_points_for(group):  # pragma: no cover
        hook = entry.load()
        if callable(hook):
            hook()
