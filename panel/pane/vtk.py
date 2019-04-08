# coding: utf-8
"""
Defines a VTKPane which renders a vtk plot using VTKPlot
bokeh model.
Adpation from :
https://kitware.github.io/vtk-js/examples/SceneExplorer.html
Licence :
https://github.com/Kitware/vtk-js/blob/master/LICENSE
"""
from __future__ import absolute_import, division, unicode_literals

import sys
import os
import json
import base64
import random
import string
import hashlib
import zipfile

try:
    from urllib.request import urlopen
except ImportError: # python 2
    from urllib import urlopen

from io import BytesIO
from six import string_types

import param

from bokeh.util.dependencies import import_optional
from pyviz_comms import JupyterComm

from .base import PaneBase

vtk = import_optional('vtk')

arrayTypesMapping = '  bBhHiIlLfdL' # last one is idtype

_js_mapping = {
        'b': 'Int8Array',
        'B': 'Uint8Array',
        'h': 'Int16Array',
        'H': 'Int16Array',
        'i': 'Int32Array',
        'I': 'Uint32Array',
        'l': 'Int32Array',
        'L': 'Uint32Array',
        'f': 'Float32Array',
        'd': 'Float64Array'
}

_writer_mapping = {}


def _random_name():
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(16)])


def _get_range_info(array, component):
    r = array.GetRange(component)
    compRange = {}
    compRange['min'] = r[0]
    compRange['max'] = r[1]
    compRange['component'] = array.GetComponentName(component)
    return compRange


def _get_ref(destDirectory, md5):
    ref = {}
    ref['id'] = md5
    ref['encode'] = 'BigEndian' if sys.byteorder == 'big' else 'LittleEndian'
    ref['basepath'] = destDirectory
    return ref


def _get_object_id(obj, objIds):
    try:
        idx = objIds.index(obj)
        return idx + 1
    except ValueError:
        objIds.append(obj)
        return len(objIds)


def _dump_data_array(scDirs, datasetDir, dataDir, array, root={}, compress=True):
    if not array:
        return None

    if array.GetDataType() == 12:
        # IdType need to be converted to Uint32
        arraySize = array.GetNumberOfTuples() * array.GetNumberOfComponents()
        newArray = vtk.vtkTypeUInt32Array()
        newArray.SetNumberOfTuples(arraySize)
        for i in range(arraySize):
            newArray.SetValue(i, -1 if array.GetValue(i) < 0 else array.GetValue(i))
        pBuffer = memoryview(newArray)
    else:
        pBuffer = memoryview(array)

    pMd5 = hashlib.md5(pBuffer).hexdigest()
    pPath = os.path.join(dataDir, pMd5)

    scDirs.append([pPath, bytes(pBuffer)])

    if compress:
        raise NotImplementedError('TODO')

    root['ref'] = _get_ref(os.path.relpath(dataDir, datasetDir), pMd5)
    root['vtkClass'] = 'vtkDataArray'
    root['name'] = array.GetName()
    root['dataType'] = _js_mapping[arrayTypesMapping[array.GetDataType()]]
    root['numberOfComponents'] = array.GetNumberOfComponents()
    root['size'] = array.GetNumberOfComponents() * array.GetNumberOfTuples()
    root['ranges'] = []
    if root['numberOfComponents'] > 1:
        for i in range(root['numberOfComponents']):
            root['ranges'].append(_get_range_info(array, i))
        root['ranges'].append(_get_range_info(array, -1))
    else:
        root['ranges'].append(_get_range_info(array, 0))

    return root


