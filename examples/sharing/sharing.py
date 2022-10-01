# Serve with panel serve examples/sharing/sharing.py --autoreload --static-dirs apps=apps/saved/target tmp-apps=apps/converted/target
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
import param
import uuid

pn.extension("ace")

APPS = "apps"
APP_FILE = "app.py"
ARGUMENT = "config"
HELLO_WORLD_CODE = """\
import panel as pn

pn.panel("Hello World").servable()"""
CONVERTED_APPS = pathlib.Path("apps/converted").absolute()
SAVED_APPS = pathlib.Path("apps/saved").absolute()

CONVERTED_APPS.mkdir(parents=True, exist_ok="ok")
SAVED_APPS.mkdir(parents=True, exist_ok="ok")


class AppState(param.Parameterized):
    user = param.String()
    project = param.String()
    requirements = param.String()
    build_index = param.Boolean()
    build_pwa = param.Boolean()
    code = param.String(default=HELLO_WORLD_CODE)
    app_file = param.String(APP_FILE)

    def to_dict(self):
        requirements = self.requirements or []
        return {
            APPS: [self.app_file],
            "source": {self.app_file: self.code},
            "build_index": self.build_index,
            "build_pwa": self.build_pwa,
            "requirements": requirements,
        }

    @property
    def url_prefix(self):
        return f"{self.user}/{self.project}"

    @property
    def converted_source_dir(self):
        return CONVERTED_APPS / "source" / self.url_prefix

    @property
    def converted_target_dir(self):
        return CONVERTED_APPS / "target" / self.url_prefix

    @property
    def converted_url(self):
        return "tmp-apps/" + self.url_prefix + "/" + to_html_file_name(self.app_file)
    
    @property
    def saved_source_dir(self):
        return SAVED_APPS / "source" / self.url_prefix

    @property
    def saved_target_dir(self):
        return SAVED_APPS / "target" / self.url_prefix

    @property
    def saved_url(self):
        return "apps/" + self.url_prefix + "/" + to_html_file_name(self.app_file)

class JSActions(pn.reactive.ReactiveHTML):
    url = param.String()
    open = param.Integer()
    copy = param.Integer()

    
    _template="""<div id="jsaction" style="height:0px;width:0px"></div>"""
    _scripts = {
        "open": "window.open(window.location.href.replace('sharing?theme=default','') +  data.url, '_blank')",
        "copy": "navigator.clipboard.writeText(window.location.href.replace('sharing?theme=default','') +  data.url)",
    }

class AppActions(param.Parameterized):
    convert = param.Event()
    save = param.Event()
    open = param.Event()
    copy = param.Event()

    _state = param.ClassSelector(class_=AppState)
    jsactions = param.ClassSelector(class_=JSActions)

    def __init__(self, state: AppState, **params):
        super().__init__(_state=state, **params, jsactions=JSActions())

    def _convert_apps(self, source: pathlib.Path, target: pathlib.path):
        configuration = self._state.to_dict()
        source.mkdir(parents=True, exist_ok="ok")
        target.mkdir(parents=True, exist_ok="ok")
        with set_directory(source):
            save_files(configuration)
            config = {
                key: value
                for key, value in configuration.items()
                if key not in ["source"]
            }
            config["dest_path"] = str(target.absolute())
            convert_apps(**config)

    @pn.depends("convert", watch=True)
    def _update(self):
        self._convert_apps(
            source=self._state.converted_source_dir,
            target=self._state.converted_target_dir,
        )

    @pn.depends("save", watch=True)
    def _save(self):
        self._convert_apps(
            source=self._state.saved_source_dir, target=self._state.saved_target_dir
        )

    @pn.depends("open", watch=True)
    def _open(self):
        print("open")
        self.jsactions.url = self._state.saved_url
        self.jsactions.open+=1

    @pn.depends("copy", watch=True)
    def _copy(self):
        print("copy")
        self.jsactions.url = self._state.saved_url
        self.jsactions.copy+=1



