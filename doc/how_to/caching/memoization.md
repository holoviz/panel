# Automatically Cache

This guide addresses how to use the `panel.cache` decorator to memoize (i.e., cache the output of) functions automatically.

---

The `pn.cache` decorator provides an easy way to cache the outputs of a function depending on its inputs and/ or Parameter dependencies (i.e., `memoization`).

If you've ever used the Python `@lru_cache` decorator, you will be familiar with this concept. However, the `pn.cache` functions support additional cache `policy`s apart from LRU (least-recently used), including `LFU` (least-frequently-used) and 'FIFO' (first-in-first-out). This means that if the specified number of `max_items` is reached, Panel will automatically evict items from the cache based on this `policy`. Additionally, items can be deleted from the cache based on a `ttl` (time-to-live) value given in seconds.

## Caching Functions

The `pn.cache` decorator can easily be combined with the different Panel APIs, including `pn.bind` and `pn.depends`, providing a powerful way to speed up your applications.

```python
@pn.cache(max_items=10, policy='LRU')
def load_data(path):
    return ... # Load some data
```

Once you have decorated your function with `pn.cache`, any call to `load_data` will be cached in memory until the `max_items` value is reached (i.e., you have loaded 10 different `path` values). At that point, the `policy` will determine which item is evicted.

The `pn.cache` decorator can easily be combined with `pn.bind` to speed up the rendering of your reactive components:

```{pyodide}
import pandas as pd
import panel as pn

pn.extension('tabulator')

DATASETS = {
    'Penguins': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv',
    'Diamonds': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv',
    'Titanic': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv',
    'MPG': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv'
}

select = pn.widgets.Select(options=DATASETS)

@pn.cache
def fetch_data(url):
    return pd.read_csv(url)

pn.Column(select, pn.bind(pn.widgets.Tabulator, pn.bind(fetch_data, select), page_size=10))
```

## Caching Functions with Dependencies

The `pn.cache` decorator can easily be combined with `pn.depends` to speed up the rendering of your reactive components:

```{pyodide}
select = pn.widgets.Select(options=DATASETS)

@pn.cache
@pn.depends(select)
def fetch_data(url):
    return pd.read_csv(url)

pn.Column(select, pn.widgets.Tabulator(fetch_data, page_size=10))
```

## Caching Methods with Dependencies

```{pyodide}
import param

class DataExplorer(pn.viewable.Viewer):
    dataset = param.Selector(objects=DATASETS)

    @pn.cache
    @param.depends("dataset")
    def fetch_data(self):
        return pd.read_csv(self.dataset)

    def __panel__(self):
        return pn.Column(self.param.dataset, pn.widgets.Tabulator(self.fetch_data, page_size=10))

DataExplorer().servable()
```

## Disk Caching

Disk backed caching persists cached results across server restarts, making it ideal for expensive operations like data loading or model inference.

### Prerequisites

First, install the [`diskcache`](https://grantjenks.com/docs/diskcache/) library:

```bash
pip install diskcache
```

### Basic Disk Caching

To enable disk caching, set `to_disk=True` when decorating your function:

```{pyodide}
import panel as pn
import time
from datetime import datetime

@pn.cache(to_disk=True)
def expensive_computation(n):
    # Simulate expensive operation
    time.sleep(2)
    return datetime.now()

# First call takes 2 seconds
result1 = expensive_computation(5)

# Subsequent calls are instant, even after server restart
result2 = expensive_computation(5)

pn.Column(result1, result2).servable()
```

By default, cached values are stored in a `./cache` directory relative to your application.

### Configuring the Cache Path

You can customize where cached values are stored in three ways:

**1. Inline configuration:**

```python
@pn.cache(to_disk=True, cache_path='./cache1')
def expensive_computation(n):
    ...
```

**2. Global configuration with `pn.extension`:**

```python
pn.extension(cache_path='./cache2')
```

**3. Direct configuration:**

```python
pn.config.cache_path = './cache3'
```

## Clearing the Cache

Once a function has been decorated with `pn.cache`, you can easily clear the cache by calling `.clear()` on that function, e.g., in the example above, you could call `load_data.clear()`. If you want to clear all caches, you may also call `pn.state.clear_caches()`.

## Per-session Caching

By default, any functions decorated or wrapped with `pn.cache` will use a global cache that will be reused across multiple sessions, i.e., multiple users visiting your app will all share the same cache. If instead, you want a session-local cache that only reuses cached outputs for the duration of each visit to your application, you can set `pn.cache(..., per_session=True)`.

## Related Resources

- [Manually Cache](./manual.md)
