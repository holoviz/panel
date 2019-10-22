import sys

from types import FunctionType
from typing import TypeVar, Type, Callable

__all__ = ["public"]

T = TypeVar("T", Callable, Type[type], type)

def public(obj: T) -> T:
    """
    Append ``obj``'s name to global ``__all__`` variable (call site).

    By using this decorator on functions or classes you achieve the same goal
    as by filling ``__all__`` variables manually, you just don't have to repeat
    yourself (object's name). You also know if object is public at definition
    site, not at some random location (where ``__all__`` was set).

    Note that in multiple decorator setup (in almost all cases) ``@public``
    decorator must be applied before any other decorators, because it relies
    on the pointer to object's global namespace. If you apply other decorators
    first, ``@public`` may end up modifying the wrong namespace.

    """
    if isinstance(obj, FunctionType):
        scope = obj.__globals__
    elif isinstance(obj, (type(type), type)):
        scope = sys.modules[obj.__module__].__dict__
    else:
        raise TypeError("expected a function or a class, got %s" % obj)

    name = obj.__name__

    if "__all__" not in scope:
        scope["__all__"] = [name]
    else:
        scope["__all__"].append(name)

    return obj
