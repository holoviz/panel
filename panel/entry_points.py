""" This module defines a function for iterating over entry points
as well as for loading them.
It is copied almost entirely from the entrypoint handling in the excellent
Hypothesis package https://github.com/HypothesisWorks/hypothesis.
"""

try:
    # We prefer to use importlib.metadata, or the backport on Python <= 3.7,
    # because it's much faster than pkg_resources (200ms import time speedup).
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

except ImportError:
    # But if we're not on Python >= 3.8 and the importlib_metadata backport
    # is not installed, we fall back to pkg_resources anyway.
    try:
        import pkg_resources
    except ImportError:
        import warnings

        warnings.warn(
            "Under Python <= 3.7, Panel requires either the importlib_metadata "
            "or setuptools package in order to load plugins via entrypoints.",
        )

        def entry_points_for(group):
            yield from ()

    else:

        def entry_points_for(group):
            yield from pkg_resources.iter_entry_points(group)


def load_entry_points(group):
    for entry in entry_points_for(group):  # pragma: no cover
        hook = entry.load()
        if callable(hook):
            hook()
