# coding: utf-8
"""
Defines a VTKPane which renders a vtk plot using VTKPlot bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import sys
import os

try:
    from urllib.request import urlopen
except ImportError: # python 2
    from urllib import urlopen

from six import string_types

from bokeh.models import ColumnDataSource

import param

from pyviz_comms import JupyterComm

from ..base import PaneBase
from ...widgets import StaticText

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

    _updates = True
    _serializers = {}

    scene = param.String(doc="""Description of the VTK scene""")
    arrays = param.Dict(doc="""Dict of gzipped VTK data arrays""")

    _rerender_params = ['object', 'scene']

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

        self.scene, self.arrays = self._get_vtkjs()

        props = self._process_param_change(self._init_properties())
        model = VTKPlot(**props)

        if root is None:
            root = model
        self._link_props(model, [ 'scene', 'arrays', 'camera', 'enable_keybindings'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

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
        else:
            available_serializer = [v for k, v in VTK._serializers.items() if isinstance(self.object, k)]
            if len(available_serializer) == 0:
                import vtk
                from .vtkjs_serializer import render_window_serializer
                VTK.register_serializer(vtk.vtkRenderWindow, render_window_serializer)
                serializer = render_window_serializer
            else:
                serializer = available_serializer[0]
            return serializer(self.object)
        return (None, None)

    def _update(self, model):
        model.scene, local_arrays = self._get_vtkjs()
        model.arrays.update(local_arrays)

