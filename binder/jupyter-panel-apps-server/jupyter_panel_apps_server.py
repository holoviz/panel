"""
Function to configure serving the panel example apps via jupyter-server-proxy.
"""
import pathlib
from glob import glob

ICON_PATH = str((pathlib.Path(__file__).parent / "examples-icon.svg").absolute())

def get_apps():
    return glob("examples/gallery/**/*.ipynb", recursive=True)

def panel_serve_examples():
    """Returns the jupyter-server-proxy configuration for serving the example notebooks as Panel
    apps.

    Returns:
        Dict: The configuration dictionary
    """
    apps =  get_apps()
    # See:
    # https://jupyter-server-proxy.readthedocs.io/en/latest/server-process.html
    # https://github.com/holoviz/jupyter-panel-proxy/blob/master/panel_server/__init__.py
    return {
        "command": [
            "panel",
            "serve",
            *apps,
            "--allow-websocket-origin=*",
            "--port",
            "{port}",
            "--prefix",
            "{base_url}panel",
        ],
        "absolute_url": True,
        "timeout": 360,
        "launcher_entry": {
            "enabled": True,
            "title": "Gallery",
            "icon_path": ICON_PATH,
        },
    }
