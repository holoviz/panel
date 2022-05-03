"""
The io module contains utilities for loading JS components, embedding
model state, and rendering panel objects.
"""
import sys

from .callbacks import PeriodicCallback # noqa
from .document import init_doc, unlocked, with_lock # noqa
from .embed import embed_state # noqa
from .logging import panel_logger # noqa
from .model import add_to_doc, remove_root, diff # noqa
from .profile import profile # noqa
from .resources import Resources # noqa
from .state import state # noqa
from .notebook import ( # noqa
    block_comm, ipywidget, _jupyter_server_extension_paths,
    load_notebook, push, push_notebook
)

if state._is_pyodide:
    from .pyodide import serve
else:
    from .server import serve # noqa
    if 'django' in sys.modules:
        try:
            from . import django # noqa
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
