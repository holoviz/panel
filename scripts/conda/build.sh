#!/usr/bin/env bash

set -euxo pipefail

PACKAGE="panel"

python -m build --sdist .

VERSION=$(python -c "import $PACKAGE; print($PACKAGE._version.__version__)")
export VERSION

# Prereleases depend on prereleases of other HoloViz packages, which are only
# published to pyviz/label/dev, so the build and test envs need that channel.
CHANNELS=$(python -c "
import os

import bokeh
from packaging.version import Version

channels = []
if Version(os.environ['VERSION']).is_prerelease:
    channels.append('pyviz/label/dev')
if Version(bokeh.__version__).is_prerelease:
    channels.append('bokeh/label/rc')
else:
    channels.append('bokeh')
channels.append('conda-forge')
print(' '.join(f'-c {channel}' for channel in channels))
")
read -ra CHANNEL_ARGS <<<"$CHANNELS"

conda build scripts/conda/recipe --no-anaconda-upload --no-verify "${CHANNEL_ARGS[@]}" --package-format 2

mv "$CONDA_PREFIX/conda-bld/noarch/$PACKAGE-$VERSION-py_0.conda" dist
