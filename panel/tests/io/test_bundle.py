import hashlib
import json
import pathlib
import subprocess

import pytest

from panel.io import bundle
from panel.io.bundle import (
    PANEL_DIST, _fetch, bundle_assets, requirement_name, resolve_requirements,
)
from panel.io.convert import convert_app, script_to_html
from panel.io.resources import CDN_DIST

button_app = """
import panel as pn
pn.widgets.Button().servable()
"""


def _lock_package(name, file_name, depends=()):
    return {
        'name': name, 'version': '1.0', 'file_name': file_name,
        'install_dir': 'site', 'sha256': '', 'package_type': 'package',
        'imports': [name], 'depends': list(depends),
    }


@pytest.fixture
def fake_node(monkeypatch, tmp_path):
    """
    Replaces the node resolver with one returning a fixed lockfile.
    """
    calls = []
    state = {'packages': {}, 'failures': 0}

    def run(cmd, **kwargs):
        calls.append(cmd)
        state['spec'] = json.loads(pathlib.Path(cmd[-2]).read_text())
        if state['failures']:
            state['failures'] -= 1
            return subprocess.CompletedProcess(cmd, 1, '', 'x' * 1000 + '\nAbortError: fetch failed')
        lock = {'info': {'python': '3.14'}, 'packages': state['packages']}
        pathlib.Path(cmd[-1]).write_text(json.dumps(lock))
        return subprocess.CompletedProcess(cmd, 0, '', '')

    monkeypatch.setattr(bundle, 'ensure_node_env', lambda: tmp_path)
    monkeypatch.setattr(bundle, '_executable', lambda name: name)
    monkeypatch.setattr(bundle.subprocess, 'run', run)
    state['calls'] = calls
    return state


@pytest.mark.parametrize('requirement, name', [
    ('pandas', 'pandas'),
    ('Typing_Extensions>=4', 'typing-extensions'),
    ('https://cdn.holoviz.org/panel/wheels/bokeh-3.10.0-py3-none-any.whl', 'bokeh'),
    ('file:/tmp/wheels/pyviz_comms-3.0.6-py3-none-any.whl', 'pyviz-comms'),
])
def test_requirement_name(requirement, name):
    assert requirement_name(requirement) == name


def test_resolve_requirements_only_includes_dependencies(fake_node):
    fake_node['packages'] = {
        'panel': _lock_package('panel', 'https://example.com/panel-1.0-py3-none-any.whl', ['param']),
        'param': _lock_package('param', 'https://example.com/param-1.0-py3-none-any.whl'),
        'numpy': _lock_package('numpy', '/node/numpy-1.0-cp314-cp314-pyemscripten_2026_0_wasm32.whl'),
    }

    lock = resolve_requirements(['panel'])

    assert list(lock['packages']) == ['panel', 'param']


def test_resolve_requirements_breaks_dependency_cycles(fake_node):
    fake_node['packages'] = {
        'panel': _lock_package('panel', 'panel-1.0-py3-none-any.whl', ['panel-material-ui', 'param']),
        'panel-material-ui': _lock_package('panel-material-ui', 'panel_material_ui-1.0-py3-none-any.whl', ['panel']),
        'param': _lock_package('param', 'param-1.0-py3-none-any.whl'),
    }

    lock = resolve_requirements(['panel'])

    packages = lock['packages']
    assert set(packages) == {'panel', 'panel-material-ui', 'param'}
    assert packages['panel']['depends'] == ['panel-material-ui', 'param']
    assert packages['panel-material-ui']['depends'] == []


def test_resolve_requirements_installs_local_wheels_from_emfs(fake_node):
    wheel = '/tmp/wheels/panel-1.0-py3-none-any.whl'
    fake_node['packages'] = {
        'panel': _lock_package('panel', 'emfs:/bundle_wheels/panel-1.0-py3-none-any.whl'),
    }

    lock = resolve_requirements([f'file:{wheel}'])

    assert fake_node['spec'] == {
        'requirements': ['emfs:/bundle_wheels/panel-1.0-py3-none-any.whl'],
        'wheels': {'panel-1.0-py3-none-any.whl': wheel},
    }
    assert lock['packages']['panel']['file_name'] == wheel


