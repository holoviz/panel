"""
Implements memoization for functions with arbitrary arguments
"""
from __future__ import annotations

import contextvars
import datetime as dt
import functools
import hashlib
import inspect
import io
import os
import pathlib
import pickle
import sys
import threading
import time
import typing as t
import unittest.mock

from contextlib import contextmanager

import param

from param.parameterized import iscoroutinefunction

from ..config import config
from .state import state

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

if t.TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Hashable
    _P = t.ParamSpec("_P")
    _R = t.TypeVar("_R")
    _CallableT = t.TypeVar("_CallableT", bound=Callable)

    class _CachedFunc(t.Protocol[_CallableT]):
        def clear(self, func_hashes: list[str | None]=[None]) -> None:
            pass

        __call__: _CallableT

_CYCLE_PLACEHOLDER = b"panel-93KZ39Q-floatingdangeroushomechose-CYCLE"

_FFI_TYPE_NAMES = ("_cffi_backend.FFI", "builtins.CompiledFFI",)

_HASH_MAP: dict[Hashable, str] = {}

# Bounds the memo of computed hashes, which would otherwise grow with
# every distinct combination of arguments seen in the process.
_HASH_MAP_MAX_ITEMS = 4096

_HASH_MAP_LOCK = threading.Lock()

_INDETERMINATE = type('INDETERMINATE', (object,), {})()

_NATIVE_TYPES = (
    bytes, str, float, int, bool, bytearray, type(None)
)

_ARRAY_SIZE_LARGE = 100_000

_ARRAY_SAMPLE_SIZE = 100_000

_DATAFRAME_ROWS_LARGE = 100_000

_DATAFRAME_SAMPLE_SIZE = 100_000

# Whether frames and arrays above the sizes above are hashed from a
# sample of their contents, set by the approximate argument of cache.
_APPROXIMATE = contextvars.ContextVar('panel_approximate_hash', default=True)

if sys.platform == 'win32':
    _TIME_FN = time.perf_counter
else:
    _TIME_FN = time.monotonic

class _Stack:

    def __init__(self):
        self._stack = {}

    def push(self, val):
        self._stack[id(val)] = val

    def pop(self):
        self._stack.popitem()

    def __contains__(self, val):
        return id(val) in self._stack

def _get_fqn(obj):
    """Get module.type_name for a given type."""
    the_type = type(obj)
    module = the_type.__module__
    name = the_type.__qualname__
    return f"{module}.{name}"

def _int_to_bytes(i: int) -> bytes:
    num_bytes = (i.bit_length() + 8) // 8
    return i.to_bytes(num_bytes, "little", signed=True)

def _is_native(obj: t.Any) -> bool:
    return isinstance(obj, _NATIVE_TYPES)

def _container_hash(obj: t.Any) -> bytes:
    h = hashlib.new("md5")
    h.update(_generate_hash(f'__{type(obj).__name__}'))
    for item in (obj.items() if isinstance(obj, dict) else obj):
        h.update(_generate_hash(item))
    return h.digest()

def _slice_hash(x: slice) -> bytes:
    return _container_hash([x.start, x.step, x.stop])

def _partial_hash(obj: t.Any) -> bytes:
    h = hashlib.new("md5")
    h.update(_generate_hash(obj.args))
    h.update(_generate_hash(obj.func))
    h.update(_generate_hash(obj.keywords))
    return h.digest()

def _pandas_hash(obj: t.Any) -> bytes:
    import pandas as pd

    if not isinstance(obj, (pd.Series, pd.DataFrame)):
        obj = pd.Series(obj)

    if _APPROXIMATE.get() and len(obj) >= _DATAFRAME_ROWS_LARGE:
        # NOTE: Sampling makes the hash approximate, i.e. a difference
        # confined to the rows that were not sampled is not visible.
        # Sampling is positional and seeded so it is stable for a given
        # length and does not itself reorder the rows being compared.
        obj = obj.sample(n=_DATAFRAME_SAMPLE_SIZE, random_state=0)
    h = hashlib.new("md5")
    h.update(type(obj).__name__.encode())
    try:
        # The reduction over the per-row hashes must be order sensitive,
        # summing them would make any permutation of the rows hash alike.
        h.update(pd.util.hash_pandas_object(obj).to_numpy().tobytes())
        if isinstance(obj, pd.DataFrame):
            h.update(pd.util.hash_pandas_object(obj.columns).to_numpy().tobytes())
            h.update(''.join(f'{c}:{d}' for c, d in obj.dtypes.items()).encode())
        else:
            h.update(f'{obj.name}:{obj.dtype}'.encode())
    except TypeError:
        # Use pickle if pandas cannot hash the object for example if
        # it contains unhashable objects.
        return b"%s" % pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
    return h.digest()

