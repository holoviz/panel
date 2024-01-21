# Serve Apps

In this section you will learn the basics of serving Panel apps:

- serve your app with a command like `panel serve app.py` or `panel serve app2.ipynb`.
- serve with *auto reload* by adding the flag `--autoreload`.
- stop your server with `CTRL+C`.

## Serve `.py` file

The simplest Panel `.py` file could look like this:

```python
import panel as pn

pn.extension()

pn.panel("Hello World").servable()
```

:::{admonition} Note
The code refers to

- `panel`: The Panel python package. Its a convention to import it as `pn`.
- `pn.extension()`: Loads javascript dependencies and configures Panel.
- `pn.panel(...)`: Creates a *displayable* Panel component.
- `.servable()`: Displays the component in a *server app*.
:::

Copy code into a file named `app.py`.

Save the file.

Run the Panel server with

```python
panel serve app.py --autoreload
```

It will look like

```bash
$ panel serve app.py --autoreload
2024-01-17 15:49:11,443 Starting Bokeh server version 3.3.2 (running on Tornado 6.3.3)
2024-01-17 15:49:11,444 User authentication hooks NOT provided (default user enabled)
2024-01-17 15:49:11,450 Bokeh app running at: http://localhost:5006/app
2024-01-17 15:49:11,450 Starting Bokeh server with process id: 47256
```

:::{admonition} Note
The command `panel serve app.py --autoreload` refers to:

- `panel`: the panel executable.
- `serve`: the command you want panel to run
- `app.py`: the file `app.py` you want to serve
- `--autoreload`: make the server restart after code changes. Use this for **development only**.
:::

In the output, you will find the line

```bash
Bokeh app running at: http://localhost:5006/app
```

That line shows the URL where your app is being served, in your local machine.


:::{admonition} Note
The `Bokeh server` is mentioned because Panel is built on top of [Bokeh](https://docs.bokeh.org).
:::

Open your browser at [http://localhost:5006/app](http://localhost:5006/app).

The application will look like.

![Panel serve single .py file](../../_static/images/panel-serve-py-app.png).

Now stop the server by pressing `CTRL+C` one or more times in the terminal.

## Serve an `.ipynb` notebook

Copy the 2 code cells below into a clean notebook named `app2.ipynb`.

```python
import panel as pn

pn.extension()
```

```python
pn.panel("Hello Notebook World").servable()
```

Run the cells in the notebook and save it as `app2.ipynb` if you have not already done it.

It should look like

![Panel Notebook App](../../_static/images/panel-serve-ipynb-notebook.png).

:::{admonition} Note
The code refers to

- `panel`: The Panel python package. Its a convention to import it as `pn`.
- `pn.extension()`: Loads javascript dependencies and configures Panel.
- `pn.panel(...)`: Creates a *displayable* Panel component.
- `.servable()`: Displays the component in a *server app*.
:::

Run the Panel server with

```bash
panel serve app2.ipynb --autoreload
```

It will look like

```bash
$ panel serve app2.ipynb --autoreload
2024-01-17 21:05:32,338 Starting Bokeh server version 3.3.3 (running on Tornado 6.4)
2024-01-17 21:05:32,339 User authentication hooks NOT provided (default user enabled)
2024-01-17 21:05:32,342 Bokeh app running at: http://localhost:5006/app2
2024-01-17 21:05:32,342 Starting Bokeh server with process id: 42008
```

:::{admonition} Note
The command `panel serve app2.ipynb --autoreload` refers to:

- `panel`: the panel executable.
- `serve`: the command you want panel to run
- `app2.ipynb`: the file `app2.ipynb` you want to serve
- `--autoreload`: make the server restart after code changes. Use this for **development only**.
:::

In the output, you will find the line

```bash
Bokeh app running at: http://localhost:5006/app2
```

That line shows the URL where your app is being served, in your local machine.

Open your browser at [http://localhost:5006/app2](http://localhost:5006/app2).

The application will look like.

![Panel serve single .ipynb file](../../_static/images/panel-serve-ipynb-app.png).

Now stop the server by pressing `CTRL+C` one or more times in the terminal.

## Recap

You can

- serve your app with a command like `panel serve app.py` or `panel serve app2.ipynb`.
- serve with *auto reload* by adding the flag `--autoreload`.
- stop your server with `CTRL+C`.

## Resources

### Tutorials

- [Serve Panel Apps (Intermediate)](../intermediate/panel_serve.md)

### How-to

- [Launch a server dynamically with `pn.serve` or `pn.show`](../how_to/server/programmatic.md)
- [Launch a server on the commandline](../how_to/server/commandline.md)
- [Serve multiple applications with `pn.serve`](../how_to/server/multiple.md)
- [Serve static files with `--static-dirs`](../how_to/server/static_files.md)
- [Write and serve apps in Markdown](../how_to/editor/markdown.md)