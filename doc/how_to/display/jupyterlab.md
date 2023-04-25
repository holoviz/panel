# Preview Apps in JupyterLab

This guide addresses how to use the Preview functionality in JupyterLab to rapidly develop applications.

---

In the Jupyter environment, first make sure to load the ``pn.extension()``. Panel objects will then render themselves if they are the last item in a notebook cell.

```{pyodide}
import panel as pn
pn.extension()
```

```{pyodide}
button = pn.widgets.Button(name='Click me', button_type='primary')
button
```

::::{admonition} Note
For versions of ``jupyterlab>=3.0`` the necessary extension is automatically bundled in the ``pyviz_comms`` package, which must be >=2.0.

:::{dropdown} Using jupyterlab < 3.0 ?
For versions of ``jupyterlab<3.0`` you must also manually install the JupyterLab extension with:

```
jupyter labextension install @pyviz/jupyterlab_pyviz
```
:::
::::

## Related Resources
