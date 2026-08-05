"""Smoke tests for jupyter_server extension discovery entry points."""

from panel import (
    _jupyter_server_extension_paths, _jupyter_server_extension_points,
)
from panel.io.notebook import (
    _jupyter_server_extension_paths as paths_from_notebook,
    _jupyter_server_extension_points as points_from_notebook,
)


def test_jupyter_server_extension_points_shape():
    points = _jupyter_server_extension_points()
    assert points == [{"module": "panel.io.jupyter_server_extension"}]
    assert points_from_notebook() == points


def test_jupyter_server_extension_paths_aliases_points():
    assert _jupyter_server_extension_paths() == _jupyter_server_extension_points()
    assert paths_from_notebook() == points_from_notebook()