def _polars_combine_hash_expr(columns):
    """
    Inspired by pd.core.util.hashing.combine_hash_arrays,
    rewritten to a Polars expression.
    """
    import polars as pl

    mult = pl.lit(1000003, dtype=pl.UInt64)
    initial_value = pl.lit(0x345678, dtype=pl.UInt64)
    increment = pl.lit(82520, dtype=pl.UInt64)
    final_addition = pl.lit(97531, dtype=pl.UInt64)

    out = initial_value
    num_items = len(columns)
    for i, col_name in enumerate(columns):
        col = pl.col(col_name).hash(seed=0)
        inverse_i = pl.lit(num_items - i, dtype=pl.UInt64)
        out = (out ^ col) * mult
        mult = mult + (increment + inverse_i + inverse_i)

    return out + final_addition

def _polars_hash(obj):
    import polars as pl

    hash_type = type(obj).__name__.encode()

    if isinstance(obj, pl.Series):
        obj = obj.to_frame()

    schema = obj.collect_schema()
    columns = schema.names()
    hash_columns = _container_hash([
        f'{name}:{dtype}' for name, dtype in zip(columns, schema.dtypes())
    ])

    # LazyFrame does not support len and sample
    # NOTE: Sampling makes the hash approximate, see _pandas_hash
    if _APPROXIMATE.get():
        if hash_type != b"LazyFrame" and len(obj) >= _DATAFRAME_ROWS_LARGE:
            obj = obj.sample(n=_DATAFRAME_SAMPLE_SIZE, seed=0)
        elif hash_type == b"LazyFrame":
            count = obj.select(pl.col(columns[0]).count()).collect().item()
            if count >= _DATAFRAME_ROWS_LARGE:
                obj = obj.select(pl.all().sample(n=_DATAFRAME_SAMPLE_SIZE, seed=0))

    hash_expr = _polars_combine_hash_expr(columns)
    # The reduction over the per-row hashes must be order sensitive,
    # summing them would make any permutation of the rows hash alike.
    hash_frame = obj.select(hash_expr.alias('__panel_row_hash'))
    if hash_type == b"LazyFrame":
        hash_frame = hash_frame.collect()
    hash_data = hash_frame.to_series().to_numpy().tobytes()

    return hash_type + hash_data + hash_columns

def _numpy_hash(obj):
    h = hashlib.new("md5")
    h.update(_generate_hash(obj.shape))
    h.update(str(obj.dtype).encode())
    if _APPROXIMATE.get() and obj.size >= _ARRAY_SIZE_LARGE:
        # NOTE: Sampling makes the hash approximate, i.e. a difference
        # confined to the elements that were not sampled is not visible.
        import numpy as np
        state = np.random.RandomState(0)
        obj = state.choice(obj.flat, size=_ARRAY_SAMPLE_SIZE)
    h.update(obj.tobytes())
    return h.digest()

def _io_hash(obj):
    h = hashlib.new("md5")
    h.update(_generate_hash(obj.tell()))
    h.update(_generate_hash(obj.getvalue()))
    return h.digest()

