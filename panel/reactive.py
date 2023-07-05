from .react import (
    LinkWatcher as _LinkWatcher, Reactive as _Reactive,
    ReactiveData as _ReactiveData, ReactiveHTML as _ReactiveHTML,
    ReactiveHTMLMetaclass as _ReactiveHTMLMetaclass, Syncable as _Syncable,
    SyncableData as _SyncableData,
)
from .util.warnings import deprecated

_public = {
    "LinkWatcher": _LinkWatcher,
    "Reactive": _Reactive,
    "ReactiveData": _ReactiveData,
    "ReactiveHTML": _ReactiveHTML,
    "ReactiveHTMLMetaclass": _ReactiveHTMLMetaclass,
    "Syncable": _Syncable,
    "SyncableData": _SyncableData,
}


def __getattr__(name):
    if name in _public:
        deprecated("1.4", f"panel.reactive.{name}", f"panel.react.{name}")
        return _public[name]
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
