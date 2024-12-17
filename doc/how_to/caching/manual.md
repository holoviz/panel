# Manually Cache

This guide addresses how to cache data and objects globally across user sessions - `pn.state.cache`.

---

The `panel.state.cache` object is a simple dictionary that is shared between all sessions on a particular Panel server process. This makes it possible to load large datasets (or other objects you want to share) once and subsequently access the cached object.

To assign to the cache manually, simply put the data load or expensive calculation in an `if`/`else` block which checks whether the custom key is already present:

```python
if 'data' in pn.state.cache:
    data = pn.state.cache['data']
else:
    pn.state.cache['data'] = data = ... # Load some data or perform an expensive computation
```

Alternatively, the `as_cached` helper function provides a slightly cleaner way to write the caching logic. Instead of writing a conditional statement you write a function that is executed only when the inputs to the function change. If provided, the `args` and `kwargs` will also be hashed making it easy to cache (or memoize) on the arguments to the function:

```python
def load_data(*args, **kwargs):
    return ... # Load some data

data = pn.state.as_cached('data', load_data, *args, **kwargs)
```

Now, the first time the app is loaded the data will be cached and subsequent sessions will simply look up the data in the cache, speeding up the process of rendering. If you want to warm up the cache before the first user visits the application you can also provide the `--warm` argument to the `panel serve` command, which will ensure the application is initialized as soon as it is launched. If you want to populate the cache in a separate script from your main application you may also provide the path to a setup script using the `--setup` argument to `panel serve`.

## Related Resources
- If you want to periodically update the cache, consult the [How to > Schedule Tasks](../callbacks/schedule) guide.
