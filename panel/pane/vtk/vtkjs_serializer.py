# coding: utf-8
"""
Serializer of vtk render windows
Adpation from :
https://kitware.github.io/vtk-js/examples/SceneExplorer.html
https://raw.githubusercontent.com/Kitware/vtk-js/master/Utilities/ParaView/export-scene-macro.py
Licence :
https://github.com/Kitware/vtk-js/blob/master/LICENSE
"""

import vtk
import base64, ctypes, io, json, os, sys, zipfile

if sys.version_info >= (2, 7):
    base64encode = lambda x: base64.b64encode(x).decode('utf-8')
else:
    base64encode = lambda x: x.encode('base64')

def render_window_serializer(render_window):
    """
    Function to convert a vtk render window in a vtk-js scene.
    """
    render_window.OffScreenRenderingOn()
    render_window.Render()

    partitioned_exporter = vtk.vtkJSONRenderWindowExporter()
    partitioned_archiver = vtk.vtkPartitionedArchiver()
    partitioned_exporter.SetArchiver(partitioned_archiver)
    partitioned_exporter.SetRenderWindow(render_window)
    partitioned_exporter.Write()

    arrays = {}
    scene = None
    
    for i in range(partitioned_archiver.GetNumberOfBuffers()):
        buffer_name = partitioned_archiver.GetBufferName(i)
        ptr = partitioned_archiver.GetBufferAddress(buffer_name)
        address = int(ptr[1:-7], 16)
        ArrayType = ctypes.c_byte*partitioned_archiver.GetBufferSize(buffer_name)
        b = ArrayType.from_address(address)
    
        stream = io.BytesIO(b)
    
        filename = os.path.split(buffer_name)[-1]
        if len(filename) != 32:
            with zipfile.ZipFile(stream) as zf:
                encoded_scene = zf.read(zf.infolist()[0])
                scene = encoded_scene.decode("utf-8")
        else:
            if not filename in arrays:
                arrays[filename] = base64encode(stream.read())

    return (scene, arrays)
