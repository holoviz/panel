# Penguin Kmeans

```python
import altair as alt
import panel as pn
import panel_material_ui as pmui
import pandas as pd

from sklearn.cluster import KMeans

pn.extension('tabulator', 'vega')
```

## Load data

```python
penguins = pn.cache(pd.read_csv)('https://datasets.holoviz.org/penguins/v1/penguins.csv').dropna()
cols = list(penguins.columns)[2:6]
```

## Define application

```python
@pn.cache
def get_clusters(n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, n_init='auto')
    est = kmeans.fit(penguins[cols].values)
    df = penguins.copy()
    df['labels'] = est.labels_.astype('str')
    return df

@pn.cache
def get_chart(x, y, df):
    centers = df.groupby('labels')[[x] if x == y else [x, y]].mean()
    return (
        alt.Chart(df)
            .mark_point(size=100)
            .encode(
                x=alt.X(x, scale=alt.Scale(zero=False)),
                y=alt.Y(y, scale=alt.Scale(zero=False)),
                shape='labels',
                color='species'
            ).add_params(brush) +
        alt.Chart(centers)
            .mark_point(size=250, shape='cross', color='black')
            .encode(x=x+':Q', y=y+':Q')
    ).properties(width='container', height='container')

intro = pn.pane.Markdown("""
This app provides an example of **building a simple dashboard using
Panel**.\n\nIt demonstrates how to take the output of **k-means
clustering on the Penguins dataset** using scikit-learn,
parameterizing the number of clusters and the variables to
plot.\n\nThe plot and the table are linked, i.e. selecting on the plot
will filter the data in the table.\n\n The **`x` marks the center** of
the cluster.
""", sizing_mode='stretch_width')

x = pmui.Select(label='x', options=cols, value='bill_depth_mm')
y = pmui.Select(label='y', options=cols, value='bill_length_mm')
n_clusters = pmui.IntSlider(label='n_clusters', start=1, end=5, value=3)

brush = alt.selection_interval(name='brush')  # selection of type "interval"

clusters = pn.bind(get_clusters, n_clusters)

chart = pn.pane.Vega(
    pn.bind(get_chart, x, y, clusters), min_height=400, max_height=800, sizing_mode='stretch_width'
)

table = pn.widgets.Tabulator(
    clusters,
    pagination='remote', page_size=10, height=600,
    sizing_mode='stretch_width'
)

def vega_filter(filters, df):
    filtered = df
    for field, drange in (filters or {}).items():
        filtered = filtered[filtered[field].between(*drange)]
    return filtered

table.add_filter(pn.bind(vega_filter, chart.selection.param.brush))
```

## Layout app

```python
pn.Row(
    pn.Column(x, y, n_clusters),
    pn.Column(
        intro, chart, table,
    ),
    sizing_mode='stretch_both',
    min_height=1000
)
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        main=[intro, chart, table],
        sidebar=[x, y, n_clusters],
        title="KMeans Clustering"
    ).servable()
```
