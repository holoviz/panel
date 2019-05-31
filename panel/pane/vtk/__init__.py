
from .vtk import VTK

try:
    import vtk
    from .vtkjs_serializer import render_window_serializer
    VTK.set_serializer(render_window_serializer)
except ImportError:
    pass
