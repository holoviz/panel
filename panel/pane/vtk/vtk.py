# coding: utf-8
"""
Defines a VTKPane which renders a vtk plot using VTKPlot bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import sys
import os
import base64

try:
    from urllib.request import urlopen
except ImportError: # python 2
    from urllib import urlopen

from six import string_types

import param
import numpy as np

from pyviz_comms import JupyterComm

from ..base import PaneBase

if sys.version_info >= (2, 7):
    base64encode = lambda x: base64.b64encode(x).decode('utf-8')
else:
    base64encode = lambda x: x.encode('base64')


class VTKVolume(PaneBase):
    _updates = True
    _serializers = {}

    spacing = param.Tuple(default=(1, 1, 1), length=3, doc="Distance between voxel in each direction")
    max_data_size = param.Number(default=(256 ** 3) * 2 / 1e6, doc="Maximum data size transfert allowed without subsampling")
    origin = param.Tuple(default=None, length=3, allow_None=True)

    def __init__(self, obj=None, **params):
        super(VTKVolume, self).__init__(obj, **params)
        self._sub_spacing = self.spacing

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
        volume_data = self._get_volume_data()

        model = VTKVolumePlot(data=volume_data,
                              **props)
        if root is None:
            root = model
        self._link_props(model, ['data'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update_object(self, old_model, doc, root, parent, comm):
        self._legend = None
        super()._update_object(old_model, doc, root, parent, comm)

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k not in ['default_layout', 'object', 'max_data_size', 'spacing', 'origin']}

    def _update(self, model):
        model.data = self._get_volume_data()

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
                    dtype=sub_array.dtype.name)

    def _get_volume_data(self):
        if self.object is None:
            return None
        elif isinstance(self.object, np.ndarray):
            return self._volume_from_array(self._subsample_array(self.object))
        else:
            available_serializer = [v for k, v in VTKVolume._serializers.items() if isinstance(self.object, k)]
            if len(available_serializer) == 0:
                import vtk
                from vtk.util import numpy_support

                def volume_serializer(imageData):
                    array = numpy_support.vtk_to_numpy(imageData.GetPointData().GetScalars())
                    dims = imageData.GetDimensions()[::-1]
                    self.spacing = imageData.GetSpacing()[::-1]
                    self.origin = imageData.GetOrigin()
                    return self._volume_from_array(self._subsample_array(array.reshape(dims, order='C')))

                VTKVolume.register_serializer(vtk.vtkImageData, volume_serializer)
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
                sub_array = array[::int(np.ceil(dowsnscale_factor[0])), ::int(np.ceil(dowsnscale_factor[1])), ::int(np.ceil(dowsnscale_factor[2]))]
            self._sub_spacing = tuple(e / (s - 1) for e, s in zip(extent, sub_array.shape))
        else:
            sub_array = array
            self._sub_spacing = self.spacing
        return sub_array


class VTK(PaneBase):
    """
    VTK panes allow rendering VTK objects.
    """

    serialize_on_instantiation = param.Boolean(default=True, doc="""
        Define if the object serialization occurs at panel instantiation
        or when the panel is displayed.
    """)

    camera = param.Dict(doc="""State of the rendered VTK camera.""")

    enable_keybindings = param.Boolean(default=False, doc="""
        Activate/Deactivate keys binding.

        Warning: These keys bind may not work as expected in a notebook
        context if they interact with already binded keys.
    """)

    orientation_widget = param.Boolean(default=False, doc="""
        Activate/Deactivate the orientation widget display.
    """)

    _updates = True
    _serializers = {}

    def __init__(self, obj=None, **params):
        super(VTK, self).__init__(obj, **params)
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
        self._link_props(model, ['data', 'camera', 'enable_keybindings', 'orientation_widget'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update_object(self, old_model, doc, root, parent, comm):
        self._legend = None
        super()._update_object(old_model, doc, root, parent, comm)

    def construct_colorbars(self, orientation='horizontal'):
        if self._legend is None:
            try:
                from .vtkjs_serializer import construct_palettes
                self._legend = construct_palettes(self.object)
            except:
                self._legend = {}
        if self._legend:
            from bokeh.models import Plot, LinearColorMapper, ColorBar, FixedTicker
            if orientation == 'horizontal':
                cbs = []
                for k, v in self._legend.items():
                    ticks = np.linspace(v['low'], v['high'], 5)
                    cbs.append(ColorBar(color_mapper=LinearColorMapper(low=v['low'], high=v['high'], palette=v['palette']), title=k,
                                        ticker=FixedTicker(ticks=ticks),
                                        label_standoff=5, background_fill_alpha=0, orientation='horizontal', location=(0, 0)))
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
                if v is not None and k not in ['default_layout', 'object', 'infer_legend', 'serialize_on_instantiation']}

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
                if os.path.isfile(self.object):
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

