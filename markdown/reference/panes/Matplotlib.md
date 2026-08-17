# Matplotlib
---
```python
import panel as pn

pn.extension('ipywidgets')
```

The `Matplotlib` pane allows displaying [Matplotlib](http://matplotlib.org) figures inside a Panel app. This includes figures created by [Seaborn](https://seaborn.pydata.org/), [Pandas `.plot`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html), [Plotnine](https://plotnine.readthedocs.io/) and any other plotting library building on top of `Matplotlib`.

The `Matplotlib` pane will render the `object` to PNG or SVG at the declared DPI and then display it.

#### Parameters:

* **``alt_text``** (str, default=None): alt text to add to the image tag. The alt text is shown when a user cannot load or display the image.
* **``dpi``** (int, default=144): The dots per inch of the exported png.
* **``encode``** (bool, default=False): Whether to encode 'svg' as base64. Default is False. 'png' will always be encoded.
* **``fixed_aspect``** (boolean, default=True): Whether the aspect ratio of the figure should be forced to be equal.
* **``format``** (str, default='png'): The format to render the figure to: 'png' or 'svg'.
* **``high_dpi``** (bool, default=True): Whether to optimize output for high-dpi displays.
* **``interactive``** (boolean, default=False): Whether to use the interactive ipympl backend.
* **``link_url``** (str, default=None): A link URL to make the figure clickable and link to some other website.
* **``object``** (matplotlib.Figure): The Matplotlib `Figure` object to display.
* **``tight``** (bool, default=False): Automatically adjust the figure size to fit the subplots and other artist elements.

#### Resources

- [How to - Style Matplotlib Plots](../../how_to/styling/matplotlib)
___

```python
import numpy as np

from matplotlib.figure import Figure
from matplotlib import cm

Y, X = np.mgrid[-3:3:100j, -3:3:100j]
U = -1 - X**2 + Y
V = 1 + X - Y**2

fig = Figure(figsize=(4, 3))
ax = fig.subplots()

strm = ax.streamplot(X, Y, U, V, color=U, linewidth=2, cmap=cm.autumn)
fig.colorbar(strm.lines)

mpl_pane = pn.pane.Matplotlib(fig, dpi=144)
mpl_pane
```

By modifying the figure and using the ``trigger`` method on the pane's object we can easily update the plot:

```python
strm.lines.set_cmap(cm.viridis)

mpl_pane.param.trigger('object')
```

Alternatively, like all other models, a ``Matplotlib`` pane can be updated by setting the ``object`` directly:

```python
from mpl_toolkits.mplot3d import axes3d

fig3d = Figure(figsize=(8, 6))
ax = fig3d.add_subplot(111, projection='3d')

X, Y, Z = axes3d.get_test_data(0.05)
ax.plot_surface(X, Y, Z, rstride=8, cstride=8, alpha=0.3)
cset = ax.contourf(X, Y, Z, zdir='z', offset=-100, cmap=cm.coolwarm)
cset = ax.contourf(X, Y, Z, zdir='x', offset=-40, cmap=cm.coolwarm)
cset = ax.contourf(X, Y, Z, zdir='y', offset=40, cmap=cm.coolwarm)

ax.set_xlabel('X')
ax.set_xlim(-40, 40)
ax.set_ylabel('Y')
ax.set_ylim(-40, 40)
ax.set_zlabel('Z')
ax.set_zlim(-100, 100)

mpl_pane.object = fig3d
```

### Using the Matplotlib pyplot interface

You might have noticed that we did not use the ``matplotlib.pyplot`` API above. We did this in order to avoid having to specifically close the figure. If the figure is not closed, it will cause memory leaks.

**You can use the `matplotlib.pyplot` interface, but then you must specifically close the figure as shown below!**

```python
import matplotlib.pyplot as plt
import numpy as np

def create_voltage_figure(figsize=(4,3)):
       t = np.arange(0.0, 2.0, 0.01)
       s = 1 + np.sin(2 * np.pi * t)

       fig, ax = plt.subplots(figsize=figsize)
       ax.plot(t, s)

       ax.set(xlabel='time (s)', ylabel='voltage (mV)',
              title='Voltage')
       ax.grid()

       plt.close(fig) # CLOSE THE FIGURE!
       return fig

pn.pane.Matplotlib(create_voltage_figure(), dpi=144, tight=True)
```

### Fixing clipping issues with `tight=True`

If you find the figure to be clipped on the edges you can set `tight=True`.

```python
pn.FlexBox(
    pn.Column("## ❌ `tight=False`", pn.pane.Matplotlib(create_voltage_figure(), dpi=144, tight=False)),
    pn.Column("## ✔️ `tight=True`", pn.pane.Matplotlib(create_voltage_figure(), dpi=144, tight=True)),
)
```

### Responsive plots

If you want to make your plots responsively fit what ever container they are inside, then you should be using the appropriate `sizing_mode` in combination with

- `format="svg"`: to get better looking resized plots,
- `fixed_aspect=True`: to allow the 'svg' image to resize its height and width independently and/ or
- `fixed_aspect=False` (default): to allow the 'svg' image to resize its height and width while keeping the aspect ratio.

Lets start by displaying using the default `'png'` format and `sizing_mode="stretch_width"`.

```python
fig = create_voltage_figure(figsize=(6,1))

pn.pane.Matplotlib(fig, tight=True, sizing_mode="stretch_width", styles={"background": "pink"})
```

If you have a wide window you will see some large, pink areas on the sides. If you decrease the window width, then you will see the plot responsively resize.

Using the `'svg'` format you can make the figure take up the full width.

```python
pn.pane.Matplotlib(fig, tight=True, format="svg", sizing_mode="stretch_width")
```

But that might make the figure too high. Lets try with a fixed `height`

```python
pn.pane.Matplotlib(fig, tight=True, height=150, format="svg", sizing_mode="stretch_width", styles={"background": "pink"})
```

But maybe we want the figure to take up the full width. Lets change the `fixed_aspect` to `False`.

```python
pn.pane.Matplotlib(fig, tight=True, height=150, format="svg", fixed_aspect=False, sizing_mode="stretch_width")
```

In summary you should be able to achieve the kind of responsive sizing you need by using the appropriate combination of `format`, `fixed_aspect` and `sizing_mode` values.

### Using the interactive Matplotlib backend

If you have installed `ipympl` you will also be able to use the `interactive` backend:

```python
fig = Figure(figsize=(8, 6))
ax = fig.add_subplot(111)

dx, dy = 0.05, 0.05

# generate 2 2d grids for the x & y bounds
y, x = np.mgrid[slice(1, 5 + dy, dy),
                slice(1, 5 + dx, dx)]

z = np.sin(x)**10 + np.cos(10 + y*x) * np.cos(x)

cf = ax.contourf(x + dx/2., y + dy/2., z)
fig.colorbar(cf, ax=ax)

pn.pane.Matplotlib(fig, interactive=True)
```

### Using Seaborn

```python
import pandas as pd
import seaborn as sns

from matplotlib.figure import Figure

sns.set_theme()
```

We recommend creating a Matplotlib `Figure` and providing it to Seaborn

```python
df = pd.DataFrame(np.random.rand(10, 10), columns=[chr(65+i) for i in range(10)], index=[chr(97+i) for i in range(10)])

fig = Figure(figsize=(2, 2))
ax = fig.add_subplot(111)
sns.heatmap(df, ax=ax)
pn.pane.Matplotlib(fig, tight=True)
```

You can also use Seaborn directly, but then you must remember to close the the `Figure` manually to avoid memory leaks.

```python
import matplotlib.pyplot as plt

dots = sns.load_dataset("dots")
fig = sns.relplot(
    data=dots, kind="line",
    x="time", y="firing_rate", col="align",
    hue="choice", size="coherence", style="choice",
    facet_kws=dict(sharex=False),
).fig
plt.close(fig) # REMEMBER TO CLOSE THE FIGURE!
pn.pane.Matplotlib(fig, height=300)
```

You can remove the Seaborn theme via `matplotlib.rcdefaults()`

```python
from matplotlib import rcdefaults

rcdefaults()
```

### Using Pandas `.plot`

We recommend creating a Matplotlib `Figure` and providing it to `pandas.plot`.

```python
import pandas as pd

from matplotlib.figure import Figure

df = pd.DataFrame({'a': range(10)})
fig = Figure(figsize=(4, 2))
ax = fig.add_subplot(111)
ax = df.plot.barh(ax=ax)

pn.pane.Matplotlib(fig, tight=True)
```

### Using Plotnine

The `plotnine.ggplot.draw` method will return the Matplotlib `Figure` object.

Please note you must close the figure your self.

```python
fig = plot.draw()
matplotlib.pyplot.close(fig) # REMEMBER TO CLOSE THE FIGURE!
```

### Controls

The `Matplotlib` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(mpl_pane.controls(jslink=True), mpl_pane)
```

---
