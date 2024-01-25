import json
import pathlib
import subprocess

package_json = json.loads(
    (pathlib.Path(__file__).parent.parent / 'panel' / 'package.json').read_text()
)
js_version = package_json['version']

sp = subprocess.Popen(['aws', 's3', 'sync', 'panel/dist', f's3://cdn.holoviz.org/panel/{js_version}/dist/'])
sp.wait()
sp2 = subprocess.Popen(['aws', 's3', 'cp', 'panel/dist/wheels/', 's3://cdn.holoviz.org/panel/wheels/', '--recursive', '--exclude', '"*"', '--include', '"bokeh*"'])
sp2.wait()
sp3 = subprocess.Popen(['aws', 's3', 'cp', 'panel/package.json', f's3://cdn.holoviz.org/panel/{js_version}/package.json'])
sp3.wait()
