# View Application Logs

The Logs page provides a detailed breakdown of the user interaction with the application. Additionally users may also log to this logger using the `pn.state.log` function, e.g. in this example we log the arguments to the clustering function:

```python
def get_clusters(x, y, n_clusters):
    pn.state.log(f'clustering {x!r} vs {y!r} into {n_clusters} clusters.')
    ...
    return ...
```

<img src="../../_static/admin_logs.png" width="80%"></img>
