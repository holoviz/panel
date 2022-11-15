"""
Helper script to convert and copy example notebooks into JupyterLite build.
"""
import glob
import pathlib

import nbformat

nbs = glob.glob('./examples/**/*/*.ipynb') + glob.glob('./examples/*/*.ipynb')
install = nbformat.v4.new_code_cell(source="import piplite\nawait piplite.install(['panel'])")
del install['id']

for nb in nbs:
    nbpath = pathlib.Path(nb)
    with open(nb) as fin:
        nb = nbformat.read(fin, 4)
        nb['cells'].insert(0, install)
    out = pathlib.Path('./lite/files') / nbpath.relative_to("./examples/")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w') as fout:
        nbformat.write(nb, fout)
