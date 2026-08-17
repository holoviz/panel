# Xgboost Classifier

```python
import panel as pn
import panel_material_ui as pmui

from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

pn.extension(sizing_mode="stretch_width")
```

This example was adapted from an example by [Bojan Tunguz](https://twitter.com/tunguz). It demonstrates how to build a simple ML demo demonstrating how hyper-parameters affect the accuracy of the XGBoostClassifier.

```python
iris_df = load_iris(as_frame=True)

n_trees = pmui.IntSlider(start=2, end=30, label="Number of trees")
max_depth = pmui.IntSlider(start=1, end=10, value=2, label="Maximum Depth") 
booster = pmui.Select(options=['gbtree', 'gblinear', 'dart'], label="Booster")

def pipeline(n_trees, max_depth, booster):
    model = XGBClassifier(max_depth=max_depth, n_estimators=n_trees, booster=booster)
    model.fit(iris_df.data, iris_df.target)
    accuracy = round(accuracy_score(iris_df.target, model.predict(iris_df.data)) * 100, 1)
    return pn.indicators.Number(
        name=f"Test score",
        value=accuracy,
        format="{value}%",
        colors=[(97.5, "red"), (99.0, "orange"), (100, "green")],
        align='center'
    )

widgets = pn.Column(booster, n_trees, max_depth, width=320)

main = pn.Column(
    "Simple example of training an XGBoost classification model on the small Iris dataset.",
    iris_df.data.head(),
    
    "Adjust the hyperparameters to re-run the XGBoost classifier. The training accuracy score will adjust accordingly:",
    pn.bind(pipeline, n_trees, max_depth, booster),
    pn.bind(lambda n_trees, max_depth, booster: f'# {n_trees=}, {max_depth=}, {booster=}', n_trees, max_depth, booster),
)

pn.Row(widgets, main)
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        main=[main],
        sidebar=[widgets],
        title="XGBoost Example"
    ).servable()
```
