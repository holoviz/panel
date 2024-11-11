import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)

del lazy

from .widget import widget  # noqa: F401, matching filename and module name
