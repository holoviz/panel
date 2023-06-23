import math
import operator

import numpy as np
import param
import pytest

from panel.depends import bind
from panel.interactive import interactive_base

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

class Parameters(param.Parameterized):

    string = param.String(default="string")

    integer = param.Integer(default=7)

    number = param.Number(default=3.14)

    function = param.Callable()

    @param.depends('integer')
    def multiply_integer(self):
        return self.integer * 2

@pytest.mark.parametrize('op', NUMERIC_BINARY_OPERATORS)
def test_interactive_numeric_binary_ops(op):
    assert op(interactive_base(1), 2).eval() == op(1, 2)
    assert op(interactive_base(2), 2).eval() == op(2, 2)

@pytest.mark.parametrize('op', COMPARISON_OPERATORS)
def test_interactive_numeric_comparison_ops(op):
    assert op(interactive_base(1), 2).eval() == op(1, 2)
    assert op(interactive_base(2), 1).eval() == op(2, 1)

@pytest.mark.parametrize('op', NUMERIC_UNARY_OPERATORS)
def test_interactive_numeric_unary_ops(op):
    assert op(interactive_base(1)).eval() == op(1)
    assert op(interactive_base(-1)).eval() == op(-1)
    assert op(interactive_base(3.142)).eval() == op(3.142)

@pytest.mark.parametrize('op', NUMERIC_BINARY_OPERATORS)
def test_interactive_numeric_binary_ops_reverse(op):
    assert op(2, interactive_base(1)).eval() == op(2, 1)
    assert op(2, interactive_base(2)).eval() == op(2, 2)

@pytest.mark.parametrize('op', LOGIC_BINARY_OPERATORS)
def test_interactive_logic_binary_ops(op):
    assert op(interactive_base(True), True).eval() == op(True, True)
    assert op(interactive_base(True), False).eval() == op(True, False)
    assert op(interactive_base(False), True).eval() == op(False, True)
    assert op(interactive_base(False), False).eval() == op(False, False)

@pytest.mark.parametrize('op', LOGIC_UNARY_OPERATORS)
def test_interactive_logic_unary_ops(op):
    assert op(interactive_base(True)).eval() == op(True)
    assert op(interactive_base(False)).eval() == op(False)

@pytest.mark.parametrize('op', LOGIC_BINARY_OPERATORS)
def test_interactive_logic_binary_ops_reverse(op):
    assert op(True, interactive_base(True)).eval() == op(True, True)
    assert op(True, interactive_base(False)).eval() == op(True, False)
    assert op(False, interactive_base(True)).eval() == op(False, True)
    assert op(False, interactive_base(False)).eval() == op(False, False)

def test_interactive_getitem_dict():
    assert interactive_base({'A': 1})['A'].eval() == 1
    assert interactive_base({'A': 1, 'B': 2})['B'].eval() == 2

def test_interactive_getitem_list():
    assert interactive_base([1, 2, 3])[1].eval() == 2
    assert interactive_base([1, 2, 3])[2].eval() == 3

@pytest.mark.parametrize('ufunc', NUMPY_UFUNCS)
def test_numpy_ufunc(ufunc):
    l = [1, 2, 3]
    assert ufunc(interactive_base(l)).eval() == ufunc(l)
    array = np.ndarray([1, 2, 3])
    assert ufunc(interactive_base(array)).eval() == ufunc(array)

def test_interactive_set_new_value():
    i = interactive_base(1)
    assert i.eval() == 1
    i.set(2)
    assert i.eval() == 2

def test_interactive_pipeline_set_new_value():
    i = interactive_base(1) + 2
    assert i.eval() == 3
    i.set(2)
    assert i.eval() == 4

def test_interactive_reflect_param_value():
    P = Parameters(integer=1)
    i = interactive_base(P.param.integer)
    assert i.eval() == 1
    P.integer = 2
    assert i.eval() == 2

def test_interactive_pipeline_reflect_param_value():
    P = Parameters(integer=1)
    i = interactive_base(P.param.integer) + 2
    assert i.eval() == 3
    P.integer = 2
    assert i.eval() == 4

def test_interactive_reflect_other_interactive():
    i = interactive_base(1)
    j = interactive_base(i)
    assert j.eval() == 1
    i.set(2)
    assert j.eval() == 2

def test_interactive_pipeline_reflect_other_interactive():
    i = interactive_base(1) + 2
    j = interactive_base(i)
    assert j.eval() == 3
    i.set(2)
    assert i.eval() == 4

def test_interactive_reflect_bound_method():
    P = Parameters(integer=1)
    i = interactive_base(P.multiply_integer)
    assert i.eval() == 2
    P.integer = 2
    assert i.eval() == 4

def test_interactive_pipeline_reflect_bound_method():
    P = Parameters(integer=1)
    i = interactive_base(P.multiply_integer) + 2
    assert i.eval() == 4
    P.integer = 2
    assert i.eval() == 6

def test_interactive_reflect_bound_function():
    P = Parameters(integer=1)
    i = interactive_base(bind(lambda v: v * 2, P.param.integer))
    assert i.eval() == 2
    P.integer = 2
    assert i.eval() == 4

def test_interactive_pipeline_reflect_bound_function():
    P = Parameters(integer=1)
    i = interactive_base(bind(lambda v: v * 2, P.param.integer)) + 2
    assert i.eval() == 4
    P.integer = 2
    assert i.eval() == 6
