"""
Defines a VTKPane which renders a vtk plot using VTKPlot bokeh model.
"""
from __future__ import annotations

import base64
import json
import sys
import zipfile

from abc import abstractmethod
from collections.abc import Mapping
from typing import (
    IO, TYPE_CHECKING, Any, ClassVar,
)
from urllib.request import urlopen

import numpy as np
import param

from bokeh.models import LinearColorMapper
from bokeh.util.serialization import make_globally_unique_id
from pyviz_comms import JupyterComm

from ...param import ParamMethod
from ...util import isfile, lazy_load
from ..base import Pane
from ..plot import Bokeh
from .enums import PRESET_CMAPS

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

base64encode = lambda x: base64.b64encode(x).decode('utf-8')


class AbstractVTK(Pane):

    axes = param.Dict(default={}, nested_refs=True, doc="""
        Parameters of the axes to construct in the 3d view.

        Must contain at least ``xticker``, ``yticker`` and ``zticker``.

        A ``ticker`` is a dictionary which contains:
          - ``ticks`` (array of numbers) - required.
              Positions in the scene coordinates of the corresponding
              axis' ticks.
          - ``labels`` (array of strings) - optional.
              Label displayed respectively to the `ticks` positions.
              If `labels` are not defined they are inferred from the
              `ticks` array.
          - ``digits``: number of decimal digits when `ticks` are converted to `labels`.
          - ``fontsize``: size in pts of the ticks labels.
          - ``show_grid``: boolean.
                If true (default) the axes grid is visible.
          - ``grid_opacity``: float between 0-1.
                Defines the grid opacity.
          - ``axes_opacity``: float between 0-1.
                Defines the axes lines opacity.
    """)

    camera = param.Dict(nested_refs=True, doc="""
      State of the rendered VTK camera.""")

    color_mappers = param.List(nested_refs=True, doc="""
      Color mapper of the actor in the scene""")

    orientation_widget = param.Boolean(default=False, doc="""
      Activate/Deactivate the orientation widget display.""")

    interactive_orientation_widget = param.Boolean(default=True, constant=True, doc="""
        If True the orientation widget is clickable and allows to rotate
        the scene in one of the orthographic projections.""")

    __abstract = True

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'axes' in msg and msg['axes'] is not None:
            VTKAxes = sys.modules['panel.models.vtk'].VTKAxes
            axes = msg['axes']
            msg['axes'] = VTKAxes(**axes)
        return msg

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
    ) -> None:
        if 'axes' in msg and msg['axes'] is not None:
            VTKAxes = sys.modules['panel.models.vtk'].VTKAxes
            axes = msg['axes']
            if isinstance(axes, dict):
                msg['axes'] = VTKAxes(**axes)
            elif isinstance(axes, VTKAxes):
                msg['axes'] = VTKAxes(**axes.properties_with_values())
        super()._update_model(events, msg, root, model, doc, comm)


class SyncHelpers:
    """
    Class containing helpers functions to update vtkRenderingWindow
    """

    def make_ren_win(self):
        import vtk
        ren = vtk.vtkRenderer()
        ren_win = vtk.vtkRenderWindow()
        ren_win.AddRenderer(ren)
        return ren_win

    def set_background(self, r, g, b):
        self.get_renderer().SetBackground(r, g, b)
        self.synchronize()

    def add_actors(self, actors):
        """
        Add a list of `actors` to the VTK renderer
        if `reset_camera` is True, the current camera and it's clipping
        will be reset.
        """
        for actor in actors:
            self.get_renderer().AddActor(actor)

    def remove_actors(self, actors):
        """
        Add a list of `actors` to the VTK renderer
        if `reset_camera` is True, the current camera and it's clipping
        will be reset.
        """
        for actor in actors:
            self.get_renderer().RemoveActor(actor)

    def remove_all_actors(self):
        self.remove_actors(self.actors)

    @property
    def vtk_camera(self):
        return self.get_renderer().GetActiveCamera()

    @vtk_camera.setter
    def vtk_camera(self, camera):
        self.get_renderer().SetActiveCamera(camera)

    @property
    def actors(self):
        return list(self.get_renderer().GetActors())

    @abstractmethod
    def synchronize(self):
        """
        function to synchronize the renderer with the view
        """

    @abstractmethod
    def reset_camera(self):
        """
        Reset the camera
        """


