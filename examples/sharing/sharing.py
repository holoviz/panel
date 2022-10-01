from __future__ import annotations

import base64
import json
import pathlib

from typing import Any, Dict

import panel as pn
import tempfile
from panel.io.convert import convert_apps
from contextlib import contextmanager
from pathlib import Path
import sys
import os

ARGUMENT = "config"
APPS = "apps"
DEST_PATH = "build"
class NoConfiguration(Exception):
    pass

class InvalidConfiguration(Exception):
    pass

def encode(configuration: Dict, encoding="utf8") -> bytes:
    converted = json.dumps(configuration).encode(encoding="utf8")
    encoded = base64.b64encode(converted)
    return encoded

def decode(configuration: bytes) -> Dict:
    decoded = base64.b64decode(configuration)
    original = json.loads(decoded)
    return original

def to_configuration(code, build_index=False, build_pwa=False):
    return {APPS: ["script.py"], "source": {"script.py": code}, "build_index": build_index, "build_pwa": build_pwa}

def get_argument(session_args: Dict) -> bytes:
    if "config" in session_args:
        return session_args[ARGUMENT][0]
    else:
        raise NoConfiguration(f"No {ARGUMENT} provided")

def validate(configuration):
    if not APPS in configuration:
        raise InvalidConfiguration(f"No files found in the {ARGUMENT}")
    if not isinstance(configuration[APPS], list):
        raise InvalidConfiguration(f"The value of files in the {ARGUMENT} is not a list")
    if not isinstance(configuration["source"], dict):
        raise InvalidConfiguration(f"The value of source in the {ARGUMENT} is not a dict")
    files = configuration[APPS]
    if not files:
        raise InvalidConfiguration(f"No files found in the {ARGUMENT}")
    if len(files)>1:
        raise InvalidConfiguration(f"More than one files found in {ARGUMENT}. This is currently not supported.")

@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)

def save_files(configuration: Dict):
    for file, text in configuration["source"].items():
        pathlib.Path(file).write_text(text)
    
    pathlib.Path("config.json").write_text(json.dumps(configuration))

def to_html_file_name(app_name):
    return app_name.replace(".py", ".html").replace(".ipynb", ".html")

def serve_html(app_html):
    template = app_html.read_text()
    pn.Template(template).servable()

def to_iframe(app_url):
    return f"""<iframe frameborder="0" title="panel app" class="preview-iframe" style="width: 100%;height:100%";flex-grow: 1;" src="{app_url}" allow="accelerometer;autoplay;camera;document-domain;encrypted-media;fullscreen;gamepad;geolocation;gyroscope;layout-animations;legacy-image-formats;microphone;oversized-images;payment;publickey-credentials-get;speaker-selection;sync-xhr;unoptimized-images;unsized-media;screen-wake-lock;web-share;xr-spatial-tracking"></iframe>"""

APPS_ROOT = pathlib.Path("apps")
SOURCE_ROOT = APPS_ROOT / "source"
TARGET_ROOT = APPS_ROOT / "target"

save_button = pn.widgets.Button(name="Save", sizing_mode="fixed", align="end")
requirements = pn.widgets.TextInput(name="Requirements", sizing_mode="stretch_width")
source_actions = pn.Row(requirements, save_button, sizing_mode="stretch_width")

code = """\
import panel as pn
pn.panel("Hello World").servable()"""
editor = pn.widgets.Ace(value=code, sizing_mode="stretch_both")
source_pane = pn.Column(source_actions, editor, sizing_mode="stretch_both")

@pn.depends(save_button)
def target_pane(_):
    code = editor.value
    configuration = to_configuration(code)

    DIR = str(hash(str(configuration))% ((sys.maxsize + 1) * 2))
    SOURCE = SOURCE_ROOT/DIR
    TARGET = TARGET_ROOT/DIR

    SOURCE.mkdir(parents=True, exist_ok="ok")
    TARGET.mkdir(parents=True, exist_ok="ok")
    configuration["dest_path"]=str(TARGET.absolute())

    with set_directory(SOURCE):
        save_files(configuration)   
        config = {key: value for key, value in configuration.items() if key not in ["source"]}
        convert_apps(**config)

    app_url = "apps/" + DIR + "/" + to_html_file_name(configuration[APPS][0])



    target_link = pn.pane.HTML(f"<a href='{app_url}' target='_blank'>App Link</a>", sizing_mode="fixed")
    iframe_pane = pn.pane.HTML(to_iframe(app_url), sizing_mode="stretch_both")
    return pn.Column(target_link, iframe_pane, sizing_mode="stretch_both")

pn.Row(source_pane, pn.panel(target_pane, sizing_mode="stretch_both"), sizing_mode="stretch_both").servable()