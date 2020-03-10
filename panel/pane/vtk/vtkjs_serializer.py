# coding: utf-8
"""
Serializer of vtk render windows
Adpation from :
https://kitware.github.io/vtk-js/examples/SceneExplorer.html
https://raw.githubusercontent.com/Kitware/vtk-js/master/Utilities/ParaView/export-scene-macro.py
Licence :
https://github.com/Kitware/vtk-js/blob/master/LICENSE
"""

import os, sys, json, hashlib, zipfile
from io import BytesIO

if sys.version_info < (3,):
    import imp
    vtk = imp.load_module('vtk', *imp.find_module('vtk'))
else:
    import vtk

from .enums import SCALAR_MODE, ACCESS_MODE

if sys.version_info >= (2, 7):
    buffer = memoryview
else:
    buffer = buffer

arrayTypesMapping = [
  ' ', # VTK_VOID            0
  ' ', # VTK_BIT             1
  'b', # VTK_CHAR            2
  'B', # VTK_UNSIGNED_CHAR   3
  'h', # VTK_SHORT           4
  'H', # VTK_UNSIGNED_SHORT  5
  'i', # VTK_INT             6
  'I', # VTK_UNSIGNED_INT    7
  'l', # VTK_LONG            8
  'L', # VTK_UNSIGNED_LONG   9
  'f', # VTK_FLOAT          10
  'd', # VTK_DOUBLE         11
  'L', # VTK_ID_TYPE        12
]

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


def _dump_data_array(scDirs, datasetDir, dataDir, array):
    root = {}
    if not array:
        return None

    if array.GetDataType() == 12:
        # IdType need to be converted to Uint32
        arraySize = array.GetNumberOfTuples() * array.GetNumberOfComponents()
        newArray = vtk.vtkTypeUInt32Array()
        newArray.SetNumberOfTuples(arraySize)
        for i in range(arraySize):
            newArray.SetValue(i, -1 if array.GetValue(i) < 0 else array.GetValue(i))
        pBuffer = buffer(newArray)
    else:
        pBuffer = buffer(array)

    pMd5 = hashlib.md5(pBuffer).hexdigest()
    pPath = os.path.join(dataDir, pMd5)

    scDirs.append([pPath, bytes(pBuffer)])

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


def _dump_color_array(scDirs, datasetDir, dataDir, colorArrayInfo, root):
    for data_loc in ['pointData', 'cellData', 'fieldData']:
        root[data_loc] = {
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

    dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, colorArray)

    if dumpedArray:
        root[location]['activeScalars'] = 0
        root[location]['arrays'].append({ 'data': dumpedArray })


def _dump_tcoords(scDirs, datasetDir, dataDir, dataset, root):
    tcoords = dataset.GetPointData().GetTCoords()
    if tcoords:
        dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, tcoords)
        root['pointData']['activeTCoords'] = len(root['pointData']['arrays'])
        root['pointData']['arrays'].append({ 'data': dumpedArray })


def _dump_normals(scDirs, datasetDir, dataDir, dataset, root):
    normals = dataset.GetPointData().GetNormals()
    if normals:
        dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, normals)
        root['pointData']['activeNormals'] = len(root['pointData']['arrays'])
        root['pointData']['arrays'].append({ 'data': dumpedArray })


def _dump_all_arrays(scDirs, datasetDir, dataDir, dataset, root):
    for data_loc in ['pointData', 'cellData', 'fieldData']:
        root[data_loc] = {
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
            dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, array)
            root['pointData']['activeScalars'] = 0
            root['pointData']['arrays'].append({ 'data': dumpedArray })

    # Cell data
    cd = dataset.GetCellData()
    cd_size = pd.GetNumberOfArrays()
    for i in range(cd_size):
        array = cd.GetArray(i)
        if array:
            dumpedArray = _dump_data_array(scDirs, datasetDir, dataDir, array)
            root['cellData']['activeScalars'] = 0
            root['cellData']['arrays'].append({ 'data': dumpedArray })