class VTK:
    """
    The VTK pane renders a VTK scene inside a panel, making it possible to
    interact with complex geometries in 3D.

    Reference: https://panel.holoviz.org/reference/panes/VTK.html

    :Example:

    >>> pn.extension('vtk')
    >>> VTK(some_vtk_object, width=500, height=500)

    This is a Class factory and allows to switch between VTKJS,
    VTKRenderWindow, and VTKRenderWindowSynchronized pane as a function of the
    object type and when the serialisation of the vtkRenderWindow occurs.

    Once a pane is returned by this class (inst = VTK(object)), one can
    use pn.help(inst) to see parameters available for the current pane
    """

    def __new__(self, obj, **params):
        if BaseVTKRenderWindow.applies(obj):
            if VTKRenderWindow.applies(obj, **params):
                return VTKRenderWindow(obj, **params)
            else:
                if params.get('interactive_orientation_widget', False):
                    param.main.param.warning("""Setting interactive_orientation_widget=True will break synchronization capabilities of the pane""")
                return VTKRenderWindowSynchronized(obj, **params)
        elif VTKJS.applies(obj):
            return VTKJS(obj, **params)

    @staticmethod
    def import_scene(filename, synchronizable=True):
        from .synchronizable_deserializer import import_synch_file
        if synchronizable:
            return VTKRenderWindowSynchronized(
                import_synch_file(filename=filename),
                serialize_on_instantiation=False
            )
        else:
            return VTKRenderWindow(
                import_synch_file(filename=filename),
                serialize_on_instantiation=True
            )


