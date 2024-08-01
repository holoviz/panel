# Toggling themes

This guide addresses how to toggle between different themes in Panel.

---

The `theme` of a Panel app primarily determines the color scheme of our application. By default there are 'default' (i.e. light) and 'dark' themes defined in Panel and we can toggle between them by setting the `config` option:

```{pyodide}
import panel as pn

pn.config.theme = 'dark'
```

:::{tip}
All `config` options can also be set via the extension, e.g. to set the theme use `pn.extension(theme='dark')`.
:::

Note that if you do not explicitly override the theme it will default to a light theme. The theme can also be overridden with by setting `theme` as a URL query parameter for your application, i.e. if your app is hosted at `https://mydomain.com/myapp` adding `?theme=dark` will switch the theme automatically.

The theme will apply to all components and combines with the [design](design.md) to provide a consistent visual language.

:::{note}
In JupyterLab and when using the pydata-sphinx-theme Panel components will automatically adapt to the global CSS variables, regardless of what theme you set.
:::
