import base64
import hashlib
import io
import struct
import time
import zipfile

from typing import Any

from vtk.vtkCommonCore import vtkTypeInt32Array, vtkTypeUInt32Array
from vtk.vtkCommonDataModel import vtkDataObject
from vtk.vtkFiltersGeometry import (
    vtkCompositeDataGeometryFilter, vtkGeometryFilter,
)
from vtk.vtkRenderingCore import vtkColorTransferFunction

from .enums import TextPosition


def iteritems(d, **kwargs):
    return iter(d.items(**kwargs))

buffer = memoryview
base64Encode = lambda x: base64.b64encode(x).decode('utf-8')

# -----------------------------------------------------------------------------
# Array helpers
# -----------------------------------------------------------------------------

arrayTypesMapping = [
    ' ',  # VTK_VOID                0
    ' ',  # VTK_BIT                 1
    'b',  # VTK_CHAR                2
    'B',  # VTK_UNSIGNED_CHAR       3
    'h',  # VTK_SHORT               4
    'H',  # VTK_UNSIGNED_SHORT      5
    'i',  # VTK_INT                 6
    'I',  # VTK_UNSIGNED_INT        7
    'l',  # VTK_LONG                8
    'L',  # VTK_UNSIGNED_LONG       9
    'f',  # VTK_FLOAT               10
    'd',  # VTK_DOUBLE              11
    'L',  # VTK_ID_TYPE             12
    ' ',  # VTK_STRING              13
    ' ',  # VTK_OPAQUE              14
    ' ',  # UNDEFINED
    'l',  # VTK_LONG_LONG           16
    'L',  # VTK_UNSIGNED_LONG_LONG  17
]

javascriptMapping = {
    'b': 'Int8Array',
    'B': 'Uint8Array',
    'h': 'Int16Array',
    'H': 'UInt16Array',
    'i': 'Int32Array',
    'I': 'Uint32Array',
    'l': 'Int32Array',
    'L': 'Uint32Array',
    'f': 'Float32Array',
    'd': 'Float64Array'
}


def hashDataArray(dataArray):
    return hashlib.md5(buffer(dataArray)).hexdigest()


def getJSArrayType(dataArray):
    return javascriptMapping[arrayTypesMapping[dataArray.GetDataType()]]


def zipCompression(name, data):
    with io.BytesIO() as in_memory:
        with zipfile.ZipFile(in_memory, mode="w") as zf:
            zf.writestr(f'data/{name}',
                        data, zipfile.ZIP_DEFLATED)
        in_memory.seek(0)
        return in_memory.read()


