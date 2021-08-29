"""
The io module contains utilities for loading JS components, embedding
model state, and rendering panel objects.
"""
import sys

from .callbacks import PeriodicCallback # noqa
from .embed import embed_state # noqa
from .logging import panel_logger # noqa
from .model import add_to_doc, remove_root, diff # noqa
from .profile import profile # noqa
from .resources import Resources # noqa
from .server import get_server, init_doc, serve, unlocked, with_lock # noqa
from .state import state # noqa
from .notebook import ( # noqa
    block_comm, ipywidget, _jupyter_server_extension_paths,
    load_notebook, push, push_notebook
)

if 'django' in sys.modules:
    from . import django # noqa
