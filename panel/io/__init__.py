"""
The io module contains utilities for loading JS components, embedding
model state, and rendering panel objects.
"""
from typing import TYPE_CHECKING as _TC


def _serve_init():
    import sys
    if '_pyodide' in sys.modules:
        from .pyodide import serve
    else:
        from .server import serve
        if 'django' in sys.modules:
            try:
                from . import django  # noqa
            except ImportError:
                pass
    return serve


from .state import state  # Matching filename and module name

if _TC:
    from .cache import cache
    from .callbacks import PeriodicCallback
    from .document import (  # noqa
        hold, immediate_dispatch, init_doc, unlocked, with_lock,
    )
    from .embed import embed_state  # noqa
    from .logging import panel_logger
    from .model import add_to_doc, diff, remove_root  # noqa
    from .notebook import (  # noqa
        _jupyter_server_extension_paths, block_comm, ipywidget, load_notebook,
        push, push_notebook,
    )
    from .profile import profile
    from .resources import Resources
    from .server import serve

_attrs = {
    "cache": "panel.io.cache:cache",
    "PeriodicCallback": "panel.io.callbacks:PeriodicCallback",
    "hold": "panel.io.document:hold",
    "immediate_dispatch": "panel.io.document:immediate_dispatch",
    "init_doc": "panel.io.document:init_doc",
    "unlocked": "panel.io.document:unlocked",
    "with_lock": "panel.io.document:with_lock",
    "embed_state": "panel.io.embed:embed_state",
    "panel_logger": "panel.io.logging:panel_logger",
    "add_to_doc": "panel.io.model:add_to_doc",
    "diff": "panel.io.model:diff",
    "remove_root": "panel.io.model:remove_root",
    "block_comm": "panel.io.notebook:block_comm",
    "ipywidget": "panel.io.notebook:ipywidget",
    "load_notebook": "panel.io.notebook:load_notebook",
    "push": "panel.io.notebook:push",
    "push_notebook": "panel.io.notebook:push_notebook",
    "profile": "panel.io.profile:profile",
    "Resources": "panel.io.resources:Resources",
    "serve": None,  # See _serve_init()
}


def __getattr__(name: str) -> object:
    if name == "serve":
        return _serve_init()
    elif name == "no_lazy":
        for attr in _attrs:
            mod = __getattr__(attr)
            if hasattr(mod, "_attrs"):
                getattr(mod._attrs, "no_lazy", None)
        return name
    elif name in _attrs:
        import importlib
        mod_name, _, attr_name = _attrs[name].partition(':')
        mod = importlib.import_module(mod_name)
        return getattr(mod, attr_name) if attr_name else mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = (
    "cache",
    "PeriodicCallback",
    "Resources",
    "hold",
    "immediate_dispatch",
    "ipywidget",
    "panel_logger",
    "profile",
    "push",
    "push_notebook",
    "serve",
    "state",
    "unlocked",
    "with_lock"
)

__dir__ = lambda: list(__all__)
