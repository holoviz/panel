# How to Create Reactive Tables with Panel

This guide will walk you through creating reactive tables using Panel's powerful reactive programming paradigm. You'll learn how to use Python methods, parameter dependencies, and caching to build interactive and efficient data visualizations.

## Introduction

Panel's reactive programming paradigm allows you to create dynamic applications that respond to user input. By leveraging Python methods, parameter dependencies, and caching, you can efficiently update views without unnecessary recomputation.

In this guide, we'll demonstrate how to create a reactive table viewer component. This component will allow users to select different datasets and control the number of rows displayed.

## Step-by-Step Guide

### Step 1: Import Required Libraries

First, import the necessary libraries:

```python
import param
import panel as pn
import pandas as pd
from panel.viewable import Viewer

pn.extension(template='fast')

DATASETS = {
    'Penguins': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv',
    'Diamonds': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv',
    'Titanic': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv',
    'MPG': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv'
}
```

### Step 2: Define the Viewer Class

Create a class `ReactiveTables` that inherits from `Viewer`. This class will manage the dataset selection and row display:

```python
class ReactiveTables(Viewer):
    dataset = param.Selector(objects=DATASETS)
    rows = param.Integer(default=10, bounds=(0, 19))

    @pn.cache(max_items=3)
    @param.depends("dataset")
    def data(self):
        # Each dataset will only be read once across all user session
        return pd.read_csv(self.dataset)

    @param.depends("data")
    def summary(self):
        return self.data().describe()

    @param.depends("data", "rows")
    def table(self):
        return self.data().iloc[: self.rows]

    def __panel__(self):
        return pn.Row(
            pn.Param(self, name="Settings", width=300),
            pn.Spacer(width=10),
            pn.Column(
                "## Description",
                pn.pane.DataFrame(self.summary, sizing_mode="stretch_width"),
                "## Table",
                pn.pane.DataFrame(self.table, sizing_mode="stretch_width"),
            ),
        )
```

### Step 3: Serve the Application

Finally, make the `ReactiveTables` class servable:

```python
ReactiveTables().servable()
```

## Conclusion

By following this guide, you've created a reactive table viewer using Panel. This application allows users to interactively select datasets and control the number of rows displayed, with efficient updates based on parameter changes.

Feel free to experiment with different datasets and parameters to further explore Panel's capabilities.

## Additional Notes

- The `max_items=3` argument in `@pn.cache` is an example. You can adjust this value or explore other supported arguments to suit your needs.
