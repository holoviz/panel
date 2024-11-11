import lazy_loader as lazy

_lazy_getattr, __dir__, __all__ = lazy.attach_stub(__name__, __file__)


def _serve_init():
    import sys

    if "_pyodide" in sys.modules:
        from .pyodide import serve
    else:
        from .server import serve

        if "django" in sys.modules:
            try:
                from . import django  # noqa
            except ImportError:
                pass
    return serve


def __getattr__(name):
    if name == "serve":
        return _serve_init()
    return _lazy_getattr(name)


del lazy

from .state import state  # noqa: F401, Matching filename and module name
