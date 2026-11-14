"""Tests for Param widget DataFrame synchronization"""
import pandas as pd
import param

from panel.widgets import Tabulator


def test_tabulator_from_param_dataframe_update():
    class MyObject(param.Parameterized):
        data = param.DataFrame()

    obj = MyObject(data=pd.DataFrame({"a": [1, 2, 3]}))
    widget = Tabulator.from_param(obj.param.data)
    widget.value = pd.DataFrame({"a": [1, 2, 5]})
    assert obj.data.equals(pd.DataFrame({"a": [1, 2, 5]}))
    assert widget.value.equals(pd.DataFrame({"a": [1, 2, 5]}))


def test_tabulator_from_param_no_spurious_updates():
    class MyObject(param.Parameterized):
        data = param.DataFrame()

    obj = MyObject(data=pd.DataFrame({"a": [1, 2, 3]}))
    widget = Tabulator.from_param(obj.param.data)
    update_count = [0]
    def on_change(event):
        update_count[0] += 1
    obj.param.watch(on_change, "data")
    widget.value = pd.DataFrame({"a": [1, 2, 5]})
    assert update_count[0] == 1, f"Expected 1 update, got {update_count[0]}"


def test_tabulator_from_param_param_update_reflects_in_widget():
    class MyObject(param.Parameterized):
        data = param.DataFrame()

    obj = MyObject(data=pd.DataFrame({"a": [1, 2, 3]}))
    widget = Tabulator.from_param(obj.param.data)
    obj.data = pd.DataFrame({"a": [4, 5, 6]})
    assert widget.value.equals(pd.DataFrame({"a": [4, 5, 6]}))
