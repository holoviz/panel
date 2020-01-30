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

    colormap = param.Selector(default='erdc_rainbow_bright', objects=PRESET_CMAPS, doc="""
        Name of the colormap used to transform pixel value in color
    """)

    rescale = param.Boolean(default=False, doc="""
        If set to True the colormap is rescale beween min and max value of the non transparent pixels
        Else the full range of the pixel even with opacity nul is used
    """)

    shadow = param.Boolean(default=True)

    sampling = param.Number(default=0.4, bounds=(0, 1), step=1e-2)

    edge_gradient = param.Number(default=0.4, bounds=(0, 1), step=1e-2)

    ambient = param.Number(default=0.2, step=1e-2)

    diffuse = param.Number(default=0.7, step=1e-2)

    specular = param.Number(default=0.3, step=1e-2)

    specular_power = param.Number(default=8.)

    slice_i = param.Integer(per_instance=True)

    slice_j = param.Integer(per_instance=True)

    slice_k = param.Integer(per_instance=True)

    display_volume = param.Boolean(default=True)

    display_slices = param.Boolean(default=False)

    _serializers = {}

    _rename = {'max_data_size': None, 'spacing': None, 'origin': None}

    _updates = True

    def __init__(self, object=None, **params):
        super(VTKVolume, self).__init__(object, **params)
        self._sub_spacing = self.spacing
        self._volume_data = self._get_volume_data()
        if self._volume_data:
            self.param.slice_i.bounds = (0, self._volume_data['dims'][0]-1)
            self.slice_i = (self._volume_data['dims'][0]-1)//2
            self.param.slice_j.bounds = (0, self._volume_data['dims'][1]-1)
            self.slice_j = (self._volume_data['dims'][1]-1)//2
            self.param.slice_k.bounds = (0, self._volume_data['dims'][2]-1)
            self.slice_k = (self._volume_data['dims'][2]-1)//2

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
        self._link_props(model, ['colormap'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update_object(self, ref, doc, root, parent, comm):
        self._legend = None
        super()._update_object(ref, doc, root, parent, comm)

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k not in [
                    'default_layout', 'object', 'max_data_size', 'spacing', 'origin'
                ]}

    def _update(self, model):
        self._volume_data = self._get_volume_data()
        if self._volume_data:
            self.param.slice_i.bounds = (0, self._volume_data['dims'][0]-1)
            self.slice_i = (self._volume_data['dims'][0]-1)//2
            self.param.slice_j.bounds = (0, self._volume_data['dims'][1]-1)
            self.slice_j = (self._volume_data['dims'][1]-1)//2
            self.param.slice_k.bounds = (0, self._volume_data['dims'][2]-1)
            self.slice_k = (self._volume_data['dims'][2]-1)//2
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
            available_serializer = [v for k, v in self._serializers.items() if isinstance(self.object, k)]
            if not available_serializer:
                import vtk
                from vtk.util import numpy_support

                def volume_serializer(imageData):
                    array = numpy_support.vtk_to_numpy(imageData.GetPointData().GetScalars())
                    dims = imageData.GetDimensions()[::-1]
                    self.spacing = imageData.GetSpacing()[::-1]
                    self.origin = imageData.GetOrigin()
                    return self._volume_from_array(self._subsample_array(array.reshape(dims, order='C')))

                self.register_serializer(vtk.vtkImageData, volume_serializer)
                serializer = volume_serializer
            else:
                serializer = available_serializer[0]
            return serializer(self.object)

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

    _rerender_params = ['axes', 'object', 'serialize_on_instantiation']

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
        super()._update_object(ref, doc, root, parent, comm)

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
