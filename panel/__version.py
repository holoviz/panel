"""Define the package version.

Called __version.py as setuptools_scm will create a _version.py
"""

import os.path

PACKAGE = "panel"

try:
    # For performance reasons on imports, avoid importing setuptools_scm
    # if not in a .git folder
    if os.path.exists(os.path.join(os.path.dirname(__file__), "..", ".git")):
        # If setuptools_scm is installed (e.g. in a development environment with
        # an editable install), then use it to determine the version dynamically.
        from setuptools_scm import get_version

        # This will fail with LookupError if the package is not installed in
        # editable mode or if Git is not installed.
        __version__ = get_version(root="..", relative_to=__file__, version_scheme="post-release")
    else:
        raise FileNotFoundError
except (ImportError, LookupError, FileNotFoundError):
    # As a fallback, use the version that is hard-coded in the file.
    try:
        # __version__ was added in _version in setuptools-scm 7.0.0, we rely on
        # the hopefully stable version variable.
        from ._version import version as __version__
    except (ModuleNotFoundError, ImportError):
        # Either _version doesn't exist (ModuleNotFoundError) or version isn't
        # in _version (ImportError). ModuleNotFoundError is a subclass of
        # ImportError, let's be explicit anyway.

        # Try something else:
        from importlib.metadata import PackageNotFoundError, version

        try:
            __version__ = version(PACKAGE)
        except PackageNotFoundError:
            # The user is probably trying to run this without having installed
            # the package.
            __version__ = "0.0.0+unknown"

__all__ = ("__version__",)
