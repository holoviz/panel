#!/usr/bin/env bash

set -euxo pipefail

python ./scripts/build_pyodide_wheels.py dist
python ./scripts/panelite/generate_panelite_content.py

# Update lockfiles
cd "$(dirname "${BASH_SOURCE[0]}")"
rm -rf node_modules
npm install .
node update_lock.js
python patch_lock.py
rm node_modules/pyodide/*.whl

jupyter lite build

cp -r node_modules/pyodide/ ../../lite/dist/pyodide
mv pyodide-lock.json ../../lite/dist/pyodide/pyodide-lock.json
mv ../../dist/* ../../lite/dist/pyodide/
