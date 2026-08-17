# Vtk Warp

```python
import panel as pn
import panel_material_ui as pmui
import numpy as np
import pyvista as pv

pn.extension('vtk', sizing_mode="stretch_width")
```

Temporal function inspired from http://holoviews.org/user_guide/Live_Data.html

```python
alpha = 2
xvals  = np.linspace(-4, 4,101)
yvals  = np.linspace(-4, 4,101)
xs, ys = np.meshgrid(xvals, yvals)

#temporal function to create data on a plane
def time_function(time):
    return np.sin(((ys/alpha)**alpha+time)*xs)

# 3d plane to support the data
mesh_ref = pv.ImageData(
    dimensions=(xvals.size, yvals.size, 1), #dims
    spacing=(xvals[1]-xvals[0],yvals[1]-yvals[0],1), #spacing
    origin=(xvals.min(),yvals.min(),0) #origin
)
mesh_ref.point_data['values'] = time_function(0).flatten(order='F')  #add data for time=0
pl_ref = pv.Plotter()
pl_ref.add_mesh(mesh_ref, cmap='rainbow')

pn.pane.VTK(pl_ref.ren_win, min_height=600)
```

We will demonstrate how to warp the surface and plot a temporal animation

```python
mesh_warped = mesh_ref.warp_by_scalar() # warp the mesh using data at time=0
#create the pyvista plotter
pl = pv.Plotter()
pl.add_mesh(mesh_warped, cmap='rainbow')

#initialize panel and widgets
camera = {
    'position': [13.443258285522461, 12.239550590515137, 12.731934547424316],
    'focalPoint': [0, 0, 0],
     'viewUp': [-0.41067028045654297, -0.40083757042884827, 0.8189500570297241]
}
vtkpan = pn.pane.VTK(pl.ren_win, orientation_widget=True, sizing_mode='stretch_both', camera=camera)
frame = pn.widgets.Player(value=0, start=0, end=50, interval=100, loop_policy="reflect", height=100)

def update_3d_warp(event):
    #the player value range in between 0 and 50, however we want time between 0 and 10
    time = event.new/5
    data = time_function(time).flatten(order='F')
    mesh_ref.point_data['values'] = data
    mesh_warped.point_data['values'] = data
    mesh_warped.points = mesh_ref.warp_by_scalar(factor=0.5).points
    vtkpan.synchronize()
    
frame.param.watch(update_3d_warp, 'value')

main = pn.Column(
    "This app demonstrates the use of Panel to animate a `VTK` rendering.",
    frame,
    vtkpan,
    min_height=800
)
    
main
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        main=[main],
        title='VTK Warp'
    ).servable()
```
