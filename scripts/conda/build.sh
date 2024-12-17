#!/usr/bin/env bash

set -euxo pipefail

PACKAGE="panel"

python -m build -w .

VERSION=$(python -c "import $PACKAGE; print($PACKAGE._version.__version__)")
export VERSION

BK_CHANNEL=$(python -c "
import bokeh
from packaging.version import Version

if Version(bokeh.__version__).is_prerelease:
    print('bokeh/label/dev')
else:
    print('bokeh')
")

conda build scripts/conda/recipe --no-anaconda-upload --no-verify -c "$BK_CHANNEL" -c conda-forge

mv "$CONDA_PREFIX/conda-bld/noarch/$PACKAGE-$VERSION-py_0.tar.bz2" dist
