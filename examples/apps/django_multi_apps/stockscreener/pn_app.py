import os

import pandas as pd

import panel as pn

from .pn_model import StockScreener


def app(doc):
    data_path = os.path.join(os.path.dirname(__file__), 'datasets/market_data.csv')
    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    ss = StockScreener(df)
    ss.panel().server_doc(doc)
