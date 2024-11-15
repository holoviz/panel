from __future__ import annotations

import inspect
import os
import warnings

import param

from packaging.version import Version

__all__ = (
    "deprecated",
    "find_stack_level",
    "PanelDeprecationWarning",
    "PanelUserWarning",
    "warn",
)


def warn(
    message: str, category: type[Warning] | None = None, stacklevel: int | None = None
) -> None:
    if stacklevel is None:
        stacklevel = find_stack_level()

    warnings.warn(message, category, stacklevel=stacklevel)


def find_stack_level() -> int:
    """
    Find the first place in the stack that is not inside Panel and Param.
    Inspired by: pandas.util._exceptions.find_stack_level
    """

    import panel as pn

    pkg_dir = os.path.dirname(pn.__file__)
    test_dir = os.path.join(pkg_dir, "tests")
    param_dir = os.path.dirname(param.__file__)

    frame = inspect.currentframe()
    stacklevel = 0
    try:
        while frame:
            fname = inspect.getfile(frame)
            if fname.startswith((pkg_dir, param_dir)) and not fname.startswith(test_dir):
                frame = frame.f_back
                stacklevel += 1
            else:
                break
    finally:
        # See: https://docs.python.org/3/library/inspect.html#inspect.Traceback
        del frame

    return stacklevel


def deprecated(
    remove_version: Version | str,
    old: str,
    new: str | None = None,
    *,
    extra: str | None = None,
    warn_version: Version | str | None = None
) -> None:
    from .. import __version__

    current_version = Version(__version__)
    base_version = Version(current_version.base_version)

    if warn_version:
        if isinstance(warn_version, str):
            warn_version = Version(warn_version)
        if base_version < warn_version:
            return

    if isinstance(remove_version, str):
        remove_version = Version(remove_version)

    if remove_version <= base_version and not (current_version.pre and current_version.pre[0] != 'rc'):
        # This error is mainly for developers to remove the deprecated.
        raise ValueError(
            f"{old!r} should have been removed in {remove_version}, current version {current_version}."
        )

    message = f"{old!r} is deprecated and will be removed in version {remove_version}."

    if new:
        message = f"{message[:-1]}, use {new!r} instead."

    if extra:
        message += " " + extra.strip()

    warn(message, PanelDeprecationWarning)


class PanelDeprecationWarning(DeprecationWarning):
    """A Panel-specific ``DeprecationWarning`` subclass.
    Used to selectively filter Panel deprecations for unconditional display.
    """


class PanelUserWarning(UserWarning):
    """A Panel-specific ``UserWarning`` subclass.
    Used to selectively filter Panel warnings for unconditional display.
    """


warnings.simplefilter("always", PanelDeprecationWarning)
warnings.simplefilter("always", PanelUserWarning)
