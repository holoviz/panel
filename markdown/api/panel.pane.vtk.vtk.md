# panel.pane.vtk.vtk module

Defines a VTKPane which renders a vtk plot using VTKPlot bokeh model.

class panel.pane.vtk.vtk.AbstractVTK(object=None, **params)
Bases: [Pane](panel.pane.base.md#panel.pane.base.Pane)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
>

`axes`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Axes',`` ``nested_refs=True)`
Parameters of the axes to construct in the 3d view. Must contain at
least `xticker`,
`yticker` and
`zticker`. A `ticker`
is a dictionary which contains: - `ticks`
(array of numbers) - required. Positions in the scene coordinates of the
corresponding axis’ ticks. - `labels` (array of
strings) - optional. Label displayed respectively to the ticks
positions. If labels are not defined they are inferred from the ticks
array. - `digits`: number of decimal digits
when ticks are converted to labels. -
`fontsize`: size in pts of the ticks labels. -
`show_grid`: boolean. If true (default) the
axes grid is visible. - `grid_opacity`: float
between 0-1. Defines the grid opacity. -
`axes_opacity`: float between 0-1. Defines the
axes lines opacity.

`camera`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Camera',`` ``nested_refs=True)`
State of the rendered VTK camera.

`color_mappers`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Color`` ``mappers',`` ``nested_refs=True)`
Color mapper of the actor in the scene

`orientation_widget`` ``=`` ``Boolean(default=False,`` ``label='Orientation`` ``widget')`
Activate/Deactivate the orientation widget display.

`interactive_orientation_widget`` ``=`` ``Boolean(constant=True,`` ``default=True,`` ``label='Interactive`` ``orientation`` ``widget')`
If True the orientation widget is clickable and allows to rotate the
scene in one of the orthographic projections.

class panel.pane.vtk.vtk.BaseVTKRenderWindow(object, **params)
Bases:
[AbstractVTK](#panel.pane.vtk.vtk.AbstractVTK)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.vtk.vtk.BaseVTKRenderWindow.applies)(object, **kwargs) | Returns boolean or float indicating whether the Pane can render the object. |
| [get_renderer](#panel.pane.vtk.vtk.BaseVTKRenderWindow.get_renderer)() | Get the vtk Renderer associated to this pane |

|                         |     |
|-------------------------|-----|
| **construct_colorbars** |     |
| **export_scene**        |     |
| **get_color_mappers**   |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.vtk.vtk.AbstractVTK"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.vtk.vtk.AbstractVTK](#panel.pane.vtk.vtk.AbstractVTK):
> axes, camera, color_mappers, orientation_widget,
> interactive_orientation_widget
>
>

`enable_keybindings`` ``=`` ``Boolean(default=False,`` ``label='Enable`` ``keybindings')`
Activate/Deactivate keys binding. Warning: These keys bind may not work
as expected in a notebook context if they interact with already binded
keys

`serialize_on_instantiation`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Serialize`` ``on`` ``instantiation')`
defines when the serialization of the vtkRenderWindow scene occurs. If
set to True the scene object is serialized when the pane is created else
(default) when the panel is displayed to the screen. This parameter is
constant, once set it can’t be modified. Warning: when the serialization
occurs at instantiation, the vtkRenderWindow and the view are not fully
synchronized. The view displays the state of the scene captured when the
panel was created, if elements where added or removed between the
instantiation and the display these changes will not be reflected.
Moreover when the pane object is updated (replaced or call to
param.trigger(‘object’)), all the scene is rebuilt from scratch.

`serialize_all_data_arrays`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Serialize`` ``all`` ``data`` ``arrays')`
If true, enable the serialization of all data arrays of vtkDataSets
(point data, cell data and field data). By default the value is False
and only active scalars of each dataset are serialized and transfer to
the javascript side. Enabling this option will increase memory and
network transfer volume but results in more reactive visualizations by
using some custom javascript functions.

classmethod applies(object, **kwargs)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

get_renderer()
Get the vtk Renderer associated to this pane

class panel.pane.vtk.vtk.SyncHelpers
Bases: `object`

Class containing helpers functions to update vtkRenderingWindow

Attributes:
**actors**

**vtk_camera**

Methods

|  |  |
|----|----|
| [add_actors](#panel.pane.vtk.vtk.SyncHelpers.add_actors)(actors) | Add a list of actors to the VTK renderer if reset_camera is True, the current camera and it's clipping will be reset. |
| [remove_actors](#panel.pane.vtk.vtk.SyncHelpers.remove_actors)(actors) | Add a list of actors to the VTK renderer if reset_camera is True, the current camera and it's clipping will be reset. |
| [reset_camera](#panel.pane.vtk.vtk.SyncHelpers.reset_camera)() | Reset the camera |
| [synchronize](#panel.pane.vtk.vtk.SyncHelpers.synchronize)() | function to synchronize the renderer with the view |

|                       |     |
|-----------------------|-----|
| **make_ren_win**      |     |
| **remove_all_actors** |     |
| **set_background**    |     |

add_actors(actors)
Add a list of actors to the VTK renderer if reset_camera is True, the
current camera and it’s clipping will be reset.

remove_actors(actors)
Add a list of actors to the VTK renderer if reset_camera is True, the
current camera and it’s clipping will be reset.

abstractmethod reset_camera()
Reset the camera

abstractmethod synchronize()
function to synchronize the renderer with the view

class panel.pane.vtk.vtk.VTK(obj, **params)
Bases: `object`

The VTK pane renders a VTK scene inside a panel, making it possible to
interact with complex geometries in 3D.

Reference: [https://panel.holoviz.org/reference/panes/VTK.html](https://panel.holoviz.org/reference/panes/VTK.html)

Example:

\>\>\>
pn.extension('vtk')
\>\>\>
VTK(some_vtk_object,
width=500,
height=500)

This is a Class factory and allows to switch between VTKJS,
VTKRenderWindow, and VTKRenderWindowSynchronized pane as a function of
the object type and when the serialisation of the vtkRenderWindow
occurs.

Once a pane is returned by this class (inst = VTK(object)), one can use
pn.help(inst) to see parameters available for the current pane

class panel.pane.vtk.vtk.VTKJS(object=None, **params)
Bases:
[AbstractVTK](#panel.pane.vtk.vtk.AbstractVTK)

The VTKJS pane allow rendering a vtk scene stored in a vtkjs.

Reference:
[https://panel.holoviz.org/reference/panes/VTKJS.html](https://panel.holoviz.org/reference/panes/VTKJS.html)

Example:

\>\>\>
pn.extension('vtk')
\>\>\>
VTK(
...
'https://raw.githubusercontent.com/Kitware/vtk-js/master/Data/StanfordDragon.vtkjs',
...
sizing_mode='stretch_width',
height=400,
enable_keybindings=True,
...
orientation_widget=True
... )

Methods

|  |  |
|----|----|
| [applies](#panel.pane.vtk.vtk.VTKJS.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [export_vtkjs](#panel.pane.vtk.vtk.VTKJS.export_vtkjs)(\[filename\]) | Exports current VTK data to .vtkjs file. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.vtk.vtk.AbstractVTK"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.vtk.vtk.AbstractVTK](#panel.pane.vtk.vtk.AbstractVTK):
> axes, camera, color_mappers, orientation_widget,
> interactive_orientation_widget
>
>

`enable_keybindings`` ``=`` ``Boolean(default=False,`` ``label='Enable`` ``keybindings')`
Activate/Deactivate keys binding. Warning: These keybindings may not
work as expected in a notebook context if they interact with already
bound keys.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

export_vtkjs(filename: str \| IO = 'vtk_panel.vtkjs')
Exports current VTK data to .vtkjs file.

class panel.pane.vtk.vtk.VTKRenderWindow(object=None, **params)
Bases: [BaseVTKRenderWindow](#panel.pane.vtk.vtk.BaseVTKRenderWindow)

VTK panes allow rendering vtkRenderWindow objects. Capture the scene of
the vtkRenderWindow passed at instantiation To update the display a new
vtkRenderWindow must be passed as object

Methods

|  |  |
|----|----|
| [applies](#panel.pane.vtk.vtk.VTKRenderWindow.applies)(object, **kwargs) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.vtk.vtk.AbstractVTK"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.vtk.vtk.AbstractVTK](#panel.pane.vtk.vtk.AbstractVTK):
> axes, camera, color_mappers, orientation_widget,
> interactive_orientation_widget
>
> [class="reference internal"
> title="panel.pane.vtk.vtk.BaseVTKRenderWindow"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.vtk.vtk.BaseVTKRenderWindow](#panel.pane.vtk.vtk.BaseVTKRenderWindow):
> enable_keybindings, serialize_on_instantiation,
> serialize_all_data_arrays
>
>

classmethod applies(object, **kwargs)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.vtk.vtk.VTKRenderWindowSynchronized(object=None, **params)
Bases: [BaseVTKRenderWindow](#panel.pane.vtk.vtk.BaseVTKRenderWindow),
[SyncHelpers](#panel.pane.vtk.vtk.SyncHelpers)

VTK panes allow rendering VTK objects. Synchronize a vtkRenderWindow
constructs on python side with a custom bokeh model on javascript side

Methods

|  |  |
|----|----|
| [applies](#panel.pane.vtk.vtk.VTKRenderWindowSynchronized.applies)(object, **kwargs) | Returns boolean or float indicating whether the Pane can render the object. |
| [link_camera](#panel.pane.vtk.vtk.VTKRenderWindowSynchronized.link_camera)(other) | Associate the camera of an other VTKSynchronized pane to this renderer |
| [reset_camera](#panel.pane.vtk.vtk.VTKRenderWindowSynchronized.reset_camera)() | Reset the camera |
| [synchronize](#panel.pane.vtk.vtk.VTKRenderWindowSynchronized.synchronize)() | function to synchronize the renderer with the view |
| [unlink_camera](#panel.pane.vtk.vtk.VTKRenderWindowSynchronized.unlink_camera)() | Create a fresh vtkCamera instance and set it to the renderer |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.vtk.vtk.AbstractVTK"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.vtk.vtk.AbstractVTK](#panel.pane.vtk.vtk.AbstractVTK):
> axes, camera, color_mappers, orientation_widget
>
> [class="reference internal"
> title="panel.pane.vtk.vtk.BaseVTKRenderWindow"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.vtk.vtk.BaseVTKRenderWindow](#panel.pane.vtk.vtk.BaseVTKRenderWindow):
> enable_keybindings, serialize_on_instantiation,
> serialize_all_data_arrays
>
>

`interactive_orientation_widget`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Interactive`` ``orientation`` ``widget')`

`_one_time_reset`` ``=`` ``Boolean(default=False,`` ``label='`` ``one`` ``time`` ``reset')`

classmethod applies(object, **kwargs)
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

link_camera(other)
Associate the camera of an other VTKSynchronized pane to this renderer

reset_camera()
Reset the camera

synchronize()
function to synchronize the renderer with the view

unlink_camera()
Create a fresh vtkCamera instance and set it to the renderer

class panel.pane.vtk.vtk.VTKVolume(object=None, **params)
Bases:
[AbstractVTK](#panel.pane.vtk.vtk.AbstractVTK)

The VTKVolume pane renders 3d volumetric data defined on regular grids.
It may be constructed from a 3D NumPy array or a vtkVolume.

The pane provides a number of interactive control which can be set
either through callbacks from Python or Javascript callbacks.

Reference:
[https://panel.holoviz.org/reference/panes/VTKVolume.html](https://panel.holoviz.org/reference/panes/VTKVolume.html)

Example:

\>\>\>
pn.extension('vtk')
\>\>\>
VTKVolume(
...
data_matrix,
spacing=(3,2,1),
interpolation='nearest',
...
edge_gradient=0,
sampling=0,
...
sizing_mode='stretch_width',
height=400,
... )

Methods

|  |  |
|----|----|
| [applies](#panel.pane.vtk.vtk.VTKVolume.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |
| [register_serializer](#panel.pane.vtk.vtk.VTKVolume.register_serializer)(class_type, serializer) | Register a serializer for a given type of class. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.vtk.vtk.AbstractVTK"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.vtk.vtk.AbstractVTK](#panel.pane.vtk.vtk.AbstractVTK):
> axes, camera, color_mappers, orientation_widget,
> interactive_orientation_widget
>
>

`ambient`` ``=`` ``Number(default=0.2,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ambient',`` ``step=0.01)`
Value to control the ambient lighting. It is the light an object gives
even in the absence of strong light. It is constant in all directions.

`controller_expanded`` ``=`` ``Boolean(default=True,`` ``label='Controller`` ``expanded')`
If True the volume controller panel options is expanded in the view

`colormap`` ``=`` ``Selector(default='erdc_rainbow_bright',`` ``label='Colormap',`` ``names={},`` ``objects=['KAAMS',`` ``'Cool`` ``to`` ``Warm',`` ``'Cool`` ``to`` ``Warm`` ``(Extended)',`` ``'Warm`` ``to`` ``Cool',`` ``'Warm`` ``to`` ``Cool`` ``(Extended)',`` ``'Rainbow`` ``Desaturated',`` ``'Cold`` ``and`` ``Hot',`` ``'Black-Body`` ``Radiation',`` ``'X`` ``Ray',`` ``'Grayscale',`` ``'BkRd',`` ``'BkGn',`` ``'BkBu',`` ``'BkMa',`` ``'BkCy',`` ``'Black,`` ``Blue`` ``and`` ``White',`` ``'Black,`` ``Orange`` ``and`` ``White',`` ``'Linear`` ``YGB`` ``1211g',`` ``'Linear`` ``Green`` ``(Gr4L)',`` ``'Linear`` ``Blue`` ``(8_31f)',`` ``'Blue`` ``to`` ``Red`` ``Rainbow',`` ``'Red`` ``to`` ``Blue`` ``Rainbow',`` ``'Rainbow`` ``Blended`` ``White',`` ``'Rainbow`` ``Blended`` ``Grey',`` ``'Rainbow`` ``Blended`` ``Black',`` ``'Blue`` ``to`` ``Yellow',`` ``'blot',`` ``'CIELab`` ``Blue`` ``to`` ``Red',`` ``'jet',`` ``'rainbow',`` ``'erdc_rainbow_bright',`` ``'erdc_rainbow_dark',`` ``'nic_CubicL',`` ``'nic_CubicYF',`` ``'gist_earth',`` ``'2hot',`` ``'erdc_red2yellow_BW',`` ``'erdc_marine2gold_BW',`` ``'erdc_blue2gold_BW',`` ``'erdc_sapphire2gold_BW',`` ``'erdc_red2purple_BW',`` ``'erdc_purple2pink_BW',`` ``'erdc_pbj_lin',`` ``'erdc_blue2green_muted',`` ``'erdc_blue2green_BW',`` ``'GREEN-WHITE_LINEAR',`` ``'erdc_green2yellow_BW',`` ``'blue2cyan',`` ``'erdc_blue2cyan_BW',`` ``'erdc_blue_BW',`` ``'BLUE-WHITE',`` ``'erdc_purple_BW',`` ``'erdc_magenta_BW',`` ``'magenta',`` ``'RED-PURPLE',`` ``'erdc_red_BW',`` ``'RED_TEMPERATURE',`` ``'erdc_orange_BW',`` ``'heated_object',`` ``'erdc_gold_BW',`` ``'erdc_brown_BW',`` ``'copper_Matlab',`` ``'pink_Matlab',`` ``'bone_Matlab',`` ``'gray_Matlab',`` ``'Purples',`` ``'Blues',`` ``'Greens',`` ``'PuBu',`` ``'BuPu',`` ``'BuGn',`` ``'GnBu',`` ``'GnBuPu',`` ``'BuGnYl',`` ``'PuRd',`` ``'RdPu',`` ``'Oranges',`` ``'Reds',`` ``'RdOr',`` ``'BrOrYl',`` ``'RdOrYl',`` ``'CIELab_blue2red',`` ``'blue2yellow',`` ``'erdc_blue2gold',`` ``'erdc_blue2yellow',`` ``'erdc_cyan2orange',`` ``'erdc_purple2green',`` ``'erdc_purple2green_dark',`` ``'coolwarm',`` ``'BuRd',`` ``'Spectral_lowBlue',`` ``'GnRP',`` ``'GYPi',`` ``'GnYlRd',`` ``'GBBr',`` ``'PuOr',`` ``'PRGn',`` ``'PiYG',`` ``'OrPu',`` ``'BrBG',`` ``'GyRd',`` ``'erdc_divHi_purpleGreen',`` ``'erdc_divHi_purpleGreen_dim',`` ``'erdc_divLow_icePeach',`` ``'erdc_divLow_purpleGreen',`` ``'Haze_green',`` ``'Haze_lime',`` ``'Haze',`` ``'Haze_cyan',`` ``'nic_Edge',`` ``'erdc_iceFire_H',`` ``'erdc_iceFire_L',`` ``'hsv',`` ``'hue_L60',`` ``'Spectrum',`` ``'Warm',`` ``'Cool',`` ``'Blues',`` ``'Wild`` ``Flower',`` ``'Citrus',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(11)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(10)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(9)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(8)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(7)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(6)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(5)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(4)',`` ``'Brewer`` ``Diverging`` ``Purple-Orange`` ``(3)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(11)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(10)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(9)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(8)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(7)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(6)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(5)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(4)',`` ``'Brewer`` ``Diverging`` ``Spectral`` ``(3)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(11)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(10)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(9)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(8)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(7)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(6)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(5)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(4)',`` ``'Brewer`` ``Diverging`` ``Brown-Blue-Green`` ``(3)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(9)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(8)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(7)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(6)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(5)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(4)',`` ``'Brewer`` ``Sequential`` ``Blue-Green`` ``(3)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(9)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(8)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(7)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(6)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(5)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(4)',`` ``'Brewer`` ``Sequential`` ``Yellow-Orange-Brown`` ``(3)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(9)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(8)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(7)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(6)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(5)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(4)',`` ``'Brewer`` ``Sequential`` ``Blue-Purple`` ``(3)',`` ``'Brewer`` ``Qualitative`` ``Accent',`` ``'Brewer`` ``Qualitative`` ``Dark2',`` ``'Brewer`` ``Qualitative`` ``Set2',`` ``'Brewer`` ``Qualitative`` ``Pastel2',`` ``'Brewer`` ``Qualitative`` ``Pastel1',`` ``'Brewer`` ``Qualitative`` ``Set1',`` ``'Brewer`` ``Qualitative`` ``Paired',`` ``'Brewer`` ``Qualitative`` ``Set3',`` ``'Traffic`` ``Lights',`` ``'Traffic`` ``Lights`` ``For`` ``Deuteranopes',`` ``'Traffic`` ``Lights`` ``For`` ``Deuteranopes`` ``2',`` ``'Muted`` ``Blue-Green',`` ``'Green-Blue`` ``Asymmetric`` ``Divergent`` ``(62Blbc)',`` ``'Asymmtrical`` ``Earth`` ``Tones`` ``(6_21b)',`` ``'Yellow`` ``15',`` ``'Magma`` ``(matplotlib)',`` ``'Inferno`` ``(matplotlib)',`` ``'Plasma`` ``(matplotlib)',`` ``'Viridis`` ``(matplotlib)',`` ``'BlueObeliskElements'])`
Name of the colormap used to transform pixel value in color.

`diffuse`` ``=`` ``Number(default=0.7,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Diffuse',`` ``step=0.01)`
Value to control the diffuse Lighting. It relies on both the light
direction and the object surface normal.

`display_volume`` ``=`` ``Boolean(default=True,`` ``label='Display`` ``volume')`
If set to True, the 3D representation of the volume is displayed using
ray casting.

`display_slices`` ``=`` ``Boolean(default=False,`` ``label='Display`` ``slices')`
If set to true, the orthgonal slices in the three (X, Y, Z) directions
are displayed. Position of each slice can be controlled using
slice\_(i,j,k) parameters.

`edge_gradient`` ``=`` ``Number(bounds=(0,`` ``1),`` ``default=0.4,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Edge`` ``gradient',`` ``step=0.01)`
Parameter to adjust the opacity of the volume based on the gradient
between voxels.

`interpolation`` ``=`` ``Selector(default='fast_linear',`` ``label='Interpolation',`` ``names={},`` ``objects=['fast_linear',`` ``'linear',`` ``'nearest'])`
interpolation type for sampling a volume. nearest interpolation will
snap to the closest voxel, linear will perform trilinear interpolation
to compute a scalar value from surrounding voxels. fast_linear under
WebGL 1 will perform bilinear interpolation on X and Y but use nearest
for Z. This is slightly faster than full linear at the cost of no Z axis
linear interpolation.

`mapper`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Mapper')`
Lookup Table in format {low, high, palette}

`max_data_size`` ``=`` ``Number(default=33.554432,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``data`` ``size')`
Maximum data size transfer allowed without subsampling

`nan_opacity`` ``=`` ``Number(bounds=(0.0,`` ``1.0),`` ``default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nan`` ``opacity')`
Opacity applied to nan values in slices

`origin`` ``=`` ``Tuple(allow_None=True,`` ``label='Origin',`` ``length=3)`
Origin of the volume in the scene coordinates. If None, the origin is
set to (0, 0, 0)

`render_background`` ``=`` ``Color(allow_named=True,`` ``default='#52576e',`` ``label='Render`` ``background')`
Allows to specify the background color of the 3D rendering. The value
must be specified as an hexadecimal color string.

`rescale`` ``=`` ``Boolean(default=False,`` ``label='Rescale')`
If set to True the colormap is rescaled between min and max value of the
non-transparent pixel, otherwise the full range of the pixel values are
used.

`shadow`` ``=`` ``Boolean(default=True,`` ``label='Shadow')`
If set to False, then the mapper for the volume will not perform shading
computations, it is the same as setting ambient=1, diffuse=0,
specular=0.

`sampling`` ``=`` ``Number(bounds=(0,`` ``1),`` ``default=0.4,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Sampling',`` ``step=0.01)`
Parameter to adjust the distance between samples used for rendering. The
lower the value is the more precise is the representation but it is more
computationally intensive.

`spacing`` ``=`` ``Tuple(default=(1,`` ``1,`` ``1),`` ``label='Spacing',`` ``length=3)`
Distance between voxel in each direction

`specular`` ``=`` ``Number(default=0.3,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Specular',`` ``step=0.01)`
Value to control specular lighting. It is the light reflects back toward
the camera when hitting the object.

`specular_power`` ``=`` ``Number(default=8.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Specular`` ``power')`
Specular power refers to how much light is reflected in a mirror like
fashion, rather than scattered randomly in a diffuse manner.

`slice_i`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slice`` ``i')`
Integer parameter to control the position of the slice normal to the X
direction.

`slice_j`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slice`` ``j')`
Integer parameter to control the position of the slice normal to the Y
direction.

`slice_k`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Slice`` ``k')`
Integer parameter to control the position of the slice normal to the Z
direction.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

classmethod register_serializer(class_type, serializer)
Register a serializer for a given type of class. A serializer is a
function which take an instance of class_type (like a vtk.vtkImageData)
as input and return a numpy array of the data

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