def _dump_color_array(scDirs, datasetDir, dataDir, colorArrayInfo, root={}, compress=True):
    root['pointData'] = {
        'vtkClass': 'vtkDataSetAttributes',
        "activeGlobalIds":-1,
        "activeNormals":-1,
        "activePedigreeIds":-1,
        "activeScalars":-1,
        "activeTCoords":-1,
        "activeTensors":-1,
        "activeVectors":-1,
        "arrays": []
    }
    root['cellData'] = {
        'vtkClass': 'vtkDataSetAttributes',
        "activeGlobalIds":-1,
        "activeNormals":-1,
        "activePedigreeIds":-1,
        "activeScalars":-1,
        "activeTCoords":-1,
        "activeTensors":-1,
        "activeVectors":-1,
        "arrays": []
    }
    root['fieldData'] = {
        'vtkClass': 'vtkDataSetAttributes',
        "activeGlobalIds":-1,
        "activeNormals":-1,
        "activePedigreeIds":-1,
        "activeScalars":-1,
        "activeTCoords":-1,
        "activeTensors":-1,
        "activeVectors":-1,
        "arrays": []
    }

    colorArray = colorArrayInfo['colorArray']
    location = colorArrayInfo['location']

    dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, colorArray, {}, compress)

    if dumpedArray:
        root[location]['activeScalars'] = 0
        root[location]['arrays'].append({ 'data': dumpedArray })

    return root


def _dump_tcoords(scDirs, datasetDir, dataDir, dataset, root={}, compress=True):
    tcoords = dataset.GetPointData().GetTCoords()
    if tcoords:
        dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, tcoords, {}, compress)
        root['pointData']['activeTCoords'] = len(root['pointData']['arrays'])
        root['pointData']['arrays'].append({ 'data': dumpedArray })


def _dump_normals(scDirs, datasetDir, dataDir, dataset, root={}, compress=True):
    normals = dataset.GetPointData().GetNormals()
    if normals:
        dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, normals, {}, compress)
        root['pointData']['activeNormals'] = len(root['pointData']['arrays'])
        root['pointData']['arrays'].append({ 'data': dumpedArray })


def _dump_all_arrays(scDirs, datasetDir, dataDir, dataset, root={}, compress=True):
    root['pointData'] = {
        'vtkClass': 'vtkDataSetAttributes',
        "activeGlobalIds":-1,
        "activeNormals":-1,
        "activePedigreeIds":-1,
        "activeScalars":-1,
        "activeTCoords":-1,
        "activeTensors":-1,
        "activeVectors":-1,
        "arrays": []
    }
    root['cellData'] = {
        'vtkClass': 'vtkDataSetAttributes',
        "activeGlobalIds":-1,
        "activeNormals":-1,
        "activePedigreeIds":-1,
        "activeScalars":-1,
        "activeTCoords":-1,
        "activeTensors":-1,
        "activeVectors":-1,
        "arrays": []
    }
    root['fieldData'] = {
        'vtkClass': 'vtkDataSetAttributes',
        "activeGlobalIds":-1,
        "activeNormals":-1,
        "activePedigreeIds":-1,
        "activeScalars":-1,
        "activeTCoords":-1,
        "activeTensors":-1,
        "activeVectors":-1,
        "arrays": []
    }

    # Point data
    pd = dataset.GetPointData()
    pd_size = pd.GetNumberOfArrays()
    for i in range(pd_size):
        array = pd.GetArray(i)
        if array:
            dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, array, {}, compress)
            root['pointData']['activeScalars'] = 0
            root['pointData']['arrays'].append({ 'data': dumpedArray })

    # Cell data
    cd = dataset.GetCellData()
    cd_size = pd.GetNumberOfArrays()
    for i in range(cd_size):
        array = cd.GetArray(i)
        if array:
            dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, array, {}, compress)
            root['cellData']['activeScalars'] = 0
            root['cellData']['arrays'].append({ 'data': dumpedArray })

    return root


