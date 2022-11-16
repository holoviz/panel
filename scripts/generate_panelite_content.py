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
DEPENDENCIES = [repr(d) for d in ['panel', 'pyodide-http', 'altair', 'hvplot', 'matplotlib', 'plotly', 'pydeck', 'scikit-learn']]

nbs = list(EXAMPLES_DIR.glob('*/*/*.ipynb')) + list(EXAMPLES_DIR.glob('*/*.*'))
install = nbformat.v4.new_code_cell(source=f"import piplite\nawait piplite.install([{', '.join(DEPENDENCIES)}])")
del install['id']

for nb in nbs:
    nbpath = pathlib.Path(nb)
    out = (PANEL_BASE / 'lite/files') / nbpath.relative_to(EXAMPLES_DIR)
    out.parent.mkdir(parents=True, exist_ok=True)
    if nb.suffix == '.ipynb':
        with open(nb, encoding='utf-8') as fin:
            nb = nbformat.read(fin, 4)
            nb['cells'].insert(0, install)
        with open(out, 'w', encoding='utf-8') as fout:
            nbformat.write(nb, fout)
    elif not nb.is_dir():
        shutil.copyfile(nb, out)

# Copy assets
shutil.copytree(
    EXAMPLES_DIR / 'assets',
    PANEL_BASE / 'lite' / 'files' / 'assets',
    dirs_exist_ok=True
)

# Download sampledata
def download():
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

download()
