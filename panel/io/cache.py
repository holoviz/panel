"""
Implements memoization for functions with arbitrary arguments
"""
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
import unittest
import unittest.mock
import weakref

from contextlib import contextmanager

import param

from .state import state

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

_CYCLE_PLACEHOLDER = b"panel-93KZ39Q-floatingdangeroushomechose-CYCLE"

_FFI_TYPE_NAMES = ("_cffi_backend.FFI", "builtins.CompiledFFI",)

_HASH_MAP = {}

_HASH_STACKS = weakref.WeakKeyDictionary()

_INDETERMINATE = type('INDETERMINATE', (object,), {})()

_NATIVE_TYPES = (
    bytes, str, float, int, bool, bytearray, type(None)
)

_NP_SIZE_LARGE = 100_000

_NP_SAMPLE_SIZE = 100_000

_PANDAS_ROWS_LARGE = 100_000

_PANDAS_SAMPLE_SIZE = 100_000

if sys.platform == 'win32':
    _TIME_FN = time.perf_counter
else:
    _TIME_FN = time.monotonic

class _Stack(object):

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
    return "%s.%s" % (module, name)

def _int_to_bytes(i):
    num_bytes = (i.bit_length() + 8) // 8
    return i.to_bytes(num_bytes, "little", signed=True)

def _is_native(obj):
    return isinstance(obj, _NATIVE_TYPES)

def _is_native_tuple(obj):
    return isinstance(obj, tuple) and all(_is_native_tuple(v) for v in obj)

def _container_hash(obj):
    h = hashlib.new("md5")
    h.update(_generate_hash(f'__{type(obj).__name__}'))
    for item in (obj.items() if isinstance(obj, dict) else obj):
        h.update(_generate_hash(item))
    return h.digest()

def _slice_hash(x):
    return _container_hash([x.start, x.step, x.stop])

def _partial_hash(obj):
    h = hashlib.new("md5")
    h.update(_generate_hash(obj.args))
    h.update(_generate_hash(obj.func))
    h.update(_generate_hash(obj.keywords))
    return h.digest()

def _pandas_hash(obj):
    import pandas as pd

    if not isinstance(obj, (pd.Series, pd.DataFrame)):
        obj = pd.Series(obj)

    if len(obj) >= _PANDAS_ROWS_LARGE:
        obj = obj.sample(n=_PANDAS_SAMPLE_SIZE, random_state=0)
    try:
        return b"%s" % pd.util.hash_pandas_object(obj).sum()
    except TypeError:
        # Use pickle if pandas cannot hash the object for example if
        # it contains unhashable objects.
        return b"%s" % pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)

def _numpy_hash(obj):
    h = hashlib.new("md5")
    h.update(_generate_hash(obj.shape))
    if obj.size >= _NP_SIZE_LARGE:
        import numpy as np
        state = np.random.RandomState(0)
        obj = state.choice(obj.flat, size=_NP_SAMPLE_SIZE)
    h.update(obj.tobytes())
    return h.digest()

def _io_hash(obj):
    h = hashlib.new("md5")
    h.update(_generate_hash(obj.tell()))
    h.update(_generate_hash(obj.getvalue()))
    return h.digest()

