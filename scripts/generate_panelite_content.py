"""
Helper script to convert and copy example notebooks into JupyterLite build.
"""
import pathlib

import nbformat

PANEL_BASE = pathlib.Path(__file__).parent.parent
EXAMPLES_DIR = PANEL_BASE / 'examples'
DEPENDENCIES = [repr(d) for d in ['panel', 'pyodide-http', 'altair', 'hvplot', 'matplotlib', 'plotly', 'pydeck', 'scikit-learn']]

nbs = list(EXAMPLES_DIR.glob('*/*/*.ipynb')) + list(EXAMPLES_DIR.glob('*/*.ipynb'))
install = nbformat.v4.new_code_cell(source=f"import piplite\nawait piplite.install([{', '.join(DEPENDENCIES)}])")
del install['id']

for nb in nbs:
    nbpath = pathlib.Path(nb)
    with open(nb) as fin:
        nb = nbformat.read(fin, 4)
        nb['cells'].insert(0, install)
    out = (PANEL_BASE / 'lite/files') / nbpath.relative_to(EXAMPLES_DIR)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w') as fout:
        nbformat.write(nb, fout)
