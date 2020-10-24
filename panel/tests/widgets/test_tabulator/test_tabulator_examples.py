"""This file contains examples testing the Tabulator"""
from typing import Dict

import pandas as pd
import panel as pn
import param
from bokeh.models import ColumnDataSource

from panel.widgets.tabulator import Tabulator, TABULATOR_CSS_THEMES
pn.config.css_files.append(TABULATOR_CSS_THEMES["site"])

def tabulator_data_specified_in_configuration():
    configuration = {
        "layout": "fitColumns",
        "data": [{"x": [1], "y": "a"}, {"x": [2], "y": "b"}],
        "initialSort": [{"column": "y", "dir": "desc"},],
        "columns": [
            {"title": "Value", "field": "x"},
            {"title": "Item", "field": "y", "hozAlign": "right", "formatter": "money"},
        ],
    }
    return Tabulator(configuration=configuration)


def tabulator_data_specified_as_data_frame_value():
    configuration = {
        "layout": "fitColumns",
        "initialSort": [{"column": "y", "dir": "desc"},],
        "columns": [
            {"title": "Value", "field": "x"},
            {"title": "Item", "field": "y", "hozAlign": "right", "formatter": "money"},
        ],
    }
    value = pd.DataFrame([{"x": [1], "y": "a"}, {"x": [2], "y": "b"}])
    return Tabulator(configuration=configuration, value=value)


def tabulator_data_specified_as_column_data_source_value():
    configuration = {
        "layout": "fitColumns",
        "initialSort": [{"column": "y", "dir": "desc"},],
        "columns": [
            {"title": "Value", "field": "x"},
            {"title": "Item", "field": "y", "hozAlign": "right", "formatter": "money"},
        ],
    }
    value = ColumnDataSource({"x": [1, 2], "y": ["a", "b"]})
    return Tabulator(configuration=configuration, value=value)

class TabulatorStylesheet(pn.pane.HTML):
    """The TabulatorStyleSheet provides methods to dynamically change the (css) style of the
    Tabulator widget"""

    theme = param.ObjectSelector(default="site", objects=sorted(list(TABULATOR_CSS_THEMES.keys())))

    # In order to not be selected by the `pn.panel` selection process
    # Cf. https://github.com/holoviz/panel/issues/1494#issuecomment-663219654
    priority = 0
    # The _rename dict is used to keep track of Panel parameters to sync to Bokeh properties.
    # As value is not a property on the Bokeh model we should set it to None
    _rename = {
        **pn.pane.HTML._rename,
        "theme": None,
    }

    def __init__(self, **params):
        params["height"] = 0
        params["width"] = 0
        params["sizing_mode"] = "fixed"
        params["margin"] = 0
        super().__init__(**params)

        self._update_object_from_parameters()

    # Don't name the function
    # `_update`, `_update_object`, `_update_model` or `_update_pane`
    # as this will override a function in the parent class.
    @param.depends("theme", watch=True)
    def _update_object_from_parameters(self, *_):
        href = TABULATOR_CSS_THEMES[self.theme]
        self.object = f'<link rel="stylesheet" href="{href}">'

    def __repr__(self, depth=0):  # pylint: disable=unused-argument
        return f"Tabulator({self.name})"

    def __str__(self):
        return f"Tabulator({self.name})"

class TabulatorDataCDSApp(pn.Column):
    """Extension Implementation"""

    tabulator = param.Parameter()

    reset = param.Action(label="RESET")
    replace = param.Action(label="REPLACE")
    stream = param.Action(label="STREAM")
    patch = param.Action(label="PATCH")

    # The _rename dict is used to keep track of Panel parameters to sync to Bokeh properties.
    # As dope is not a property on the Bokeh model we should set it to None
    _rename = {
        **pn.Column._rename,
        "tabulator": None,
        "reset": None,
        "replace": None,
        "stream": None,
        "patch": None,
    }

    def __init__(self, configuration: Dict, data: pd.DataFrame, **params):
        super().__init__(**params)

        self.data = data
        self.data_reset = ColumnDataSource(self.data.iloc[0:10,])

        self.tabulator = Tabulator(
            configuration=configuration,
            value=self.data_reset,
            sizing_mode="stretch_both",
            background="salmon",
        )
        self.sizing_mode = "stretch_width"
        self.height = 950

        self.rows_count = len(self.data)
        self.stream_count = 15

        self.reset = self._reset_action
        self.replace = self._replace_action
        self.stream = self._stream_action
        self.patch = self._patch_action
        stylesheet = TabulatorStylesheet(theme="site")
        actions_pane = pn.Param(
            self, parameters=["reset", "replace", "stream", "patch"], name="Actions"
        )
        tabulator_pane = pn.Param(self.tabulator, parameters=["selection"])
        self[:] = [
            stylesheet,
            self.tabulator,
            pn.WidgetBox(
                stylesheet.param.theme, actions_pane, tabulator_pane, sizing_mode="fixed", width=400
            ),
        ]

    def _reset_action(self, *events):
        value = self.data.iloc[
            0:10,
        ]
        self.tabulator.value.data = value

    def _replace_action(self, *events):
        data = self.data.iloc[
            10:15,
        ]
        self.tabulator.value.data = data

    def _stream_action(self, *events):
        if self.stream_count == len(self.data):
            self.stream_count = 15
            self._reset_action()
        else:
            stream_data = self.data.iloc[
                self.stream_count : self.stream_count + 1,
            ]
            self.tabulator.stream(stream_data)
            self.stream_count += 1

    def _patch_action(self, *events):
        def _patch(value):
            value += 10
            if value >= 100:
                return 0
            return value

        data = self.tabulator.value.data
        progress = data["progress"]
        new_progress = [_patch(value) for value in progress]
        patches = {
            "progress": [(slice(len(progress)), new_progress)],
        }
        self.tabulator.patch(patches)

    def __repr__(self):
        return f"Tabulator({self.name})"

    def __str__(self):
        return f"Tabulator({self.name})"


