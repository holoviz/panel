import datetime as dt
import io
import pathlib
import time

import numpy as np
import pandas as pd
import param
import pytest

try:
    import diskcache
except Exception:
    diskcache = None
diskcache_available = pytest.mark.skipif(diskcache is None, reason="requires diskcache")

from panel.io.cache import _find_hash_func, cache
from panel.io.state import set_curdoc

################
# Test hashing #
################

def hashes_equal(v1, v2):
    a, b = _find_hash_func(v1)(v1), _find_hash_func(v2)(v2)
    return a == b

def test_str_hash():
    assert hashes_equal('foo', 'foo')
    assert not hashes_equal('foo', 'bar')

def test_int_hash():
    assert hashes_equal(12, 12)
    assert not hashes_equal(1, 2)

def test_float_hash():
    assert hashes_equal(3.14, 3.14)
    assert not hashes_equal(1.2, 3.14)

def test_bool_hash():
    assert hashes_equal(True, True)
    assert hashes_equal(False, False)
    assert not hashes_equal(True, False)

def test_none_hash():
    assert hashes_equal(None, None)
    assert not hashes_equal(None, False)

def test_bytes_hash():
    assert hashes_equal(b'0', b'0')
    assert not hashes_equal(b'0', b'1')

def test_date_hash():
    assert hashes_equal(dt.date(1988, 4, 14), dt.date(1988, 4, 14))
    assert not hashes_equal(dt.date(1988, 4, 14), dt.date(1988, 4, 15))

def test_datetime_hash():
    assert hashes_equal(dt.datetime(1988, 4, 14, 12, 3, 2, 1), dt.datetime(1988, 4, 14, 12, 3, 2, 1))
    assert not hashes_equal(dt.datetime(1988, 4, 14, 12, 3, 2, 1), dt.datetime(1988, 4, 14, 12, 3, 2, 2))

def test_list_hash():
    assert hashes_equal([0], [0])
    assert hashes_equal(['a', ['b']], ['a', ['b']])
    assert not hashes_equal([0], [1])
    assert not hashes_equal(['a', ['b']], ['a', ['c']])

    # Recursion
    l = [0]
    l.append(l)
    assert hashes_equal(l, list(l))

def test_tuple_hash():
    assert hashes_equal((0,), (0,))
    assert hashes_equal(('a', ('b',)), ('a', ('b',)))
    assert not hashes_equal((0,), (1,))
    assert not hashes_equal(('a', ('b',)), ('a', ('c',)))

def test_dict_hash():
    assert hashes_equal({'a': 0}, {'a': 0})
    assert hashes_equal({'a': {'b': 0}}, {'a': {'b': 0}})
    assert not hashes_equal({'a': 0}, {'b': 0})
    assert not hashes_equal({'a': 0}, {'a': 1})
    assert not hashes_equal({'a': {'b': 0}}, {'a': {'b': 1}})

    # Recursion
    d = {'a': {}}
    d['a'] = d
    assert hashes_equal(d, dict(d))

def test_stringio_hash():
    sio1, sio2 = io.StringIO(), io.StringIO()
    sio1.write('foo')
    sio2.write('foo')
    sio1.seek(0)
    sio2.seek(0)
    assert hashes_equal(sio1, sio2)
    sio3 = io.StringIO()
    sio3.write('bar')
    sio3.seek(0)
    assert not hashes_equal(sio1, sio3)

def test_bytesio_hash():
    bio1, bio2 = io.BytesIO(), io.BytesIO()
    bio1.write(b'foo')
    bio2.write(b'foo')
    bio1.seek(0)
    bio2.seek(0)
    assert hashes_equal(bio1, bio2)
    bio3 = io.BytesIO()
    bio3.write(b'bar')
    bio3.seek(0)
    assert not hashes_equal(bio1, bio3)

def test_pathlib_hash():
    assert hashes_equal(pathlib.Path('./'), pathlib.Path('./'))
    assert not hashes_equal(pathlib.Path('./'), pathlib.Path('../'))

def test_ndarray_hash():
    assert hashes_equal(np.array([0, 1, 2]), np.array([0, 1, 2]))
    assert not hashes_equal(
        np.array([0, 1, 2], dtype='uint32'),
        np.array([0, 1, 2], dtype='float64')
    )
    assert not hashes_equal(
        np.array([0, 1, 2]),
        np.array([2, 1, 0])
    )

