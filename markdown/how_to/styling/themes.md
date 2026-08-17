# Toggling themes

This guide addresses how to toggle between different themes in Panel.

---

The `theme` of a Panel app primarily determines the color scheme of our application. By default there are 'default' (i.e. light) and 'dark' themes defined in Panel and we can toggle between them by setting the `config` option:

```python
import panel as pn

pn.config.theme = 'dark'
```

Note that if you do not explicitly override the theme it will default to a light theme. The theme can also be overridden with by setting `theme` as a URL query parameter for your application, i.e. if your app is hosted at `https://mydomain.com/myapp` adding `?theme=dark` will switch the theme automatically.

The theme will apply to all components and combines with the `design` to provide a consistent visual language.
