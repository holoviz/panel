# coding: utf-8

from __future__ import absolute_import

import pytest
import numpy as np

try:
    import vtk
except Exception:
    vtk = None

from six import string_types
from panel.models.vtk import VTKPlot
from panel.pane import Pane, PaneBase, VTK,VTKVolume

vtk_available = pytest.mark.skipif(vtk is None, reason="requires vtk")


def make_render_window():
    cone = vtk.vtkConeSource()
    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())
    coneActor = vtk.vtkActor()
    coneActor.SetMapper(coneMapper)
    ren = vtk.vtkRenderer()
    ren.AddActor(coneActor)
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    return renWin

def make_image_data():
    image_data = vtk.vtkImageData()
    image_data.SetDimensions(3, 4, 5)
    image_data.AllocateScalars(vtk.VTK_DOUBLE, 1)

    dims = image_data.GetDimensions()

    # Fill every entry of the image data with random double
    for z in range(dims[2]):
        for y in range(dims[1]):
            for x in range(dims[0]):
                image_data.SetScalarComponentFromDouble(x, y, z, 0, np.random.rand())
    return image_data


def test_get_vtk_pane_type_from_url():
    url = r'https://raw.githubusercontent.com/Kitware/vtk-js/master/Data/StanfordDragon.vtkjs'
    assert PaneBase.get_pane_type(url) is VTK


def test_get_vtk_pane_type_from_file():
    file = r'StanfordDragon.vtkjs'
    assert PaneBase.get_pane_type(file) is VTK


@vtk_available
def test_get_vtk_pane_type_from_render_window():
    renWin = make_render_window()
    assert PaneBase.get_pane_type(renWin) is VTK


def test_vtk_pane_from_url(document, comm):
    url = r'https://raw.githubusercontent.com/Kitware/vtk-js/master/Data/StanfordDragon.vtkjs'

    pane = Pane(url)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VTKPlot)
    assert pane._models[model.ref['id']][0] is model
    assert isinstance(model.data, string_types)


@vtk_available
def test_vtk_data_array_dump():
    from panel.pane.vtk.vtkjs_serializer import _dump_data_array
    root_keys = ['ref', 'vtkClass', 'name', 'dataType',
                 'numberOfComponents', 'size', 'ranges']
    renWin = make_render_window()
    renderers = list(renWin.GetRenderers())
    ren_props = list(renderers[0].GetViewProps())
    mapper = ren_props[0].GetMapper()
    mapper.Update() # create data
    data = mapper.GetInput().GetPoints().GetData()
    scDir = []
    root = _dump_data_array(scDir, '', 'test', data)
    assert len(set(root_keys) - set(root.keys())) == 0
    assert len(scDir) == 1
    assert isinstance(scDir[0][0], string_types)
    assert isinstance(scDir[0][1], bytes)

def test_vtk_volume_from_np_array():
    assert PaneBase.get_pane_type(np.random.rand(10,10,10)) is VTKVolume

@vtk_available
def test_vtk_volume_from_vtk_image():
    image_data = make_image_data()
    assert PaneBase.get_pane_type(image_data) is VTKVolume