class BaseVTKRenderWindow(AbstractVTK):


    enable_keybindings = param.Boolean(default=False, doc="""
        Activate/Deactivate keys binding.

        Warning: These keys bind may not work as expected in a notebook
        context if they interact with already binded keys
    """)

    serialize_on_instantiation = param.Boolean(default=False, constant=True, doc="""
         defines when the serialization of the vtkRenderWindow scene occurs.
         If set to True the scene object is serialized when the pane is created
         else (default) when the panel is displayed to the screen.

         This parameter is constant, once set it can't be modified.

         Warning: when the serialization occurs at instantiation, the vtkRenderWindow and
         the view are not fully synchronized. The view displays the state of the scene
         captured when the panel was created, if elements where added or removed between the
         instantiation and the display these changes will not be reflected.
         Moreover when the pane object is updated (replaced or call to param.trigger('object')),
         all the scene is rebuilt from scratch.
    """)

    serialize_all_data_arrays = param.Boolean(default=False, constant=True, doc="""
        If true, enable the serialization of all data arrays of vtkDataSets (point data, cell data and field data).
        By default the value is False and only active scalars of each dataset are serialized and transfer to the
        javascript side.

        Enabling this option will increase memory and network transfer volume but results in more reactive visualizations
        by using some custom javascript functions.
    """)

    _applies_kw = True

    _rename: ClassVar[Mapping[str, str | None]] = {'serialize_on_instantiation': None, 'serialize_all_data_arrays': None}

    __abstract = True

    def __init__(self, object, **params):
        self._debug_serializer = params.pop('debug_serializer', False)
        super().__init__(object, **params)
        import panel.pane.vtk.synchronizable_serializer as rws
        rws.initializeSerializers()

    @classmethod
    def applies(cls, obj, **kwargs):
        if 'vtk' not in sys.modules and 'vtkmodules' not in sys.modules:
            return False
        else:
            import vtk
            return isinstance(obj, vtk.vtkRenderWindow)

    def get_renderer(self):
        """
        Get the vtk Renderer associated to this pane
        """
        return list(self.object.GetRenderers())[0]

    def _vtklut2bkcmap(self, lut, name):
        table = lut.GetTable()
        low, high = lut.GetTableRange()
        rgba_arr =  np.frombuffer(memoryview(table),  dtype=np.uint8).reshape((-1, 4))
        palette = [self._rgb2hex(*rgb) for rgb in rgba_arr[:,:3]]
        return LinearColorMapper(low=low, high=high, name=name, palette=palette)

    def get_color_mappers(self, infer=False):
        if not infer:
            cmaps = []
            for view_prop in self.get_renderer().GetViewProps():
                if view_prop.IsA('vtkScalarBarActor'):
                    name = view_prop.GetTitle()
                    lut = view_prop.GetLookupTable()
                    cmaps.append(self._vtklut2bkcmap(lut, name))
        else:
            infered_cmaps = {}
            for actor in self.get_renderer().GetActors():
                mapper = actor.GetMapper()
                cmap_name = mapper.GetArrayName()
                if cmap_name and cmap_name not in infered_cmaps:
                    lut = mapper.GetLookupTable()
                    infered_cmaps[cmap_name] = self._vtklut2bkcmap(lut, cmap_name)
            cmaps = infered_cmaps.values()
        return cmaps

    @param.depends('color_mappers')
    def _construct_colorbars(self, color_mappers=None):
        if not color_mappers:
            color_mappers = self.color_mappers
        from bokeh.models import ColorBar, FixedTicker, Plot
        cbs = []
        for color_mapper in color_mappers:
            ticks = np.linspace(color_mapper.low, color_mapper.high, 5)
            cbs.append(ColorBar(
                color_mapper=color_mapper,
                title=color_mapper.name,
                ticker=FixedTicker(ticks=ticks),
                label_standoff=5, background_fill_alpha=0, orientation='horizontal', location=(0, 0)
            ))
        plot = Plot(toolbar_location=None, frame_height=0, sizing_mode='stretch_width',
                    outline_line_width=0)
        [plot.add_layout(cb, 'below') for cb in cbs]
        return plot

    def construct_colorbars(self, infer=True):
        if infer:
            color_mappers = self.get_color_mappers(infer=True)
            model = self._construct_colorbars(color_mappers)
            return Bokeh(model)
        else:
            return ParamMethod(self._construct_colorbars)

    def export_scene(self, filename='vtk_scene', all_data_arrays=False):
        if '.' not in filename:
            filename += '.synch'
        import panel.pane.vtk.synchronizable_serializer as rws
        context = rws.SynchronizationContext(serialize_all_data_arrays=all_data_arrays, debug=self._debug_serializer)
        scene, arrays, annotations = self._serialize_ren_win(self.object, context, binary=True, compression=False)

        with zipfile.ZipFile(filename, mode='w') as zf:
            zf.writestr('index.json', json.dumps(scene))
            for name, data in arrays.items():
                zf.writestr(f'data/{name}', data, zipfile.ZIP_DEFLATED)
            zf.writestr('annotations.json', json.dumps(annotations))
        return filename

    def _update_color_mappers(self):
        color_mappers = self.get_color_mappers()
        if self.color_mappers != color_mappers:
            self.color_mappers = color_mappers

    def _serialize_ren_win(self, ren_win, context, binary=False, compression=True, exclude_arrays=None):
        import panel.pane.vtk.synchronizable_serializer as rws
        if exclude_arrays is None:
            exclude_arrays = []
        ren_win.OffScreenRenderingOn() # to not pop a vtk windows
        ren_win.Modified()
        ren_win.Render()
        scene = rws.serializeInstance(None, ren_win, context.getReferenceId(ren_win), context, 0)
        scene['properties']['numberOfLayers'] = 2 #On js side the second layer is for the orientation widget
        arrays = {
            name: context.getCachedDataArray(name, binary=True, compression=False)
            for name in context.dataArrayCache.keys() if name not in exclude_arrays
        }
        annotations = context.getAnnotations()
        return scene, arrays, annotations

    @staticmethod
    def _rgb2hex(r, g, b):
        int_type = (int, np.integer)
        if isinstance(r, int_type) and isinstance(g, int_type) is isinstance(b, int_type):
            return f"#{r:02x}{g:02x}{b:02x}"
        else:
            return f"#{int(255 * r):02x}{int(255 * g):02x}{int(255 * b):02x}"


class VTKRenderWindow(BaseVTKRenderWindow):
    """
    VTK panes allow rendering vtkRenderWindow objects.
    Capture the scene of the vtkRenderWindow passed at instantiation
    To update the display a new vtkRenderWindow must be passed as object
    """

    _updates = True

    @classmethod
    def applies(cls, obj, **kwargs):
        serialize_on_instantiation = kwargs.get('serialize_on_instantiation', False)
        return (super().applies(obj, **kwargs) and
                serialize_on_instantiation)

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        if object is not None:
            self.color_mappers = self.get_color_mappers()
            self._update(None, None)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        VTKSynchronizedPlot = lazy_load(
            'panel.models.vtk', 'VTKSynchronizedPlot', isinstance(comm, JupyterComm), root
        )
        props = self._get_properties(doc)
        if self.object is not None:
            props.update(scene=self._scene, arrays=self._arrays, color_mappers=self.color_mappers)
        model = VTKSynchronizedPlot(**props)
        root = root or model
        self._link_props(
            model, ['enable_keybindings', 'orientation_widget'], doc, root, comm
        )
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, ref: str, model: Model) -> None:
        import panel.pane.vtk.synchronizable_serializer as rws
        context = rws.SynchronizationContext(
            id_root=make_globally_unique_id(),
            serialize_all_data_arrays=self.serialize_all_data_arrays,
            debug=self._debug_serializer
        )
        self._scene, self._arrays, self._annotations = self._serialize_ren_win(
            self.object,
            context,
        )
        if model is not None:
            model.update(rebuild=True, arrays=self._arrays, scene=self._scene, annotations=self._annotations)


