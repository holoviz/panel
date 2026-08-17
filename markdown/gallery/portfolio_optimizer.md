# Portfolio Optimizer

```python
from io import BytesIO

import numpy as np
import pandas as pd
import holoviews as hv
import panel as pn
import panel_material_ui as pmui

from scipy.optimize import minimize

pn.extension('tabulator', loading_indicator=True)
import hvplot.pandas
```

## Load data

```python
@pn.cache
def get_stocks(data):
    if data is None:
        stock_file = 'https://datasets.holoviz.org/stocks/v1/stocks.csv'
    else:
        stock_file = BytesIO(data)
    return pd.read_csv(stock_file, index_col='Date', parse_dates=True)

file_input = pmui.FileInput(sizing_mode='stretch_width')

stocks = hvplot.bind(get_stocks, file_input).interactive()

selector = pmui.MultiSelect(
    label='Select stocks', sizing_mode='stretch_width',
    options=stocks.columns.to_list()
)

selected_stocks = stocks.pipe(
    lambda df, cols: df[cols] if cols else df, selector
)
```

## Business logic

```python
def compute_random_allocations(log_return, num_ports=15000):
    _, ncols = log_return.shape
    
    # Compute log and mean return
    mean_return = np.nanmean(log_return, axis=0)
    
    # Allocate normalized weights
    weights = np.random.random((num_ports, ncols))
    normed_weights = (weights.T / np.sum(weights, axis=1)).T
    data = dict(zip(log_return.columns, normed_weights.T))

    # Compute expected return and volatility of random portfolios
    data['Return'] = expected_return = np.sum((mean_return * normed_weights) * 252, axis=1)
    return_covariance = np.cov(log_return[1:], rowvar=False) * 252
    if not return_covariance.shape:
        return_covariance = np.array([[252.]])
    data['Volatility'] = volatility = np.sqrt((normed_weights * np.tensordot(return_covariance, normed_weights.T, axes=1).T).sum(axis=1))
    data['Sharpe'] = sharpe_ratio = expected_return/volatility
    
    df = pd.DataFrame(data)
    df.attrs['mean_return'] = mean_return
    df.attrs['log_return'] = log_return
    return df

def check_sum(weights):
    return np.sum(weights) - 1

def get_return(mean_ret, weights):
    return np.sum(mean_ret * weights) * 252

def get_volatility(log_ret, weights):
    return np.sqrt(np.dot(weights.T, np.dot(np.cov(log_ret[1:], rowvar=False) * 252, weights)))

def compute_frontier(df, n=30):
    frontier_ret = np.linspace(df.Return.min(), df.Return.max(), n)
    frontier_volatility = []

    cols = len(df.columns) - 3
    bounds = tuple((0, 1) for i in range(cols))
    init_guess = [1./cols for i in range(cols)]
    for possible_return in frontier_ret:
        cons = (
            {'type':'eq', 'fun': check_sum},
            {'type':'eq', 'fun': lambda w: get_return(df.attrs['mean_return'], w) - possible_return}
        )
        result = minimize(lambda w: get_volatility(df.attrs['log_return'], w), init_guess, bounds=bounds, constraints=cons)
        frontier_volatility.append(result['fun'])
    return pd.DataFrame({'Volatility': frontier_volatility, 'Return': frontier_ret})

def minimize_difference(weights, des_vol, des_ret, log_ret, mean_ret):
    ret = get_return(mean_ret, weights)
    vol = get_volatility(log_ret, weights)
    return abs(des_ret-ret) + abs(des_vol-vol)

@pn.cache
def find_best_allocation(log_return, vol, ret):
    cols = log_return.shape[1]
    vol = vol or 0
    ret = ret or 0
    mean_return = np.nanmean(log_return, axis=0)
    bounds = tuple((0, 1) for i in range(cols))
    init_guess = [1./cols for i in range(cols)]
    cons = (
        {'type':'eq','fun': check_sum},
        {'type':'eq','fun': lambda w: get_return(mean_return, w) - ret},
        {'type':'eq','fun': lambda w: get_volatility(log_return, w) - vol}
    )
    opt = minimize(
        minimize_difference, init_guess, args=(vol, ret, log_return, mean_return),
        bounds=bounds, constraints=cons
    )
    ret = get_return(mean_return, opt.x)
    vol = get_volatility(log_return, opt.x)
    return pd.Series(list(opt.x)+[ret, vol], index=list(log_return.columns)+['Return', 'Volatility'], name='Weight')
```

## Declare UI components

