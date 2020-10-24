"""This file contains examples testing the Tabulator"""
import pathlib

import pandas as pd
import panel as pn
import param
from bokeh.models import ColumnDataSource

from awesome_panel_extensions.widgets.tabulator import Tabulator

TABULATOR_DATA_PATH = pathlib.Path(__file__).parent / "tabulator_data.csv"


def _dataframe():
    df = pd.read_csv(TABULATOR_DATA_PATH)
    df = df.fillna("nan")
    return df


def _data_records():
    df = _dataframe()
    return df.to_dict(orient="records")


def _column_data_source():
    return ColumnDataSource(_dataframe())


def _configuration_basic():
    return {
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
            {"title": "Name", "field": "name",},
            {
                "title": "Task Progress",
                "field": "progress",
                "hozAlign": "left",
                "formatter": "progress",
            },
            {"title": "Gender", "field": "gender", "width": 95,},
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
            {"title": "Index", "field": "index", "width": 90, "hozAlign": "right",},
        ],
    }


def _configuration():
    return {
        "layout": "fitColumns",
        "responsiveLayout": "hide",
        "tooltips": True,
        "addRowPos": "top",
        "history": True,
        "pagination": "local",
        "paginationSize": 7,
        "movableColumns": True,
        "resizableRows": True,
        "initialSort": [{"column": "name", "dir": "asc"},],
        "columns": [
            {"title": "Name", "field": "name", "editor": "input",},
            {
                "title": "Task Progress",
                "field": "progress",
                "hozAlign": "left",
                "formatter": "progress",
                "editor": True,
            },
            {
                "title": "Gender",
                "field": "gender",
                "width": 95,
                "editor": "select",
                "editorParams": {"values": ["male", "female"]},
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
                "editor": True,
            },
        ],
    }
