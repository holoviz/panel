# coding: utf-8
"""
Defines a VTKPane which renders a vtk plot using VTKPlot bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import sys
import base64

try:
    from urllib.request import urlopen
except ImportError: # python 2
    from urllib import urlopen

from six import string_types

import param
import numpy as np

from pyviz_comms import JupyterComm

from .enums import PRESET_CMAPS
from ..base import PaneBase
from ...util import isfile

if sys.version_info >= (2, 7):
    base64encode = lambda x: base64.b64encode(x).decode('utf-8')
else:
    base64encode = lambda x: x.encode('base64')


class VTKVolume(PaneBase):

    max_data_size = param.Number(default=(256 ** 3) * 2 / 1e6, doc="""
        Maximum data size transfert allowed without subsampling""")

    origin = param.Tuple(default=None, length=3, allow_None=True)

    spacing = param.Tuple(default=(1, 1, 1), length=3, doc="""
        Distance between voxel in each direction""")

    render_background = param.Color(default='#52576e', doc="""
        Allows to specify the background color of the 3D rendering. The value must be specified
        as an hexadecimal color string
    """)

    colormap = param.Selector(default='erdc_rainbow_bright', objects=PRESET_CMAPS, doc="""
        Name of the colormap used to transform pixel value in color
    """)

    rescale = param.Boolean(default=False, doc="""
        If set to True the colormap is rescale beween min and max value of the non transparent pixels
        Else the full range of the pixel values are used
    """)

    shadow = param.Boolean(default=True, doc="""
        If set to False, then the mapper for the volume will not perform shading
        computations, it is the same as setting ambient=1, diffuse=0, specular=0
    """)

    sampling = param.Number(default=0.4, bounds=(0, 1), step=1e-2, doc="""
        Parameter to adjust the distance between samples used for rendering. The lower the value is
        the more precise is the representation but it is more computationnaly intensive
    """)

    edge_gradient = param.Number(default=0.4, bounds=(0, 1), step=1e-2, doc="""
        Parameter to adjust the opacity of the volume based on the gradient between voxels
    """)

    interpolation = param.Selector(default='fast_linear', objects=['fast_linear','linear','nearest'], doc="""
        interpolation type for sampling a volume. `nearest` interpolation will snap to the closest voxel,
        `linear` will perform trilinear interpolation to compute a scalar value from surrounding voxels.
        `fast_linear` under WebGL 1 will perform bilinear interpolation on X and Y but use nearest
        for Z. This is slightly faster than full linear at the cost of no Z axis linear interpolation.
    """)

    ambient = param.Number(default=0.2, step=1e-2, doc="""
        Value to control the ambient lighting. It is the light an object gives even in the absence
        of strong light. It is constant in all directions.
    """)

    diffuse = param.Number(default=0.7, step=1e-2, doc="""
        Value to control the diffuse Lighting. It relies on both the light direction and the
        object surface normal.
    """)

    specular = param.Number(default=0.3, step=1e-2, doc="""
        Value to control specular lighting. It is the light reflects back toward the camera when hitting the
        object
    """)

    specular_power = param.Number(default=8., doc="""
        Specular power refers to how much light is reflected in a mirror like fashion,
        rather than scattered randomly in a diffuse manner
    """)

    slice_i = param.Integer(per_instance=True, doc="""
        Integer parameter to control the position of the slice normal to the X direction
    """)

    slice_j = param.Integer(per_instance=True, doc="""
        Integer parameter to control the position of the slice normal to the Y direction
    """)

    slice_k = param.Integer(per_instance=True, doc="""
        Integer parameter to control the position of the slice normal to the Z direction
    """)

    display_volume = param.Boolean(default=True, doc="""
        If set to True, the 3D respresentation of the volume is displayed using ray casting
    """)

    display_slices = param.Boolean(default=False, doc="""
        If set to true, the orthgonal slices in the three (X, Y, Z) directions are displayed.
        Postition of each slice can be controlled using slice_(i,j,k) parameters
    """)

    orientation_widget = param.Boolean(default=False, doc="""
        Activate/Deactivate the orientation widget display
    """)

    camera = param.Dict(doc="""
        State of the rendered VTK camera
    """)

    mapper = param.Dict(doc="""
        Lookup Table in format {low, high, palette}
    """)

    _serializers = {}

    _rename = {'max_data_size': None, 'spacing': None, 'origin': None}

    _updates = True

    def __init__(self, object=None, **params):
        super(VTKVolume, self).__init__(object, **params)
        self._sub_spacing = self.spacing
        self._update()

    @classmethod
    def applies(cls, obj):
        if ((isinstance(obj, np.ndarray) and obj.ndim == 3) or
            any([isinstance(obj, k) for k in cls._serializers.keys()])):
            return True
        elif 'vtk' not in sys.modules:
            return False
        else:
            import vtk
            return isinstance(obj, vtk.vtkImageData)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        if 'panel.models.vtk' not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning('VTKVolumePlot was not imported on instantiation '
                                   'and may not render in a notebook. Restart '
                                   'the notebook kernel and ensure you load '
                                   'it as part of the extension using:'
                                   '\n\npn.extension(\'vtk\')\n')
            from ...models.vtk import VTKVolumePlot
        else:
            VTKVolumePlot = getattr(sys.modules['panel.models.vtk'], 'VTKVolumePlot')

        props = self._process_param_change(self._init_properties())
        volume_data = self._volume_data

        model = VTKVolumePlot(data=volume_data,
                              **props)
        if root is None:
            root = model
        self._link_props(model, ['colormap', 'orientation_widget', 'camera', 'mapper'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update_object(self, ref, doc, root, parent, comm):
        self._legend = None
        super(VTKVolume, self)._update_object(ref, doc, root, parent, comm)

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k not in [
                    'default_layout', 'object', 'max_data_size', 'spacing', 'origin'
                ]}

    def _get_object_dimensions(self):
        if isinstance(self.object, np.ndarray):
            return self.object.shape
        else:
            return self.object.GetDimensions()

    def _process_param_change(self, msg):
        msg = super(VTKVolume, self)._process_param_change(msg)
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
        msg = super(VTKVolume, self)._process_property_change(msg)
        if self.object is not None:
            slice_params = {'slice_i':0, 'slice_j':1, 'slice_k':2}
            for k, v in msg.items():
                sub_dim = self._subsample_dimensions
                ori_dim = self._orginal_dimensions
                if k in slice_params:
                    index = slice_params[k]
                    msg[k] = int(np.round(v * ori_dim[index] / sub_dim[index]))
        return msg

    def _update(self, model=None):
        self._volume_data = self._get_volume_data()
        if self._volume_data:
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
        Register a seriliazer for a given type of class.
        A serializer is a function which take an instance of `class_type`
        (like a vtk.vtkImageData) as input and return a numpy array of the data
        """
        cls._serializers.update({class_type:serializer})

    def _volume_from_array(self, sub_array):
        return dict(buffer=base64encode(sub_array.ravel(order='F' if sub_array.flags['F_CONTIGUOUS'] else 'C')),
                    dims=sub_array.shape if sub_array.flags['F_CONTIGUOUS'] else sub_array.shape[::-1],
                    spacing=self._sub_spacing if sub_array.flags['F_CONTIGUOUS'] else self._sub_spacing[::-1],
                    origin=self.origin,
                    data_range=(sub_array.min(), sub_array.max()),
                    dtype=sub_array.dtype.name)

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
                    dims = imageData.GetDimensions()[::-1]
                    inst.spacing = imageData.GetSpacing()[::-1]
                    inst.origin = imageData.GetOrigin()
                    return inst._volume_from_array(inst._subsample_array(array.reshape(dims, order='C')))

                VTKVolume.register_serializer(vtk.vtkImageData, volume_serializer)
                serializer = volume_serializer
            else:
                serializer = available_serializer[0]
            return serializer(self)

    def _subsample_array(self, array):
        original_shape = array.shape
        spacing = self.spacing
        extent = tuple((o_s - 1) * s for o_s, s in zip(original_shape, spacing))
        dim_ratio = np.cbrt((np.prod(original_shape) / 1e6) / self.max_data_size)
        max_shape = tuple(int(o_s / dim_ratio) for o_s in original_shape)
        dowsnscale_factor = [max(o_s, m_s) / m_s for m_s, o_s in zip(max_shape, original_shape)]

        if any([d_f > 1 for d_f in dowsnscale_factor]):
            try:
                import scipy.ndimage as nd
                sub_array = nd.interpolation.zoom(array, zoom=[1 / d_f for d_f in dowsnscale_factor], order=0)
            except ImportError:
                sub_array = array[::int(np.ceil(dowsnscale_factor[0])),
                                  ::int(np.ceil(dowsnscale_factor[1])),
                                  ::int(np.ceil(dowsnscale_factor[2]))]
            self._sub_spacing = tuple(e / (s - 1) for e, s in zip(extent, sub_array.shape))
        else:
            sub_array = array
            self._sub_spacing = self.spacing
        return sub_array


