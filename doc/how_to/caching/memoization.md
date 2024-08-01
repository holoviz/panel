# Automatically Cache

This guide addresses how to use the `panel.cache` decorator to memoize (i.e. cache the output of) functions automatically.

---

The `pn.cache` decorator provides an easy way to cache the outputs of a function depending on its inputs (i.e. `memoization`). If you've ever used the Python `@lru_cache` decorator you will be familiar with this concept. However the `pn.cache` functions support additional cache `policy`s apart from LRU (least-recently used), including `LFU` (least-frequently-used) and 'FIFO' (first-in-first-out). This means that if the specified number of `max_items` is reached Panel will automatically evict items from the cache based on this `policy`. Additionally items can be deleted from the cache based on a `ttl` (time-to-live) value given in seconds.

## Caching in memory

The `pn.cache` decorator can easily be combined with the different Panel APIs including `pn.bind` and `pn.depends` providing a powerful way to speed up your applications.

```python
@pn.cache(max_items=10, policy='LRU')
def load_data(path):
    return ... # Load some data
```

Once you have decorated your function with `pn.cache` any call to `load_data` will be cached in memory until `max_items` value is reached (i.e. you have loaded 10 different `path` values). At that point the `policy` will determine which item is evicted.

The `pn.cache` decorator can easily be combined with `pn.bind` to speed up rendering of your reactive components:

```{pyodide}
import pandas as pd
import panel as pn

pn.extension('tabulator')

select = pn.widgets.Select(options={
    'Penguins': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv',
    'Diamonds': 'https://raw.githucbusercontent.com/mwaskom/seaborn-data/master/diamonds.csv',
    'Titanic': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv',
    'MPG': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/mastser/mpg.csv'
})

@pn.cache
def fetch_data(url):
    return pd.read_csv(url)

pn.Column(select, pn.bind(pn.widgets.Tabulator, pn.bind(fetch_data, select), page_size=10))
```

## Disk caching

If you have `diskcache` installed you can also cache the results to disk by setting `to_disk=True`. The `diskcache` library will then cache the value to the supplied `cache_path` (defaulting to `./cache`). Making use of disk caching allows you to cache items even if the server is restarted.

## Clearing the cache

Once a function has been decorated with `pn.cache` you can easily clear the cache by calling `.clear()` on that function, e.g. in the example above you could call `load_data.clear()`. If you want to clear all caches you may also call `pn.state.clear_caches()`.

## Per-session caching

By default any functions decorated or wrapped with `pn.cache` will use a global cache that will be reused across multiple sessions, i.e. multiple users visiting your app will all share the same cache. If instead you want a session-local cache, that only reuses cached outputs for the duration of each visit to your application, you can set `pn.cache(..., per_session=True)`.

## Related Resources
