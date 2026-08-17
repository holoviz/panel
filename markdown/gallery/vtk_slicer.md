# Vtk Slicer

```python
from functools import partial

import holoviews as hv
import numpy as np
import panel as pn
import panel_material_ui as pmui
import param

from holoviews.operation.datashader import rasterize
from bokeh.util.serialization import make_globally_unique_id
from pyvista import examples
from scipy.ndimage import zoom

import pyvista as pv # Import after datashader to avoid segfault on some systems

js_files = {'jquery': 'https://code.jquery.com/jquery-1.11.1.min.js',
            'goldenlayout': 'https://golden-layout.com/files/latest/js/goldenlayout.min.js'}
css_files = ['https://golden-layout.com/files/latest/css/goldenlayout-base.css',
             'https://golden-layout.com/files/latest/css/goldenlayout-dark-theme.css']

pn.extension('vtk', js_files=js_files, css_files=css_files, sizing_mode="stretch_width")

hv.renderer('bokeh').theme = 'dark_minimal'
hv.opts.defaults(hv.opts.Image(responsive=True, tools=['hover']))
```

## Declare callbacks

```python
class ImageSmoother(param.Parameterized):
    
    smooth_fun = param.Parameter(default=None)
    smooth_level = param.Integer(default=5, bounds=(1,10))
    order = param.Selector(default=1, objects=[1,2,3])
    
    def __init__(self, **params):
        super(ImageSmoother, self).__init__(**params)
        self._update_fun()

    @param.depends('order', 'smooth_level', watch=True)
    def _update_fun(self):
        self.smooth_fun = lambda x: zoom(x, zoom=self.smooth_level, order=self.order)

def update_camera_projection(*evts):
    volume.camera['parallelProjection'] = evts[0].new
    volume.param.trigger('camera')

def hook_reset_range(plot, elem, lbrt):
    bkplot = plot.handles['plot']
    x_range = lbrt[0], lbrt[2]
    y_range = lbrt[1], lbrt[3]
    old_x_range_reset = bkplot.x_range.reset_start, bkplot.x_range.reset_end
    old_y_range_reset = bkplot.y_range.reset_start, bkplot.y_range.reset_end  
    if x_range != old_x_range_reset or y_range != old_y_range_reset:
        bkplot.x_range.reset_start, bkplot.x_range.reset_end = x_range
        bkplot.x_range.start, bkplot.x_range.end = x_range
        bkplot.y_range.reset_start, bkplot.y_range.reset_end = y_range
        bkplot.y_range.start, bkplot.y_range.end = y_range
    
def image_slice(dims, array, lbrt, mapper, smooth_fun):
    array = np.asarray(array)
    low = mapper['low'] if mapper else array.min()
    high = mapper['high'] if mapper else array.max()
    cmap = mapper['palette'] if mapper else 'fire'
    img = hv.Image(smooth_fun(array), bounds=lbrt, kdims=dims, vdims='Intensity')
    reset_fun = partial(hook_reset_range, lbrt=lbrt)
    return img.opts(clim=(low, high), cmap=cmap, hooks=[reset_fun])
```

## Declare Panel

```python
# Download datasets
head = examples.download_head()
brain = examples.download_brain()

dataset_selection = pmui.Select(label='Dataset', value=head, options={'Head': head, 'Brain': brain})

volume = pn.pane.VTKVolume(
    dataset_selection.value, sizing_mode='stretch_both', min_height=400, 
    display_slices=True, orientation_widget=True, render_background="#222222",
    colormap='Rainbow Desaturated'
)

@pn.depends(dataset_selection, watch=True)
def update_volume_object(value):
    controller.loading=True
    volume.object = value
    controller.loading=False

volume_controls = volume.controls(jslink=False, parameters=[
    'render_background', 'display_volume', 'display_slices',
    'slice_i', 'slice_j', 'slice_k', 'rescale'
])

toggle_parallel_proj = pmui.Toggle(label='Parallel Projection', value=False)

toggle_parallel_proj.param.watch(update_camera_projection, ['value'], onlychanged=True)

smoother = ImageSmoother()

def image_slice_i(si, mapper, smooth_fun, vol):
    arr = vol.active_scalars.reshape(vol.dimensions, order='F')
    lbrt = vol.bounds[2], vol.bounds[4], vol.bounds[3], vol.bounds[5]
    return image_slice(['y','z'], arr[si,:,::-1].T, lbrt, mapper, smooth_fun)

def image_slice_j(sj, mapper, smooth_fun, vol):
    arr = vol.active_scalars.reshape(vol.dimensions, order='F')
    lbrt = vol.bounds[0], vol.bounds[4], vol.bounds[1], vol.bounds[5]
    return image_slice(['x','z'], arr[:,sj,::-1].T, lbrt, mapper, smooth_fun)

def image_slice_k(sk, mapper, smooth_fun, vol):
    arr = vol.active_scalars.reshape(vol.dimensions, order='F')
    lbrt = vol.bounds[0], vol.bounds[2], vol.bounds[1], vol.bounds[3]
    return image_slice(['x', 'y'], arr[:,::-1,sk].T, lbrt, mapper, smooth_fun)

common = dict(
    mapper=volume.param.mapper,
    smooth_fun=smoother.param.smooth_fun,
    vol=volume.param.object,
)

dmap_i = rasterize(hv.DynamicMap(pn.bind(image_slice_i, si=volume.param.slice_i, **common)))
dmap_j = rasterize(hv.DynamicMap(pn.bind(image_slice_j, sj=volume.param.slice_j, **common)))
dmap_k = rasterize(hv.DynamicMap(pn.bind(image_slice_k, sk=volume.param.slice_k, **common)))

controller = pn.Column(
    pn.Column(dataset_selection, toggle_parallel_proj, *volume_controls[1:]),
    pn.Param(smoother, parameters=['smooth_level', 'order']),
    pn.panel("This app demos **advanced 3D visualisation** using [Panel](https://panel.holoviz.org/) and [PyVista](https://docs.pyvista.org/).", margin=(5,15)),
    pn.layout.VSpacer(),
)
```

## Set up template

```python
template = """
{%% extends base %%}

{%% block contents %%}
{%% set context = '%s' %%}
{%% if context == 'notebook' %%}
    {%% set slicer_id = get_id() %%}
    
{%% endif %%}

{%% endblock %%}
"""

tmpl = pn.Template(template=(template % 'server'), nb_template=(template % 'notebook'))
tmpl.nb_template.globals['get_id'] = make_globally_unique_id

tmpl.add_panel('controller', controller)
tmpl.add_panel('scene3d', volume)
tmpl.add_panel('slice_i', pn.panel(dmap_i, sizing_mode='stretch_both'))
tmpl.add_panel('slice_j', pn.panel(dmap_j, sizing_mode='stretch_both'))
tmpl.add_panel('slice_k', pn.panel(dmap_k, sizing_mode='stretch_both'))

tmpl.servable(title='VTKSlicer')
```