_hash_funcs = {
    # Types
    int          : _int_to_bytes,
    str          : lambda obj: obj.encode(),
    float        : lambda obj: _int_to_bytes(hash(obj)),
    bool         : lambda obj: b'1' if obj is True else b'0',
    type(None)   : lambda obj: b'0',
    slice: _slice_hash,
    (bytes, bytearray) : lambda obj: obj,
    (list, tuple, dict): _container_hash,
    pathlib.Path       : lambda obj: str(obj).encode(),
    functools.partial  : _partial_hash,
    unittest.mock.Mock : lambda obj: _int_to_bytes(id(obj)),
    (io.StringIO, io.BytesIO): _io_hash,
    dt.date      : lambda obj: f'{type(obj).__name__}{obj}'.encode('utf-8'),
    # Fully qualified type strings
    'numpy.ndarray'              : _numpy_hash,
    'pandas.core.series.Series'  : _pandas_hash,
    'pandas.core.frame.DataFrame': _pandas_hash,
    'pandas.core.indexes.base.Index': _pandas_hash,
    'pandas.core.indexes.numeric.Int64Index': _pandas_hash,
    'pandas.core.indexes.range.RangeIndex': _slice_hash,
    'builtins.mappingproxy'      : lambda obj: _container_hash(dict(obj)),
    'builtins.dict_items'        : lambda obj: _container_hash(dict(obj)),
    'builtins.getset_descriptor' : lambda obj: obj.__qualname__.encode(),
    "numpy.ufunc"                : lambda obj: obj.__name__.encode(),
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
            )
        return output
    if hasattr(obj, '__reduce__'):
        h = hashlib.new("md5")
        try:
            reduce_data = obj.__reduce__()
        except BaseException:
            raise ValueError(f'Could not hash object of type {type(obj).__name__}')
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
    if obj is None:
        return None
    elif _is_native(obj) or _is_native_tuple(obj):
        return obj
    elif isinstance(obj, list):
        if all(_is_native(item) for item in obj):
            return ('__list', *obj)
    elif (
        _get_fqn(obj) == "pandas.core.frame.DataFrame"
        or _get_fqn(obj) == "numpy.ndarray"
        or inspect.isbuiltin(obj)
        or inspect.isroutine(obj)
        or inspect.iscode(obj)
    ):
        return id(obj)
    return _INDETERMINATE

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
def _override_hash_funcs(hash_funcs):
    backup = dict(_hash_funcs)
    _hash_funcs.update(hash_funcs)
    try:
        yield
    finally:
        _hash_funcs.clear()
        _hash_funcs.update(backup)

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def compute_hash(func, hash_funcs, args, kwargs):
    """
    Computes a hash given a function and its arguments.

    Arguments
    ---------
    func: callable
        The function to cache.
    hash_funcs: dict
        A dictionary of custom hash functions indexed by type
    args: tuple
        Arguments to hash
    kwargs: dict
        Keyword arguments to hash
    """
    key = (func, _key(args), _key(kwargs))
    if _INDETERMINATE not in key and key in _HASH_MAP:
        return _HASH_MAP[key]
    hasher = hashlib.new("md5")
    with _override_hash_funcs(hash_funcs):
        if args:
            hasher.update(_generate_hash(args))
        if kwargs:
            hasher.update(_generate_hash(kwargs))
    hash_value = hasher.hexdigest()
    if _INDETERMINATE not in key:
        _HASH_MAP[key] = hash_value
    return hash_value


def cache(
    func=None, hash_funcs=None, max_items=None, policy='LRU',
    ttl=None, to_disk=False, cache_path='./cache', per_session=False
):
    """
    Memoizes functions for a user session. Can be used as function annotation or just directly.

    For global caching across user sessions use `pn.state.as_cached`.

    Arguments
    ---------
    func: callable
        The function to cache.
    hash_funcs: dict or None
        A dictionary mapping from a type to a function which returns
        a hash for an object of that type. If provided this will
        override the default hashing function provided by Panel.
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
    cache_dir: str
        Directory to cache to on disk.
    per_session: bool
        Whether to cache data only for the current session.
    """
    if policy.lower() not in ('fifo', 'lru', 'lfu'):
        raise ValueError(
            f"Cache policy must be one of 'FIFO', 'LRU' or 'LFU', not {policy}."
        )

    hash_funcs = hash_funcs or {}
    if func is None:
        return lambda f: cache(
            func=f,
            hash_funcs=hash_funcs,
            max_items=max_items,
            ttl=ttl,
            to_disk=to_disk,
            cache_path=cache_path
        )
    func_hash = None # noqa

    lock = threading.RLock()

    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        global func_hash
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
        hash_value = compute_hash(func, hash_funcs, hash_args, hash_kwargs)

        time = _TIME_FN()

        # If the function is defined inside a bokeh/panel application
        # it is recreated for each session, therefore we cache by
        # filen, class and function name
        module = sys.modules[func.__module__]
        fname = '__main__' if func.__module__ == '__main__' else module.__file__
        if is_method:
            func_hash = (fname, type(args[0]).__name__, func.__name__)
        else:
            func_hash = (fname, func.__name__)
        if per_session:
            func_hash += (id(state.curdoc),)
        func_hash = hashlib.sha256(_generate_hash(func_hash)).hexdigest()

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
            with lock:
                ret, ts, count, _ = func_cache[hash_value]
                func_cache[hash_value] = (ret, ts, count+1, time)
                return ret

        if max_items is not None:
            _cleanup_cache(func_cache, policy, max_items, time)

        ret = func(*args, **kwargs)
        with lock:
            func_cache[hash_value] = (ret, time, 0, time)
        return ret

    def clear(session_context=None):
        global func_hash
        if func_hash is None:
            return
        if to_disk:
            from diskcache import Index
            cache = Index(os.path.join(cache_path, func_hash))
            cache.clear()
        else:
            cache = state._memoize_cache.get(func_hash, {})
        cache.clear()
    wrapped_func.clear = clear

    if per_session and state.curdoc and state.curdoc.session_context:
        state.curdoc.on_session_destroyed(clear)

    try:
        wrapped_func.__dict__.update(func.__dict__)
    except AttributeError:
        pass

    return wrapped_func
