from .react import (
    LinkWatcher as _LinkWatcher,
    Syncable as _Syncable,
    Reactive as _Reactive,
    SyncableData as _SyncableData,
    ReactiveData as _ReactiveData,
    ReactiveHTMLMetaclass as _ReactiveHTMLMetaclass,
    ReactiveHTML as _ReactiveHTML,
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
