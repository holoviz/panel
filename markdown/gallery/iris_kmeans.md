# Iris Kmeans

```python
import numpy as np
import pandas as pd
import panel as pn
import panel_material_ui as pmui
import hvplot.pandas

from sklearn.cluster import KMeans
from bokeh.sampledata import iris

pn.extension()
```

This app provides an example of building a simple dashboard using Panel. It demonstrates how to take the output of  k-means clustering on the Iris dataset (performed using scikit-learn), parameterizing the number of clusters and the x and y variables to plot. The entire clustering and plotting pipeline is expressed as a single reactive function that returns a plot that responsively updates when one of the widgets changes.

```python
flowers = iris.flowers.copy()
cols = list(flowers.columns)[:-1]

x = pmui.Select(label='x', options=cols)
y = pmui.Select(label='y', options=cols, value='sepal_width')
n_clusters = pmui.IntSlider(label='n_clusters', start=1, end=5, value=3)

def get_clusters(x, y, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, n_init='auto')
    est = kmeans.fit(iris.flowers.iloc[:, :-1].values)
    flowers['labels'] = est.labels_.astype('str')
    centers = flowers.groupby('labels')[[x] if x == y else [x, y]].mean()
    return (
        flowers.sort_values('labels').hvplot.scatter(
            x, y, c='labels', size=100, height=500, responsive=True
        ) *
        centers.hvplot.scatter(
            x, y, marker='x', c='black', size=400, padding=0.1, line_width=5
        )
    )

widgets = pn.Column(
    """This app provides an example of **building a simple dashboard using Panel**.\n\nIt demonstrates how to take the output of **k-means clustering on the Iris dataset** using scikit-learn, parameterizing the number of clusters and the variables to plot.\n\nThe entire clustering and plotting pipeline is expressed as a **single reactive function** that responsively returns an updated plot when one of the widgets changes.\n\n The **`x` marks the center** of the cluster.""",
    x, y, n_clusters
)

plot = pn.pane.HoloViews(
    pn.bind(get_clusters, x, y, n_clusters), sizing_mode='stretch_width'
)

pn.Row(
    pn.WidgetBox(
        '# Iris K-Means Clustering',
        widgets, max_width=400
    ),
    plot
)
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        main=[plot],
        sidebar=[widgets],
        title='Iris K-Means Clustering'
    ).servable()
```
