#!/usr/bin/env bash

set -euxo pipefail

PACKAGE="panel"

for file in dist/*.whl dist/*.tar.bz2; do
    if [ -e "$file" ]; then
        echo "dist folder already contains $(basename "$file"). Please delete it before running this script."
        exit 1
    fi
done

git diff --exit-code
python -m build . # Can add -w when this is solved: https://github.com/pypa/hatch/issues/1305

VERSION=$(find dist -name "*.whl" -exec basename {} \; | cut -d- -f2)
export VERSION
conda build scripts/conda/recipe --no-anaconda-upload --no-verify -c bokeh

mv "$CONDA_PREFIX/conda-bld/noarch/$PACKAGE-$VERSION-py_0.tar.bz2" dist
