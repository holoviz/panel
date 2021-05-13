"""
Function to configure serving the panel example apps via jupyter-server-proxy.
"""
import pathlib
from glob import glob

ICON_PATH = str((pathlib.Path(__file__).parent / "examples-icon.svg").absolute())

DONT_SERVE = [
    "examples/gallery/demos/attractors.ipynb",
    "examples/gallery/demos/gapminders.ipynb",
    "examples/gallery/demos/glaciers.ipynb",
    "examples/gallery/demos/nyc_taxi.ipynb",
    "examples/gallery/demos/portfolio-optimizer.ipynb",
]


def get_apps():
    return [
        app
        for app in glob("examples/gallery/**/*.ipynb", recursive=True)
        if not app in DONT_SERVE
    ]


def voila_serve_examples():
    """Returns the jupyter-server-proxy configuration for serving the example notebooks as Voila
    Apps.

    Returns:
        Dict: The configuration dictionary
    """
    # See:
    # https://jupyter-server-proxy.readthedocs.io/en/latest/server-process.html
    # https://github.com/holoviz/jupyter-panel-proxy/blob/master/panel_server/__init__.py
    return {
        "command": [
            "voila", # voila examples/gallery/dynamic --strip_sources=False --base_url
            "examples",
            "--no-browser",
            "--strip_sources=False",
            "--port",
            "{port}",
            "--base_url",
            "{base_url}docs/",
            "--VoilaConfiguration.file_whitelist",
            "'*.*'",
        ],
        "absolute_url": True,
        "timeout": 360,
        "launcher_entry": {
            "enabled": True,
            "title": "Docs",
            "icon_path": ICON_PATH,
        },
    }