_hash_funcs: dict[str | type[t.Any] | tuple[type, ...] | Callable[[t.Any], bool], bytes | Callable[[t.Any], bytes]] = {
    # Types
    # NOTE: The scalar hashes are prefixed with their type since the
    # values themselves do not distinguish them, e.g. 0, 0.0, False and
    # b'\x00' would otherwise all hash alike and share a cached result.
    int          : lambda obj: b'int:' + _int_to_bytes(obj),
    str          : lambda obj: b'str:' + obj.encode(),
    float        : lambda obj: b'float:' + _int_to_bytes(hash(obj)),
    bool         : lambda obj: b'bool:1' if obj is True else b'bool:0',
    type(None)   : lambda obj: b'none',
    slice: _slice_hash,
    (bytes, bytearray) : lambda obj: b'bytes:' + bytes(obj),
    (list, tuple, dict): _container_hash,
    pathlib.Path       : lambda obj: str(obj).encode(),
    functools.partial  : _partial_hash,
    unittest.mock.Mock : lambda obj: _int_to_bytes(id(obj)),
    (io.StringIO, io.BytesIO): _io_hash,
    dt.date      : lambda obj: f'{type(obj).__name__}{obj}'.encode(),
    # Fully qualified type strings
    'numpy.ndarray'              : _numpy_hash,
    # Pandas >=3 imports
    'pandas.DataFrame'           : _pandas_hash,
    'pandas.Series'              : _pandas_hash,
    'pandas.Index'               : _pandas_hash,
    'pandas.RangeIndex'          : _slice_hash,
    # Pandas <3 imports
    'pandas.core.series.Series'  : _pandas_hash,
    'pandas.core.frame.DataFrame': _pandas_hash,
    'pandas.core.indexes.base.Index': _pandas_hash,
    'pandas.core.indexes.numeric.Int64Index': _pandas_hash,
    'pandas.core.indexes.range.RangeIndex': _slice_hash,
    'builtins.mappingproxy'      : lambda obj: _container_hash(dict(obj)),
    'builtins.dict_items'        : lambda obj: _container_hash(dict(obj)),
    'builtins.getset_descriptor' : lambda obj: obj.__qualname__.encode(),
    "numpy.ufunc"                : lambda obj: obj.__name__.encode(),
    "polars.series.series.Series": _polars_hash,
    "polars.dataframe.frame.DataFrame": _polars_hash,
    "polars.lazyframe.frame.LazyFrame": _polars_hash,
    # Functions
    inspect.isbuiltin          : lambda obj: obj.__name__.encode(),
    inspect.ismodule           : lambda obj: obj.__name__,
    lambda x: hasattr(x, "tobytes") and x.shape == (): lambda x: x.tobytes(),  # Single numpy dtype like: np.int32
}

for name in _FFI_TYPE_NAMES:
    _hash_funcs[name] = b'0'

def _find_hash_func(obj):
    fqn_type = _get_fqn(obj)
    if fqn_type in _hash_funcs:
        return _hash_funcs[fqn_type]
    obj_type = type(obj)
    if obj_type in _hash_funcs:
        # Exact type matches avoid the scan below and ensure a subclass
        # does not pick up the hash function of its base, e.g. bool
        # being hashed as an int
        return _hash_funcs[obj_type]
    for otype, hash_func in _hash_funcs.items():
        if isinstance(otype, str):
            if otype == fqn_type:
                return hash_func
        elif inspect.isfunction(otype):
            if otype(obj):
                return hash_func
        elif isinstance(obj, otype):
            return hash_func

def _generate_hash_inner(obj):
    hash_func = _find_hash_func(obj)
    if hash_func is not None:
        try:
            output = hash_func(obj)
        except BaseException as e:
            raise ValueError(
                f'User hash function {hash_func!r} failed for input '
                f'{obj!r} with following error: {type(e).__name__}("{e}").'
            ) from e
        return output
    if hasattr(obj, '__reduce__') and inspect.isclass(obj):
        h = hashlib.new("md5")
        try:
            reduce_data = obj.__reduce__()
        except BaseException:
            raise ValueError(f'Could not hash object of type {type(obj).__name__}') from None
        for item in reduce_data:
            h.update(_generate_hash(item))
        return h.digest()
    return _int_to_bytes(id(obj))

def _generate_hash(obj):
    # Break recursive cycles.
    hash_stack = state._current_stack
    if obj in hash_stack:
        return _CYCLE_PLACEHOLDER
    hash_stack.push(obj)
    try:
        hash_value = _generate_hash_inner(obj)
    finally:
        hash_stack.pop()
    return hash_value

def _key(obj):
    """
    Returns a hashable key uniquely describing an object, or
    _INDETERMINATE if no such key can cheaply be derived.

    The key is used to memoize computed hashes in _HASH_MAP, so it may
    only be derived from values that are cheap to key, immutable and
    compare (and hash) unambiguously. In particular it must include the
    type, since 0, 0.0 and False are equal and hash alike, and it must
    not be derived from the identity of a mutable object, since the
    address may be recycled and the contents may change in place.
    """
    if obj is None:
        return None
    elif isinstance(obj, bytearray):
        return ('bytearray', bytes(obj))
    elif _is_native(obj):
        return (type(obj).__name__, obj)
    elif isinstance(obj, (list, tuple)):
        keys = tuple(_key(item) for item in obj)
        if any(key is _INDETERMINATE for key in keys):
            return _INDETERMINATE
        # Tagged by type to match _container_hash, so that e.g. a
        # namedtuple does not key the same as a plain tuple
        return (f'__{type(obj).__name__}', keys)
    elif isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            kkey, vkey = _key(k), _key(v)
            if kkey is _INDETERMINATE or vkey is _INDETERMINATE:
                return _INDETERMINATE
            items.append((kkey, vkey))
        return (f'__{type(obj).__name__}', tuple(items))
    return _INDETERMINATE

