import os

import pytest

pytest.importorskip("jupyter_server")

from panel.io.jupyter_server_extension import _load_jupyter_server_extension
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
