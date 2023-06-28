import math
import operator

import numpy as np
import pandas as pd
import param
import pytest

from panel.depends import bind
from panel.layout import Column, Row
from panel.pane.base import PaneBase
from panel.ref import ref, ref_base
from panel.widgets import IntSlider

NUMERIC_BINARY_OPERATORS = (
    operator.add, divmod, operator.floordiv, operator.mod, operator.mul,
    operator.pow, operator.sub, operator.truediv,
)
LOGIC_BINARY_OPERATORS = (
    operator.and_, operator.or_, operator.xor
)

NUMERIC_UNARY_OPERATORS = (
    abs, math.ceil, math.floor, math.trunc, operator.neg, operator.pos, round
)

COMPARISON_OPERATORS = (
    operator.eq, operator.ge, operator.gt, operator.le, operator.lt, operator.ne,
)

LOGIC_UNARY_OPERATORS = (operator.inv,)

NUMPY_UFUNCS = (np.min, np.max)

@pytest.fixture(scope='module')
def series():
    return pd.Series(np.arange(5.0), name='A')

@pytest.fixture(scope='module')
def df():
    return pd._testing.makeMixedDataFrame()

class Parameters(param.Parameterized):

    string = param.String(default="string")

    integer = param.Integer(default=7)

    number = param.Number(default=3.14)

    function = param.Callable()

    @param.depends('integer')
    def multiply_integer(self):
        return self.integer * 2

@pytest.mark.parametrize('op', NUMERIC_BINARY_OPERATORS)
def test_ref_numeric_binary_ops(op):
    assert op(ref_base(1), 2).eval() == op(1, 2)
    assert op(ref_base(2), 2).eval() == op(2, 2)

@pytest.mark.parametrize('op', COMPARISON_OPERATORS)
def test_ref_numeric_comparison_ops(op):
    assert op(ref_base(1), 2).eval() == op(1, 2)
    assert op(ref_base(2), 1).eval() == op(2, 1)

@pytest.mark.parametrize('op', NUMERIC_UNARY_OPERATORS)
def test_ref_numeric_unary_ops(op):
    assert op(ref_base(1)).eval() == op(1)
    assert op(ref_base(-1)).eval() == op(-1)
    assert op(ref_base(3.142)).eval() == op(3.142)

@pytest.mark.parametrize('op', NUMERIC_BINARY_OPERATORS)
def test_ref_numeric_binary_ops_reverse(op):
    assert op(2, ref_base(1)).eval() == op(2, 1)
    assert op(2, ref_base(2)).eval() == op(2, 2)

@pytest.mark.parametrize('op', LOGIC_BINARY_OPERATORS)
def test_ref_logic_binary_ops(op):
    assert op(ref_base(True), True).eval() == op(True, True)
    assert op(ref_base(True), False).eval() == op(True, False)
    assert op(ref_base(False), True).eval() == op(False, True)
    assert op(ref_base(False), False).eval() == op(False, False)

@pytest.mark.parametrize('op', LOGIC_UNARY_OPERATORS)
def test_ref_logic_unary_ops(op):
    assert op(ref_base(True)).eval() == op(True)
    assert op(ref_base(False)).eval() == op(False)

@pytest.mark.parametrize('op', LOGIC_BINARY_OPERATORS)
def test_ref_logic_binary_ops_reverse(op):
    assert op(True, ref_base(True)).eval() == op(True, True)
    assert op(True, ref_base(False)).eval() == op(True, False)
    assert op(False, ref_base(True)).eval() == op(False, True)
    assert op(False, ref_base(False)).eval() == op(False, False)

def test_ref_getitem_dict():
    assert ref_base({'A': 1})['A'].eval() == 1
    assert ref_base({'A': 1, 'B': 2})['B'].eval() == 2

def test_ref_getitem_list():
    assert ref_base([1, 2, 3])[1].eval() == 2
    assert ref_base([1, 2, 3])[2].eval() == 3

