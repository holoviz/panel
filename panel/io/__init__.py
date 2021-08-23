"""
The io module contains utilities for loading JS components, embedding
model state, and rendering panel objects.
"""

import logging
import sys

from ..config import config

from .callbacks import PeriodicCallback # noqa
from .embed import embed_state # noqa
from .state import state # noqa
from .model import add_to_doc, remove_root, diff # noqa
from .profile import profile # noqa
from .resources import Resources # noqa
from .server import get_server, init_doc, serve, unlocked, with_lock # noqa
from .notebook import ( # noqa
    block_comm, ipywidget, _jupyter_server_extension_paths,
    load_notebook, push, push_notebook
)

if 'django' in sys.modules:
    from . import django # noqa

panel_logger = logging.getLogger('panel')
panel_logger.propagate = False

def _setup_logging():
    panel_logger.setLevel(logging.DEBUG)
    panel_logger.handlers.clear()
    panel_log_handler = logging.StreamHandler()
    panel_log_handler.setStream(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(name)s - %(message)s')
    panel_log_handler.setFormatter(formatter)
    panel_logger.addHandler(panel_log_handler)
    if config.log_level is not None:
        panel_log_handler.setLevel(config.log_level)

_setup_logging()
