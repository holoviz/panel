import json
import re
import struct
import zipfile

import vtk

from .synchronizable_serializer import arrayTypesMapping

METHODS_RENAME = {
    "AddTexture": "SetTexture",
    "SetUseGradientOpacity": None,
    "SetRGBTransferFunction": "SetColor",
}
WRAP_ID_RE = re.compile(r"instance:\${([^}]+)}")
ARRAY_TYPES = {
    'Int8Array': vtk.vtkCharArray,
    'Uint8Array': vtk.vtkUnsignedCharArray,
    'Int16Array': vtk.vtkShortArray,
    'UInt16Array': vtk.vtkUnsignedShortArray,
    'Int32Array': vtk.vtkIntArray,
    'Uint32Array': vtk.vtkUnsignedIntArray,
    'Float32Array': vtk.vtkFloatArray,
    'Float64Array': vtk.vtkDoubleArray,
}

def capitalize(name):
    "Upper the first letter letting the rest unchange"
    return name[0].upper() + name[1:]

def fill_array(vtk_arr, state, zf):
    vtk_arr.SetNumberOfComponents(state['numberOfComponents'])
    vtk_arr.SetNumberOfTuples(state['size']//state['numberOfComponents'])
    data = zf.read('data/{}'.format(state['hash']))
    dataType = arrayTypesMapping[vtk_arr.GetDataType()]
    elementSize = struct.calcsize(dataType)
    if vtk_arr.GetDataType() == 12:
        # we need to cast the data to Uint64
        import numpy as np
        data = np.frombuffer(data, dtype=np.uint32).astype(np.uint64).tobytes()
        elementSize = 8
    vtk_arr.SetVoidArray(data, len(data)//elementSize, 1)
    vtk_arr._reference = data

def color_fun_builder(state, zf, register):
    instance = getattr(vtk, state['type'])()
    register.update({state['id']: instance})
    nodes = state['properties'].pop('nodes')
    set_properties(instance, state['properties'])
    for node in nodes:
        instance.AddRGBPoint(*node)

def piecewise_fun_builder(state, zf, register):
    instance = getattr(vtk, state['type'])()
    register.update({state['id']: instance})
    nodes = state['properties'].pop('nodes')
    set_properties(instance, state['properties'])
    for node in nodes:
        instance.AddPoint(*node)

def poly_data_builder(state, zf, register):
    instance = vtk.vtkPolyData()
    register.update({state['id']: instance})
    # geometry
    if 'points' in state['properties']:
        points = state['properties']['points']
        vtkpoints = vtk.vtkPoints()
        points_data_arr = ARRAY_TYPES[points['dataType']]()
        fill_array(points_data_arr, points, zf)
        vtkpoints.SetData(points_data_arr)
        instance.SetPoints(vtkpoints)
    for cell_type in ['verts', 'lines', 'polys', 'strips']:
        if cell_type in state['properties']:
            cell_arr = vtk.vtkCellArray()
            cell_data_arr = vtk.vtkIdTypeArray()
            fill_array(cell_data_arr, state['properties'][cell_type], zf)
            cell_arr.ImportLegacyFormat(cell_data_arr)
            getattr(instance, 'Set' + capitalize(cell_type))(cell_arr)

    # datasets
    fields = state['properties']['fields']
    for dataset in fields:
        data_arr = ARRAY_TYPES[dataset['dataType']]()
        fill_array(data_arr, dataset, zf)
        location = getattr(instance, 'Get' + capitalize(dataset['location']))()
        getattr(location, capitalize(dataset.get("registration", "addArray")))(data_arr)

def volume_mapper_builder(state, zf, register):
    instance = generic_builder(state, zf, register)
    instance.SetScalarMode(1) #need to force the scalar mode to be on points

def generic_builder(state, zf, register=None):
    if register is None:
        register = {}
    instance = getattr(vtk, state['type'])()
    register.update({state['id']: instance})
    set_properties(instance, state['properties'])
    dependencies = state.get('dependencies', None)
    if dependencies:
        for dep in dependencies:
            builder = TYPE_HANDLERS[dep['type']]
            if builder:
                builder(dep, zf, register)
            else:
                print(f'No builder for {dep["type"]}')
    calls = state.get('calls', None)
    if calls:
        for call in calls:
            args=[]
            skip=False
            for arg in call[1]:
                try:
                    extract_instance = WRAP_ID_RE.findall(arg)[0]
                    args.append(register[extract_instance])
                except (IndexError, TypeError):
                    args.append(arg)
                except KeyError:
                    skip = True
            if skip: continue
            if capitalize(call[0]) not in METHODS_RENAME:
                method = capitalize(call[0])
            else:
                method = METHODS_RENAME[capitalize(call[0])]
            if method is None: continue
            if method == "SetInputData" and len(args)==2:
                getattr(instance, method + "Object")(*args[::-1])
            else:
                getattr(instance, method)(*args)
    arrays = state.get('arrays', None)
    if arrays:
        for array_meta in arrays:
            vtk_array = ARRAY_TYPES[array_meta['dataType']]()
            fill_array(vtk_array, array_meta, zf)
            location = (instance
                if 'location' not in array_meta
                else getattr(instance, 'Get'+capitalize(array_meta['location']))())
            getattr(location, capitalize(array_meta['registration']))(vtk_array)
    return instance

def set_properties(instance, properties):
    for k, v in properties.items():
        fn = getattr(instance, 'Set'+capitalize(k), None)
        if fn:
            fn(v)

def import_synch_file(filename):
    with zipfile.ZipFile(filename, 'r') as zf:
        scene = json.loads(zf.read('index.json').decode())
        scene['properties']['numberOfLayers'] = 1
        renwin = generic_builder(scene, zf)
    return renwin


def make_type_handlers():
    aliases = {
        'vtkMapper': ['vtkOpenGLPolyDataMapper', 'vtkCompositePolyDataMapper2', 'vtkDataSetMapper'],
        'vtkProperty': ['vtkOpenGLProperty'],
        'vtkRenderer': ['vtkOpenGLRenderer'],
        'vtkCamera': ['vtkOpenGLCamera'],
        'vtkColorTransferFunction': ['vtkPVDiscretizableColorTransferFunction'],
        'vtkActor': ['vtkOpenGLActor', 'vtkPVLODActor'],
        'vtkLight': ['vtkOpenGLLight', 'vtkPVLight'],
        'vtkTexture': ['vtkOpenGLTexture'],
        'vtkVolumeMapper': ['vtkFixedPointVolumeRayCastMapper', 'vtkSmartVolumeMapper'],
        "vtkGlyph3DMapper": ["vtkOpenGLGlyph3DMapper"],
    }

    type_handlers = {
        'vtkRenderer': generic_builder,
        'vtkLookupTable': generic_builder,
        'vtkLight': None,
        'vtkCamera': generic_builder,
        'vtkPolyData': poly_data_builder,
        'vtkImageData': generic_builder,
        'vtkMapper': generic_builder,
        'vtkGlyph3DMapper': generic_builder,
        'vtkProperty': generic_builder,
        'vtkActor': generic_builder,
        'vtkFollower': generic_builder,
        'vtkColorTransferFunction': color_fun_builder,
        'vtkPiecewiseFunction': piecewise_fun_builder,
        'vtkTexture': generic_builder,
        'vtkVolumeMapper': volume_mapper_builder,
        'vtkVolume': generic_builder,
        'vtkVolumeProperty': generic_builder
    }

    for k, alias_list in aliases.items():
        for alias in alias_list:
            type_handlers.update({
                alias: type_handlers[k]
            })

    return type_handlers

TYPE_HANDLERS = make_type_handlers()
