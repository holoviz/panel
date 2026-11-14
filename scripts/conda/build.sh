#!/usr/bin/env bash

set -euxo pipefail

PACKAGE="panel"

python -m build --sdist .

VERSION=$(python -c "import $PACKAGE; print($PACKAGE._version.__version__)")
export VERSION

# pyviz/label/dev is needed for prereleases of other HoloViz packages, and
# temporarily for final releases too: conda-forge's panel-material-ui depends on
# panel-core, which has no release compatible with Bokeh 3.10 yet.
CHANNELS=$(python -c "
import bokeh
from packaging.version import Version

channels = ['pyviz/label/dev']
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
