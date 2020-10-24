"""This module contains base functions and classes used to implement
'DataFrame' widgets like the PerspectiveViewer and Tabulator"""
from typing import Any, Dict, Union

import pandas as pd
import panel as pn
import param
from bokeh.models import ColumnDataSource
from panel.widgets.base import Widget


class DataFrameWithStreamAndPatchBaseWidget(Widget):
    """Base Class for the DataFrame based widgets like PerspectiveViewer, Tabulator etc widgets"""

    value = param.DataFrame(
        doc="""A pandas.DataFrame

        Please note when specifying a Pandas.Dataframe we currently have some narrow requirements
        """,
    )
    _source = param.ClassSelector(
        class_=ColumnDataSource,
        doc="""Used to transfer the `value` efficiently to frontend. \
        Should always be in sync with value""",
    )
    # pylint: disable=line-too-long
    # Need this because ColumnDataSource not provides streamed value only streamed events
    # https://discourse.bokeh.org/t/how-do-i-get-the-new-data-only-when-i-stream-via-a-columndatasource/6186/2
    # pylint: enable=line-too-long
    _source_stream = param.ClassSelector(
        class_=ColumnDataSource,
        doc="""Used to transfer a streamed (i.e appended) `value` efficiently to frontend.""",
    )
    # pylint: disable=line-too-long
    # Need this because ColumnDataSource not provides patched value only patched events
    # https://discourse.bokeh.org/t/how-do-i-get-the-new-data-only-when-i-stream-via-a-columndatasource/6186/2
    # pylint: enable=line-too-long
    _source_patch = param.ClassSelector(
        class_=ColumnDataSource,
        doc="""Used to transfer a patched (i.e updated) `value` efficiently to frontend.""",
    )
    _rename = {
        "value": None,
        "_source": "source",
        "_source_stream": "source_stream",
        "_source_patch": "source_patch",
    }

    def __init__(self, **params):
        super().__init__(**params)

        self._pause_cds_updates = False
        self._source_patch = ColumnDataSource({})
        self._source_stream = ColumnDataSource({})
        self._set_source()

    @param.depends("value", watch=True)
    def _set_source(self):
        if self._pause_cds_updates:
            return

        if isinstance(self.value, pd.DataFrame) and (
            not isinstance(self.value.index, pd.RangeIndex)
            or self.value.index.start != 0
            or self.value.index.step != 1
        ):
            raise ValueError(
                "Please provide a DataFrame with RangeIndex starting at 0 and with step 1"
            )

        if self._source is None:
            if self.value is None:
                self._source = ColumnDataSource({})
            else:
                self._source = ColumnDataSource(self.value)
        else:
            if self.value is None:
                self._source.data = {}
            else:
                self._source.data = self.value

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
        >>> widget = DataFrameWithStreamAndPatchBaseWidget(value=value)
        >>> stream_value = pd.Series({"x": 4, "y": "d"})
        >>> widget.stream(stream_value)
        >>> widget.value.to_dict("list")
        {'x': [1, 2, 4], 'y': ['a', 'b', 'd']}

        Example: Stream a Dataframe to a Dataframe

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> widget = DataFrameWithStreamAndPatchBaseWidget(value=value)
        >>> stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
        >>> widget.stream(stream_value)
        >>> widget.value.to_dict("list")
        {'x': [1, 2, 3, 4], 'y': ['a', 'b', 'c', 'd']}


        Example: Stream a Dictionary row to a DataFrame

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> widget = DataFrameWithStreamAndPatchBaseWidget(value=value)
        >>> stream_value = {"x": 4, "y": "d"}
        >>> widget.stream(stream_value)
        >>> widget.value.to_dict("list")
        {'x': [1, 2, 4], 'y': ['a', 'b', 'd']}

        Example: Stream a Dictionary of Columns to a Dataframe

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> widget = DataFrameWithStreamAndPatchBaseWidget(value=value)
        >>> stream_value = {"x": [3, 4], "y": ["c", "d"]}
        >>> widget.stream(stream_value)
        >>> widget.value.to_dict("list")
        {'x': [1, 2, 3, 4], 'y': ['a', 'b', 'c', 'd']}
        """

        if isinstance(self.value, pd.DataFrame):
            if isinstance(stream_value, pd.DataFrame):
                self._stream_dataframe(stream_value, reset_index)
            elif isinstance(stream_value, pd.Series):
                self._stream_series(stream_value)
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
            self._source_stream.data = stream_value
            self.param.trigger("value")
            self._pause_cds_updates = False

    def _stream_dataframe(self, stream_value, reset_index):
        value_index_start = self.value.index.max() + 1
        if reset_index:
            stream_value = stream_value.reset_index(drop=True)
            stream_value.index += value_index_start
        self._pause_cds_updates = True
        self._source.stream(stream_value)
        new_value = pd.concat([self.value, stream_value])
        value_index_end = new_value.index.max() + 1
        stream_value2 = (
            new_value.loc[value_index_start:value_index_end,].reset_index().to_dict("list")
        )
        self._source_stream.data = stream_value2
        self.value = new_value
        self._pause_cds_updates = False

    def _stream_series(self, stream_value):
        value_index_start = self.value.index.max() + 1
        self._pause_cds_updates = True
        self.value.loc[value_index_start] = stream_value
        self._source.stream(stream_value)
        stream_value2 = {k: [v] for k, v in stream_value.to_dict().items()}
        stream_value2["index"] = [value_index_start]
        self._source_stream.data = stream_value2
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
        >>> widget = DataFrameWithStreamAndPatchBaseWidget(value=value)
        >>> patch_value = {"x": [(0, 3)]}
        >>> widget.patch(patch_value)
        >>> widget.value.to_dict("list")
        {'x': [3, 2], 'y': ['a', 'b']}

        Example: Patch a Dataframe with a Dictionary of Columns.

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> widget = DataFrameWithStreamAndPatchBaseWidget(value=value)
        >>> patch_value = {"x": [(slice(2), (3,4))], "y": [(1,'d')]}
        >>> widget.patch(patch_value)
        >>> widget.value.to_dict("list")
        {'x': [3, 4], 'y': ['a', 'd']}

        Example: Patch a DataFrame with a Series. Please note the index is used in the update

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> widget = DataFrameWithStreamAndPatchBaseWidget(value=value)
        >>> patch_value = pd.Series({"index": 1, "x": 4, "y": "d"})
        >>> widget.patch(patch_value)
        >>> widget.value.to_dict("list")
        {'x': [1, 4], 'y': ['a', 'd']}

        Example: Patch a Dataframe with a Dataframe. Please note the index is used in the update.

        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> widget = DataFrameWithStreamAndPatchBaseWidget(value=value)
        >>> patch_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
        >>> widget.patch(patch_value)
        >>> widget.value.to_dict("list")
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
                self._cds_patch(patch_value)
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
        self._cds_patch(patch_value)
        self.param.trigger("value")
        self._pause_cds_updates = False

    def _cds_patch(self, patch_value):
        self._source.patch(patch_value)
        self._source_patch.data = patch_value

    @classmethod
    def config(cls):
        """Adds the required js files to pn.config.js_files"""
        for key, value in cls._widget_type.__js_require__["paths"].items():
            pn.config.js_files[key.replace("-", "")] = value + ".js"