class VTK(PaneBase):
    """
    VTK panes allow rendering VTK objects.
    """

    axes = param.Dict(doc="""
        Parameters of the axes to construct in the 3d view.

        Must contain at least ``xticker``, ``yticker`` and ``zticker``.
        A ``ticker`` is a dictionary which contains:
            - ``ticks`` (array of numbers) - required. Positions in the scene coordinates
            of the coresponding axe ticks
            - ``labels`` (array of strings) - optional. Label displayed respectively to
            the `ticks` positions.

            If `labels` are not defined they are infered from the `ticks` array.
        ``digits``: number of decimal digits when `ticks` are converted to `labels`.
        ``fontsize``: size in pts of the ticks labels.
        ``show_grid``: boolean. If true (default) the axes grid is visible.
        ``grid_opactity``: float between 0-1. Defines the grid opacity.
        ``axes_opactity``: float between 0-1. Defines the axes lines opacity.
    """)

    camera = param.Dict(doc="State of the rendered VTK camera.")

    enable_keybindings = param.Boolean(default=False, doc="""
        Activate/Deactivate keys binding.

        Warning: These keys bind may not work as expected in a notebook
        context if they interact with already binded keys.
    """)

    orientation_widget = param.Boolean(default=False, doc="""
        Activate/Deactivate the orientation widget display.
    """)

    serialize_on_instantiation = param.Boolean(default=True, doc="""
        Define if the object serialization occurs at panel instantiation
        or when the panel is displayed.
    """)

    _updates = True

    _rerender_params = ['object', 'serialize_on_instantiation']

    _serializers = {}

    def __init__(self, object=None, **params):
        super(VTK, self).__init__(object, **params)
        self._legend = None
        self._vtkjs = None
        if self.serialize_on_instantiation:
            self._vtkjs = self._get_vtkjs()

    @classmethod
    def applies(cls, obj):
        if (isinstance(obj, string_types) and obj.endswith('.vtkjs') or
            any([isinstance(obj, k) for k in cls._serializers.keys()])):
            return True
        elif 'vtk' not in sys.modules:
            return False
        else:
            import vtk
            return isinstance(obj, vtk.vtkRenderWindow)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        if 'panel.models.vtk' not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning('VTKPlot was not imported on instantiation '
                                   'and may not render in a notebook. Restart '
                                   'the notebook kernel and ensure you load '
                                   'it as part of the extension using:'
                                   '\n\npn.extension(\'vtk\')\n')
            from ...models.vtk import VTKPlot
        else:
            VTKPlot = getattr(sys.modules['panel.models.vtk'], 'VTKPlot')

        vtkjs = self._get_vtkjs()
        data = base64encode(vtkjs) if vtkjs is not None else vtkjs
        props = self._process_param_change(self._init_properties())
        model = VTKPlot(data=data, **props)
        if root is None:
            root = model
        self._link_props(model, ['camera', 'enable_keybindings', 'orientation_widget'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update_object(self, ref, doc, root, parent, comm):
        self._legend = None
        super(VTK, self)._update_object(ref, doc, root, parent, comm)

    def construct_colorbars(self, orientation='horizontal'):
        if self._legend is None:
            try:
                from .vtkjs_serializer import construct_palettes
                self._legend = construct_palettes(self.object)
            except Exception:
                self._legend = {}
        if self._legend:
            from bokeh.models import Plot, LinearColorMapper, ColorBar, FixedTicker
            if orientation == 'horizontal':
                cbs = []
                for k, v in self._legend.items():
                    ticks = np.linspace(v['low'], v['high'], 5)
                    cbs.append(ColorBar(
                        color_mapper=LinearColorMapper(low=v['low'], high=v['high'], palette=v['palette']),
                        title=k,
                        ticker=FixedTicker(ticks=ticks),
                        label_standoff=5, background_fill_alpha=0, orientation='horizontal', location=(0, 0)
                    ))
                plot = Plot(toolbar_location=None, frame_height=0, sizing_mode='stretch_width',
                            outline_line_width=0)
                [plot.add_layout(cb, 'below') for cb in cbs]
                return plot
            else:
                raise ValueError('orientation can only be horizontal')
        else:
            return None

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k not in ['default_layout', 'object', 'infer_legend',
                'serialize_on_instantiation']}

    def _process_param_change(self, msg):
        msg = super(VTK, self)._process_param_change(msg)
        if 'axes' in msg and msg['axes'] is not None:
            VTKAxes = getattr(sys.modules['panel.models.vtk'], 'VTKAxes')
            axes = msg['axes']
            msg['axes'] = VTKAxes(**axes)
        return msg

    @classmethod
    def register_serializer(cls, class_type, serializer):
        """
        Register a seriliazer for a given type of class.
        A serializer is a function which take an instance of `class_type`
        (like a vtk.vtkRenderWindow) as input and return the binary zip
        stream of the corresponding `vtkjs` file
        """
        cls._serializers.update({class_type:serializer})

    def _get_vtkjs(self):
        if self._vtkjs is None and self.object is not None:
            if isinstance(self.object, string_types) and self.object.endswith('.vtkjs'):
                if isfile(self.object):
                    with open(self.object, 'rb') as f:
                        vtkjs = f.read()
                else:
                    data_url = urlopen(self.object)
                    vtkjs = data_url.read()
            elif hasattr(self.object, 'read'):
                vtkjs = self.object.read()
            else:
                available_serializer = [v for k, v in VTK._serializers.items() if isinstance(self.object, k)]
                if len(available_serializer) == 0:
                    import vtk
                    from .vtkjs_serializer import render_window_serializer

                    VTK.register_serializer(vtk.vtkRenderWindow, render_window_serializer)
                    serializer = render_window_serializer
                else:
                    serializer = available_serializer[0]
                vtkjs = serializer(self.object)
            self._vtkjs = vtkjs

        return self._vtkjs

    def _update(self, model):
        self._vtkjs = None
        vtkjs = self._get_vtkjs()
        model.data = base64encode(vtkjs) if vtkjs is not None else vtkjs

    def export_vtkjs(self, filename='vtk_panel.vtkjs'):
        with open(filename, 'wb') as f:
            f.write(self._get_vtkjs())
