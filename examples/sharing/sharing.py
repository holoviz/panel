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

# Test

test_configuration = {APPS: {"script.py": """
import panel as pn
pn.panel("Hello World").servable()
"""}}

encoded = encode(test_configuration)
print("test url:", f'http://localhost:5006/sharing?{ARGUMENT}={encoded.decode("utf8")}')
decoded = decode(encoded)
assert decoded == test_configuration

def get_argument() -> bytes:
    if "config" in pn.state.session_args:
        return pn.state.session_args[ARGUMENT][0]
    else:
        raise NoConfiguration(f"No {ARGUMENT} provided")

def to_configuration(argument: bytes)->Dict:
    try:
        return decode(argument)
    except json.decoder.JSONDecodeError as ex:
        raise InvalidConfiguration(f"Could not convert the {ARGUMENT} to a dictionary") from ex

def validate(configuration):
    if not APPS in configuration:
        raise InvalidConfiguration(f"No files found in the {ARGUMENT}")
    if not isinstance(configuration[APPS], dict):
        raise InvalidConfiguration(f"The value of files in the {ARGUMENT} is not a dictionary")
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
    for file, text in configuration[APPS].items():
        pathlib.Path(file).write_text(text)

def to_html_file_name(app_name):
    return app_name.replace(".py", ".html").replace(".ipynb", ".html")

def serve_html(app_html):
    template = app_html.read_text()
    pn.Template(template).servable()

argument = get_argument()
configuration = to_configuration(argument)
validate(configuration)

with tempfile.TemporaryDirectory() as directory:
     with set_directory(directory):
        save_files(configuration)
        configuration["dest_path"]=DEST_PATH
        configuration[APPS]=list(configuration[APPS].keys())
        convert_apps(**configuration)
        app_html_name = to_html_file_name(configuration[APPS][0])
        app_html = pathlib.Path(directory)/DEST_PATH/app_html_name
        serve_html(app_html)



