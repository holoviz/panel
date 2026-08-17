# panel.models.vtk module

Defines custom VTKPlot bokeh model to render VTK objects.

class panel.models.vtk.AbstractVTKPlot(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `HTMLBox`

>
>
> Abstract Bokeh model for vtk plots that wraps around a vtk-js library
> and renders it inside a Bokeh plot.
>
>

Note

This is an abstract base class used to help organize the hierarchy of
Bokeh model types. **It is not useful to instantiate on its own.**

Attributes:
**annotations**

**axes**

**camera**

**color_mappers**

**interactive_orientation_widget**

**orientation_widget**

class panel.models.vtk.VTKAxes(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Model`

A Bokeh model for axes

Attributes:
**axes_opacity**

**digits**

**fontsize**

**grid_opacity**

**origin**

**show_grid**

**xticker**

**yticker**

**zticker**

class panel.models.vtk.VTKJSPlot(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases:
[AbstractVTKPlot](#panel.models.vtk.AbstractVTKPlot)

Bokeh model for plotting a 3D scene saved in the .vtk-js format

Attributes:
**data**
The serialized vtk.js data

**data_url**
The data URL

**enable_keybindings**

data
The serialized vtk.js data

data_url
The data URL

class panel.models.vtk.VTKSynchronizedPlot(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases:
[AbstractVTKPlot](#panel.models.vtk.AbstractVTKPlot)

Bokeh model for plotting a VTK render window

Attributes:
**arrays**

**arrays_processed**

**enable_keybindings**

**one_time_reset**

**rebuild**
If true when scene change all the render is rebuilt from scratch

**scene**
The serialized vtk.js scene on json format

rebuild
If true when scene change all the render is rebuilt from scratch

scene
The serialized vtk.js scene on json format

class panel.models.vtk.VTKVolumePlot(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases:
[AbstractVTKPlot](#panel.models.vtk.AbstractVTKPlot)

Bokeh model dedicated to plot a volumetric object with the help of
vtk-js

Attributes:
**ambient**

**colormap**
Colormap Name

**controller_expanded**
If True the volume controller panel options is expanded in the view

**data**

**diffuse**

**display_slices**

**display_volume**

**edge_gradient**

**interpolation**

**mapper**

**nan_opacity**

**render_background**

**rescale**

**sampling**

**shadow**

**slice_i**

**slice_j**

**slice_k**

**specular**

**specular_power**

colormap
Colormap Name

controller_expanded
If True the volume controller panel options is expanded in the view

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
