# VTK
---
```python
import panel as pn
pn.extension('vtk')
```

The ``VTK`` pane renders a VTK scene inside a panel, making it possible to interact with complex geometries in 3D.
It allows keeping state synchronized between the ``vtkRenderWindow`` defined on the python side and the one displayed in the pane through vtk-js.
Here Python acts as a server, sending information about the scene to the client.
The synchronization is done in only one direction: Python => JavaScript. Modifications done on the JavaScript side are not reflected back to the Python ``vtkRenderWindow``.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``axes``** (dict): A dictionary with the parameters of the axes to construct in the 3d view.
    Must contain at least ``xticker``, ``yticker`` and ``zticker``.
    - ``[x|y|z]ticker`` is a dictionary which contains:
        - ``ticks`` (array of numbers) - required. Positions in the scene coordinates
        of the corresponding axe ticks
        - ``labels`` (array of strings) - optional. Label displayed respectively to
        the `ticks` positions.

        If `labels` are not defined they are inferred from the `ticks` array.
    - ``digits``: number of decimal digits when `ticks` are converted to `labels`.
    - ``fontsize``: size in pts of the ticks labels.
    - ``show_grid``: boolean. If true (default) the axes grid is visible.
    - ``grid_opacity``: float between 0-1. Defines the grid opacity.
    - ``axes_opacity``: float between 0-1. Defines the axes lines opacity.
* **``camera``** (dict): A dictionary reflecting the current state of the VTK camera
* **``enable_keybindings``** (bool): A boolean to activate/deactivate keybindings. Bound keys are:
  - s: set representation of all actors to *surface*
  - w: set representation of all actors to *wireframe*
  - v: set representation of all actors to *vertex*
  - r: center the actors and move the camera so that all actors are visible

  The mouse must be over the pane to work
  <br>**Warning**: These keybindings may not work as expected in a notebook context, if they interact with already bound keys
* **``orientation_widget``** (bool): A boolean to activate/deactivate the orientation widget in the 3D pane.
* **``ìnteractive_orientation_widget``** (bool): If True the orientation widget is clickable and allows to rotate the scene in one of the orthographic projections.
  <br>**Warning**: if set to True, synchronization capabilities of `VTKRenderWindowSynchronized` panes could not work.
* **``object``** (object): Must be a ``vtkRenderWindow`` instance.

#### Properties:

* **``actors``** : return the list of the vtkActors in the scene

* **``vtk_camera``** :  return the vtkCamera of the renderer held by the panel

#### Methods:

Several helpers to work with the VTK scene are exposed:

* **``set_background(r: float, g: float, b: float)``** : Set the color of the scene background as an RGB color, where `r`, `g`, and `b` are floats in the range (0, 1)

* **``synchronize()``** : Synchronize the Python-side ``vtkRenderWindow`` object state with JavaScript

* **``unlink_camera()``** : Create a new vtkCamera object, allowing the panel to have its own camera.

* **``link_camera(other: VTK)``** : Set both panels to share the same camera; any change in either panel's camera will be applied to the other

**Warning** after using any of these methods to modify the state of vtkRenderWindow, the `synchronize()` method must be called for those changes to affect the display
___

## Rendering VTK objects

Compared to working with ``VTK`` directly, there are some differences when using it in Panel. As rendering of the objects and interactions with the view are handled by the VTK panel, we do not need to make a call to the `Render` method of the `vtkRenderWindow` (which would pop up the classical VTK window), nor do we need to specify a `vtkRenderWindowInteractor`.

```python
import vtk
from vtk.util.colors import tomato

# This creates a polygonal cylinder model with eight circumferential
# facets.
cylinder = vtk.vtkCylinderSource()
cylinder.SetResolution(8)

# The mapper is responsible for pushing the geometry into the graphics
# library. It may also do color mapping, if scalars or other
# attributes are defined.
cylinderMapper = vtk.vtkPolyDataMapper()
cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

# The actor is a grouping mechanism: besides the geometry (mapper), it
# also has a property, transformation matrix, and/or texture map.
# Here we set its color and rotate it -22.5 degrees.
cylinderActor = vtk.vtkActor()
cylinderActor.SetMapper(cylinderMapper)
cylinderActor.GetProperty().SetColor(tomato)
# We must set ScalarVisibilty to 0 to use tomato Color
cylinderMapper.SetScalarVisibility(0)
cylinderActor.RotateX(30.0)
cylinderActor.RotateY(-45.0)

# Create the graphics structure. The renderer renders into the render
# window.
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# Add the actors to the renderer, set the background and size
ren.AddActor(cylinderActor)
ren.SetBackground(0.1, 0.2, 0.4)

geom_pane = pn.pane.VTK(renWin, width=500, height=500)

geom_pane
```

We can also add additional actors to the plot, then call the `synchronize` method to update the panel:

```python
sphere = vtk.vtkSphereSource()

sphereMapper = vtk.vtkPolyDataMapper()
sphereMapper.SetInputConnection(sphere.GetOutputPort())

sphereActor = vtk.vtkActor()
sphereActor.SetMapper(sphereMapper)
sphereActor.GetProperty().SetColor(tomato)
sphereMapper.SetScalarVisibility(0)
sphereActor.SetPosition(0.5, 0.5, 0.5)

ren.AddActor(sphereActor)
geom_pane.reset_camera()
geom_pane.synchronize()
```

### Working with `PyVista`

