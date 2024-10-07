import random

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

import panel as pn

pn.extension('perspective')

data = {
    'int': [random.randint(-10, 10) for _ in range(9)],
    'float': [random.uniform(-10, 10) for _ in range(9)],
    'date': [(datetime.now() + timedelta(days=i)).date() for i in range(9)],
    'datetime': [(datetime.now() + timedelta(hours=i)) for i in range(9)],
    'category': ['Category A', 'Category B', 'Category C', 'Category A', 'Category B',
             'Category C', 'Category A', 'Category B', 'Category C',],
    'link': ['https://panel.holoviz.org/', 'https://discourse.holoviz.org/', 'https://github.com/holoviz/panel']*3,
}
df = pd.DataFrame(data)

pn.pane.Perspective(df, width=1000).servable()