def _dump_poly_data(scDirs, datasetDir, dataDir, dataset, colorArrayInfo, root):
    root['vtkClass'] = 'vtkPolyData'

    # Points
    root['points'] = _dump_data_array(scDirs, datasetDir, dataDir, dataset.GetPoints().GetData())
    root['points']['vtkClass'] = 'vtkPoints'

    # Cells
    # # Verts
    for cell_type in ['verts', 'lines', 'polys', 'strips']:
        cell = getattr(dataset, 'Get' + cell_type.capitalize())()
        if cell and cell.GetData().GetNumberOfTuples() > 0:
            root[cell_type] = _dump_data_array(scDirs, datasetDir, dataDir, cell.GetData())
            root[cell_type]['vtkClass'] = 'vtkCellArray'

    _dump_color_array(scDirs, datasetDir, dataDir, colorArrayInfo, root)

    # # PointData TCoords
    _dump_tcoords(scDirs, datasetDir, dataDir, dataset, root)

    # # PointData Normals
    _dump_normals(scDirs, datasetDir, dataDir, dataset, root)


_writer_mapping['vtkPolyData'] = _dump_poly_data


def _dump_image_data(scDirs, datasetDir, dataDir, dataset, colorArrayInfo, root):
    root['vtkClass'] = 'vtkImageData'

    root['spacing'] = dataset.GetSpacing()
    root['origin'] = dataset.GetOrigin()
    root['extent'] = dataset.GetExtent()

    _dump_all_arrays(scDirs, datasetDir, dataDir, dataset, root)


_writer_mapping['vtkImageData'] = _dump_image_data


def _write_data_set(scDirs, dataset, colorArrayInfo, newDSName):

    dataDir = os.path.join(newDSName, 'data')

    root = {}
    root['metadata'] = {}
    root['metadata']['name'] = newDSName

    writer = _writer_mapping[dataset.GetClassName()]
    if writer:
        writer(scDirs, newDSName, dataDir, dataset, colorArrayInfo, root)
    else:
        raise Warning('{} is not supported'.format(dataset.GetClassName()))

    scDirs.append([os.path.join(newDSName, 'index.json'), json.dumps(root, indent=2)])


def get_dataset_scalars(dataset, scalar_mode, array_access_mode, array_id, array_name):

    if scalar_mode == SCALAR_MODE.Default:
        scalars = dataset.GetPointData().GetScalars()
        cell_flag = 'pointData'
        if not scalars:
            scalars = dataset.GetCellData().GetScalars()
            cell_flag = 'cellData'
    elif scalar_mode == SCALAR_MODE.UsePointData:
        scalars = dataset.GetPointData().GetScalars()
        cell_flag = 'pointData'
    elif scalar_mode == SCALAR_MODE.UseCellData:
        scalars = dataset.GetCellData().GetScalars()
        cell_flag = 'cellData'
    elif scalar_mode == SCALAR_MODE.UsePointFieldData:
        pd = dataset.GetPointData()
        if array_access_mode == ACCESS_MODE.ById:
            scalars = pd.GetAbstractArray(array_id)
        else:
            scalars = pd.GetAbstractArray(array_name)
        cell_flag = 'pointData'
    elif scalar_mode == SCALAR_MODE.UseCellFieldData:
        cd = dataset.GetCellData()
        if array_access_mode == ACCESS_MODE.ById:
            scalars = cd.GetAbstractArray(array_id)
        else:
            scalars = cd.GetAbstractArray(array_name)
        cell_flag = 'cellData'
    elif scalar_mode == SCALAR_MODE.UseFieldData:
        fd = dataset.GetFieldData()
        if array_access_mode == ACCESS_MODE.ById:
            scalars = fd.GetAbstractArray(array_id)
        else:
            scalars = fd.GetAbstractArray(array_name)
        cell_flag = 'fieldData'
    return scalars, cell_flag


