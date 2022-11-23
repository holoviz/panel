"""
Script that removes large files from bokeh wheel and repackages it
to be included in the NPM bundle.
"""

import glob
import os
import pathlib
import shutil
import subprocess
import sys
import zipfile

PANEL_BASE = pathlib.Path(__file__).parent.parent

sp = subprocess.Popen(['pip', 'wheel', '.', '-w', str(PANEL_BASE / 'build')], env=dict(os.environ, PANEL_LITE='1'))
sp.wait()

if len(sys.argv) > 1:
    out = pathlib.Path(sys.argv[1])
else:
    out = PANEL_BASE / 'panel/dist/wheels'

out.mkdir(exist_ok=True)

panel_wheels = list(PANEL_BASE.glob('build/panel-*-py3-none-any.whl'))
if not panel_wheels:
    raise RuntimeError('Panel wheel not found.')
panel_wheel = sorted(panel_wheels)[-1]

shutil.copyfile(panel_wheel, out / os.path.basename(panel_wheel).replace(".dirty", ""))

bokeh_wheels = PANEL_BASE.glob('build/bokeh-*-py3-none-any.whl')
if not bokeh_wheels:
    raise RuntimeError('Bokeh wheel not found.')
bokeh_wheel = sorted(bokeh_wheels)[-1]

zin = zipfile.ZipFile (bokeh_wheel, 'r')

zout = zipfile.ZipFile(out / os.path.basename(bokeh_wheel), 'w')
exts = ['.js', '.d.ts', '.tsbuildinfo']
for item in zin.infolist():
    filename = item.filename
    buffer = zin.read(filename)
    if (not filename.startswith('bokeh/core/_templates') and (
            filename.endswith('bokeh.json') or
            any(filename.endswith(ext) for ext in exts)
    )):
        continue
    elif filename.startswith('bokeh-') and filename.endswith('METADATA'):
        # remove tornado dependency
        buffer = '\n'.join([
            line for line in buffer.decode('utf-8').split('\n')
            if not ('Requires-Dist:' in line and 'tornado' in line)
        ]).encode('utf-8')
    zout.writestr(item, buffer)

zout.close()
zin.close()
