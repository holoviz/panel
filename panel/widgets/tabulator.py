"""The Tabulator Pane wraps the [Tabulator](http://tabulator.info/) table to provide an awesome
interative table.

You can
- Specify an initial `configuration`.
- Provide a `value` as a Pandas DataFrame or Bokeh ColumnDataSource.
- Edit cell values in the browser.
- Select rows in the browser or in code.
- `stream` (append) to the `value`.
- `patch` (update) the `value`.
- Change the (css) style using the TabulatorStylesheet.
"""
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import panel as pn
import param
from bokeh.models.sources import ColumnDataSource
from panel.widgets.base import Widget

from panel.models.tabulator_model import CSS_HREFS
from panel.models.tabulator_model import TabulatorModel as _BkTabulator

_DEFAULT_CONFIGURATION = {"autoColumns": True}
_FORMATTERS = {
    "bool": "plaintext",
    "category": "plaintext",
    "datetime64": "datetime",
    "datetime64[ns]": "datetime",
    "float64": "money",
    "int64": "money",
    "object": "plaintext",
    "timedelta[ns]": "datetimediff",
}
_SORTERS = {
    "bool": "tickCross",
    "category": "string",
    "datetime64": "datetime",
    "datetime64[ns]": "datetime",
    "float64": "number",
    "int64": "number",
    "object": "string",
    "timedelta[ns]": "datetime",
}
_HOZ_ALIGNS = {
    "bool": "center",
    "category": "left",
    "datetime64": "left",
    "datetime64[ns]": "left",
    "float64": "right",
    "int64": "right",
    "object": "left",
    "timedelta[ns]": "right",
}