property_list = ['color', 'ambientColor', 'diffuseColor', 'specularColor', 'edgeColor',
                 'ambient', 'diffuse', 'specular', 'specularPower', 'opacity',
                 'interpolation', 'representation', 'edgeVisibility', 'backfaceCulling',
                 'frontfaceCulling', 'pointSize', 'lineWidth', 'lighting', 'shading']


def extract_renprop_properties(renprop):
    if hasattr(renprop, 'GetProperty'): # default properties
        properties = {property_name: getattr(renprop.GetProperty(), 'Get' + property_name[0].upper() + property_name[1:])()
                      for property_name in property_list}
    else :
        properties = None
    return properties


def vtk_lut_to_palette(lut):
    if lut.GetScale() != 0:
        raise NotImplementedError('Only linear Scale lookup tables are implemented')
    scale = 'Linear'
    low, high = lut.GetTableRange()
    nb_values = lut.GetNumberOfTableValues()
    rgb_values = [lut.GetTableValue(val)[:-1] for val in range(nb_values)]
    palette = ["#{0:02x}{1:02x}{2:02x}".format(int(255 * r), int(255 * g), int(255 * b)) for r, g, b in rgb_values]
    return {"palette": palette, "low":low, "high":high, "scale": scale}


def construct_palettes(render_window):
    """
    """
    legend = {}
    render_window.OffScreenRenderingOn() # to not pop a vtk windows
    render_window.Render()
    renderers = render_window.GetRenderers()
    for renderer in renderers:
        for renProp in renderer.GetViewProps():
            if not renProp.GetVisibility() or not isinstance(renProp, vtk.vtkActor):
                continue
            if hasattr(renProp, 'GetMapper'):
                mapper = renProp.GetMapper()
                if mapper is None:
                    continue
                dataObject = mapper.GetInputDataObject(0, 0)
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
                    scalar_visibility = mapper.GetScalarVisibility()
                    array_access_mode = mapper.GetArrayAccessMode()
                    array_name = mapper.GetArrayName() # if arrayAccessMode == 1 else mapper.GetArrayId()
                    array_id = mapper.GetArrayId()
                    scalar_mode = mapper.GetScalarMode()
                    dataArray = None
                    lookupTable = mapper.GetLookupTable()

                    if scalar_visibility:
                        dataArray, _ = get_dataset_scalars(dataset, scalar_mode, array_access_mode, array_id, array_name)
                        # component = -1 => let specific instance get scalar from vector before mapping
                        if dataArray:
                            if dataArray.GetLookupTable():
                                lookupTable = dataArray.GetLookupTable()
                            if array_name and legend is not None:
                                legend.update({array_name: vtk_lut_to_palette(lookupTable)})
    return legend


