# coding: utf-8

from __future__ import absolute_import

import pytest

try:
    import vtk
except:
    vtk = None

from six import string_types
from panel.models.vtk import VTKPlot
from panel.pane import Pane, PaneBase, VTK

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
    root = {}
    _dump_data_array(scDir, '', 'test', data, root=root, compress=False)
    assert len(set(root_keys) - set(root.keys())) == 0
    assert len(scDir) == 1
    assert isinstance(scDir[0][0], string_types)
    assert isinstance(scDir[0][1], bytes)