def _memoize_hash(key, hash_value):
    """
    Stores a computed hash in the bounded _HASH_MAP.
    """
    with _HASH_MAP_LOCK:
        if key in _HASH_MAP:
            return
        excess = (len(_HASH_MAP) + 1) - _HASH_MAP_MAX_ITEMS
        if excess > 0:
            # dicts preserve insertion order, so this evicts FIFO
            for stale in list(_HASH_MAP)[:excess]:
                del _HASH_MAP[stale]
        _HASH_MAP[key] = hash_value

def _closure_key(func):
    """
    Returns a hash of the values a function closes over at the time it
    is decorated.

    Functions are bucketed by the file and name they were defined with,
    so that a function recreated for each session shares a cache. Two
    functions generated by the same factory share both, therefore the
    values they close over have to be part of the key, otherwise e.g.
    times2 and times3 returned by a multiplier factory would collide.

    This is computed once, when the function is decorated, so that
    rebinding or mutating the captured values later does not move the
    function to a different cache.
    """
    cells = getattr(func, '__closure__', None) or ()
    if not cells:
        return b''
    h = hashlib.new("md5")
    for cell in cells:
        try:
            contents = cell.cell_contents
        except ValueError:
            # The cell is empty, e.g. a function referring to itself
            h.update(b'__empty_cell')
            continue
        try:
            h.update(_generate_hash(contents))
        except ValueError:
            h.update(_int_to_bytes(id(contents)))
    return h.digest()

def _cleanup_cache(cache, policy, max_items, time):
    """
    Deletes items in the cache if the exceed the number of items or
    their TTL (time-to-live) has expired.
    """
    while len(cache) >= max_items:
        if policy.lower() == 'fifo':
            key = list(cache.keys())[0]
        elif policy.lower() == 'lru':
            key = sorted(((k, time-t) for k, (_, _, _, t) in cache.items()),
                         key=lambda o: o[1])[-1][0]
        elif policy.lower() == 'lfu':
            key = sorted(cache.items(), key=lambda o: o[1][2])[0][0]
        del cache[key]

def _cleanup_ttl(cache, ttl, time):
    """
    Deletes items in the cache if their TTL (time-to-live) has expired.
    """
    for key, (_, ts, _, _) in list(cache.items()):
        if (time-ts) > ttl:
            del cache[key]

@contextmanager
def _hash_context(hash_funcs, approximate=True):
    backup = dict(_hash_funcs)
    _hash_funcs.update(hash_funcs)
    token = _APPROXIMATE.set(approximate)
    try:
        yield
    finally:
        _APPROXIMATE.reset(token)
        _hash_funcs.clear()
        _hash_funcs.update(backup)

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def compute_hash(func, hash_funcs, args, kwargs, approximate=True):
    """
    Computes a hash given a function and its arguments.

    Parameters
    ----------
    func: callable
        The function to cache.
    hash_funcs: dict
        A dictionary of custom hash functions indexed by type
    args: tuple
        Arguments to hash
    kwargs: dict
        Keyword arguments to hash
    approximate: bool
        Whether DataFrames, Series and arrays above 100k rows (or
        elements) may be hashed from a sample of their contents.
    """
    # Memoizing is only sound if the key describes the arguments
    # unambiguously and the hash functions applied to them are the
    # default ones, since custom hash functions may compute a different
    # hash for the very same arguments.
    key = _INDETERMINATE
    if not hash_funcs:
        args_key, kwargs_key = _key(args), _key(kwargs)
        if args_key is not _INDETERMINATE and kwargs_key is not _INDETERMINATE:
            key = (func, args_key, kwargs_key, approximate)
            try:
                if key in _HASH_MAP:
                    return _HASH_MAP[key]
            except TypeError:
                # The callable itself is not hashable
                key = _INDETERMINATE
    hasher = hashlib.new("md5")
    with _hash_context(hash_funcs, approximate):
        if args:
            hasher.update(_generate_hash(args))
        if kwargs:
            hasher.update(_generate_hash(kwargs))
    hash_value = hasher.hexdigest()
    if key is not _INDETERMINATE:
        _memoize_hash(key, hash_value)
    return hash_value

