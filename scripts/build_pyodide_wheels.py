"""
Script that removes large files from bokeh wheel and repackages it
to be included in the NPM bundle.
"""

import glob
import os
import shutil
import subprocess
import zipfile

sp = subprocess.Popen(['pip', 'wheel', '.', '-w', './build'], env=dict(os.environ, PANEL_LITE='1'))
sp.wait()

os.mkdir('panel/dist/wheels')

panel_wheels = glob.glob('build/panel-*-py3-none-any.whl')

if not panel_wheels:
    raise RuntimeError('Panel wheel not found.')

panel_wheel = sorted(panel_wheels)[-1]
shutil.copyfile(panel_wheel, f'panel/dist/wheels/{os.path.basename(panel_wheel).replace(".dirty", "")}')

bokeh_wheels = glob.glob('build/bokeh-*-py3-none-any.whl')
if not bokeh_wheels:
    raise RuntimeError('Bokeh wheel not found.')

bokeh_wheel = sorted(bokeh_wheels)[-1]
zin = zipfile.ZipFile (bokeh_wheel, 'r')
zout = zipfile.ZipFile (f'panel/dist/wheels/{os.path.basename(bokeh_wheel)}', 'w')
exts = ['.js', '.d.ts', '.tsbuildinfo']
for item in zin.infolist():
    buffer = zin.read(item.filename)
    if not (item.filename.endswith('bokeh.json') or any(item.filename.endswith(ext) for ext in exts)):
        zout.writestr(item, buffer)

zout.close()
zin.close()