def _dump_poly_data(scDirs, datasetDir, dataDir, dataset, colorArrayInfo, root={}, compress=True):
    root['vtkClass'] = 'vtkPolyData'
    container = root

    # Points
    points = _dump_data_array(scDirs, datasetDir, dataDir, dataset.GetPoints().GetData(), {}, compress)
    points['vtkClass'] = 'vtkPoints'
    container['points'] = points

    # Cells
    _cells = container

    # # Verts
    if dataset.GetVerts() and dataset.GetVerts().GetData().GetNumberOfTuples() > 0:
        _verts = _dump_data_array(scDirs, datasetDir, dataDir, dataset.GetVerts().GetData(), {}, compress)
        _cells['verts'] = _verts
        _cells['verts']['vtkClass'] = 'vtkCellArray'

    # # Lines
    if dataset.GetLines() and dataset.GetLines().GetData().GetNumberOfTuples() > 0:
        _lines = _dump_data_array(scDirs, datasetDir, dataDir, dataset.GetLines().GetData(), {}, compress)
        _cells['lines'] = _lines
        _cells['lines']['vtkClass'] = 'vtkCellArray'

    # # Polys
    if dataset.GetPolys() and dataset.GetPolys().GetData().GetNumberOfTuples() > 0:
        _polys = _dump_data_array(scDirs, datasetDir, dataDir, dataset.GetPolys().GetData(), {}, compress)
        _cells['polys'] = _polys
        _cells['polys']['vtkClass'] = 'vtkCellArray'

    # # Strips
    if dataset.GetStrips() and dataset.GetStrips().GetData().GetNumberOfTuples() > 0:
        _strips = _dump_data_array(scDirs, datasetDir, dataDir, dataset.GetStrips().GetData(), {}, compress)
        _cells['strips'] = _strips
        _cells['strips']['vtkClass'] = 'vtkCellArray'

    _dump_color_array(scDirs, datasetDir, dataDir, colorArrayInfo, container, compress)

    # # PointData TCoords
    _dump_tcoords(scDirs, datasetDir, dataDir, dataset, container, compress)

    return root


_writer_mapping['vtkPolyData'] = _dump_poly_data


def _dump_image_data(scDirs, datasetDir, dataDir, dataset, colorArrayInfo, root={}, compress=True):
    root['vtkClass'] = 'vtkImageData'
    container = root

    container['spacing'] = dataset.GetSpacing()
    container['origin'] = dataset.GetOrigin()
    container['extent'] = dataset.GetExtent()

    _dump_all_arrays(scDirs, datasetDir, dataDir, dataset, container, compress)

    return root


_writer_mapping['vtkImageData'] = _dump_image_data


def _write_data_set(scDirs, dataset, colorArrayInfo, newDSName, compress=True):

    dataDir = os.path.join(newDSName, 'data')

    root = {}
    root['metadata'] = {}
    root['metadata']['name'] = newDSName

    writer = _writer_mapping[dataset.GetClassName()]
    if writer:
        writer(scDirs, newDSName, dataDir, dataset, colorArrayInfo, root, compress)
    else:
        print(dataset.GetClassName(), 'is not supported')

    scDirs.append([os.path.join(newDSName, 'index.json'), json.dumps(root, indent=2)])