class VTKRenderWindowSynchronized(BaseVTKRenderWindow, SyncHelpers):
    """
    VTK panes allow rendering VTK objects.
    Synchronize a vtkRenderWindow constructs on python side
    with a custom bokeh model on javascript side
    """

    interactive_orientation_widget = param.Boolean(default=False, constant=True, doc="""
    """)

    _one_time_reset = param.Boolean(default=False)

    _rename: ClassVar[Mapping[str, str | None]] = dict(_one_time_reset='one_time_reset',
                   **BaseVTKRenderWindow._rename)

    _updates = True

    @classmethod
    def applies(cls, obj, **kwargs):
        serialize_on_instantiation = kwargs.get('serialize_on_instantiation', False)
        return super().applies(obj, **kwargs) and not serialize_on_instantiation

    def __init__(self, object=None, **params):
        if object is None:
            object = self.make_ren_win()
        super().__init__(object, **params)
        self._contexts = {}

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        VTKSynchronizedPlot = lazy_load(
            'panel.models.vtk', 'VTKSynchronizedPlot', isinstance(comm, JupyterComm), root
        )
        import panel.pane.vtk.synchronizable_serializer as rws
        context = rws.SynchronizationContext(
            id_root=make_globally_unique_id(),
            serialize_all_data_arrays=self.serialize_all_data_arrays,
            debug=self._debug_serializer
        )
        scene, arrays, annotations = self._serialize_ren_win(self.object, context)
        self._update_color_mappers()
        props = self._get_properties(doc)
        props.update(scene=scene, arrays=arrays, annotations=annotations, color_mappers=self.color_mappers)
        model = VTKSynchronizedPlot(**props)
        root = root or model
        linked = ['camera', 'color_mappers', 'enable_keybindings', 'one_time_reset', 'orientation_widget']
        self._link_props(model, linked, doc, root, comm)
        self._contexts[model.id] =  context
        self._models[root.ref['id']] = (model, parent)
        return model

    def _cleanup(self, root: Model | None = None) -> None:
        if root:
            ref = root.ref['id']
            self._contexts.pop(ref, None)
        super()._cleanup(root)

    def _update(self, ref: str, model: Model) -> None:
        context = self._contexts[model.id]
        scene, arrays, annotations = self._serialize_ren_win(
            self.object,
            context,
            exclude_arrays=model.arrays_processed
        )
        context.checkForArraysToRelease()
        model.update(arrays=arrays, scene=scene, annotations=annotations)

    def synchronize(self):
        self.param.trigger('object')

    def link_camera(self, other):
        """
        Associate the camera of an other VTKSynchronized pane to this renderer
        """
        if not isinstance(other, VTKRenderWindowSynchronized):
            raise TypeError('Only instance of VTKRenderWindow class can be linked')
        else:
            self.vtk_camera = other.vtk_camera

    def reset_camera(self):
        self.get_renderer().ResetCamera()
        self._one_time_reset = not self._one_time_reset #trigger event

    def unlink_camera(self):
        """
        Create a fresh vtkCamera instance and set it to the renderer
        """
        import vtk
        old_camera = self.vtk_camera
        new_camera = vtk.vtkCamera()
        self.vtk_camera = new_camera
        exclude_properties = [
            'mtime',
            'projectionMatrix',
            'viewMatrix',
            'physicalTranslation',
            'physicalScale',
            'physicalViewUp',
            'physicalViewNorth',
            'remoteId',
        ]
        if self.camera is not None:
            for k, v in self.camera.items():
                if k not in exclude_properties:
                    if isinstance(v, list):
                        getattr(new_camera, 'Set' + k[0].capitalize() + k[1:])(*v)
                    else:
                        getattr(new_camera, 'Set' + k[0].capitalize() + k[1:])(v)
        else:
            new_camera.DeepCopy(old_camera)