class TabulatorDataFrameApp(pn.Column):
    """Extension Implementation"""

    tabulator = param.Parameter()

    reset = param.Action(label="RESET")
    replace = param.Action(label="REPLACE")
    stream = param.Action(label="STREAM")
    patch = param.Action(label="PATCH")

    avg_rating = param.Number(default=0, constant=True)
    value_edits = param.Number(default=-1, constant=True)

    # The _rename dict is used to keep track of Panel parameters to sync to Bokeh properties.
    # As dope is not a property on the Bokeh model we should set it to None
    _rename = {
        **pn.Column._rename,
        "tabulator": None,
        "avg_rating": None,
        "value_edits": None,
        "reset": None,
        "replace": None,
        "stream": None,
        "patch": None,
    }

    def __init__(self, configuration, data: pd.DataFrame, **params):
        super().__init__(**params)
        self.data = data
        self.tabulator = params["tabulator"] = Tabulator(
            configuration=configuration,
            value=self.data.copy(deep=True).iloc[0:10,],
            sizing_mode="stretch_both",
            background="salmon",
        )
        self.sizing_mode = "stretch_width"
        self.height = 950

        self.rows_count = len(self.data)
        self.stream_count = 15

        self.reset = self._reset_action
        self.replace = self._replace_action
        self.stream = self._stream_action
        self.patch = self._patch_action
        stylesheet = TabulatorStylesheet(theme="site")
        actions_pane = pn.Param(
            self,
            parameters=["reset", "replace", "stream", "patch", "avg_rating", "value_edits"],
            name="Actions",
        )
        tabulator_pane = pn.Param(self.tabulator, parameters=["selection"])
        self[:] = [
            stylesheet,
            self.tabulator,
            pn.WidgetBox(
                stylesheet.param.theme, actions_pane, tabulator_pane, sizing_mode="fixed", width=400
            ),
        ]
        self._update_avg_rating()
        self.tabulator.param.watch(self._update_avg_rating, "value")

    def _reset_action(self, *events):
        value = self.data.copy(deep=True).iloc[
            0:10,
        ]
        self.tabulator.value = value

    def _replace_action(self, *events):
        # Please note that it is required that the index is reset
        # Please also remember to add drop=True. Otherwise stream and patch raises errors
        value = self.data.copy(deep=True).iloc[10:15,].reset_index(drop=True)
        self.tabulator.value = value

    def _stream_action(self, *events):
        if self.stream_count == len(self.data):
            self.stream_count = 15
            self._reset_action()
        else:
            stream_data = self.data.iloc[
                self.stream_count : self.stream_count + 1,
            ]
            self.tabulator.stream(stream_data)
            self.stream_count += 1
            # Alternatively you can use
            # self.tabulator.value.stream(stream_data)
            # But this will not raise a value changed event

    def _patch_action(self, *events):
        def _patch(value):
            value += 10
            if value >= 100:
                return 0
            return value

        data = self.tabulator.value
        progress = data["progress"]
        new_progress = progress.map(_patch)
        self.tabulator.patch(new_progress)
        # Alternatively you can use
        # self.tabulator.value.patch(patches)
        # But this will not raise a value changed event

    def _update_avg_rating(self, *events):
        with param.edit_constant(self):
            self.avg_rating = self.tabulator.value["rating"].mean()
            self.value_edits += 1

    def __repr__(self):
        return f"Tabulator({self.name})"

    def __str__(self):
        return f"Tabulator({self.name})"

if __name__.startswith("bokeh"):
    configuration = {
        "layout": "fitColumns",
        "responsiveLayout": "hide",
        "tooltips": True,
        "addRowPos": "top",
        "history": True,
        "pagination": "local",
        "paginationSize": 20,
        "movableColumns": True,
        "resizableRows": True,
        "initialSort": [{"column": "name", "dir": "asc"},],
        "selectable": True,
        "columns": [
            {"title": "Name", "field": "name", },
            {
                "title": "Task Progress",
                "field": "progress",
                "hozAlign": "left",
                "formatter": "progress",
            },
            {
                "title": "Gender",
                "field": "gender",
                "width": 95,
            },
            {
                "title": "Rating",
                "field": "rating",
                "formatter": "star",
                "hozAlign": "center",
                "width": 100,
                "editor": True,

            },
            {"title": "Color", "field": "col", "width": 130},
            {
                "title": "Date Of Birth",
                "field": "dob",
                "width": 130,
                "sorter": "date",
                "hozAlign": "center",
            },
            {
                "title": "Driver",
                "field": "car",
                "width": 90,
                "hozAlign": "center",
                "formatter": "tickCross",
                "sorter": "boolean",
            },
            {
                "title": "Index",
                "field": "index",
                "width": 90,
                "hozAlign": "right",
            },
        ],
    }
    TABULATOR_DATA_URL = "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-extensions/master/tests/widgets/test_tabulator/tabulator_data.csv"
    data = pd.read_csv(TABULATOR_DATA_URL)
    data = data.fillna("nan") # Clean up the data. Tabulator does not work with NaN values.
    TabulatorDataFrameApp(
        configuration=configuration,
        data=data,
    ).servable()