class Tabulator(Widget):
    """The Tabulator Pane wraps the [Tabulator](http://tabulator.info/) table to provide an
awesome interative table.

You can
- Specify a `configuration` dictionary at instantation. See http://tabulator.info/.
- Provide an initial `value` as a Pandas DataFrame or Bokeh ColumnDataSource.
- `stream` (append) to the `value`.
- `patch` (update) the `value`.

Example: Data specified in configuration

>>> from panel.widgets.tabulator import Tabulator
>>> configuration = {
...     "layout": "fitColumns",
...     "data": [
...         {"x": [1], "y": 'a'},
...         {"x": [2], "y": 'b'}
...         ],
...     "initialSort":[
...         {"column":"y", "dir":"desc"},
...     ],
...     "columns":[
...         {"title": "Value", "field":"x"},
...         {"title": "Item", "field":"y", "hozAlign":"right", "formatter":"money"}
...     ],
... }
>>> Tabulator(configuration=configuration)
Tabulator(...)

Example: Data specified as Pandas.DataFrame value

>>> import pandas as pd
>>> configuration = {
...     "layout": "fitColumns",
...     "initialSort":[
...         {"column":"y", "dir":"desc"},
...     ],
...     "columns":[
...         {"title": "Value", "field":"x"},
...         {"title": "Item", "field":"y", "hozAlign":"right", "formatter":"money"}
...     ],
... }
>>> value = pd.DataFrame([
...     {"x": [1], "y": 'a'},
...     {"x": [2], "y": 'b'}
... ])
>>> Tabulator(configuration=configuration, value=value)
Tabulator(...)

Example: Data specified as Bokeh ColumnDataSource value

>>> configuration = {
...     "layout": "fitColumns",
...     "initialSort":[
...         {"column":"y", "dir":"desc"},
...     ],
...     "columns":[
...         {"title": "Value", "field":"x"},
...         {"title": "Item", "field":"y", "hozAlign":"right", "formatter":"money"}
...     ],
... }
>>> value = ColumnDataSource({"x": [1,2], "y": ["a", "b"]})
>>> Tabulator(configuration=configuration, value=value)
Tabulator(...)
"""

    value = param.Parameter(
        doc="""One of pandas.DataFrame or bokeh.models.ColumnDataSource.

        Please note when specifying a Pandas.Dataframe we currently have some narrow requirements

        - The index should be a single index which should be called 'index' and be unique. To make
        sure things work we suggest you `.reset_index()` before usage.
        """
    )
    selection = param.List(doc="The list of selected row indexes. For example [1,4]. Default is []")
    configuration = param.Dict(
        constant=True,
        doc="""The initial Tabulator configuration. See https://tabulator.info for lots of
        examples.

        If None is provided at instantiation, then {'autocolumns': True} is added

        Please note that in order to get things working we add the below to the configuration
        on the js side.
        {
            "rowSelectionChanged": rowSelectionChanged,
            "cellEdited": cellEdited,
            "index": "index",
        }
        """,
    )

    height = param.Integer(
        default=300,
        bounds=(0, None),
        doc="""The height of the Tabulator table. Specifying a height is mandatory.""",
    )

    _source = param.ClassSelector(
        class_=ColumnDataSource, doc="Used to transfer the `value` efficiently to frontend"
    )
    _cell_change = param.Dict(
        doc="""Changed whenever the user updates a cell in the client. Sends something like
        {"c": "<COLUMN NAME>", "i": "<INDEX>", "v": "<NEW VALUE>"}. Used to transfer the change
        efficiently and update the DataFrame as I could not find a similar property/ event on the
        ColumnDataSource"""
    )

    _rename = {
        "value": None,
        "selection": None,
        "_source": "source",
    }
    _widget_type = _BkTabulator

    def __init__(self, **params):
        """The Tabulator Pane wraps the [Tabulator](http://tabulator.info/) table to provide an
        awesome interative table.

You can
- Specify a `configuration` dictionary at instantation. See http://tabulator.info/.
- Provide an initial `value` as a Pandas DataFrame or Bokeh ColumnDataSource.
- `stream` (append) to the `value`.
- `patch` (update) the `value`.

Example: Data specified in configuration

>>> from panel.widgets.tabulator import Tabulator
>>> configuration = {
...     "layout": "fitColumns",
...     "data": [
...         {"x": [1], "y": 'a'},
...         {"x": [2], "y": 'b'}
...         ],
...     "initialSort":[
...         {"column":"y", "dir":"desc"},
...     ],
...     "columns":[
...         {"title": "Value", "field":"x"},
...         {"title": "Item", "field":"y", "hozAlign":"right", "formatter":"money"}
...     ],
... }
>>> Tabulator(configuration=configuration)
Tabulator(...)

Example: Data specified as Pandas.DataFrame value

>>> import pandas as pd
>>> configuration = {
...     "layout": "fitColumns",
...     "initialSort":[
...         {"column":"y", "dir":"desc"},
...     ],
...     "columns":[
...         {"title": "Value", "field":"x"},
...         {"title": "Item", "field":"y", "hozAlign":"right", "formatter":"money"}
...     ],
... }
>>> value = pd.DataFrame([
...     {"x": [1], "y": 'a'},
...     {"x": [2], "y": 'b'}
... ])
>>> Tabulator(configuration=configuration, value=value)
Tabulator(...)

Example: Data specified as Bokeh ColumnDataSource value

>>> configuration = {
...     "layout": "fitColumns",
...     "initialSort":[
...         {"column":"y", "dir":"desc"},
...     ],
...     "columns":[
...         {"title": "Value", "field":"x"},
...         {"title": "Item", "field":"y", "hozAlign":"right", "formatter":"money"}
...     ],
... }
>>> value = ColumnDataSource({"x": [1,2], "y": ["a", "b"]})
>>> Tabulator(configuration=configuration, value=value)
Tabulator(...)
"""
        if "configuration" not in params:
            params["configuration"] = _DEFAULT_CONFIGURATION.copy()
        if "selection" not in params:
            params["selection"] = []

        super().__init__(**params)

        self._pause_cds_updates = False
        self._update_column_data_source()

    @param.depends("value", watch=True)
    def _update_column_data_source(self, *_):
        if self._pause_cds_updates:
            return

        if self.value is None:
            self._source = ColumnDataSource({})
        elif isinstance(self.value, pd.DataFrame):
            if (
                not isinstance(self.value.index, pd.RangeIndex)
                or self.value.index.start != 0
                or self.value.index.step != 1
            ):
                raise ValueError(
                    "Please provide a DataFrame with RangeIndex starting at 0 and with step 1"
                )

            if self._source:
                self._source.data = self.value
            else:
                self._source = ColumnDataSource(self.value)
        elif isinstance(self.value, ColumnDataSource):
            self._source = self.value
        else:
            raise ValueError("The `data` provided is not of a supported type!")

    @param.depends("_cell_change", watch=True)
    def _update_value_with_cell_change(self):
        if isinstance(self.value, pd.DataFrame):
            column = self._cell_change["c"]  # pylint: disable=unsubscriptable-object
            index = self._cell_change["i"]  # pylint: disable=unsubscriptable-object
            new_value = self._cell_change["v"]  # pylint: disable=unsubscriptable-object
            self._pause_cds_updates = True
            self.value.at[index, column] = new_value
            self.param.trigger("value")
            self._pause_cds_updates = False

    def stream(self, stream_value: Union[pd.DataFrame, pd.Series, Dict], reset_index: bool = True):
        """Streams (appends) the `stream_value` provided to the existing value in an efficient
        manner.

        Args:
            stream_value (Union[pd.DataFrame, pd.Series, Dict]): The new value(s) to append to the
                existing value.
            reset_index (bool, optional): If the stream_value is a DataFrame and `reset_index` is
                True then the index of it is reset if True. Helps to keep the index unique and
                named `index`. Defaults to True.

        Raises:
            ValueError: Raised if the stream_value is not a supported type.

        Example: Stream a Series to a DataFrame

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> stream_value = pd.Series({"x": 4, "y": "d"})
        >>> tabulator.stream(stream_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 2, 4], 'y': ['a', 'b', 'd']}

        Example: Stream a Dataframe to a Dataframe

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
        >>> tabulator.stream(stream_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 2, 3, 4], 'y': ['a', 'b', 'c', 'd']}


        Example: Stream a Dictionary row to a DataFrame

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> stream_value = {"x": 4, "y": "d"}
        >>> tabulator.stream(stream_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 2, 4], 'y': ['a', 'b', 'd']}

         Example: Stream a Dictionary of Columns to a Dataframe

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> stream_value = {"x": [3, 4], "y": ["c", "d"]}
        >>> tabulator.stream(stream_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 2, 3, 4], 'y': ['a', 'b', 'c', 'd']}
        """

        if isinstance(self.value, pd.DataFrame):
            value_index_start = self.value.index.max() + 1
            if isinstance(stream_value, pd.DataFrame):
                if reset_index:
                    stream_value = stream_value.reset_index(drop=True)
                    stream_value.index += value_index_start
                self._pause_cds_updates = True
                self.value = pd.concat([self.value, stream_value])
                self._source.stream(stream_value)
                self._pause_cds_updates = False
            elif isinstance(stream_value, pd.Series):
                self._pause_cds_updates = True
                self.value.loc[value_index_start] = stream_value
                self._source.stream(stream_value)
                self.param.trigger("value")
                self._pause_cds_updates = False
            elif isinstance(stream_value, dict):
                if stream_value:
                    try:
                        stream_value = pd.DataFrame(stream_value)
                    except ValueError:
                        stream_value = pd.Series(stream_value)
                    self.stream(stream_value)
            else:
                raise ValueError("The patch value provided is not a DataFrame, Series or Dict!")
        else:
            self._pause_cds_updates = True
            self._source.stream(stream_value)
            self.param.trigger("value")
            self._pause_cds_updates = False

    def patch(self, patch_value: Union[pd.DataFrame, pd.Series, Dict]):
        """Patches (updates) the existing value with the `patch_value` in an efficient manner.

        Args:
            patch_value (Union[pd.DataFrame, pd.Series, Dict]): The value(s) to patch the
                existing value with.

        Raises:
            ValueError: Raised if the patch_value is not a supported type.



        Example: Patch a DataFrame with a Dictionary row.

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> patch_value = {"x": [(0, 3)]}
        >>> tabulator.patch(patch_value)
        >>> tabulator.value.to_dict("list")
        {'x': [3, 2], 'y': ['a', 'b']}

         Example: Patch a Dataframe with a Dictionary of Columns.

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> patch_value = {"x": [(slice(2), (3,4))], "y": [(1,'d')]}
        >>> tabulator.patch(patch_value)
        >>> tabulator.value.to_dict("list")
        {'x': [3, 4], 'y': ['a', 'd']}

        Example: Patch a DataFrame with a Series. Please note the index is used in the update

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> patch_value = pd.Series({"index": 1, "x": 4, "y": "d"})
        >>> tabulator.patch(patch_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 4], 'y': ['a', 'd']}

        Example: Patch a Dataframe with a Dataframe. Please note the index is used in the update.

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> patch_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
        >>> tabulator.patch(patch_value)
        >>> tabulator.value.to_dict("list")
        {'x': [3, 4], 'y': ['c', 'd']}
        """
        if isinstance(self.value, pd.DataFrame):
            if isinstance(patch_value, pd.DataFrame):
                patch_value_dict = self._patch_dataframe_to_dict(patch_value)
                self.patch(patch_value_dict)
            elif isinstance(patch_value, pd.Series):
                patch_value_dict = self._patch_series_to_dict(patch_value)
                self.patch(patch_value_dict)
            elif isinstance(patch_value, dict):
                self._patch_from_dict(patch_value)
            else:
                raise ValueError(
                    f"""Patching a patch_value of type {type(patch_value)} is not supported.
                    Please provide a DataFrame, Series or Dict"""
                )
        else:
            if isinstance(patch_value, dict):
                self._pause_cds_updates = True
                self._source.patch(patch_value)
                self.param.trigger("value")
                self._pause_cds_updates = False
            else:
                raise ValueError(
                    f"""Patching a patch_value of type {type(patch_value)} is not supported.
                    Please provide a dict"""
                )

    @staticmethod
    def _patch_dataframe_to_dict(patch_value: pd.DataFrame) -> Dict:
        patch_value_dict: Dict[Any, Any] = {}
        for column in patch_value.columns:
            patch_value_dict[column] = []
            for index in patch_value.index:
                patch_value_dict[column].append((index, patch_value.loc[index, column]))

        return patch_value_dict

    @staticmethod
    def _patch_series_to_dict(patch_value: pd.Series) -> Dict:
        if "index" in patch_value:  # Series orient is row
            patch_value_dict = {k: [(patch_value["index"], v)] for k, v in patch_value.items()}
            patch_value_dict.pop("index")
        else:  # Series orient is column
            patch_value_dict = {patch_value.name: list(patch_value.items())}
        return patch_value_dict

    def _patch_from_dict(self, patch_value: Dict):
        self._pause_cds_updates = True
        for key, value in patch_value.items():
            for update in value:
                self.value.loc[update[0], key] = update[1]
        self._source.patch(patch_value)
        self.param.trigger("value")
        self._pause_cds_updates = False

    @classmethod
    def to_columns_configuration(
        cls, value: Union[pd.DataFrame, ColumnDataSource]
    ) -> List[Dict[str, str]]:
        """Returns a nice starter `columns` dictionary from the specified `value`.

        Args:
            value (Union[pd.DataFrame, ColumnDataSource]): The data source to transform.

        Returns:
            Dict: The columns configuration

        Example:

        >>> import pandas as pd
        >>> value = {"name": ["python", "panel"]}
        >>> df = pd.DataFrame(value)
        >>> Tabulator.to_columns_configuration(df)
        [{'title': 'Name', 'field': 'name', 'sorter': 'string', 'formatter': 'plaintext', \
'hozAlign': 'left'}]
        """
        col_conf = []
        for field in value.columns:
            dtype = str(value.dtypes[field])
            conf = cls._core(field=field, dtype=dtype)
            col_conf.append(conf)
        return col_conf

    @classmethod
    def _core(cls, field: str, dtype: str) -> Dict[str, str]:
        dtype_str = str(dtype)
        return {
            "title": cls._to_title(field),
            "field": field,
            "sorter": _SORTERS.get(dtype_str, "string"),
            "formatter": _FORMATTERS.get(dtype_str, "plaintext"),
            "hozAlign": _HOZ_ALIGNS.get(dtype_str, "left"),
        }

    @staticmethod
    def _to_title(field: str) -> str:
        return field.replace("_", " ").title()

    @staticmethod
    def config(css: Optional[str] = "default"):
        """Adds the specified css theme to pn.config.css_files

        Args:
            css (Optional[str], optional): [description]. Defaults to "default".
        """
        if css:
            href = CSS_HREFS[css]
            if href not in pn.config.css_files:
                pn.config.css_files.append(href)

    @property
    def selected_values(self) -> Union[pd.DataFrame, ColumnDataSource, None]:
        """Returns the selected rows of the data based

        Raises:
            ValueError: If the value is not of the supported type.

        Returns:
            Union[pd.DataFrame, ColumnDataSource, None]: The selected values of the same type as
                value. Based on the the current selection.
        """
        # Selection is a list of row indices. For example [0,2]
        if self.value is None:
            return None
        if isinstance(self.value, pd.DataFrame):
            return self.value.iloc[
                self.selection,
            ]
        if isinstance(self.value, ColumnDataSource):
            # I could not find a direct way to get a selected ColumnDataSource
            selected_data = self.value.to_df().iloc[
                self.selection,
            ]
            return ColumnDataSource(selected_data)
        raise ValueError("The value is not of a supported type!")

    @param.depends("selection", watch=True)
    def _update_source_selected_indices(self, *_):
        self._source.selected.indices = self.selection

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = super()._get_model(doc=doc, root=root, parent=parent, comm=comm)
        if root is None:
            root = model
        self._link_props(model.source.selected, ["indices"], doc, root, comm)
        return model

    def _process_events(self, events):
        if "indices" in events:
            self.selection = events.pop("indices")
        super()._process_events(events)


class TabulatorStylesheet(pn.pane.HTML):
    """The TabulatorStyleSheet provides methods to dynamically change the (css) style of the
    Tabulator widget"""

    theme = param.ObjectSelector(default="site", objects=sorted(list(CSS_HREFS.keys())))

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
        href = CSS_HREFS[self.theme]
        self.object = f'<link rel="stylesheet" href="{href}">'

    def __repr__(self, depth=0):  # pylint: disable=unused-argument
        return f"Tabulator({self.name})"

    def __str__(self):
        return f"Tabulator({self.name})"
