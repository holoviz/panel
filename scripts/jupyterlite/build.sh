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

rm -rf static/pyodide
mkdir -p static
cp -r node_modules/pyodide static/pyodide
mv pyodide-lock.json static/pyodide/pyodide-lock.json
mv ../../dist/* static/pyodide

jupyter lite build
