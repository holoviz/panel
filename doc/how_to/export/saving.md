# Save App to File

This guide addresses how to export an app to a HTML or PNG file.

---

In case you don't need an actual server or simply want to export a static snapshot of a panel app, you can use the ``save`` method, which allows exporting the app to a standalone HTML or PNG file.

By default, the HTML file generated will depend on loading JavaScript code for BokehJS from the online ``CDN`` repository, to reduce the file size. If you need to work in an air-gapped or no-network environment, you can declare that ``INLINE`` resources should be used instead of ``CDN``:

```python
from bokeh.resources import INLINE
panel.save('test.html', resources=INLINE)
```

Additionally the save method also allows enabling the `embed` option, which, as explained above, will embed the apps state in the app or save the state to json files which you can ship alongside the exported HTML.

Finally, if a 'png' file extension is specified, the exported plot will be rendered as a PNG, which currently requires Selenium and PhantomJS to be installed:

```python
pane.save('test.png')
```

## Customize the favicon

For standalone HTML exported from a regular layout such as `pn.Row` or `pn.Column`, set the `app_favicon` template variable. This also works with `embed=True`, without using a Panel template or editing the generated HTML:

```python
import panel as pn

layout = pn.Column("# My report")
layout.save(
    "report.html",
    title="My report",
    embed=True,
    template_variables={"app_favicon": "favicon.ico"},
)
```

The value can be a URL or a data URI. Relative URLs are resolved relative to the exported HTML, so place `favicon.ico` alongside `report.html`. Panel does not read or copy the icon file when it is passed through `template_variables`.

To embed the favicon itself, encode a local icon as a data URI. `INLINE` resources bundle JavaScript and stylesheets, but do not automatically embed an icon referenced by a URL:

```python
import base64
from pathlib import Path

from bokeh.resources import INLINE

favicon = base64.b64encode(Path("favicon.ico").read_bytes()).decode("ascii")
layout.save(
    "report.html",
    title="My report",
    embed=True,
    resources=INLINE,
    template_variables={"app_favicon": f"data:image/x-icon;base64,{favicon}"},
)
```

Use the MIME type matching the icon file, such as `image/png` for a PNG icon. These examples use the default HTML export template; a custom Jinja2 `template` must render `app_favicon` itself.

## Related Resources