def test_resolve_requirements_retries_failures(fake_node):
    fake_node['packages'] = {'param': _lock_package('param', 'param-1.0-py3-none-any.whl')}
    fake_node['failures'] = 2

    lock = resolve_requirements(['param'])

    assert len(fake_node['calls']) == 3
    assert list(lock['packages']) == ['param']


def test_resolve_requirements_raises_after_retries(fake_node):
    fake_node['failures'] = 3

    with pytest.raises(RuntimeError) as excinfo:
        resolve_requirements(['param'])

    message = str(excinfo.value)
    assert 'AbortError: fetch failed' in message
    assert 'x' * 1000 not in message


def test_fetch_copies_local_file(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text('content')
    dest = tmp_path / 'nested' / 'dest.txt'

    _fetch(source, dest)

    assert dest.read_text() == 'content'
    assert dest.stat().st_mode & 0o777 == 0o644


def test_fetch_replaces_changed_file(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text('new')
    dest = tmp_path / 'dest.txt'
    dest.write_text('old')

    _fetch(source, dest)

    assert dest.read_text() == 'new'


def test_fetch_hash_mismatch(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text('content')
    dest = tmp_path / 'dest.txt'

    with pytest.raises(ValueError, match='Hash mismatch'):
        _fetch(source, dest, sha256=hashlib.sha256(b'other').hexdigest())

    assert list(tmp_path.iterdir()) == [source]


def test_bundle_assets_rewrites_and_copies_panel_assets(tmp_path):
    tabulator = 'bundled/datatabulator/tabulator-tables@6.4.0/dist/js/tabulator.min.js'
    html = (
        f'<link href="{CDN_DIST}css/loading.css">'
        f'<script src="{CDN_DIST}{tabulator}"></script>'
    )

    bundled = bundle_assets(html, tmp_path)

    assert CDN_DIST not in bundled
    assert f'./{PANEL_DIST}css/loading.css' in bundled
    panel_dist = tmp_path / PANEL_DIST
    assert (panel_dist / tabulator).is_file()
    assert (panel_dist / 'bundled' / 'datatabulator' / 'tabulator-tables@6.4.0' / 'dist' / 'css').is_dir()
    assert (panel_dist / 'css' / 'loading.css').is_file()
    assert (panel_dist / 'bundled' / 'font-awesome' / 'css' / 'all.min.css').is_file()


def test_bundle_assets_copies_extension_assets(tmp_path):
    html = '<link href="static/extensions/panel/css/loading.css?v=1">'

    bundled = bundle_assets(html, tmp_path)

    assert bundled == html
    assert (tmp_path / 'static' / 'extensions' / 'panel' / 'css' / 'loading.css').is_file()


@pytest.mark.parametrize('offline', [False, True])
def test_script_to_html_bundle_worker(tmp_path, offline):
    app = tmp_path / 'app.py'
    app.write_text(button_app)

    _, worker = script_to_html(
        app, requirements=['panel'], runtime='pyodide-worker',
        bundle='pyodide/app-lock.json', offline=offline
    )

    assert 'import { loadPyodide } from "./pyodide/pyodide.mjs"' in worker
    assert 'lockFileURL: new URL("./pyodide/app-lock.json", location.href).href' in worker
    assert 'packageBaseUrl: new URL("./pyodide/", location.href).href' in worker
    assert "loadPackage(['panel'])" in worker
    assert 'micropip' not in worker
    assert ('PANEL_CDN_ROOT' in worker) is offline


def test_script_to_html_bundle_main_thread(tmp_path):
    app = tmp_path / 'app.py'
    app.write_text(button_app)

    html, _ = script_to_html(
        app, requirements=['panel'], runtime='pyodide', bundle='pyodide/app-lock.json'
    )

    assert '<script src="./pyodide/pyodide.js" defer></script>' in html
    assert "loadPackage(['panel'])" in html
    assert 'micropip' not in html


@pytest.mark.parametrize('runtime', ['pyscript', 'pyscript-worker'])
def test_convert_app_bundle_pyscript_unsupported(tmp_path, runtime):
    app = tmp_path / 'app.py'
    app.write_text(button_app)

    with pytest.raises(ValueError, match='Bundling is only supported'):
        convert_app(app, tmp_path, runtime=runtime, bundle=True)
