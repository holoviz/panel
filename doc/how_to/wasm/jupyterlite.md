# Setting up JupyterLite

[JupyterLite](https://jupyterlite.readthedocs.io/en/latest/) is a JupyterLab distribution built from all the usual components and extensions that come with JupyterLab, but now running entirely in the browser with no external server needed. In order to use Panel in JupyterLite you will have to build your own distribution. We call this [Panelite](https://panelite.holoviz.org). You can try out Panelite [here](https://panelite.holoviz.org).

As a starting point we recommend [this guide](https://jupyterlite.readthedocs.io/en/latest/howto/configure/simple_extensions.html) in the JupyterLite documentation, which will tell you how to set up an environment to begin building JupyterLite.

## Create a `<lite-dir>`

Once your environment is set up, create a new directory, which will become the source for your JupyterLite distribution. Once created place the file contents you want to make available in JupyterLite into `<lite-dir>/files`.

## Adding extensions

In order for Panel to set up communication channels inside JupyterLite we have to add the `pyviz_comms` extension to the environment. Ensure this package is installed in the environment you are building Panel from, e.g. by running `pip install pyviz_comms` OR by including it in the `requirements.txt` you used when setting up your build environment.

## Optimized wheels (optional)

To get Panel installed inside a Jupyterlite session we have to install it with `piplite`. The default Bokeh and Panel packages are quite large since they contain contents which are needed in a server environment. Since we will be running inside Jupyter these contents are not needed. To bundle the optimized packages download them from the CDN and place them in the `<lite-dir>/pypi` directory. You can download them from the CDN (replacing the latest version numbers):

```
https://cdn.holoviz.org/panel/{{PANEL_VERSION}}/dist/wheels/bokeh-{{BOKEH_VERSION}}-py3-none-any.whl
https://cdn.holoviz.org/panel/{{PANEL_VERSION}}/dist/wheels/panel-{{PANEL_VERSION}}-py3-none-any.whl
```

## Building Panelite

Finally `cd` into your `<lite-dir>` and run `jupyter lite build --output-dir ./dist`. This will bundle up the file contents, extensions and wheels into your JupyterLite distribution. You can now easily deploy this to [GitHub pages](https://jupyterlite.readthedocs.io/en/latest/quickstart/deploy.html) or elsewhere.