def dataTableToList(dataTable):
    dataType = arrayTypesMapping[dataTable.GetDataType()]
    elementSize = struct.calcsize(dataType)
    nbValues = dataTable.GetNumberOfValues()
    nbComponents = dataTable.GetNumberOfComponents()
    nbytes = elementSize * nbValues
    if dataType != ' ':
        with io.BytesIO(buffer(dataTable)) as stream:
            data = list(struct.unpack(dataType*nbValues ,stream.read(nbytes)))
        return [data[idx*nbComponents:(idx+1)*nbComponents]
                    for idx in range(nbValues//nbComponents)]


def getScalars(mapper, dataset):
    scalars = None
    cell_flag = 0
    scalar_mode = mapper.GetScalarMode()
    array_access_mode = mapper.GetArrayAccessMode()
    array_id = mapper.GetArrayId()
    array_name = mapper.GetArrayName()
    pd = dataset.GetPointData()
    cd = dataset.GetCellData()
    fd = dataset.GetFieldData()
    if scalar_mode == 0: # VTK_SCALAR_MODE_DEFAULT
        scalars = pd.GetScalars()
        cell_flag = 0
        if scalars is None:
            scalars = cd.GetScalars()
            cell_flag = 1
    elif scalar_mode == 1: # VTK_SCALAR_MODE_USE_POINT_DATA
        scalars = pd.GetScalars()
        cell_flag = 0
    elif scalar_mode == 2: # VTK_SCALAR_MODE_USE_CELL_DATA
        scalars = cd.GetScalars()
        cell_flag = 1
    elif scalar_mode == 3: # VTK_SCALAR_MODE_USE_POINT_FIELD_DATA
        if array_access_mode == 0: # VTK_GET_ARRAY_BY_ID
            scalars = pd.GetAbstractArray(array_id)
        else: # VTK_GET_ARRAY_BY_NAME
            scalars = pd.GetAbstractArray(array_name)
        cell_flag = 0
    elif scalar_mode == 4: # VTK_SCALAR_MODE_USE_CELL_FIELD_DATA
        if array_access_mode == 0: # VTK_GET_ARRAY_BY_ID
            scalars = cd.GetAbstractArray(array_id)
        else: # VTK_GET_ARRAY_BY_NAME
            scalars = cd.GetAbstractArray(array_name)
        cell_flag = 1
    else: # VTK_SCALAR_MODE_USE_FIELD_DATA
        if array_access_mode == 0: # VTK_GET_ARRAY_BY_ID
            scalars = fd.GetAbstractArray(array_id)
        else: # VTK_GET_ARRAY_BY_NAME
            scalars = fd.GetAbstractArray(array_name)
        cell_flag = 2
    return scalars, cell_flag


def retrieveArrayName(mapper_instance, scalar_mode):
    colorArrayName = None
    try:
        ds = [deps for deps in mapper_instance['dependencies'] if deps['id'].endswith('dataset')][0]
        location = "pointData" if scalar_mode in (1, 3) else "cellData"
        for arrayMeta in ds['properties']['fields']:
            if arrayMeta["location"] == location and arrayMeta.get("registration", None) == "setScalars":
                colorArrayName = arrayMeta["name"]
    except Exception:
        pass
    return colorArrayName


def linspace(start, stop, num):
    delta = (stop - start)/(num-1)
    return [start + i*delta for i in range(num)]

# -----------------------------------------------------------------------------
# Convenience class for caching data arrays, storing computed sha sums, keeping
# track of valid actors, etc...
# -----------------------------------------------------------------------------


class SynchronizationContext:

    def __init__(self, id_root=None, serialize_all_data_arrays=False, debug=False):
        self.serializeAllDataArrays = serialize_all_data_arrays
        self.dataArrayCache = {}
        self.lastDependenciesMapping = {}
        self.ingoreLastDependencies = False
        self.idRoot = id_root
        self.debugSerializers = debug
        self.debugAll = debug
        self.annotations = {}

    def getReferenceId(self, instance):
        if not self.idRoot or (hasattr(instance, 'IsA') and instance.IsA('vtkCamera')):
            return getReferenceId(instance)
        else:
            return self.idRoot + getReferenceId(instance)

    def addAnnotation(self, parent, prop, propId):
        if prop.GetClassName() == "vtkCornerAnnotation":
            annotation = {
                "id": propId,
                "viewport": parent.GetViewport(),
                "fontSize": prop.GetLinearFontScaleFactor() * 2,
                "fontFamily": prop.GetTextProperty().GetFontFamilyAsString(),
                "color": prop.GetTextProperty().GetColor(),
                **{pos.name: prop.GetText(pos.value) for pos in TextPosition}
            }
            if self.annotations is None:
                self.annotations = {propId: annotation}
            else:
                self.annotations.update({propId: annotation})

    def getAnnotations(self):
        return list(self.annotations.values())

    def setIgnoreLastDependencies(self, force):
        self.ingoreLastDependencies = force

    def cacheDataArray(self, pMd5, data):
        self.dataArrayCache[pMd5] = data

    def getCachedDataArray(self, pMd5, binary=False, compression=False):
        cacheObj = self.dataArrayCache[pMd5]
        array = cacheObj['array']
        cacheTime = cacheObj['mTime']

        if cacheTime != array.GetMTime():
            if context.debugAll:
                print(' ***** ERROR: you asked for an old cache key! ***** ')

        if array.GetDataType() in (12, 16, 17):
            arraySize = array.GetNumberOfTuples() * array.GetNumberOfComponents()
            if array.GetDataType() in (12, 17):
                # IdType and unsigned long long need to be converted to Uint32
                newArray = vtkTypeUInt32Array()
            else:
                #  long long need to be converted to Int32
                newArray = vtkTypeInt32Array()
            newArray.SetNumberOfTuples(arraySize)
            for i in range(arraySize):
                newArray.SetValue(i, -1 if array.GetValue(i)
                                  < 0 else array.GetValue(i))
            pBuffer = buffer(newArray)
        else:
            pBuffer = buffer(array)

        if binary:
            # Convert the vtkUnsignedCharArray into a bytes object, required by
            # Autobahn websockets
            return pBuffer.tobytes() if not compression else zipCompression(pMd5, pBuffer.tobytes())

        return base64Encode(pBuffer if not compression else zipCompression(pMd5, pBuffer.tobytes()))

    def checkForArraysToRelease(self, timeWindow=20):
        cutOffTime = time.time() - timeWindow
        shasToDelete = []
        for sha in self.dataArrayCache:
            record = self.dataArrayCache[sha]
            array = record['array']
            count = array.GetReferenceCount()

            if count == 1 and record['ts'] < cutOffTime:
                shasToDelete.append(sha)

        for sha in shasToDelete:
            del self.dataArrayCache[sha]

    def getLastDependencyList(self, idstr):
        lastDeps = []
        if idstr in self.lastDependenciesMapping and not self.ingoreLastDependencies:
            lastDeps = self.lastDependenciesMapping[idstr]
        return lastDeps

    def setNewDependencyList(self, idstr, depList):
        self.lastDependenciesMapping[idstr] = depList

    def buildDependencyCallList(self, idstr, newList, addMethod, removeMethod):
        oldList = self.getLastDependencyList(idstr)

        calls = []
        calls += [[addMethod, [wrapId(x)]]
                  for x in newList if x not in oldList]
        calls += [[removeMethod, [wrapId(x)]]
                  for x in oldList if x not in newList]

        self.setNewDependencyList(idstr, newList)
        return calls

# -----------------------------------------------------------------------------
# Global variables
# -----------------------------------------------------------------------------

SERIALIZERS = {}
context = None

# -----------------------------------------------------------------------------
# Global API
# -----------------------------------------------------------------------------


def registerInstanceSerializer(name, method):
    global SERIALIZERS
    SERIALIZERS[name] = method

# -----------------------------------------------------------------------------


def serializeInstance(parent, instance, instanceId, context, depth):
    instanceType = instance.GetClassName()
    serializer = SERIALIZERS[
        instanceType] if instanceType in SERIALIZERS else None

    if serializer:
        return serializer(parent, instance, instanceId, context, depth)

    if context.debugSerializers:
        print(f'{pad(depth)}!!!No serializer for {instanceType} with id {instanceId}')

# -----------------------------------------------------------------------------


def initializeSerializers():
    # Annotations
    registerInstanceSerializer('vtkCornerAnnotation', annotationSerializer)

    # Actors/viewProps
    registerInstanceSerializer('vtkImageSlice', genericProp3DSerializer)
    registerInstanceSerializer('vtkVolume', genericProp3DSerializer)
    registerInstanceSerializer('vtkOpenGLActor', genericActorSerializer)
    registerInstanceSerializer('vtkFollower', genericActorSerializer)
    registerInstanceSerializer('vtkPVLODActor', genericActorSerializer)


    # Mappers
    registerInstanceSerializer(
        'vtkOpenGLPolyDataMapper', genericPolyDataMapperSerializer)
    registerInstanceSerializer(
        'vtkCompositePolyDataMapper2', genericPolyDataMapperSerializer)
    registerInstanceSerializer('vtkDataSetMapper', genericPolyDataMapperSerializer)
    registerInstanceSerializer(
        'vtkFixedPointVolumeRayCastMapper', genericVolumeMapperSerializer)
    registerInstanceSerializer(
        'vtkSmartVolumeMapper', genericVolumeMapperSerializer)
    registerInstanceSerializer(
        'vtkOpenGLImageSliceMapper', imageSliceMapperSerializer)
    registerInstanceSerializer(
        'vtkOpenGLGlyph3DMapper', glyph3DMapperSerializer)

    # LookupTables/TransferFunctions
    registerInstanceSerializer('vtkLookupTable', lookupTableSerializer2)
    registerInstanceSerializer(
        'vtkPVDiscretizableColorTransferFunction', colorTransferFunctionSerializer)
    registerInstanceSerializer(
        'vtkColorTransferFunction', colorTransferFunctionSerializer)

    # opacityFunctions
    registerInstanceSerializer(
        'vtkPiecewiseFunction', piecewiseFunctionSerializer)

    # Textures
    registerInstanceSerializer('vtkOpenGLTexture', textureSerializer)

    # Property
    registerInstanceSerializer('vtkOpenGLProperty', propertySerializer)
    registerInstanceSerializer('vtkVolumeProperty', volumePropertySerializer)
    registerInstanceSerializer('vtkImageProperty', imagePropertySerializer)

    # Datasets
    registerInstanceSerializer('vtkPolyData', polydataSerializer)
    registerInstanceSerializer('vtkImageData', imageDataSerializer)
    registerInstanceSerializer(
        'vtkStructuredGrid', mergeToPolydataSerializer)
    registerInstanceSerializer(
        'vtkUnstructuredGrid', mergeToPolydataSerializer)
    registerInstanceSerializer(
        'vtkMultiBlockDataSet', mergeToPolydataSerializer)

    # RenderWindows
    registerInstanceSerializer('vtkCocoaRenderWindow', renderWindowSerializer)
    registerInstanceSerializer(
        'vtkXOpenGLRenderWindow', renderWindowSerializer)
    registerInstanceSerializer(
        'vtkWin32OpenGLRenderWindow', renderWindowSerializer)
    registerInstanceSerializer('vtkEGLRenderWindow', renderWindowSerializer)
    registerInstanceSerializer('vtkOpenVRRenderWindow', renderWindowSerializer)
    registerInstanceSerializer(
        'vtkGenericOpenGLRenderWindow', renderWindowSerializer)
    registerInstanceSerializer(
        'vtkOSOpenGLRenderWindow', renderWindowSerializer)
    registerInstanceSerializer('vtkOpenGLRenderWindow', renderWindowSerializer)
    registerInstanceSerializer('vtkIOSRenderWindow', renderWindowSerializer)
    registerInstanceSerializer(
        'vtkExternalOpenGLRenderWindow', renderWindowSerializer)

    # Renderers
    registerInstanceSerializer('vtkOpenGLRenderer', rendererSerializer)

    # Cameras
    registerInstanceSerializer('vtkOpenGLCamera', cameraSerializer)


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def pad(depth):
    padding = ''
    for _ in range(depth):
        padding += '  '
    return padding

# -----------------------------------------------------------------------------


def wrapId(idStr):
    return f'instance:${{{idStr}}}'

# -----------------------------------------------------------------------------


def getReferenceId(ref):
    if ref:
        try:
            return ref.__this__[1:17]
        except Exception:
            idStr = str(ref)[-12:-1]
            print(f'====> fallback ID {idStr} for {ref}')
            return idStr
    return '0x0'

# -----------------------------------------------------------------------------

dataArrayShaMapping: dict[str, dict[str, Any]] = {}


def digest(array):
    objId = getReferenceId(array)

    record = None
    if objId in dataArrayShaMapping:
        record = dataArrayShaMapping[objId]

    if record and record['mtime'] == array.GetMTime():
        return record['sha']

    record = {
        'sha': hashDataArray(array),
        'mtime': array.GetMTime()
    }

    dataArrayShaMapping[objId] = record
    return record['sha']

# -----------------------------------------------------------------------------


def getRangeInfo(array, component):
    r = array.GetRange(component)
    compRange = {}
    compRange['min'] = r[0]
    compRange['max'] = r[1]
    compRange['component'] = array.GetComponentName(component)
    return compRange

# -----------------------------------------------------------------------------


def getArrayDescription(array, context):
    if not array:
        return None

    pMd5 = digest(array)
    context.cacheDataArray(pMd5, {
        'array': array,
        'mTime': array.GetMTime(),
        'ts': time.time()
    })

    root = {}
    root['hash'] = pMd5
    root['vtkClass'] = 'vtkDataArray'
    root['name'] = array.GetName()
    root['dataType'] = getJSArrayType(array)
    root['numberOfComponents'] = array.GetNumberOfComponents()
    root['size'] = array.GetNumberOfComponents() * array.GetNumberOfTuples()
    root['ranges'] = []
    if root['numberOfComponents'] > 1:
        for i in range(root['numberOfComponents']):
            root['ranges'].append(getRangeInfo(array, i))
        root['ranges'].append(getRangeInfo(array, -1))
    else:
        root['ranges'].append(getRangeInfo(array, 0))

    return root

# -----------------------------------------------------------------------------


def extractAllDataArrays(extractedFields, dataset, context):
    pointData = dataset.GetPointData()
    for id_arr in range(pointData.GetNumberOfArrays()):
        arrayMeta = getArrayDescription(pointData.GetArray(id_arr), context)
        if arrayMeta:
            arrayMeta['location'] = 'pointData'
            extractedFields.append(arrayMeta)
    cellData = dataset.GetCellData()
    for id_arr in range(cellData.GetNumberOfArrays()):
        arrayMeta = getArrayDescription(cellData.GetArray(id_arr), context)
        if arrayMeta:
            arrayMeta['location'] = 'cellData'
            extractedFields.append(arrayMeta)
    fieldData = dataset.GetCellData()
    for id_arr in range(fieldData.GetNumberOfArrays()):
        arrayMeta = getArrayDescription(fieldData.GetArray(id_arr), context)
        if arrayMeta:
            arrayMeta['location'] = 'fieldData'
            extractedFields.append(arrayMeta)

# -----------------------------------------------------------------------------


def extractRequiredFields(extractedFields, parent, dataset, context, requestedFields=['Normals', 'TCoords']):
    # FIXME should evolve and support funky mapper which leverage many arrays
    if any(parent.IsA(cls) for cls in ['vtkMapper', 'vtkVolumeMapper', 'vtkImageSliceMapper', 'vtkTexture']):
        if parent.IsA("vtkAbstractMapper"): # GetScalars method should exists
            scalarVisibility = 1 if not hasattr(parent, "GetScalarVisibility") else parent.GetScalarVisibility()
            scalars, cell_flag = getScalars(parent, dataset)
            if context.serializeAllDataArrays:
                extractAllDataArrays(extractedFields, dataset, context)
                if scalars:
                    for arrayMeta in extractedFields:
                        if arrayMeta['name'] == scalars.GetName():
                            arrayMeta['registration'] = 'setScalars'
            elif scalars and scalarVisibility and not context.serializeAllDataArrays:
                arrayMeta = getArrayDescription(scalars, context)
                if cell_flag == 0:
                    arrayMeta['location'] = 'pointData'
                elif cell_flag == 1:
                    arrayMeta['location'] = 'cellData'
                else:
                    raise NotImplementedError("Scalars on field data not handled")
                arrayMeta['registration'] = 'setScalars'
                extractedFields.append(arrayMeta)
        elif dataset.GetPointData().GetScalars():
            arrayMeta = getArrayDescription(dataset.GetPointData().GetScalars(), context)
            arrayMeta['location'] = 'pointData'
            arrayMeta['registration'] = 'setScalars'
            extractedFields.append(arrayMeta)

    if parent.IsA("vtkGlyph3DMapper") and not context.serializeAllDataArrays:
        scaleArrayName = parent.GetInputArrayInformation(parent.SCALE).Get(vtkDataObject.FIELD_NAME())
        if scaleArrayName is not None and scaleArrayName not in [field['name'] for field in extractedFields]:
            arrayMeta = getArrayDescription(dataset.GetPointData().GetAbstractArray(scaleArrayName), context)
            if arrayMeta is not None:
                arrayMeta['location'] = 'pointData'
                arrayMeta['registration'] = 'addArray'
                extractedFields.append(arrayMeta)

        scaleOrientationArrayName = parent.GetInputArrayInformation(parent.ORIENTATION).Get(vtkDataObject.FIELD_NAME())
        if scaleOrientationArrayName is not None and scaleOrientationArrayName not in [field['name'] for field in extractedFields]:
            arrayMeta = getArrayDescription(dataset.GetPointData().GetAbstractArray(scaleOrientationArrayName), context)
            if arrayMeta is not None:
                arrayMeta['location'] = 'pointData'
                arrayMeta['registration'] = 'addArray'
                extractedFields.append(arrayMeta)

    # Normal handling
    if 'Normals' in requestedFields:
        normals = dataset.GetPointData().GetNormals()
        if normals:
            arrayMeta = getArrayDescription(normals, context)
            if arrayMeta:
                arrayMeta['location'] = 'pointData'
                arrayMeta['registration'] = 'setNormals'
                extractedFields.append(arrayMeta)

    # TCoord handling
    if 'TCoords' in requestedFields:
        tcoords = dataset.GetPointData().GetTCoords()
        if tcoords:
            arrayMeta = getArrayDescription(tcoords, context)
            if arrayMeta:
                arrayMeta['location'] = 'pointData'
                arrayMeta['registration'] = 'setTCoords'
                extractedFields.append(arrayMeta)

# -----------------------------------------------------------------------------
# Concrete instance serializers
# -----------------------------------------------------------------------------

def annotationSerializer(parent, prop, propId, context, depth):
    if context.debugSerializers:
        print(f'{pad(depth)}!!!Annotations are not handled directly by vtk.js but by bokeh model')

    context.addAnnotation(parent, prop, propId)

    return None

def genericPropSerializer(parent, prop, popId, context, depth):
    # This kind of actor has two "children" of interest, a property and a
    # mapper (optionally a texture)
    mapperInstance = None
    propertyInstance = None
    calls = []
    dependencies = []

    mapper = None
    if not hasattr(prop, 'GetMapper'):
        if context.debugAll:
            print('This volume does not have a GetMapper method')
    else:
        mapper = prop.GetMapper()

    if mapper:
        mapperId = context.getReferenceId(mapper)
        mapperInstance = serializeInstance(
            prop, mapper, mapperId, context, depth + 1)
        if mapperInstance:
            dependencies.append(mapperInstance)
            calls.append(['setMapper', [wrapId(mapperId)]])

    properties = None
    if hasattr(prop, 'GetProperty'):
        properties = prop.GetProperty()
    else:
        if context.debugAll:
            print('This image does not have a GetProperty method')

    if properties:
        propId = context.getReferenceId(properties)
        propertyInstance = serializeInstance(
            prop, properties, propId, context, depth + 1)
        if propertyInstance:
            dependencies.append(propertyInstance)
            calls.append(['setProperty', [wrapId(propId)]])

    # Handle texture if any
    texture = None
    if hasattr(prop, 'GetTexture'):
        texture = prop.GetTexture()

    if texture:
        textureId = context.getReferenceId(texture)
        textureInstance = serializeInstance(
            prop, texture, textureId, context, depth + 1)
        if textureInstance:
            dependencies.append(textureInstance)
            calls.append(['addTexture', [wrapId(textureId)]])

    return {
        'parent': context.getReferenceId(parent),
        'id': popId,
        'type': prop.GetClassName(),
        'properties': {
            # vtkProp
            'visibility': prop.GetVisibility(),
            'pickable': prop.GetPickable(),
            'dragable': prop.GetDragable(),
            'useBounds': prop.GetUseBounds(),
        },
        'calls': calls,
        'dependencies': dependencies
    }

# -----------------------------------------------------------------------------


def genericProp3DSerializer(parent, prop3D, prop3DId, context, depth):
    # This kind of actor has some position properties to add
    instance = genericPropSerializer(parent, prop3D, prop3DId, context, depth)

    if not instance: return

    instance['properties'].update({
        # vtkProp3D
        'origin': prop3D.GetOrigin(),
        'position': prop3D.GetPosition(),
        'scale': prop3D.GetScale(),
        'orientation': prop3D.GetOrientation(),
    })

    if prop3D.GetUserMatrix():
        instance['properties'].update({
            'userMatrix': [prop3D.GetUserMatrix().GetElement(i%4,i//4) for i in range(16)],
        })
    return instance

# -----------------------------------------------------------------------------


def genericActorSerializer(parent, actor, actorId, context, depth):
    # may have texture and
    instance = genericProp3DSerializer(parent, actor, actorId, context, depth)

    if not instance: return

    # # actor may have a backface property instance (not used by vtkjs rendering)
    # # https://github.com/Kitware/vtk-js/issues/1545

    # backfaceProperties = actor.GetBackfaceProperty()

    # if backfaceProperties:
    #     backfacePropId = context.getReferenceId(backfaceProperties)
    #     backPropertyInstance = serializeInstance(
    #         actor, backfaceProperties, backfacePropId, context, depth + 1)
    #     if backPropertyInstance:
    #         instance['dependencies'].append(backPropertyInstance)
    #         instance['calls'].append(['setBackfaceProperty', [wrapId(backfacePropId)]])

    instance['properties'].update({
        # vtkActor
        'forceOpaque': actor.GetForceOpaque(),
        'forceTranslucent': actor.GetForceTranslucent()
    })

    if actor.IsA('vtkFollower'):
        camera = actor.GetCamera()
        cameraId = context.getReferenceId(camera)
        cameraInstance = serializeInstance(
            actor, camera, cameraId, context, depth + 1)
        if cameraInstance:
            instance['dependencies'].append(cameraInstance)
            instance['calls'].append(['setCamera', [wrapId(cameraId)]])

    return instance

# -----------------------------------------------------------------------------


def genericMapperSerializer(parent, mapper, mapperId, context, depth):
    # This kind of mapper requires us to get 2 items: input data and lookup
    # table
    dataObject = None
    dataObjectInstance = None
    lookupTableInstance = None
    calls = []
    dependencies = []

    if not hasattr(mapper, 'GetInputDataObject'):
        if context.debugAll:
                print('This mapper does not have GetInputDataObject method')
    else:
        for port in range(mapper.GetNumberOfInputPorts()): # Glyph3DMapper can define input data objects on 2 ports (input, source)
            dataObject = mapper.GetInputDataObject(port, 0)
            if dataObject:
                dataObjectId = f'{mapperId}-dataset-{port}'
                if parent.IsA('vtkActor') and not mapper.IsA('vtkTexture'):
                    # vtk-js actors can render only surfacic datasets
                    # => we ensure to convert the dataset in polydata
                    dataObjectInstance = mergeToPolydataSerializer(
                        mapper, dataObject, dataObjectId, context, depth + 1)
                else:
                    dataObjectInstance = serializeInstance(
                        mapper, dataObject, dataObjectId, context, depth + 1)
                if dataObjectInstance:
                    dependencies.append(dataObjectInstance)
                    calls.append(['setInputData', [wrapId(dataObjectId), port]])

    lookupTable = None

    if hasattr(mapper, 'GetLookupTable'):
        lookupTable = mapper.GetLookupTable()
    elif parent.IsA('vtkActor'):
        if context.debugAll:
            print('This mapper actor not have GetLookupTable method')

    if lookupTable:
        lookupTableId = context.getReferenceId(lookupTable)
        lookupTableInstance = serializeInstance(
            mapper, lookupTable, lookupTableId, context, depth + 1)
        if lookupTableInstance:
            dependencies.append(lookupTableInstance)
            calls.append(['setLookupTable', [wrapId(lookupTableId)]])

    if dataObjectInstance:
        return {
            'parent': context.getReferenceId(parent),
            'id': mapperId,
            'properties': {},
            'calls': calls,
            'dependencies': dependencies
        }

# -----------------------------------------------------------------------------


def genericPolyDataMapperSerializer(parent, mapper, mapperId, context, depth):
    instance = genericMapperSerializer(parent, mapper, mapperId, context, depth)

    if not instance: return

    instance['type'] = mapper.GetClassName()
    instance['properties'].update({
        'resolveCoincidentTopology': mapper.GetResolveCoincidentTopology(),
        'renderTime': mapper.GetRenderTime(),
        'arrayAccessMode': 1, # since we can't set mapper arrayId on vtkjs, we force access mode by name and use retrieve name function
        'scalarRange': mapper.GetScalarRange(),
        'useLookupTableScalarRange': 1 if mapper.GetUseLookupTableScalarRange() else 0,
        'scalarVisibility': mapper.GetScalarVisibility(),
        'colorByArrayName': retrieveArrayName(instance, mapper.GetScalarMode()),
        'colorMode': mapper.GetColorMode(),
        'scalarMode': mapper.GetScalarMode(),
        'interpolateScalarsBeforeMapping': 1 if mapper.GetInterpolateScalarsBeforeMapping() else 0
    })
    return instance

# -----------------------------------------------------------------------------


def genericVolumeMapperSerializer(parent, mapper, mapperId, context, depth):
    instance = genericMapperSerializer(parent, mapper, mapperId, context, depth)

    if not instance: return

    imageSampleDistance = (
        mapper.GetImageSampleDistance()
        if hasattr(mapper, 'GetImageSampleDistance')
        else 1
    )
    instance['type'] = mapper.GetClassName()
    instance['properties'].update({
        'sampleDistance': mapper.GetSampleDistance(),
        'imageSampleDistance': imageSampleDistance,
        # 'maximumSamplesPerRay',
        'autoAdjustSampleDistances': mapper.GetAutoAdjustSampleDistances(),
        'blendMode': mapper.GetBlendMode(),
    })
    return instance

# -----------------------------------------------------------------------------


def glyph3DMapperSerializer(parent, mapper, mapperId, context, depth):
    instance = genericPolyDataMapperSerializer(parent, mapper, mapperId, context, depth)

    if not instance: return
    instance['type'] = mapper.GetClassName()
    instance['properties'].update({
        'orient': mapper.GetOrient(),
        'orientationMode': mapper.GetOrientationMode(),
        'scaling': mapper.GetScaling(),
        'scaleFactor': mapper.GetScaleFactor(),
        'scaleMode': mapper.GetScaleMode(),
        'scaleArray': mapper.GetInputArrayInformation(mapper.SCALE).Get(vtkDataObject.FIELD_NAME()),
        'orientationArray': mapper.GetInputArrayInformation(mapper.ORIENTATION).Get(vtkDataObject.FIELD_NAME()),
    })
    return instance

# -----------------------------------------------------------------------------


def textureSerializer(parent, texture, textureId, context, depth):
    instance = genericMapperSerializer(parent, texture, textureId, context, depth)

    if not instance: return

    instance['type'] = texture.GetClassName()
    instance['properties'].update({
        'interpolate': texture.GetInterpolate(),
        'repeat': texture.GetRepeat(),
        'edgeClamp': texture.GetEdgeClamp(),
    })
    return instance

# -----------------------------------------------------------------------------


def imageSliceMapperSerializer(parent, mapper, mapperId, context, depth):
    # On vtkjs side : vtkImageMapper connected to a vtkImageReslice filter

    instance = genericMapperSerializer(parent, mapper, mapperId, context, depth)

    if not instance: return

    instance['type'] = mapper.GetClassName()

    return instance

# -----------------------------------------------------------------------------


def lookupTableSerializer(parent, lookupTable, lookupTableId, context, depth):
    # No children in this case, so no additions to bindings and return empty list
    # But we do need to add instance
    arrays = []
    lookupTableRange = lookupTable.GetRange()

    lookupTableHueRange = [0.5, 0]
    if hasattr(lookupTable, 'GetHueRange'):
        try:
            lookupTable.GetHueRange(lookupTableHueRange)
        except Exception:
            pass

    lutSatRange = lookupTable.GetSaturationRange()
    # lutAlphaRange = lookupTable.GetAlphaRange()
    if lookupTable.GetTable():
        arrayMeta = getArrayDescription(lookupTable.GetTable(), context)
        if arrayMeta:
            arrayMeta['registration'] = 'setTable'
            arrays.append(arrayMeta)

    return {
        'parent': context.getReferenceId(parent),
        'id': lookupTableId,
        'type': lookupTable.GetClassName(),
        'properties': {
            'numberOfColors': lookupTable.GetNumberOfColors(),
            'valueRange': lookupTableRange,
            'range': lookupTableRange,
            'hueRange': lookupTableHueRange,
            # 'alphaRange': lutAlphaRange,  # Causes weird rendering artifacts on client
            'saturationRange': lutSatRange,
            'nanColor': lookupTable.GetNanColor(),
            'belowRangeColor': lookupTable.GetBelowRangeColor(),
            'aboveRangeColor': lookupTable.GetAboveRangeColor(),
            'useAboveRangeColor': True if lookupTable.GetUseAboveRangeColor() else False,
            'useBelowRangeColor': True if lookupTable.GetUseBelowRangeColor() else False,
            'alpha': lookupTable.GetAlpha(),
            'vectorSize': lookupTable.GetVectorSize(),
            'vectorComponent': lookupTable.GetVectorComponent(),
            'vectorMode': lookupTable.GetVectorMode(),
            'indexedLookup': lookupTable.GetIndexedLookup(),
        },
        'arrays': arrays,
    }

# -----------------------------------------------------------------------------


def lookupTableToColorTransferFunction(lookupTable):
    dataTable = lookupTable.GetTable()
    table = dataTableToList(dataTable)
    if table:
        ctf = vtkColorTransferFunction()
        tableRange = lookupTable.GetTableRange()
        points = linspace(*tableRange, num=len(table))
        for x, rgba in zip(points, table):
            ctf.AddRGBPoint(x, *[x/255 for x in rgba[:3]])
        ctf.SetAboveRangeColor(lookupTable.GetAboveRangeColor()[:3])
        ctf.SetBelowRangeColor(lookupTable.GetBelowRangeColor()[:3])
        ctf.SetUseAboveRangeColor(lookupTable.GetUseAboveRangeColor())
        ctf.SetUseBelowRangeColor(lookupTable.GetUseBelowRangeColor())
        ctf.SetNanColorRGBA(lookupTable.GetNanColor())
        return ctf

# -----------------------------------------------------------------------------


def lookupTableSerializer2(parent, lookupTable, lookupTableId, context, depth):
    ctf = lookupTableToColorTransferFunction(lookupTable)
    if ctf:
        return colorTransferFunctionSerializer(parent, ctf, lookupTableId, context, depth)

# -----------------------------------------------------------------------------


def propertySerializer(parent, propObj, propObjId, context, depth):
    representation = propObj.GetRepresentation() if hasattr(
        propObj, 'GetRepresentation') else 2
    colorToUse = propObj.GetDiffuseColor() if hasattr(
        propObj, 'GetDiffuseColor') else [1, 1, 1]
    if representation == 1 and hasattr(propObj, 'GetColor'):
        colorToUse = propObj.GetColor()

    return {
        'parent': context.getReferenceId(parent),
        'id': propObjId,
        'type': propObj.GetClassName(),
        'properties': {
            'representation': representation,
            'diffuseColor': colorToUse,
            'color': propObj.GetColor(),
            'ambientColor': propObj.GetAmbientColor(),
            'specularColor': propObj.GetSpecularColor(),
            'edgeColor': propObj.GetEdgeColor(),
            'ambient': propObj.GetAmbient(),
            'diffuse': propObj.GetDiffuse(),
            'specular': propObj.GetSpecular(),
            'specularPower': propObj.GetSpecularPower(),
            'opacity': propObj.GetOpacity(),
            'interpolation': propObj.GetInterpolation(),
            'edgeVisibility': 1 if propObj.GetEdgeVisibility() else 0,
            'backfaceCulling': 1 if propObj.GetBackfaceCulling() else 0,
            'frontfaceCulling': 1 if propObj.GetFrontfaceCulling() else 0,
            'pointSize': propObj.GetPointSize(),
            'lineWidth': propObj.GetLineWidth(),
            'lighting': 1 if propObj.GetLighting() else 0,
        }
    }

# -----------------------------------------------------------------------------

def volumePropertySerializer(parent, propObj, propObjId, context, depth):
    dependencies = []
    calls = []
    # TODO: for the moment only component 0 handle

    #OpactiyFunction
    ofun = propObj.GetScalarOpacity()
    if ofun:
        ofunId = context.getReferenceId(ofun)
        ofunInstance = serializeInstance(
            propObj, ofun, ofunId, context, depth + 1)
        if ofunInstance:
            dependencies.append(ofunInstance)
            calls.append(['setScalarOpacity', [0, wrapId(ofunId)]])

    # ColorTranferFunction
    ctfun = propObj.GetRGBTransferFunction()
    if ctfun:
        ctfunId = context.getReferenceId(ctfun)
        ctfunInstance = serializeInstance(
            propObj, ctfun, ctfunId, context, depth + 1)
        if ctfunInstance:
            dependencies.append(ctfunInstance)
            calls.append(['setRGBTransferFunction', [0, wrapId(ctfunId)]])

    calls += [
        ['setScalarOpacityUnitDistance', [0, propObj.GetScalarOpacityUnitDistance(0)]],
        ['setComponentWeight', [0, propObj.GetComponentWeight(0)]],
        ['setUseGradientOpacity', [0, int(not propObj.GetDisableGradientOpacity())]],
    ]

    return {
        'parent': context.getReferenceId(parent),
        'id': propObjId,
        'type': propObj.GetClassName(),
        'properties': {
            'independentComponents': propObj.GetIndependentComponents(),
            'interpolationType': propObj.GetInterpolationType(),
            'ambient': propObj.GetAmbient(),
            'diffuse': propObj.GetDiffuse(),
            'shade': propObj.GetShade(),
            'specular': propObj.GetSpecular(0),
            'specularPower': propObj.GetSpecularPower(),
        },
        'dependencies': dependencies,
        'calls': calls,
    }

# -----------------------------------------------------------------------------


def imagePropertySerializer(parent, propObj, propObjId, context, depth):
    calls = []
    dependencies = []

    lookupTable = propObj.GetLookupTable()
    if lookupTable:
        ctfun = lookupTableToColorTransferFunction(lookupTable)
        ctfunId = context.getReferenceId(ctfun)
        ctfunInstance = serializeInstance(
            propObj, ctfun, ctfunId, context, depth + 1)
        if ctfunInstance:
            dependencies.append(ctfunInstance)
            calls.append(['setRGBTransferFunction', [wrapId(ctfunId)]])

    return {
        'parent': context.getReferenceId(parent),
        'id': propObjId,
        'type': propObj.GetClassName(),
        'properties': {
            'interpolationType': propObj.GetInterpolationType(),
            'colorWindow': propObj.GetColorWindow(),
            'colorLevel': propObj.GetColorLevel(),
            'ambient': propObj.GetAmbient(),
            'diffuse': propObj.GetDiffuse(),
            'opacity': propObj.GetOpacity(),
        },
        'dependencies': dependencies,
        'calls': calls,
    }

# -----------------------------------------------------------------------------


def imageDataSerializer(parent, dataset, datasetId, context, depth):
    datasetType = dataset.GetClassName()

    if hasattr(dataset, 'GetDirectionMatrix'):
        direction = [dataset.GetDirectionMatrix().GetElement(0, i)
                     for i in range(9)]
    else:
        direction = [1, 0, 0,
                     0, 1, 0,
                     0, 0, 1]

    # Extract dataset fields
    arrays = []
    extractRequiredFields(arrays, parent, dataset, context)

    return {
        'parent': context.getReferenceId(parent),
        'id': datasetId,
        'type': datasetType,
        'properties': {
            'spacing': dataset.GetSpacing(),
            'origin': dataset.GetOrigin(),
            'dimensions': dataset.GetDimensions(),
            'direction': direction,
        },
        'arrays': arrays
    }

# -----------------------------------------------------------------------------


def polydataSerializer(parent, dataset, datasetId, context, depth):
    datasetType = dataset.GetClassName()

    if dataset and dataset.GetPoints():
        properties = {}

        # Points
        points = getArrayDescription(dataset.GetPoints().GetData(), context)
        points['vtkClass'] = 'vtkPoints'
        properties['points'] = points

        # Verts
        if dataset.GetVerts() and dataset.GetVerts().GetData().GetNumberOfTuples() > 0:
            _verts = getArrayDescription(dataset.GetVerts().GetData(), context)
            properties['verts'] = _verts
            properties['verts']['vtkClass'] = 'vtkCellArray'

        # Lines
        if dataset.GetLines() and dataset.GetLines().GetData().GetNumberOfTuples() > 0:
            _lines = getArrayDescription(dataset.GetLines().GetData(), context)
            properties['lines'] = _lines
            properties['lines']['vtkClass'] = 'vtkCellArray'

        # Polys
        if dataset.GetPolys() and dataset.GetPolys().GetData().GetNumberOfTuples() > 0:
            _polys = getArrayDescription(dataset.GetPolys().GetData(), context)
            properties['polys'] = _polys
            properties['polys']['vtkClass'] = 'vtkCellArray'

        # Strips
        if dataset.GetStrips() and dataset.GetStrips().GetData().GetNumberOfTuples() > 0:
            _strips = getArrayDescription(
                dataset.GetStrips().GetData(), context)
            properties['strips'] = _strips
            properties['strips']['vtkClass'] = 'vtkCellArray'

        # Fields
        properties['fields'] = []
        extractRequiredFields(properties['fields'], parent, dataset, context)

        return {
            'parent': context.getReferenceId(parent),
            'id': datasetId,
            'type': datasetType,
            'properties': properties
        }

    if context.debugAll:
        print('This dataset has no points!')

# -----------------------------------------------------------------------------


def mergeToPolydataSerializer(parent, dataObject, dataObjectId, context, depth):
    dataset = None

    if dataObject.IsA('vtkCompositeDataSet'):
        gf = vtkCompositeDataGeometryFilter()
        gf.SetInputData(dataObject)
        gf.Update()
        dataset = gf.GetOutput()
    elif not dataObject.IsA('vtkPolyData'):
        gf = vtkGeometryFilter()
        gf.SetInputData(dataObject)
        gf.Update()
        dataset = gf.GetOutput()
    else:
        dataset = dataObject

    return polydataSerializer(parent, dataset, dataObjectId, context, depth)

# -----------------------------------------------------------------------------


def colorTransferFunctionSerializer(parent, instance, objId, context, depth):
    nodes = []

    for i in range(instance.GetSize()):
        # x, r, g, b, midpoint, sharpness
        node = [0, 0, 0, 0, 0, 0]
        instance.GetNodeValue(i, node)
        nodes.append(node)

    return {
        'parent': context.getReferenceId(parent),
        'id': objId,
        'type': instance.GetClassName(),
        'properties': {
            'clamping': 1 if instance.GetClamping() else 0,
            'colorSpace': instance.GetColorSpace(),
            'hSVWrap': 1 if instance.GetHSVWrap() else 0,
            'nanColor': instance.GetNanColor() + (instance.GetNanOpacity(),),
            'belowRangeColor': instance.GetBelowRangeColor() + (1,),
            'aboveRangeColor': instance.GetAboveRangeColor() + (1,),
            'useAboveRangeColor': 1 if instance.GetUseAboveRangeColor() else 0,
            'useBelowRangeColor': 1 if instance.GetUseBelowRangeColor() else 0,
            'allowDuplicateScalars': 1 if instance.GetAllowDuplicateScalars() else 0,
            'alpha': instance.GetAlpha(),
            'vectorComponent': instance.GetVectorComponent(),
            'vectorSize': instance.GetVectorSize(),
            'vectorMode': instance.GetVectorMode(),
            'indexedLookup': instance.GetIndexedLookup(),
            'nodes': nodes
        }
    }

# -----------------------------------------------------------------------------


def piecewiseFunctionSerializer(parent, instance, objId, context, depth):
    nodes = []

    for i in range(instance.GetSize()):
        # x, y, midpoint, sharpness
        node = [0, 0, 0, 0]
        instance.GetNodeValue(i, node)
        nodes.append(node)

    return {
        'parent': context.getReferenceId(parent),
        'id': objId,
        'type': instance.GetClassName(),
        'properties': {
            'clamping': instance.GetClamping(),
            'allowDuplicateScalars': instance.GetAllowDuplicateScalars(),
            'nodes': nodes,
        }
    }
# -----------------------------------------------------------------------------


def rendererSerializer(parent, instance, objId, context, depth):
    dependencies = []
    viewPropIds = []
    calls = []

    # Camera
    camera = instance.GetActiveCamera()
    cameraId = context.getReferenceId(camera)
    cameraInstance = serializeInstance(
        instance, camera, cameraId, context, depth + 1)
    if cameraInstance:
        dependencies.append(cameraInstance)
        calls.append(['setActiveCamera', [wrapId(cameraId)]])

    # View prop as representation containers
    viewPropCollection = instance.GetViewProps()
    for rpIdx in range(viewPropCollection.GetNumberOfItems()):
        viewProp = viewPropCollection.GetItemAsObject(rpIdx)
        viewPropId = context.getReferenceId(viewProp)

        viewPropInstance = serializeInstance(
            instance, viewProp, viewPropId, context, depth + 1)
        if viewPropInstance:
            dependencies.append(viewPropInstance)
            viewPropIds.append(viewPropId)

    calls += context.buildDependencyCallList(f'{objId}-props', viewPropIds, 'addViewProp', 'removeViewProp')

    return {
        'parent': context.getReferenceId(parent),
        'id': objId,
        'type': instance.GetClassName(),
        'properties': {
            'background': instance.GetBackground(),
            'background2': instance.GetBackground2(),
            'viewport': instance.GetViewport(),
            # These commented properties do not yet have real setters in vtk.js
            # 'gradientBackground': instance.GetGradientBackground(),
            # 'aspect': instance.GetAspect(),
            # 'pixelAspect': instance.GetPixelAspect(),
            # 'ambient': instance.GetAmbient(),
            'twoSidedLighting': instance.GetTwoSidedLighting(),
            'lightFollowCamera': instance.GetLightFollowCamera(),
            'layer': instance.GetLayer(),
            'preserveColorBuffer': instance.GetPreserveColorBuffer(),
            'preserveDepthBuffer': instance.GetPreserveDepthBuffer(),
            'nearClippingPlaneTolerance': instance.GetNearClippingPlaneTolerance(),
            'clippingRangeExpansion': instance.GetClippingRangeExpansion(),
            'useShadows': instance.GetUseShadows(),
            'useDepthPeeling': instance.GetUseDepthPeeling(),
            'occlusionRatio': instance.GetOcclusionRatio(),
            'maximumNumberOfPeels': instance.GetMaximumNumberOfPeels(),
            'interactive': instance.GetInteractive(),
        },
        'dependencies': dependencies,
        'calls': calls
    }

# -----------------------------------------------------------------------------


def cameraSerializer(parent, instance, objId, context, depth):
    return {
        'parent': context.getReferenceId(parent),
        'id': objId,
        'type': instance.GetClassName(),
        'properties': {
            'focalPoint': instance.GetFocalPoint(),
            'position': instance.GetPosition(),
            'viewUp': instance.GetViewUp(),
            'clippingRange': instance.GetClippingRange(),
        }
    }

# -----------------------------------------------------------------------------


def renderWindowSerializer(parent, instance, objId, context, depth):
    dependencies = []
    rendererIds = []

    rendererCollection = instance.GetRenderers()
    for rIdx in range(rendererCollection.GetNumberOfItems()):
        # Grab the next vtkRenderer
        renderer = rendererCollection.GetItemAsObject(rIdx)
        rendererId = context.getReferenceId(renderer)
        rendererInstance = serializeInstance(
            instance, renderer, rendererId, context, depth + 1)
        if rendererInstance:
            dependencies.append(rendererInstance)
            rendererIds.append(rendererId)

    calls = context.buildDependencyCallList(
        objId, rendererIds, 'addRenderer', 'removeRenderer')

    return {
        'parent': context.getReferenceId(parent),
        'id': objId,
        'type': instance.GetClassName(),
        'properties': {
            'numberOfLayers': instance.GetNumberOfLayers()
        },
        'dependencies': dependencies,
        'calls': calls,
        'mtime': instance.GetMTime(),
    }
