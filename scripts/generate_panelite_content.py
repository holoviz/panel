"""
Helper script to convert and copy example notebooks into JupyterLite build.
"""
import pathlib
import shutil

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
