import math
import operator

import pytest

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

@pytest.mark.parametrize('op', NUMERIC_BINARY_OPERATORS)
def test_interactive_constant_value_numeric_binary_ops(op):
    assert op(interactive_base(1), 2) == op(1, 2)
    assert op(interactive_base(2), 2) == op(2, 2)

@pytest.mark.parametrize('op', COMPARISON_OPERATORS)
def test_interactive_constant_value_numeric_comparison_ops(op):
    assert op(interactive_base(1), 2) == op(1, 2)
    assert op(interactive_base(2), 1) == op(2, 1)

@pytest.mark.parametrize('op', NUMERIC_UNARY_OPERATORS)
def test_interactive_constant_value_numeric_unary_ops(op):
    assert op(interactive_base(1)) == op(1)
    assert op(interactive_base(-1)) == op(-1)
    assert op(interactive_base(3.142)) == op(3.142)

@pytest.mark.parametrize('op', NUMERIC_BINARY_OPERATORS)
def test_interactive_constant_value_numeric_binary_ops_reverse(op):
    assert op(2, interactive_base(1)) == op(2, 1)
    assert op(2, interactive_base(2)) == op(2, 2)

@pytest.mark.parametrize('op', LOGIC_BINARY_OPERATORS)
def test_interactive_constant_value_logic_binary_ops(op):
    assert op(interactive_base(True), True) == op(True, True)
    assert op(interactive_base(True), False) == op(True, False)
    assert op(interactive_base(False), True) == op(False, True)
    assert op(interactive_base(False), False) == op(False, False)

@pytest.mark.parametrize('op', LOGIC_UNARY_OPERATORS)
def test_interactive_constant_value_logic_unary_ops(op):
    assert op(interactive_base(True)) == op(True)
    assert op(interactive_base(False)) == op(False)

@pytest.mark.parametrize('op', LOGIC_BINARY_OPERATORS)
def test_interactive_constant_value_logic_binary_ops_reverse(op):
    assert op(True, interactive_base(True)) == op(True, True)
    assert op(True, interactive_base(False)) == op(True, False)
    assert op(False, interactive_base(True)) == op(False, True)
    assert op(False, interactive_base(False)) == op(False, False)