def test_dataframe_hash():
    df1, df2 = pd._testing.makeMixedDataFrame(), pd._testing.makeMixedDataFrame()
    assert hashes_equal(df1, df2)
    df2['A'] = df2['A'].values[::-1]
    assert not hashes_equal(df1, df2)

def test_series_hash():
    series1 = pd._testing.makeStringSeries()
    series2 = series1.copy()
    assert hashes_equal(series1, series2)
    series2.iloc[0] = 3.14
    assert not hashes_equal(series1, series2)

def test_ufunc_hash():
    assert hashes_equal(np.absolute, np.absolute)
    assert not hashes_equal(np.sin, np.cos)

def test_builtin_hash():
    assert hashes_equal(max, max)
    assert not hashes_equal(max, min)

def test_module_hash():
    assert hashes_equal(np, np)
    assert not hashes_equal(np, io)

################
# Test caching #
################

OFFSET = {}

def function_with_args(a, b):
    global OFFSET
    offset = OFFSET.get((a, b), 0)
    result = a + b + offset
    OFFSET[(a, b)] = offset + 1
    return result

def test_cache_with_args():
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args)
    assert fn(0, 0) == 0
    assert fn(0, 0) == 0

def test_cache_with_kwargs():
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args)
    assert fn(a=0, b=0) == 0
    assert fn(a=0, b=0) == 0

def test_cache_clear():
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args)
    assert fn(0, 0) == 0
    fn.clear()
    assert fn(0, 0) == 1

def test_per_session_cache(document):
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, per_session=True)
    with set_curdoc(document):
        assert fn(a=0, b=0) == 0
    assert fn(a=0, b=0) == 1
    with set_curdoc(document):
        assert fn(a=0, b=0) == 0
    assert fn(a=0, b=0) == 1

@pytest.mark.xdist_group("cache")
@diskcache_available
def test_disk_cache():
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, to_disk=True)

    assert fn(0, 0) == 0
    assert pathlib.Path('./cache').exists()
    assert list(pathlib.Path('./cache').glob('*'))
    assert fn(0, 0) == 0
    fn.clear()
    assert fn(0, 0) == 1

@pytest.mark.xdist_group("cache")
@pytest.mark.parametrize('to_disk', (True, False))
def test_cache_fifo(to_disk):
    if to_disk and diskcache is None:
        pytest.skip('requires diskcache')
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, max_items=2, policy='fifo', to_disk=to_disk)
    assert fn(0, 0) == 0
    assert fn(0, 1) == 1
    assert fn(0, 0) == 0
    assert fn(0, 2) == 2 # (0, 0) should be evicted
    assert fn(0, 0) == 1

@pytest.mark.xdist_group("cache")
@pytest.mark.parametrize('to_disk', (True, False))
def test_cache_lfu(to_disk):
    if to_disk and diskcache is None:
        pytest.skip('requires diskcache')
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, max_items=2, policy='lfu', to_disk=to_disk)
    assert fn(0, 0) == 0
    assert fn(0, 0) == 0
    assert fn(0, 1) == 1
    assert fn(0, 2) == 2 # (0, 1) should be evicted
    assert fn(0, 1) == 2

@pytest.mark.xdist_group("cache")
@pytest.mark.parametrize('to_disk', (True, False))
def test_cache_lru(to_disk):
    if to_disk and diskcache is None:
        pytest.skip('requires diskcache')
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, max_items=3, policy='lru', to_disk=to_disk)
    assert fn(0, 0) == 0
    assert fn(0, 1) == 1
    assert fn(0, 2) == 2
    assert fn(0, 0) == 0
    assert fn(0, 3) == 3 # (0, 1) should be evicted
    assert fn(0, 0) == 0
    assert fn(0, 1) == 2

@pytest.mark.xdist_group("cache")
@pytest.mark.parametrize('to_disk', (True, False))
def test_cache_ttl(to_disk):
    if to_disk and diskcache is None:
        pytest.skip('requires diskcache')
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, ttl=0.1, to_disk=to_disk)
    assert fn(0, 0) == 0
    time.sleep(0.2)
    assert fn(0, 0) == 1

@pytest.mark.xdist_group("cache")
def test_cache_on_undecorated_parameterized_method():
    class Model(param.Parameterized):
        data = param.Parameter(default=1)
        executions = param.Integer(default=0)

        @cache
        def expensive_calculation(self, value):
            self.executions += 1
            return 2*value

    model = Model()
    assert model.expensive_calculation(1) == 2
    assert model.expensive_calculation(1) == 2

    assert model.executions == 1

    assert model.expensive_calculation(2) == 4

    assert model.executions == 2
