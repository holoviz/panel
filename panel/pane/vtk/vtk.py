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

from pyviz_comms import JupyterComm

from ..base import PaneBase

if sys.version_info >= (2, 7):
    base64encode = lambda x: base64.b64encode(x).decode('utf-8')
else:
    base64encode = lambda x: x.encode('base64')


class VTKVolume(PaneBase):
    _updates = True
    _serializers = {}

    @classmethod
    def applies(cls, obj):
        if (isinstance(obj, string_types) and obj.endswith('.vti') or
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

        volume_serial = self._serialize()
        data = base64encode(volume_serial) if volume_serial is not None else volume_serial
        props = self._process_param_change(self._init_properties())
        model = VTKVolumePlot(data=data, **props)
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
                if v is not None and k not in ['default_layout', 'object']}

    @classmethod
    def register_serializer(cls, class_type, serializer):
        """
        Register a seriliazer for a given type of class.
        A serializer is a function which take an instance of `class_type`
        (like a vtk.vtkRenderWindow) as input and return the binary zip
        stream of the corresponding `vtkjs` file
        """
        cls._serializers.update({class_type:serializer})

    def _serialize(self):
        if self.object is None:
            volume_serial = None
        elif isinstance(self.object, string_types) and self.object.endswith('.vti'):
            if os.path.isfile(self.object):
                with open(self.object, 'rb') as f:
                    volume_serial = f.read()
            else:
                data_url = urlopen(self.object)
                volume_serial = data_url.read()
        elif hasattr(self.object, 'read'):
            volume_serial = self.object.read()
        else:
            available_serializer = [v for k, v in VTK._serializers.items() if isinstance(self.object, k)]
            if len(available_serializer) == 0:
                import vtk
                if isinstance(self.object, vtk.vtkImageData):
                    from .vtkjs_serializer import volume_serializer

                    VTK.register_serializer(vtk.vtkImageData, volume_serializer)
                    serializer = volume_serializer

            else:
                serializer = available_serializer[0]
            volume_serial = serializer(self.object)

        return volume_serial

    def _update(self, model):
        volume_serial = self._serialize()
        model.data = base64encode(volume_serial) if volume_serial is not None else volume_serial


class VTK(PaneBase):
    """
    VTK panes allow rendering VTK objects.
    """

    camera = param.Dict(doc="""State of the rendered VTK camera.""")

    enable_keybindings = param.Boolean(default=False, doc="""
        Activate/Deactivate keys binding.

        Warning: These keys bind may not work as expected in a notebook
        context if they interact with already binded keys
    """)

    orientation_widget = param.Boolean(default=False, doc="""
        Activate/Deactivate the orientation widget display.
    """)

    event_sources = param.List(default=[], doc="""
        List of ColumnDataSource to enable custom interaction
    """)

    _updates = True
    _serializers = {}
    _rename = {'event_sources': 'data_sources'}

    def __init__(self, obj=None, **params):
        super(VTK, self).__init__(obj, **params)
        self._legend = None

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
            import numpy as np
            from bokeh.plotting import figure
            from bokeh.models import LinearColorMapper, ColorBar, FixedTicker
            if orientation == 'horizontal':
                cbs = []
                for k, v in self._legend.items():
                    ticks = np.linspace(v['low'], v['high'], 5)
                    cbs.append(ColorBar(color_mapper=LinearColorMapper(low=v['low'], high=v['high'], palette=v['palette']), title=k,
                                        ticker=FixedTicker(ticks=ticks),
                                        label_standoff=5, background_fill_alpha=0, orientation='horizontal', location=(0, 0)))
                plot = figure(x_range=(0, 1), y_range=(0, 1), toolbar_location=None, height=90 * len(cbs),
                              sizing_mode='stretch_width')
                plot.xaxis.visible = False
                plot.yaxis.visible = False
                plot.grid.visible = False
                plot.outline_line_alpha = 0
                [plot.add_layout(cb, 'below') for cb in cbs]
                return plot
            else:
                raise ValueError('orientation can only be horizontal')
        else:
            return None

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k not in ['default_layout', 'object', 'infer_legend']}

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
        if self.object is None:
            vtkjs = None
        elif isinstance(self.object, string_types) and self.object.endswith('.vtkjs'):
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

        return vtkjs

    def _update(self, model):
        vtkjs = self._get_vtkjs()
        model.data = base64encode(vtkjs) if vtkjs is not None else vtkjs

    def export_vtkjs(self, filename='vtk_panel.vtkjs'):
        with open(filename, 'wb') as f:
            f.write(self._get_vtkjs())