Most of these examples use the [PyVista](https://docs.pyvista.org/) library as a convenient interface to VTK.

Though these examples can generally be rewritten to depend only on VTK itself, `pyvista` supports a Pythonic and concise syntax for the main features needed to work with VTK objects.

For instance, the VTK example above can be rewritten using PyVista as follows:

 - Link PyVista and Panel:

```python
import pyvista as pv

plotter = pv.Plotter() # we define a pyvista plotter
plotter.background_color = (0.1, 0.2, 0.4)
# we create a `VTK` panel around the render window
geo_pan_pv = pn.panel(plotter.ren_win, width=500, height=500) 
```

 - Create and add some objects to the PyVista plotter, displaying them using the VTK panel

```python
pvcylinder = pv.Cylinder(resolution=8, direction=(0,1,0))
cylinder_actor = plotter.add_mesh(pvcylinder, color=tomato, smooth_shading=True)
cylinder_actor.RotateX(30.0)
cylinder_actor.RotateY(-45.0)
sphere_actor = plotter.add_mesh(pv.Sphere(
    theta_resolution=8, phi_resolution=8,
    center=(0.5, 0.5, 0.5)),color=tomato, smooth_shading=True
)
# we can link camera of both panes
geom_pane.jslink(geo_pan_pv, camera='camera', bidirectional=True)
pn.Row(geom_pane, geo_pan_pv)
```

### Export the scene

- The scene can be exported and the file generated can be loaded by the official vtk-js scene importer:

```python
import os
filename = geo_pan_pv.export_scene(filename='geo_example')
print("The file is exported in :", os.path.join(os.getcwd(), filename))
pn.pane.HTML('<iframe width=100% height=400 src=https://kitware.github.io/vtk-js/examples/SynchronizableRenderWindow/index.html></iframe>', sizing_mode='stretch_width')
```

## Advanced usage and interactivity

This examples will show :
 - where information about `scalars` used to color 3D objects can be found in the scene
 - utilization of the `orientation widget`
 - how to add `axes` in the scene
 - adding a `player` widget to create an animation

### Scene creation

First we create a scene with a nice spline inspired by this examples : [Creating a Spline](https://docs.pyvista.org/examples/00-load/create-spline.html#creating-a-spline)

```python
import numpy as np

def make_points():
    """Helper to make XYZ points"""
    theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
    z = np.linspace(-2, 2, 100)
    r = z**2 + 1
    x = r * np.sin(theta)
    y = r * np.cos(theta)
    return np.column_stack((x, y, z))

def lines_from_points(points):
    """Given an array of points, make a line set"""
    poly = pv.PolyData()
    poly.points = points
    cells = np.full((len(points)-1, 3), 2, dtype=np.int32)
    cells[:, 1] = np.arange(0, len(points)-1, dtype=np.int32)
    cells[:, 2] = np.arange(1, len(points), dtype=np.int32)
    poly.lines = cells
    return poly

points = make_points()
line = lines_from_points(points)
line["scalars"] = np.arange(line.n_points) # By default pyvista use viridis colormap
tube = line.tube(radius=0.1) #=> the object we will represent in the scene

pl = pv.Plotter()
pl.camera_position =  [(4.440892098500626e-16, -21.75168228149414, 4.258553981781006),
                       (4.440892098500626e-16, 0.8581731039809382, 0),
                       (0, 0.1850949078798294, 0.982720673084259)]

pl.add_mesh(tube, smooth_shading=True)
spline_pan = pn.panel(pl.ren_win, width=500, orientation_widget=True)
spline_pan
```

By clicking on the three dots, a colorbar can be displayed

The orientation widget on the bottom right of the panel is clickable too, allowing you to orient the camera in a specific direction.

### Adding axes to the VTK scene

Using the `axes` parameter, it is possible to display axes in the 3D view.

The `Axes` object (like `orientation widget` and `colorbar`) is a client-side object instantiated only on the JavaScript side, and is not synchronized back to the Python `vtkRenderWindow`.

```python
axes = dict(
    origin = [-5, 5, -2],
    xticker = {'ticks': np.linspace(-5,5,5)},
    yticker = {'ticks': np.linspace(-5,5,5)},
    zticker = {'ticks': np.linspace(-2,2,5), 'labels': [''] + [str(int(item)) for item in np.linspace(-2,2,5)[1:]]},
    fontsize = 12,
    digits = 1,
    grid_opacity = 0.5,
    show_grid=True
)
spline_pan.axes = axes
```

### Working with Volumes

All previous panes use geometric examples, but `VTK` can work with both geometric and volume objects:

```python
import pyvista.examples as examples
head = examples.download_head()

plotter = pv.Plotter()
plotter.camera_position = [
    [565, -340, 219],
    [47, 112, 52],
    [0, 0, 1],
]
plotter.add_volume(head)

volume_pan = pn.panel(plotter.ren_win, width=500, orientation_widget=True)
volume_pan
```

As for other examples, we can add easily new objects in the pane.

For example, we can create 3 orthogonal slices and add them to the scene:

```python
actor, mapper = plotter.add_mesh(head.slice_orthogonal(x=100, y=120, z=30))
volume_pan.synchronize()
```

### Create an animation

We will reuse the panel used for the spline.

For this animation, we will rotate the actor and roll the scalars on the spline tube:

```python
pan_clone = spline_pan.clone() # we clone the panel to animate only this panel
pan_clone.unlink_camera() # we don't want to share the camera with the previous panel
player = pn.widgets.Player(label='Player', start=0, end=100, value=0, loop_policy='reflect', interval=100)
scalars = tube["scalars"]

def animate(value):
    tube["scalars"] = np.roll(scalars, 200*value)
    pan_clone.actors[0].SetOrientation(0, 0, -20*value)
    pan_clone.synchronize()

pn.Column(pan_clone, player, pn.bind(animate, player)).servable()
```

---
