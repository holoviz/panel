"""
The io module contains utilities for loading JS components, embedding
model state, and rendering panel objects.
"""
import sys

from .cache import cache  # noqa
from .callbacks import PeriodicCallback  # noqa
from .document import init_doc, unlocked, with_lock  # noqa
from .embed import embed_state  # noqa
from .logging import panel_logger  # noqa
from .model import add_to_doc, diff, remove_root  # noqa
from .notebook import (  # noqa
    _jupyter_server_extension_paths, block_comm, ipywidget, load_notebook,
    push, push_notebook,
)
from .profile import profile  # noqa
from .resources import Resources  # noqa
from .state import state  # noqa

if state._is_pyodide:
    from .pyodide import serve
else:
    from .server import serve  # noqa
    if 'django' in sys.modules:
        try:
            from . import django  # noqa
        except ImportError:
            pass

__all__ = (
    "PeriodicCallback",
    "Resources",
    "ipywidget",
    "panel_logger"
    "profile",
    "push",
    "push_notebook",
    "serve",
    "state",
    "unlocked",
    "with_lock"
)
