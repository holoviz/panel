import numpy as np
import pandas as pd
import param

from param import reactive

from panel.layout import Row, WidgetBox
from panel.pane.base import PaneBase
from panel.param import ReactiveExpr
from panel.widgets import IntSlider


class Parameters(param.Parameterized):

    string = param.String(default="string")

    integer = param.Integer(default=7)

    number = param.Number(default=3.14)

    function = param.Callable()

    @param.depends('integer')
    def multiply_integer(self):
        return self.integer * 2

def test_reactive_widget_input():
    slider = IntSlider()
    expr = ReactiveExpr(reactive(slider))
    assert slider in expr.widgets

def test_reactive_widget_operator():
    slider = IntSlider()
    expr = ReactiveExpr(reactive(1) + slider)
    assert slider in expr.widgets

def test_reactive_widget_method_arg():
    slider = IntSlider()
    expr = ReactiveExpr(reactive('{}').format(slider))
    assert slider in expr.widgets

def test_reactive_widget_method_kwarg():
    slider = IntSlider()
    expr = ReactiveExpr(reactive('{value}').format(value=slider))
    assert slider in expr.widgets

def test_reactive_widget_order():
    slider1 = IntSlider(name='Slider1')
    slider2 = IntSlider(name='Slider2')
    expr = ReactiveExpr(reactive(slider1) + reactive(slider2))
    assert list(expr.widgets) == [slider1, slider2]

def test_reactive_dataframe_method_chain(dataframe):
    dfi = reactive(dataframe).groupby('str')[['float']].mean().reset_index()
    pd.testing.assert_frame_equal(dfi.rx.resolve(), dataframe.groupby('str')[['float']].mean().reset_index())

def test_reactive_dataframe_attribute_chain(dataframe):
    array = reactive(dataframe).str.values.rx.resolve()
    np.testing.assert_array_equal(array, dataframe.str.values)

def test_reactive_dataframe_param_value_method_chain(dataframe):
    P = Parameters(string='str')
    dfi = reactive(dataframe).groupby(P.param.string)[['float']].mean().reset_index()
    pd.testing.assert_frame_equal(dfi.rx.resolve(), dataframe.groupby('str')[['float']].mean().reset_index())
    P.string = 'int'
    pd.testing.assert_frame_equal(dfi.rx.resolve(), dataframe.groupby('int')[['float']].mean().reset_index())

def test_reactive_layout_default_with_widgets():
    w = IntSlider(value=2, start=1, end=5)
    i = reactive(1)
    layout = ReactiveExpr(i + w).layout

    assert isinstance(layout, Row)
    assert len(layout) == 1
    assert isinstance(layout[0], Row)
    assert len(layout[0]) == 2
    assert isinstance(layout[0][0], WidgetBox)
    assert isinstance(layout[0][1], PaneBase)
    assert len(layout[0][0]) == 1
    assert isinstance(layout[0][0][0], IntSlider)

def test_reactive_dataframe_handler_opts(dataframe):
    i = reactive(dataframe, max_rows=7)
    assert 'max_rows' in i._display_opts
    assert i._display_opts['max_rows'] == 7
