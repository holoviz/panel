import pandas as pd
import param

import panel as pn


def test_tabulator_from_param_dataframe_update():
    class MyObject(param.Parameterized):
        data = param.DataFrame()

    obj = MyObject(data=pd.DataFrame({"a": [1, 2, 3]}))

    widget = pn.widgets.Tabulator.from_param(obj.param.data)

    widget.value = pd.DataFrame({"a": [1, 2, 5]})

    assert obj.data.equals(pd.DataFrame({"a": [1, 2, 5]}))
