#!/usr/bin/env bash

set -euxo pipefail

git status

export SETUPTOOLS_ENABLE_FEATURES="legacy-editable"
python -m build .

git diff --exit-code

export VERSION="$(echo "$(ls dist/*.whl)" | cut -d- -f2)"
conda build conda.recipe/ --no-test --no-anaconda-upload --no-verify