```python
n_samples = pmui.IntSlider(
    label='Random samples', value=10_000, start=1000, end=20_000, step=1000, sizing_mode='stretch_width'
)
button = pmui.Button(label='Run Analysis', sizing_mode='stretch_width')
posxy = hv.streams.Tap(x=None, y=None)

text = """
#  Portfolio optimization

This application performs portfolio optimization given a set of stock time series.

To optimize your portfolio:

1. Upload a CSV of the daily stock time series for the stocks you are considering
2. Select the stocks to be included.
3. Run the Analysis
4. Click on the Return/Volatility plot to select the desired risk/reward profile

Upload a CSV containing stock data:
"""

explanation = """
The code for this app was taken from [this excellent introduction to Python for Finance](https://github.com/PrateekKumarSingh/Python/tree/master/Python%20for%20Finance/Python-for-Finance-Repo-master).
To learn some of the background and theory about portfolio optimization see [this notebook](https://github.com/PrateekKumarSingh/Python/blob/master/Python%20for%20Finance/Python-for-Finance-Repo-master/09-Python-Finance-Fundamentals/02-Portfolio-Optimization.ipynb).
"""

sidebar = pn.Column(
    pn.pane.Markdown(text, margin=(0, 10)),
    file_input,
    selector,
    n_samples,
    explanation,
    max_width=350,
    sizing_mode='stretch_width'
)

sidebar
```

## Plot

### Portfolio optimization plot

```python
# Set up data pipelines
log_return = np.log(selected_stocks/selected_stocks.shift(1))
random_allocations = log_return.pipe(compute_random_allocations, n_samples)
closest_allocation = log_return.pipe(find_best_allocation, posxy.param.x, posxy.param.y)
efficient_frontier = random_allocations.pipe(compute_frontier)
max_sharpe = random_allocations.pipe(lambda df: df[df.Sharpe==df.Sharpe.max()])

# Generate plots
opts = {'x': 'Volatility', 'y': 'Return', 'responsive': True}

allocations_scatter = random_allocations.hvplot.scatter(
    alpha=0.1, color='Sharpe', cmap='plasma', **opts
).dmap().opts(tools=[])

frontier_curve = efficient_frontier.hvplot(
    line_dash='dashed', color='green', **opts
).dmap()

max_sharpe_point = max_sharpe.hvplot.scatter(
    line_color='black', size=50, **opts
).dmap()

closest_point = closest_allocation.to_frame().T.hvplot.scatter(color='green', line_color='black', size=50, **opts).dmap()

posxy.source = allocations_scatter

summary = pn.pane.Markdown(
    pn.bind(lambda p: f"""
    The selected portfolio has a volatility of {p.Volatility:.2f}, a return of {p.Return:.2f}
    and Sharpe ratio of {p.Return/p.Volatility:.2f}.""", closest_allocation), width=250
)

table = pn.widgets.Tabulator(closest_allocation.to_frame().iloc[:-2])

plot = (allocations_scatter * frontier_curve * max_sharpe_point * closest_point).opts(min_height=400, show_grid=True)

pn.Row(plot, pn.Column(summary, table), sizing_mode='stretch_both')
```

### Portfolio Performance plot

```python
investment = pmui.IntInput(label='Investment Value in $', value=5000, step=1000, start=1000, end=100000)
year = pmui.DateRangeSlider(label='Year', value=(stocks.index.min().eval(), stocks.index.max().eval()), start=stocks.index.min(), end=stocks.index.max())

stocks_between_dates = selected_stocks[year.param.value_start:year.param.value_end]
price_on_start_date = selected_stocks[year.param.value_start:].iloc[0]
allocation = (closest_allocation.iloc[:-2] * investment)

performance_plot = (stocks_between_dates * allocation / price_on_start_date).sum(axis=1).rename().hvplot.line(
    ylabel='Total Value ($)', title='Portfolio performance', responsive=True, min_height=400
).dmap()

performance = pn.Column(
    pn.Row(year, investment),
    performance_plot,
    sizing_mode='stretch_both'
)

performance
```

### Plot stock prices

```python
timeseries = selected_stocks.hvplot.line(
    'Date', group_label='Stock', value_label='Stock Price ($)', title='Daily Stock Price',
    min_height=300, responsive=True, grid=True, legend='top_left'
).dmap()

timeseries
```

### Log return plots

```python
log_ret_hists = log_return.hvplot.hist(min_height=300, min_width=400, responsive=True, bins=100, subplots=True, group_label='Stock').cols(2).opts(sizing_mode='stretch_both').panel()

log_ret_hists
```

### Overall layout

```python
main = pmui.Tabs(
    ('Analysis', pn.Column(
            pn.Row(
                plot, pn.Column(summary, table),
                sizing_mode='stretch_both'
            ),
            performance,
            sizing_mode='stretch_both'
        )
    ),
    ('Timeseries', timeseries),
    ('Log Return', pn.Column(
        '## Daily normalized log returns',
        'Width of distribution indicates volatility and center of distribution the mean daily return.',
        log_ret_hists,
        sizing_mode='stretch_both'
    )),
    sizing_mode='stretch_both', min_height=1000
)

pn.Row(sidebar, main)
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        main=[main],
        sidebar=[sidebar],
        title='Portfolio Optimizer'
    ).servable()
```