@pytest.mark.parametrize('ufunc', NUMPY_UFUNCS)
def test_numpy_ufunc(ufunc):
    l = [1, 2, 3]
    assert ufunc(ref_base(l)).eval() == ufunc(l)
    array = np.ndarray([1, 2, 3])
    assert ufunc(ref_base(array)).eval() == ufunc(array)

def test_ref_set_new_value():
    i = ref_base(1)
    assert i.eval() == 1
    i.set(2)
    assert i.eval() == 2

def test_ref_pipeline_set_new_value():
    i = ref_base(1) + 2
    assert i.eval() == 3
    i.set(2)
    assert i.eval() == 4

def test_ref_reflect_param_value():
    P = Parameters(integer=1)
    i = ref_base(P.param.integer)
    assert i.eval() == 1
    P.integer = 2
    assert i.eval() == 2

def test_ref_pipeline_reflect_param_value():
    P = Parameters(integer=1)
    i = ref_base(P.param.integer) + 2
    assert i.eval() == 3
    P.integer = 2
    assert i.eval() == 4

def test_ref_reflect_other_ref():
    i = ref_base(1)
    j = ref_base(i)
    assert j.eval() == 1
    i.set(2)
    assert j.eval() == 2

def test_ref_pipeline_reflect_other_ref():
    i = ref_base(1) + 2
    j = ref_base(i)
    assert j.eval() == 3
    i.set(2)
    assert i.eval() == 4

def test_ref_reflect_bound_method():
    P = Parameters(integer=1)
    i = ref_base(P.multiply_integer)
    assert i.eval() == 2
    P.integer = 2
    assert i.eval() == 4

def test_ref_pipeline_reflect_bound_method():
    P = Parameters(integer=1)
    i = ref_base(P.multiply_integer) + 2
    assert i.eval() == 4
    P.integer = 2
    assert i.eval() == 6

def test_ref_reflect_bound_function():
    P = Parameters(integer=1)
    i = ref_base(bind(lambda v: v * 2, P.param.integer))
    assert i.eval() == 2
    P.integer = 2
    assert i.eval() == 4

def test_ref_pipeline_reflect_bound_function():
    P = Parameters(integer=1)
    i = ref_base(bind(lambda v: v * 2, P.param.integer)) + 2
    assert i.eval() == 4
    P.integer = 2
    assert i.eval() == 6

def test_ref_dataframe_method_chain(dataframe):
    dfi = ref_base(dataframe).groupby('str')[['float']].mean().reset_index()
    pd.testing.assert_frame_equal(dfi.eval(), dataframe.groupby('str')[['float']].mean().reset_index())

def test_ref_dataframe_attribute_chain(dataframe):
    array = ref_base(dataframe).str.values.eval()
    np.testing.assert_array_equal(array, dataframe.str.values)

def test_ref_dataframe_param_value_method_chain(dataframe):
    P = Parameters(string='str')
    dfi = ref_base(dataframe).groupby(P.param.string)[['float']].mean().reset_index()
    pd.testing.assert_frame_equal(dfi.eval(), dataframe.groupby('str')[['float']].mean().reset_index())
    P.string = 'int'
    pd.testing.assert_frame_equal(dfi.eval(), dataframe.groupby('int')[['float']].mean().reset_index())

def test_ref_layout_default_with_widgets():
    w = IntSlider(value=2, start=1, end=5)
    i = ref(1)
    layout = (i + w).layout()

    assert isinstance(layout, Row)
    assert len(layout) == 1
    assert isinstance(layout[0], Column)
    assert len(layout[0]) == 2
    assert isinstance(layout[0][0], Column)
    assert isinstance(layout[0][1], PaneBase)
    assert len(layout[0][0]) == 1
    assert isinstance(layout[0][0][0], IntSlider)

def test_ref_pandas_layout_loc_with_widgets():
    i = ref(1, loc='top_right', center=True)
    expected = {'loc': 'top_right', 'center': True}
    for k, v in expected.items():
        assert k in i._display_opts
        assert i._display_opts[k] == v

def test_ref_dataframe_handler_opts(dataframe):
    i = ref(dataframe, max_rows=7)
    assert 'max_rows' in i._display_opts
    assert i._display_opts['max_rows'] == 7
