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

## Related Resources