def render_window_serializer(render_window):
    """
    Function to convert a vtk render window in a list of 2-tuple where first value
    correspond to a relative file path in the `vtkjs` directory structure and values
    of the binary content of the corresponding file.
    """
    render_window.OffScreenRenderingOn() # to not pop a vtk windows
    render_window.Render()
    renderers = render_window.GetRenderers()

    objIds = []
    scDirs = []

    sceneComponents = []
    textureToSave = {}

    for renderer in renderers:
        for renProp in renderer.GetViewProps():
            if not renProp.GetVisibility() or not isinstance(renProp, vtk.vtkActor):
                continue
            if hasattr(renProp, 'GetMapper'):
                mapper = renProp.GetMapper()
                if mapper is None:
                    continue
                dataObject = mapper.GetInputDataObject(0, 0)
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
                    scalar_visibility = mapper.GetScalarVisibility()
                    array_access_mode = mapper.GetArrayAccessMode()
                    array_name = mapper.GetArrayName() # if arrayAccessMode == 1 else mapper.GetArrayId()
                    array_id = mapper.GetArrayId()
                    color_mode = mapper.GetColorMode()
                    scalar_mode = mapper.GetScalarMode()

                    arrayLocation = ''
                    colorArray = None
                    dataArray = None
                    colorArrayName = ''
                    lookupTable = mapper.GetLookupTable()

                    if scalar_visibility:
                        dataArray, arrayLocation = get_dataset_scalars(dataset, scalar_mode, array_access_mode, array_id, array_name)
                        # component = -1 => let specific instance get scalar from vector before mapping
                        if dataArray:
                            if dataArray.GetLookupTable():
                                lookupTable = dataArray.GetLookupTable()
                                colorArray = dataArray.GetLookupTable().MapScalars(dataArray, color_mode, -1)
                            else:
                                colorArray = lookupTable.MapScalars(dataArray, color_mode, -1)
                            colorArrayName = '__CustomRGBColorArray__'
                            colorArray.SetName(colorArrayName)
                            color_mode = 0

                    colorArrayInfo = {
                        'colorArray': colorArray,
                        'location': arrayLocation
                    }

                    _write_data_set(scDirs, dataset, colorArrayInfo, newDSName=componentName)

                    # Handle texture if any
                    textureName = None
                    if renProp.GetTexture() and renProp.GetTexture().GetInput():
                        textureData = renProp.GetTexture().GetInput()
                        textureName = 'texture_%d' % _get_object_id(textureData, objIds)
                        textureToSave[textureName] = textureData

                    sceneComponents.append({
                        "name": componentName,
                        "type": "httpDataSetReader",
                        "httpDataSetReader": {
                            "url": componentName
                        },
                        "actor": {
                            # customProp
                            "id": renProp.__this__,
                            # vtkProp
                            "visibility": renProp.GetVisibility() if renProp.IsA('vtkProp') else 0,
                            "pickable": renProp.GetPickable()  if renProp.IsA('vtkProp') else 0,
                            "dragable": renProp.GetDragable() if renProp.IsA('vtkProp') else 0,
                            "useBounds": renProp.GetUseBounds() if renProp.IsA('vtkProp') else 0,
                            # vtkProp3D
                            "origin": renProp.GetOrigin() if renProp.IsA('vtkProp3D') else [0, 0, 0],
                            "scale": renProp.GetScale() if renProp.IsA('vtkProp3D') else [1, 1, 1],
                            "position": renProp.GetPosition() if renProp.IsA('vtkProp3D') else [0, 0, 0],
                            # vtkActor
                            'forceOpaque': renProp.GetForceOpaque() if renProp.IsA('vtkActor') else 0,
                            'forceTranslucent': renProp.GetForceTranslucent() if renProp.IsA('vtkActor') else 0,
                        },
                        "actorRotation": renProp.GetOrientationWXYZ() if renProp.IsA('vtkProp3D') else [0, 0, 0, 0],
                        "mapper": {
                            "colorByArrayName": colorArrayName,
                            "colorMode": color_mode,
                            "scalarMode": scalar_mode
                        },
                        "property": extract_renprop_properties(renProp),
                        "lookupTable": {
                            "range": lookupTable.GetRange(),
                            "hueRange": lookupTable.GetHueRange() if hasattr(lookupTable, 'GetHueRange') else [0.5, 0]
                        }
                    })

                    if textureName:
                        sceneComponents[-1]['texture'] = textureName

    # Save texture data if any
    for key, val in textureToSave.items():
        _write_data_set(scDirs, val, None, newDSName=key)

    activeCamera = renderer.GetActiveCamera()
    background = renderer.GetBackground()
    sceneDescription = {
        "fetchGzip": False,
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

    # create binary stream of the vtkjs directory structure
    compression = zipfile.ZIP_DEFLATED
    with BytesIO() as in_memory:
        zf = zipfile.ZipFile(in_memory, mode="w")
        try:
            for dirPath, data in scDirs:
                zf.writestr(dirPath, data, compress_type=compression)
        finally:
                zf.close()
        in_memory.seek(0)
        return in_memory.read()

