import os
import sys

import pytest

pytest.importorskip("jupyter_server")

from panel.io.jupyter_server_extension import (
    ExtensionStaticHandler, _load_jupyter_server_extension,
    find_extension_dist,
)
from panel.io.resources import JUPYTER_ENDPOINT_ENV, jupyter_endpoint_available


class _WebApp:

    settings = {'base_url': '/'}

    def add_handlers(self, host_pattern, host_handlers):
        pass


class _App:

    web_app = _WebApp()


def test_server_extension_announces_endpoint_to_kernels(monkeypatch):
    # Registers the variable so monkeypatch removes it again afterwards.
    monkeypatch.setenv(JUPYTER_ENDPOINT_ENV, '')
    assert not jupyter_endpoint_available()

    _load_jupyter_server_extension(_App())

    assert os.environ[JUPYTER_ENDPOINT_ENV]
    assert jupyter_endpoint_available()


@pytest.fixture
def extension_package(tmp_path, monkeypatch):
    package = tmp_path / 'panel_test_ext'
    dist = package / 'dist'
    dist.mkdir(parents=True)
    (package / '__init__.py').write_text('raise RuntimeError("must not be imported")')
    (dist / 'panel-test-ext.bundle.js').write_text('export default {}')
    monkeypatch.syspath_prepend(str(tmp_path))
    return dist


def test_find_extension_dist_does_not_import(extension_package):
    assert find_extension_dist('panel-test-ext') == extension_package
    assert 'panel_test_ext' not in sys.modules


@pytest.mark.parametrize('name', ['panel-test-missing', '..', 'os.path', ''])
def test_find_extension_dist_unresolvable(name):
    assert find_extension_dist(name) is None


def test_extension_static_handler_resolves_unregistered_extension(extension_package):
    root = {}
    path = ExtensionStaticHandler.get_absolute_path(
        root, os.path.join('panel-test-ext', 'panel-test-ext.bundle.js')
    )

    assert root == {'panel-test-ext': extension_package}
    assert path == str(extension_package / 'panel-test-ext.bundle.js')
