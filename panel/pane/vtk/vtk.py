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
    _serializer = None

    @classmethod
    def applies(cls, obj):
        if isinstance(obj, string_types) and obj.endswith('.vtkjs'):
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

        data = self._get_vtkjs()
        props = self._process_param_change(self._init_properties())
        model = VTKPlot(data=data, **props)
        if root is None:
            root = model
        self._link_props(model, ['data', 'camera', 'enable_keybindings'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    @classmethod
    def set_serializer(cls, serializer):
        """
        A serializer is a function which take a `vtk` render window as input
        and return the binary zip stream of the corresponding `vtkjs` file 
        """
        cls._serializer = serializer

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
            if VTK._serializer is None:
                from .vtkjs_serializer import render_window_serializer
                VTK.set_serializer(render_window_serializer)
            vtkjs = VTK._serializer(self.object).read()
        return base64encode(vtkjs) if vtkjs is not None else vtkjs

    def _update(self, model):
        model.data = self._get_vtkjs()