class NoConfiguration(Exception):
    pass


class InvalidConfiguration(Exception):
    pass


def get_argument(session_args: Dict) -> bytes:
    if "config" in session_args:
        return session_args[ARGUMENT][0]
    else:
        raise NoConfiguration(f"No {ARGUMENT} provided")


def validate(configuration):
    if not APPS in configuration:
        raise InvalidConfiguration(f"No files found in the {ARGUMENT}")
    if not isinstance(configuration[APPS], list):
        raise InvalidConfiguration(
            f"The value of files in the {ARGUMENT} is not a list"
        )
    if not isinstance(configuration["source"], dict):
        raise InvalidConfiguration(
            f"The value of source in the {ARGUMENT} is not a dict"
        )
    files = configuration[APPS]
    if not files:
        raise InvalidConfiguration(f"No files found in the {ARGUMENT}")
    if len(files) > 1:
        raise InvalidConfiguration(
            f"More than one files found in {ARGUMENT}. This is currently not supported."
        )


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
    return f"""<iframe frameborder="0" title="panel app" style="width: 100%;height:100%";flex-grow: 1" src="{app_url}" allow="accelerometer;autoplay;camera;document-domain;encrypted-media;fullscreen;gamepad;geolocation;gyroscope;layout-animations;legacy-image-formats;microphone;oversized-images;payment;publickey-credentials-get;speaker-selection;sync-xhr;unoptimized-images;unsized-media;screen-wake-lock;web-share;xr-spatial-tracking"></iframe>"""


state = AppState(
    user="guest",
    project="tmp", # str(uuid.uuid4())
)

actions = AppActions(state)

configuration_tab = pn.Param(
    state,
    parameters=["requirements", "user", "project"],
    sizing_mode="stretch_width",
    name="Configuration",
)

editor = pn.widgets.Ace.from_param(
    state.param.code,
    language="python",
    theme="monokai",
    sizing_mode="stretch_both",
    name="Code",
)
servable = pn.widgets.TextInput(
    value="$ panel serve script.py", sizing_mode="stretch_width", disabled=True
)
source_pane = pn.Tabs(editor, configuration_tab, sizing_mode="stretch_both")

convert_button = pn.widgets.Button.from_param(
    actions.param.convert,
    name="▶️ CONVERT",
    sizing_mode="stretch_width",
    align="end",
    button_type="success",
)
save_button = pn.widgets.Button.from_param(
    actions.param.save,
    name="💾 SAVE",
    sizing_mode="stretch_width",
    align="end",
    button_type="success",
)
open_button = pn.widgets.Button.from_param(
    actions.param.open, name="🚪 OPEN SAVED LINK", sizing_mode="stretch_width", align="end", button_type="success"
)
copy_link = pn.widgets.Button.from_param(
    actions.param.copy, name="🔗 COPY SAVED LINK", sizing_mode="stretch_width", align="end", button_type="success"
)

target_actions = pn.Row(
    convert_button, save_button, copy_link, open_button, sizing_mode="stretch_width"
)
iframe_pane=pn.pane.HTML(sizing_mode="stretch_both")

@pn.depends(actions.param.convert, watch=True)
def _update_iframe_pane(_=None):
    iframe_pane.object = ""
    iframe_pane.object = to_iframe(state.converted_url)
_update_iframe_pane()

target_pane = pn.Column(actions.jsactions, target_actions, pn.panel(iframe_pane, sizing_mode="stretch_both"), sizing_mode="stretch_both")


template = pn.template.FastGridTemplate(
    site="Awesome Panel", title="Panel Sharing", theme_toggle=False, prevent_collision=True, save_layout=True,
)
template.main[0:6, 0:6] = source_pane
template.main[0:6, 6:12] = pn.panel(target_pane, sizing_mode="stretch_both")
template.servable()