class VTK(PaneBase):
    """
    VTK panes allow rendering VTK objects.
    """

    camera = param.Dict(doc="""State of the rendered VTK camera.""")

    _updates = True

    @classmethod
    def applies(cls, obj):
        return (isinstance(obj, getattr(vtk, 'vtkRenderWindow', type(None))) or
                hasattr(obj, 'read') or (isinstance(obj, string_types) and obj.endswith('.vtkjs')))

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
            from ..models.vtk import VTKPlot
        else:
            VTKPlot = getattr(sys.modules['panel.models.vtk'], 'VTKPlot')

        data = self._get_vtkjs()
        props = self._process_param_change(self._init_properties())
        model = VTKPlot(data=data, **props)
        if root is None:
            root = model
        self._link_props(model, ['data', 'camera'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _get_vtkjs(self):
        if self.object is None:
            vtkjs = None
        elif isinstance(self.object, string_types) and self.object.endswith('.vtkjs'):
            if os.path.isfile(self.object):
                with open(self.object, 'rb') as f:
                    vtkjs = base64.b64encode(f.read()).decode('utf-8')
            else:
                data_url = urlopen(self.object)
                vtkjs = base64.b64encode(data_url.read()).decode('utf-8')
        elif hasattr(self.object, 'read'):
            vtkjs = base64.b64encode(self.object.read()).decode('utf-8')
        else:
            vtkjs = self._vtksjs_from_render_window(self.object)
        return vtkjs

    def _update(self, model):
        model.data = self._get_vtkjs()

    def _vtksjs_from_render_window(self, render_window):
        render_window.OffScreenRenderingOn() # to not pop a vtk windows
        render_window.Render()
        renderers = render_window.GetRenderers()

        doCompressArrays = False

        objIds = []
        scDirs = []

        sceneComponents = []
        textureToSave = {}

        for renderer in renderers:
            renProps = renderer.GetViewProps()
            for rpIdx in range(renProps.GetNumberOfItems()):
                renProp = renProps.GetItemAsObject(rpIdx)
                if not renProp.GetVisibility():
                    continue
                if hasattr(renProp, 'GetMapper'):
                    mapper = renProp.GetMapper()
                    if mapper is None:
                        continue
                    dataObject = mapper.GetInputDataObject(0, 0);
                    dataset = None

                    if dataObject.IsA('vtkCompositeDataSet'):
                        if dataObject.GetNumberOfBlocks() == 1:
                            dataset = dataObject.GetBlock(0)
                        else:
                            gf = vtk.vtkCompositeDataGeometryFilter()
                            gf.SetInputData(dataObject)
                            gf.Update()
                            dataset = gf.GetOutput()
                    elif dataObject.IsA('vtkUnstructuredGrid'):
                        gf = vtk.vtkGeometryFilter()
                        gf.SetInputData(dataObject)
                        gf.Update()
                        dataset = gf.GetOutput()
                    else:
                        dataset = mapper.GetInput()
                        
                    if dataset and not isinstance(dataset, (vtk.vtkPolyData)):
                        # All data must be PolyData surfaces!
                        gf = vtk.vtkGeometryFilter()
                        gf.SetInputData(dataset)
                        gf.Update()
                        dataset = gf.GetOutputDataObject(0)

                    if dataset and dataset.GetPoints():
                        componentName = str(id(renProp))
                        scalarVisibility = mapper.GetScalarVisibility()
                        arrayAccessMode = mapper.GetArrayAccessMode()
                        colorArrayName = mapper.GetArrayName() if arrayAccessMode == 1 else mapper.GetArrayId()
                        colorMode = mapper.GetColorMode()
                        scalarMode = mapper.GetScalarMode()
                        lookupTable = mapper.GetLookupTable()

                        dsAttrs = None
                        arrayLocation = ''

                        if scalarVisibility:
                            if scalarMode == 0:
                                # By default (ScalarModeToDefault), the filter will use point data,
                                # and if no point data is available, then cell data is used
                                # https://vtk.org/doc/nightly/html/classvtkMapper.html#af330900726eb1a5e18e5f7f557306e52
                                if dataset.GetPointData().GetNumberOfArrays() >= 1:
                                    dsAttrs = dataset.GetPointData()
                                    arrayLocation = 'pointData'
                                else:
                                    dsAttrs = dataset.GetCellData()
                                    arrayLocation = 'cellData'
                            if scalarMode == 3 or scalarMode == 1: # VTK_SCALAR_MODE_USE_POINT_FIELD_DATA or VTK_SCALAR_MODE_USE_POINT_DATA
                                dsAttrs = dataset.GetPointData()
                                arrayLocation = 'pointData'
                            elif scalarMode == 4 or scalarMode == 2: # VTK_SCALAR_MODE_USE_CELL_FIELD_DATA or VTK_SCALAR_MODE_USE_CELL_DATA
                                dsAttrs = dataset.GetCellData()
                                arrayLocation = 'cellData'

                        colorArray = None
                        dataArray = None

                        if dsAttrs:
                            if colorArrayName >= 0:
                                dataArray = dsAttrs.GetArray(colorArrayName)
                            elif dsAttrs.GetNumberOfArrays() >= 1:
                                dataArray = dsAttrs.GetArray(0)

                        if dataArray:
                            # component = -1 => let specific instance get scalar from vector before mapping
                            colorArray = lookupTable.MapScalars(dataArray, colorMode, -1);
                            colorArrayName = '__CustomRGBColorArray__'
                            colorArray.SetName(colorArrayName)
                            colorMode = 0
                        else:
                            colorArrayName = ''

                        colorArrayInfo = {
                            'colorArray': colorArray,
                            'location': arrayLocation
                        }

                        _write_data_set(scDirs, dataset, colorArrayInfo, newDSName=componentName, compress=doCompressArrays)

                        # Handle texture if any
                        textureName = None
                        if renProp.GetTexture() and renProp.GetTexture().GetInput():
                            textureData = renProp.GetTexture().GetInput()
                            textureName = 'texture_%d' % _get_object_id(textureData, objIds);
                            textureToSave[textureName] = textureData

                        representation = renProp.GetProperty().GetRepresentation() if hasattr(renProp, 'GetProperty') else 2
                        if representation == 1:
                            colorToUse = renProp.GetProperty().GetColor() if hasattr(renProp, 'GetProperty') else [1, 1, 1]
                        else:
                            colorToUse = renProp.GetProperty().GetDiffuseColor() if hasattr(renProp, 'GetProperty') else [1, 1, 1]
                        pointSize = renProp.GetProperty().GetPointSize() if hasattr(renProp, 'GetProperty') else 1.0
                        opacity = renProp.GetProperty().GetOpacity() if hasattr(renProp, 'GetProperty') else 1.0
                        edgeVisibility = renProp.GetProperty().GetEdgeVisibility() if hasattr(renProp, 'GetProperty') else False

                        p3dPosition = renProp.GetPosition() if renProp.IsA('vtkProp3D') else [0, 0, 0]
                        p3dScale = renProp.GetScale() if renProp.IsA('vtkProp3D') else [1, 1, 1]
                        p3dOrigin = renProp.GetOrigin() if renProp.IsA('vtkProp3D') else [0, 0, 0]
                        p3dRotateWXYZ = renProp.GetOrientationWXYZ() if renProp.IsA('vtkProp3D') else [0, 0, 0, 0]

                        sceneComponents.append({
                            "name": componentName,
                            "type": "httpDataSetReader",
                            "httpDataSetReader": {
                                "url": componentName
                            },
                            "actor": {
                                "origin": p3dOrigin,
                                "scale": p3dScale,
                                "position": p3dPosition,
                            },
                            "actorRotation": p3dRotateWXYZ,
                            "mapper": {
                                "colorByArrayName": colorArrayName,
                                "colorMode": colorMode,
                                "scalarMode": scalarMode
                            },
                            "property": {
                                "representation": representation,
                                "edgeVisibility": edgeVisibility,
                                "diffuseColor": colorToUse,
                                "pointSize": pointSize,
                                "opacity": opacity
                            },
                            "lookupTable": {
                                "tableRange": lookupTable.GetRange(),
                                "hueRange": lookupTable.GetHueRange() if hasattr(lookupTable, 'GetHueRange') else [0.5, 0]
                            }
                        })

                        if textureName:
                            sceneComponents[-1]['texture'] = textureName

        # Save texture data if any
        for key, val in textureToSave.items():
            _write_data_set(scDirs, val, None, newDSName=key, compress=doCompressArrays)

        activeCamera = renderer.GetActiveCamera()
        background = renderer.GetBackground()
        sceneDescription = {
            "fetchGzip": doCompressArrays,
            "background": background,
            "camera": {
                "focalPoint": activeCamera.GetFocalPoint(),
                "position": activeCamera.GetPosition(),
                "viewUp": activeCamera.GetViewUp(),
                "clippingRange": activeCamera.GetClippingRange()
            },
            "centerOfRotation": renderer.GetCenter(),
            "scene": sceneComponents,
        }

        scDirs.append(['index.json', json.dumps(sceneDescription, indent=4)])

        compression = zipfile.ZIP_DEFLATED
        in_memory = BytesIO()
        zf = zipfile.ZipFile(in_memory, mode="w")
        try:
            for dirPath, data in (scDirs):
                zf.writestr(dirPath, data, compress_type=compression)
        finally:
                zf.close()

        in_memory.seek(0)
        return base64.b64encode(in_memory.read()).decode('utf-8')
