# coding: utf-8

from __future__ import absolute_import

import os
import base64
from io import BytesIO
from zipfile import ZipFile

import pytest
import numpy as np

try:
    import vtk
except Exception:
    vtk = None

try:
    import pyvista as pv
except Exception:
    pv = None

from six import string_types
from panel.models.vtk import VTKPlot, VTKVolumePlot, VTKAxes
from panel.pane import Pane, PaneBase, VTK,VTKVolume

vtk_available = pytest.mark.skipif(vtk is None, reason="requires vtk")
pyvista_available = pytest.mark.skipif(pv is None, reason="requires pyvista")


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

def pyvista_render_window():
    """
    Allow to download and create a more complex example easily
    """
    from pyvista import examples
    globe = examples.load_globe() #add texture
    pl = pv.Plotter()
    pl.add_mesh(globe)
    sphere = pv.Sphere()
    scalars=sphere.points[:, 2]
    sphere._add_point_array(scalars, 'test', set_active=True) #allow to test scalars
    pl.add_mesh(sphere)
    return pl.ren_win

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
    assert PaneBase.get_pane_type(vtk.vtkRenderWindow()) is VTK


def test_vtk_volume_pane_type_from_np_array():
    assert PaneBase.get_pane_type(np.array([]).reshape((0,0,0))) is VTKVolume


@vtk_available
def test_vtk_volume_pane_type_from_vtk_image():
    image_data = make_image_data()
    assert PaneBase.get_pane_type(image_data) is VTKVolume


def test_vtk_pane_from_url(document, comm):
    url = r'https://raw.githubusercontent.com/Kitware/vtk-js/master/Data/StanfordDragon.vtkjs'

    pane = Pane(url)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VTKPlot)
    assert pane._models[model.ref['id']][0] is model
    assert isinstance(model.data, string_types)


@vtk_available
def test_vtk_pane_from_renwin(document, comm, tmp_path):
    renWin = make_render_window()
    pane = VTK(renWin)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VTKPlot)
    assert pane._models[model.ref['id']][0] is model

    with BytesIO(base64.b64decode(model.data.encode())) as in_memory:
        with ZipFile(in_memory) as zf:
            filenames = zf.namelist()
            assert len(filenames) == 4
            assert 'index.json' in filenames

    # Export Update and Read
    tmpfile = os.path.join(*tmp_path.joinpath('export.vtkjs').parts)
    pane.export_vtkjs(filename=tmpfile)
    with open(tmpfile, 'rb') as  file_exported:
        pane.object = file_exported

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@pyvista_available
def test_vtk_pane_more_complex(document, comm):
    renWin = pyvista_render_window()
    pane = VTK(renWin)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VTKPlot)
    assert pane._models[model.ref['id']][0] is model

    #test colorbar
    colorbars_plot = pane.construct_colorbars()
    cb_model = colorbars_plot.below[0]
    cb_title = cb_model.title
    assert cb_title == 'test'
    assert cb_model.color_mapper.palette == pane._legend[cb_title]['palette']

    with BytesIO(base64.b64decode(model.data.encode())) as in_memory:
        with ZipFile(in_memory) as zf:
            filenames = zf.namelist()
            assert len(filenames) == 12
            assert 'index.json' in filenames

    # add axes
    pane.axes = dict(
        origin = [-5, 5, -2],
        xticker = {'ticks': np.linspace(-5,5,5)},
        yticker = {'ticks': np.linspace(-5,5,5)},
        zticker = {'ticks': np.linspace(-2,2,5),
                   'labels': [''] + [str(int(item)) for item in np.linspace(-2,2,5)[1:]]},
        fontsize = 12,
        digits = 1,
        grid_opacity = 0.5,
        show_grid=True
    )
    assert isinstance(model.axes, VTKAxes)

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@vtk_available
def test_vtk_pane_volume_from_np_array(document, comm):
    pane = VTKVolume(np.ones((10,10,10)))
    from operator import eq
    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VTKVolumePlot)
    assert pane._models[model.ref['id']][0] is model
    assert np.all(np.frombuffer(base64.b64decode(model.data['buffer'].encode())) == 1)
    assert all([eq(getattr(pane, k), getattr(model, k))
                for k in ['slice_i', 'slice_j', 'slice_k']])

    # Test update data
    pane.object = 2*np.ones((10,10,10))
    assert np.all(np.frombuffer(base64.b64decode(model.data['buffer'].encode())) == 2)

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@vtk_available
def test_vtk_pane_volume_from_image_data(document, comm):
    image_data = make_image_data()
    pane = VTKVolume(image_data)
    from operator import eq
    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VTKVolumePlot)
    assert pane._models[model.ref['id']][0] is model
    assert all([eq(getattr(pane, k), getattr(model, k))
                for k in ['slice_i', 'slice_j', 'slice_k']])
    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}
