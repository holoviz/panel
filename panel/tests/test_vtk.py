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
    ren.SetBackground(0.1, 0.2, 0.4)

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
    cone = vtk.vtkConeSource()
    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())
    coneActor = vtk.vtkActor()
    coneActor.SetMapper(coneMapper)
    ren = vtk.vtkRenderer()
    ren.AddActor(coneActor)
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    assert PaneBase.get_pane_type(renWin) is VTK


def test_vtk_pane_from_url(document, comm):
    url = r'https://raw.githubusercontent.com/Kitware/vtk-js/master/Data/StanfordDragon.vtkjs'

    pane = Pane(url)

    # Create pane
    model = pane._get_root(document, comm=comm)
    assert isinstance(model, VTKPlot)
    assert pane._models[model.ref['id']][0] is model
    assert isinstance(model.vtkjs, string_types)


@vtk_available
def test_vtk_pane_from_render_window(document, comm):
    render_window = make_render_window()

    pane = Pane(render_window)

    # Create pane
    model = pane._get_root(document, comm=comm)
    assert isinstance(model, VTKPlot)
    assert pane._models[model.ref['id']][0] is model
    assert isinstance(model.vtkjs, string_types)

