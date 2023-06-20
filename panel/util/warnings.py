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
    while frame:
        fname = inspect.getfile(frame)
        if fname.startswith((pkg_dir, param_dir)) and not fname.startswith(test_dir):
            frame = frame.f_back
            stacklevel += 1
        else:
            break

    return stacklevel


def deprecated(
    remove_version: Version | str,
    old: str,
    new: str | None = None,
    extra: str | None = None,
) -> None:

    import panel as pn

    current_version = Version(Version(pn.__version__).base_version)

    if isinstance(remove_version, str):
        remove_version = Version(remove_version)

    if remove_version <= current_version:
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
