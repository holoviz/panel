DEPENDENCY_NOT_INSTALLABLE = [
    "aiohttp", # https://github.com/aio-libs/aiohttp/issues/7253
    "datashader", # https://github.com/holoviz/datashader/issues/1200
    "pyarrow", # https://github.com/apache/arrow/issues/34996
    "pygraphviz", # https://github.com/pygraphviz/pygraphviz/issues/453
    "pyvista", # https://gitlab.kitware.com/vtk/vtk/-/issues/18806
    "streamz", # https://github.com/python-streamz/streamz/issues/467,
    "vtk", # https://gitlab.kitware.com/vtk/vtk/-/issues/18806
]

NOTEBOOK_ISSUES = {
    "gallery/vtk_interactive.ipynb": ["https://gitlab.kitware.com/vtk/vtk/-/issues/18806"],
    "gallery/vtk_slicer.ipynb": ["https://gitlab.kitware.com/vtk/vtk/-/issues/18806"],
    "gallery/vtk_warp.ipynb": ["https://gitlab.kitware.com/vtk/vtk/-/issues/18806"],
    "gallery/glaciers.ipynb": ["https://github.com/holoviz/panel/issues/4656"],
    "how_to/callbacks/async.md": ["https://github.com/aio-libs/aiohttp/issues/7253"],
    "reference/panes/DataFrame.ipynb": ["https://github.com/python-streamz/streamz/issues/467"],
    "reference/panes/IPyWidget.ipynb": ["https://github.com/holoviz/panel/issues/4394"],
    "reference/panes/Matplotlib.ipynb": ["https://github.com/holoviz/panel/issues/4394"],
    "reference/panes/Reacton.ipynb": ["https://github.com/holoviz/panel/issues/4394"],
    "reference/panes/Streamz.ipynb": ["https://github.com/python-streamz/streamz/issues/467"],
    "reference/panes/VTK.ipynb": ["https://gitlab.kitware.com/vtk/vtk/-/issues/18806"],
    "reference/panes/VTKVolume.ipynb": ["https://gitlab.kitware.com/vtk/vtk/-/issues/18806"],
    "reference/widgets/Debugger.ipynb": ["https://github.com/holoviz/panel/issues/4399"],
    "reference/widgets/EditableIntSlider.ipynb": ["https://github.com/holoviz/panel/issues/4400"],
    "reference/widgets/FileDownload.ipynb": ["https://github.com/holoviz/panel/issues/4401"],
    "reference/widgets/IntRangeSlider.ipynb": ["https://github.com/holoviz/panel/issues/4402"],
    "reference/widgets/MultiChoice.ipynb": ["https://github.com/holoviz/panel/issues/4403"],
    "reference/widgets/RangeSlider.ipynb": ["https://github.com/holoviz/panel/issues/4402"],
    "reference/widgets/SpeechToText.ipynb": ["https://github.com/holoviz/panel/issues/4404"],
    "reference/widgets/Terminal.ipynb": ["https://github.com/holoviz/panel/issues/4407"],
}
