"""
Helper script to convert and copy example notebooks into JupyterLite build.
"""
import hashlib
import json
import os
import pathlib
import shutil

import bokeh.sampledata
import nbformat

PANEL_BASE = pathlib.Path(__file__).parent.parent
EXAMPLES_DIR = PANEL_BASE / 'examples'

# Add piplite command to notebooks
DEFAULT_DEPENDENCIES = ['panel', 'pyodide-http', 'altair', 'hvplot', 'matplotlib', 'plotly', 'pydeck', 'scikit-learn']
with open(PANEL_BASE/"scripts"/"panelite_dependencies.json", "r", encoding="utf8") as file:
    DEPENDENCIES = json.load(file)
DEPENDENCY_NOT_IMPORTABLE = [
    "streamz", # https://github.com/python-streamz/streamz/issues/467,
    "vtk", # https://gitlab.kitware.com/vtk/vtk/-/issues/18806
]
NOTEBOOK_ISSUES = {
    "Getting_Started.ipynb": ["https://github.com/holoviz/panel/issues/4416"],
    "reference/panes/DataFrame.ipynb": ["https://github.com/python-streamz/streamz/issues/467"],
    "reference/panes/HoloViews.ipynb": ["https://github.com/holoviz/panel/issues/4393"],
    "reference/panes/IPyWidget.ipynb": ["https://github.com/holoviz/panel/issues/4394", "https://github.com/widgetti/ipyvolume/issues/427"],
    "reference/panes/Matplotlib.ipynb": ["https://github.com/holoviz/panel/issues/4394"],
    "reference/panes/Param.ipynb": ["https://github.com/holoviz/panel/issues/4393"],
    "reference/panes/Reacton.ipynb": ["https://github.com/holoviz/panel/issues/4394"],
    "reference/panes/Str.ipynb": ["https://github.com/holoviz/panel/issues/4396"],
    "reference/panes/Streamz.ipynb": ["https://github.com/python-streamz/streamz/issues/467"],
    "reference/panes/VTK.ipynb": ["https://gitlab.kitware.com/vtk/vtk/-/issues/18806"],
    "reference/panes/VTKVolume.ipynb": ["https://gitlab.kitware.com/vtk/vtk/-/issues/18806"],
    "reference/widgets/CrossSelector.ipynb": ["https://github.com/holoviz/panel/issues/4398"],
    "reference/widgets/Debugger.ipynb": ["https://github.com/holoviz/panel/issues/4399"],
    "reference/widgets/EditableIntSlider.ipynb": ["https://github.com/holoviz/panel/issues/4400"],
    "reference/widgets/FileDownload.ipynb": ["https://github.com/holoviz/panel/issues/4401"],
    "reference/widgets/IntRangeSlider.ipynb": ["https://github.com/holoviz/panel/issues/4402"],
    "reference/widgets/MultiChoice.ipynb": ["https://github.com/holoviz/panel/issues/4403"],
    "reference/widgets/RangeSlider.ipynb": ["https://github.com/holoviz/panel/issues/4402"],
    "reference/widgets/SpeechToText.ipynb": ["https://github.com/holoviz/panel/issues/4404"],
    "reference/widgets/Terminal.ipynb": ["https://github.com/holoviz/panel/issues/4407"],
    "gallery/components/VuePdbInput.ipynb": ["https://github.com/holoviz/panel/issues/4417"],
}

def _get_dependencies(nbpath: pathlib.Path):
    key = str(nbpath).split("examples/")[-1]
    dependencies = DEPENDENCIES.get(key, DEFAULT_DEPENDENCIES)
    dependencies = [repr(d) for d in dependencies if not d in DEPENDENCY_NOT_IMPORTABLE]
    return dependencies


def _to_source(dependencies):
    return f"import piplite\nawait piplite.install([{', '.join(dependencies)}])"


def _get_install_code_cell(nbpath: pathlib.Path):
    dependencies = _get_dependencies(nbpath)
    source = _to_source(dependencies)
    install = nbformat.v4.new_code_cell(source=source)
    del install['id']
    return install

def copy_examples():
    nbs = list(EXAMPLES_DIR.glob('*/*/*.ipynb')) + list(EXAMPLES_DIR.glob('*/*.*'))
    for nb in nbs:
        nbpath = pathlib.Path(nb)
        out = (PANEL_BASE / 'lite/files') / nbpath.relative_to(EXAMPLES_DIR)
        out.parent.mkdir(parents=True, exist_ok=True)
        if nb.suffix == '.ipynb':
            with open(nb, encoding='utf-8') as fin:
                nb = nbformat.read(fin, 4)
                install = _get_install_code_cell(nbpath)
                nb['cells'].insert(0, install)
            with open(out, 'w', encoding='utf-8') as fout:
                nbformat.write(nb, fout)
        elif not nb.is_dir():
            shutil.copyfile(nb, out)

def copy_assets():
    shutil.copytree(
        EXAMPLES_DIR / 'assets',
        PANEL_BASE / 'lite' / 'files' / 'assets',
        dirs_exist_ok=True
    )

def download_sample_data():
    """
    Download larger data sets for various Bokeh examples.
    """
    from bokeh.util.sampledata import _download_file

    data_dir = PANEL_BASE / 'lite' / 'files' / 'assets' / 'sampledata'
    data_dir.mkdir(parents=True, exist_ok=True)

    s3 = 'http://sampledata.bokeh.org'
    files = json.loads((pathlib.Path(bokeh.util.sampledata.__file__).parent / 'sampledata.json').read_text())

    for filename, md5 in files:
        real_name, ext = os.path.splitext(filename)
        if ext == '.zip':
            if not os.path.splitext(real_name)[1]:
                real_name += ".csv"
        else:
            real_name += ext
        real_path = data_dir / real_name

        if real_path.is_file():
            local_md5 = hashlib.md5(open(real_path,'rb').read()).hexdigest()
            if local_md5 == md5:
                print(f"Skipping {filename!r} (checksum match)")
                continue
            else:
                print(f"Re-fetching {filename!r} (checksum mismatch)")
        _download_file(s3, filename, data_dir, progress=False)

if __name__=="__main__":
    copy_examples()
    copy_assets()
    download_sample_data()