@t.overload
def cache(
    func: t.Literal[None] = ...,
    hash_funcs: dict[type[t.Any], Callable[[t.Any], bytes]] | None = ...,
    max_items: int | None = ...,
    policy: t.Literal['FIFO', 'LRU', 'LFU'] = ...,
    ttl: float | None = ...,
    to_disk: bool = ...,
    cache_path: str | os.PathLike | None = ...,
    per_session: bool = ...,
    approximate: bool = ...,
) -> Callable[[Callable[_P, _R]], _CachedFunc[Callable[_P, _R]]]:
    ...

@t.overload
def cache(
    func: Callable[_P, _R],
    hash_funcs: dict[type[t.Any], Callable[[t.Any], bytes]] | None = ...,
    max_items: int | None = ...,
    policy: t.Literal['FIFO', 'LRU', 'LFU'] = ...,
    ttl: float | None = ...,
    to_disk: bool = ...,
    cache_path: str | os.PathLike | None = ...,
    per_session: bool = ...,
    approximate: bool = ...,
) -> _CachedFunc[Callable[_P, _R]]:
    ...

def cache(
    func: Callable[_P, _R] | None = None,
    hash_funcs: dict[type[t.Any], Callable[[t.Any], bytes]] | None = None,
    max_items: int | None = None,
    policy: t.Literal['FIFO', 'LRU', 'LFU'] = 'LRU',
    ttl: float | None = None,
    to_disk: bool = False,
    cache_path: str | os.PathLike | None = None,
    per_session: bool = False,
    approximate: bool = True,
) -> _CachedFunc[Callable[_P, _R]] | Callable[[Callable[_P, _R]], _CachedFunc[Callable[_P, _R]]]:
    """
    Memoizes functions for a user session. Can be used as function annotation or just directly.

    For global caching across user sessions use `pn.state.as_cached`.

    Cached results are stored and handed out as they are, i.e. every hit
    returns the very same object. Mutating a returned value therefore
    changes what later hits see, so treat results as read-only or copy
    them before modifying.

    Arguments are hashed by their contents on every call, so a cache hit
    on a large DataFrame or array still costs a pass over the data. By
    default inputs above 100k rows (or elements) are hashed from a fixed
    pseudo-random sample of 100k rows, which makes the hash approximate:
    a difference confined to the rows that were not sampled is invisible
    and returns the previously cached result. Set ``approximate=False``
    to hash all the data, or pass a ``hash_funcs`` entry for the type to
    hash such inputs some other way, e.g. by a version or timestamp you
    maintain yourself.

    Arguments that are mutated in place between calls are also invisible
    once the result has been cached, since the mutated object may hash
    the same as the object that was cached.

    Parameters
    ----------
    func: callable
        The function to cache.
    hash_funcs: dict or None
        A dictionary mapping from a type to a function which returns
        a hash for an object of that type. If provided this will
        override the default hashing function provided by Panel.
    max_items: int or None
        The maximum items to keep in the cache. Default is None, which does
        not limit number of items stored in the cache.
    policy: str
        A caching policy when max_items is set, must be one of:
          - FIFO: First in - First out
          - LRU: Least recently used
          - LFU: Least frequently used
    ttl: float or None
        The number of seconds to keep an item in the cache, or None if
        the cache should not expire. The default is None.
    to_disk: bool
        Whether to cache to disk using diskcache.
    cache_path: str
        Directory to cache to on disk (if not provided default will be
        inherited from config.cache_path).
    per_session: bool
        Whether to cache data only for the current session.
    approximate: bool
        Whether DataFrames, Series and arrays above 100k rows (or
        elements) may be hashed from a sample of their contents, which
        is cheaper but can return the result cached for a different
        input. Set to False to hash all the data.
    """
    if policy.lower() not in ('fifo', 'lru', 'lfu'):
        raise ValueError(
            f"Cache policy must be one of 'FIFO', 'LRU' or 'LFU', not {policy}."
        )

    if cache_path is None:
        cache_path = config.cache_path

    hash_funcs = hash_funcs or {}
    if func is None:
        def decorator(func: Callable[_P, _R]) -> _CachedFunc[Callable[_P, _R]]:
            return cache(
                func=func,
                hash_funcs=hash_funcs,
                max_items=max_items,
                policy=policy,
                ttl=ttl,
                to_disk=to_disk,
                cache_path=cache_path,
                per_session=per_session,
                approximate=approximate,
            )
        return decorator
    func_hashes = [None] # noqa

    # Computed once so that mutating or rebinding a captured value does
    # not move the function to a different cache.
    with _hash_context(hash_funcs, approximate):
        closure_key = _closure_key(func)

    lock = threading.RLock()

    def hash_func(*args, **kwargs):
        # Handle param.depends method by adding parameters to arguments
        func_name = func.__name__
        is_method = (
            args and isinstance(args[0], object) and
            getattr(type(args[0]), func_name, None) is wrapped_func
        )
        hash_args, hash_kwargs = args, kwargs
        if (is_method and isinstance(args[0], param.Parameterized)):
            dinfo = getattr(wrapped_func, '_dinfo', {})
            hash_args = tuple(getattr(args[0], d) for d in dinfo.get('dependencies', ())) + args[1:]
            hash_kwargs = dict(dinfo.get('kw', {}), **kwargs)
        hash_value = compute_hash(func, hash_funcs, hash_args, hash_kwargs, approximate)

        time = _TIME_FN()

        # If the function is defined inside a bokeh/panel application
        # it is recreated for each session, therefore we cache by
        # file, class and qualified function name. Since that is shared
        # by all functions a factory generates we also key on the values
        # the function closes over.
        module = sys.modules[func.__module__]
        fname = '__main__' if func.__module__ == '__main__' else module.__file__
        qualname = getattr(func, '__qualname__', func_name)
        if is_method:
            func_hash = (fname, type(args[0]).__name__, qualname)
        else:
            func_hash = (fname, qualname)
        func_hash += (closure_key,)
        if per_session:
            func_hash += (id(state.curdoc),)
        func_hash = hashlib.sha256(_generate_hash(func_hash)).hexdigest()

        func_hashes[0] = func_hash
        func_cache = state._memoize_cache.get(func_hash)

        if func_cache is None:
            if to_disk:
                from diskcache import Index
                cache = Index(os.path.join(cache_path, func_hash))
            else:
                cache = {}
            state._memoize_cache[func_hash] = func_cache = cache

        if ttl is not None:
            _cleanup_ttl(func_cache, ttl, time)

        if hash_value in func_cache:
            return func_cache, hash_value, time

        if max_items is not None:
            _cleanup_cache(func_cache, policy, max_items, time)

        return func_cache, hash_value, time

    if iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapped_func(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            func_cache, hash_value, time = hash_func(*args, **kwargs)
            if hash_value in func_cache:
                with lock:
                    ret, ts, count, _ = func_cache[hash_value]
                    func_cache[hash_value] = (ret, ts, count+1, time)
            else:
                ret = await t.cast("Awaitable[t.Any]", func(*args, **kwargs))
                with lock:
                    func_cache[hash_value] = (ret, time, 0, time)
            return ret
    else:
        @functools.wraps(func)
        def wrapped_func(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            func_cache, hash_value, time = hash_func(*args, **kwargs)
            if hash_value in func_cache:
                with lock:
                    ret, ts, count, _ = func_cache[hash_value]
                    func_cache[hash_value] = (ret, ts, count+1, time)
            else:
                ret = func(*args, **kwargs)
                with lock:
                    func_cache[hash_value] = (ret, time, 0, time)
            return ret

    def clear(func_hashes=func_hashes):
        # clear called before anything is cached.
        if func_hashes[0] is None:
            return
        cache = state._memoize_cache.get(func_hashes[0])
        if cache:
            cache.clear()

    wrapped_func.clear = clear  # type: ignore[attr-defined]

    if per_session and state.curdoc and state.curdoc.session_context:
        def server_clear(session_context, clear=clear):
            clear()
        state.curdoc.on_session_destroyed(server_clear)

    try:
        wrapped_func.__dict__.update(func.__dict__)
    except AttributeError:
        pass

    return wrapped_func  # type: ignore

def is_equal(value, other)->bool:
    """Returns True if value and other are equal

    Supports complex values like DataFrames
    """
    return value is other or _generate_hash(value)==_generate_hash(other)