class VTKVolume(AbstractVTK):
    """
    The `VTKVolume` pane renders 3d volumetric data defined on regular grids.
    It may be constructed from a 3D NumPy array or a vtkVolume.

    The pane provides a number of interactive control which can be set either
    through callbacks from Python or Javascript callbacks.

    Reference: https://panel.holoviz.org/reference/panes/VTKVolume.html

    :Example:

    >>> pn.extension('vtk')
    >>> VTKVolume(
    ...    data_matrix, spacing=(3,2,1), interpolation='nearest',
    ...    edge_gradient=0, sampling=0,
    ...    sizing_mode='stretch_width', height=400,
    ... )
    """

    ambient = param.Number(default=0.2, step=1e-2, doc="""
        Value to control the ambient lighting. It is the light an
        object gives even in the absence of strong light. It is
        constant in all directions.""")

    controller_expanded = param.Boolean(default=True, doc="""
        If True the volume controller panel options is expanded in the view""")

    colormap = param.Selector(default='erdc_rainbow_bright', objects=PRESET_CMAPS, doc="""
        Name of the colormap used to transform pixel value in color.""")

    diffuse = param.Number(default=0.7, step=1e-2, doc="""
        Value to control the diffuse Lighting. It relies on both the
        light direction and the object surface normal.""")

    display_volume = param.Boolean(default=True, doc="""
        If set to True, the 3D representation of the volume is
        displayed using ray casting.""")

    display_slices = param.Boolean(default=False, doc="""
        If set to true, the orthgonal slices in the three (X, Y, Z)
        directions are displayed. Position of each slice can be
        controlled using slice_(i,j,k) parameters.""")

    edge_gradient = param.Number(default=0.4, bounds=(0, 1), step=1e-2, doc="""
        Parameter to adjust the opacity of the volume based on the
        gradient between voxels.""")

    interpolation = param.Selector(default='fast_linear', objects=['fast_linear','linear','nearest'], doc="""
        interpolation type for sampling a volume. `nearest`
        interpolation will snap to the closest voxel, `linear` will
        perform trilinear interpolation to compute a scalar value from
        surrounding voxels.  `fast_linear` under WebGL 1 will perform
        bilinear interpolation on X and Y but use nearest for Z. This
        is slightly faster than full linear at the cost of no Z axis
        linear interpolation.""")

    mapper = param.Dict(doc="Lookup Table in format {low, high, palette}")

    max_data_size = param.Number(default=(256 ** 3) * 2 / 1e6, doc="""
        Maximum data size transfer allowed without subsampling""")

    nan_opacity = param.Number(default=1., bounds=(0., 1.), doc="""
        Opacity applied to nan values in slices""")

    origin = param.Tuple(default=None, length=3, allow_None=True, doc="""
        Origin of the volume in the scene coordinates.
        If None, the origin is set to (0, 0, 0)""")

    render_background = param.Color(default='#52576e', doc="""
        Allows to specify the background color of the 3D rendering.
        The value must be specified as an hexadecimal color string.""")

    rescale = param.Boolean(default=False, doc="""
        If set to True the colormap is rescaled between min and max
        value of the non-transparent pixel, otherwise  the full range
        of the pixel values are used.""")

    shadow = param.Boolean(default=True, doc="""
        If set to False, then the mapper for the volume will not
        perform shading computations, it is the same as setting
        ambient=1, diffuse=0, specular=0.""")

    sampling = param.Number(default=0.4, bounds=(0, 1), step=1e-2, doc="""
        Parameter to adjust the distance between samples used for
        rendering. The lower the value is the more precise is the
        representation but it is more computationally intensive.""")

    spacing = param.Tuple(default=(1, 1, 1), length=3, doc="""
        Distance between voxel in each direction""")

    specular = param.Number(default=0.3, step=1e-2, doc="""
        Value to control specular lighting. It is the light reflects
        back toward the camera when hitting the object.""")

    specular_power = param.Number(default=8., doc="""
        Specular power refers to how much light is reflected in a
        mirror like fashion, rather than scattered randomly in a
        diffuse manner.""")

    slice_i = param.Integer(per_instance=True, doc="""
        Integer parameter to control the position of the slice normal
        to the X direction.""")

    slice_j = param.Integer(per_instance=True, doc="""
        Integer parameter to control the position of the slice normal
        to the Y direction.""")

    slice_k = param.Integer(per_instance=True, doc="""
        Integer parameter to control the position of the slice normal
        to the Z direction.""")

    _serializers: dict[type, Any] = {}

    _rename: ClassVar[Mapping[str, str | None]] = {'max_data_size': None, 'spacing': None, 'origin': None}

    _updates = True

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._sub_spacing = self.spacing
        self._update(None, None)

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if ((isinstance(obj, np.ndarray) and obj.ndim == 3) or
            any([isinstance(obj, k) for k in cls._serializers.keys()])):
            return True
        elif 'vtk' not in sys.modules and 'vtkmodules' not in sys.modules:
            return False
        else:
            import vtk
            return isinstance(obj, vtk.vtkImageData)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        VTKVolumePlot = lazy_load(
            'panel.models.vtk', 'VTKVolumePlot', isinstance(comm, JupyterComm), root
        )
        props = self._process_param_change(self._init_params())
        if self._volume_data is not None:
            props['data'] = self._volume_data

        model = VTKVolumePlot(**props)
        if root is None:
            root = model
        self._link_props(model, ['colormap', 'orientation_widget', 'camera', 'mapper', 'controller_expanded', 'nan_opacity'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update_object(self, ref, doc, root, parent, comm):
        self._legend = None
        super()._update_object(ref, doc, root, parent, comm)

    def _get_object_dimensions(self):
        if isinstance(self.object, np.ndarray):
            return self.object.shape
        else:
            return self.object.GetDimensions()

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if self.object is not None:
            slice_params = {'slice_i':0, 'slice_j':1, 'slice_k':2}
            for k, v in msg.items():
                sub_dim = self._subsample_dimensions
                ori_dim = self._orginal_dimensions
                if k in slice_params:
                    index = slice_params[k]
                    msg[k] = int(np.round(v * sub_dim[index] / ori_dim[index]))
        return msg

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if self.object is not None:
            slice_params = {'slice_i':0, 'slice_j':1, 'slice_k':2}
            for k, v in msg.items():
                sub_dim = self._subsample_dimensions
                ori_dim = self._orginal_dimensions
                if k in slice_params:
                    index = slice_params[k]
                    msg[k] = int(np.round(v * ori_dim[index] / sub_dim[index]))
        return msg

    def _update(self, ref: str, model: Model) -> None:
        self._volume_data = self._get_volume_data()
        if self._volume_data is not None:
            self._orginal_dimensions = self._get_object_dimensions()
            self._subsample_dimensions = self._volume_data['dims']
            self.param.slice_i.bounds = (0, self._orginal_dimensions[0]-1)
            self.slice_i = (self._orginal_dimensions[0]-1)//2
            self.param.slice_j.bounds = (0, self._orginal_dimensions[1]-1)
            self.slice_j = (self._orginal_dimensions[1]-1)//2
            self.param.slice_k.bounds = (0, self._orginal_dimensions[2]-1)
            self.slice_k = (self._orginal_dimensions[2]-1)//2
        if model is not None:
            model.data = self._volume_data

    @classmethod
    def register_serializer(cls, class_type, serializer):
        """
        Register a serializer for a given type of class.
        A serializer is a function which take an instance of `class_type`
        (like a vtk.vtkImageData) as input and return a numpy array of the data
        """
        cls._serializers.update({class_type: serializer})

    def _volume_from_array(self, sub_array):
        return dict(
            buffer=base64encode(sub_array.ravel(order='F')),
            dims=sub_array.shape,
            spacing=self._sub_spacing,
            origin=self.origin,
            data_range=(np.nanmin(sub_array), np.nanmax(sub_array)),
            dtype=sub_array.dtype.name
        )

    def _get_volume_data(self):
        if self.object is None:
            return None
        elif isinstance(self.object, np.ndarray):
            return self._volume_from_array(self._subsample_array(self.object))
        else:
            available_serializer = [v for k, v in VTKVolume._serializers.items() if isinstance(self.object, k)]
            if not available_serializer:
                import vtk

                from vtk.util import numpy_support

                def volume_serializer(inst):
                    imageData = inst.object
                    array = numpy_support.vtk_to_numpy(imageData.GetPointData().GetScalars())
                    dims = imageData.GetDimensions()
                    inst.spacing = imageData.GetSpacing()
                    inst.origin = imageData.GetOrigin()
                    return inst._volume_from_array(inst._subsample_array(array.reshape(dims, order='F')))

                VTKVolume.register_serializer(vtk.vtkImageData, volume_serializer)
                serializer = volume_serializer
            else:
                serializer = available_serializer[0]
            return serializer(self)

    def _subsample_array(self, array):
        original_shape = array.shape
        spacing = self.spacing
        extent = tuple((o_s - 1) * s for o_s, s in zip(original_shape, spacing))
        dim_ratio = np.cbrt((array.nbytes / 1e6) / self.max_data_size)
        max_shape = tuple(int(o_s / dim_ratio) for o_s in original_shape)
        dowsnscale_factor = [max(o_s, m_s) / m_s for m_s, o_s in zip(max_shape, original_shape)]

        if any([d_f > 1 for d_f in dowsnscale_factor]):
            try:
                import scipy.ndimage as nd
                if hasattr(nd, "zoom"):
                    sub_array = nd.zoom(array, zoom=[1 / d_f for d_f in dowsnscale_factor], order=0, mode="nearest")
                else:  # Slated for removal in 2.0
                    sub_array = nd.interpolation.zoom(array, zoom=[1 / d_f for d_f in dowsnscale_factor], order=0, mode="nearest")
            except ImportError:
                sub_array = array[::int(np.ceil(dowsnscale_factor[0])),
                                  ::int(np.ceil(dowsnscale_factor[1])),
                                  ::int(np.ceil(dowsnscale_factor[2]))]
            self._sub_spacing = tuple(e / (s - 1) for e, s in zip(extent, sub_array.shape))
        else:
            sub_array = array
            self._sub_spacing = self.spacing
        return sub_array


class VTKJS(AbstractVTK):
    """
    The VTKJS pane allow rendering a vtk scene stored in a vtkjs.

    Reference: https://panel.holoviz.org/reference/panes/VTKJS.html

    :Example:

    >>> pn.extension('vtk')
    >>> VTK(
    ...    'https://raw.githubusercontent.com/Kitware/vtk-js/master/Data/StanfordDragon.vtkjs',
    ...     sizing_mode='stretch_width', height=400, enable_keybindings=True,
    ...     orientation_widget=True
    ... )
    """

    enable_keybindings = param.Boolean(default=False, doc="""
        Activate/Deactivate keys binding.

        Warning: These keybindings may not work as expected in a
                 notebook context if they interact with already
                 bound keys.""")

    _serializers: dict[type, Any] = {}

    _updates = True

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._vtkjs = None

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if isinstance(obj, str) and obj.endswith('.vtkjs'):
            return True
        return None

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        """
        Should return the bokeh model to be rendered.
        """
        VTKJSPlot = lazy_load('panel.models.vtk', 'VTKJSPlot', isinstance(comm, JupyterComm), root)
        props = self._get_properties(doc)
        props['data_url'], props['data'] = self._get_vtkjs()
        model = VTKJSPlot(**props)
        root = root or model
        self._link_props(model, ['camera', 'enable_keybindings', 'orientation_widget'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _get_vtkjs(self, fetch=True):
        data_path, data_url = None, None
        if isinstance(self.object, str) and self.object.endswith('.vtkjs'):
            data_path = data_path
            if not isfile(self.object):
                data_url = self.object
        if self._vtkjs is None and self.object is not None:
            vtkjs = None
            if data_url and fetch:
                vtkjs = urlopen(data_url).read() if fetch else data_url
            elif data_path:
                with open(self.object, 'rb') as f:
                    vtkjs = f.read()
            elif hasattr(self.object, 'read'):
                vtkjs = self.object.read()
            self._vtkjs = vtkjs
        return data_url, self._vtkjs

    def _update(self, ref: str, model: Model) -> None:
        self._vtkjs = None
        data_url, vtkjs = self._get_vtkjs()
        model.update(data_url=data_url, data=vtkjs)

    def export_vtkjs(self, filename: str | IO ='vtk_panel.vtkjs'):
        """
        Exports current VTK data to .vtkjs file.

        Arguments
        ---------
        filename: str | IO
        """
        _, vtkjs = self._get_vtkjs()
        if hasattr(filename, 'write'):
            filename.write(vtkjs)
        else:
            with open(filename, 'wb') as f:
                f.write(vtkjs)
