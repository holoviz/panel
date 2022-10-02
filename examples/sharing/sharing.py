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
import datetime as dt
import time

pn.extension("ace", notifications=True)

APPS = "apps"
APP_FILE = "app.py"
ARGUMENT = "config"
DEFAULT_CODE = """\
import panel as pn

pn.extension(template="fast")
pn.state.template.param.update(site="Panel", title="New")

pn.panel("Hello World").servable()"""
HELLO_WORLD_CODE = """\
import panel as pn

pn.panel("Hello World").servable()"""
CONVERTED_APPS = pathlib.Path("apps/converted").absolute()
SAVED_APPS = pathlib.Path("apps/saved").absolute()

(CONVERTED_APPS / "target").mkdir(parents=True, exist_ok="ok")
(SAVED_APPS / "target").mkdir(parents=True, exist_ok="ok")


class AppState(param.Parameterized):
    user = param.String("guest", constant=True)
    project = param.String("new")
    code = param.String(default=DEFAULT_CODE)
    requirements = param.String()

    build_index = param.Boolean(constant=True)
    build_pwa = param.Boolean(constant=True)

    code_file_type = param.String(".py", readonly=True)

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
    def app_file(self):
        return APP_FILE

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
    open = param.Event()
    copy = param.Event()

    _template = """<div id="jsaction" style="height:0px;width:0px"></div>"""
    _scripts = {
        "open": "window.open(window.location.href.replace('sharing?theme=default','') +  data.url, '_blank')",
        "copy": "navigator.clipboard.writeText(window.location.href.replace('sharing?theme=default','') +  data.url)",
    }

    @pn.depends("copy", watch=True)
    def _hello(self):
        print("go copy")


GALLERY_ENTRIES = {
    "Default": {"code": DEFAULT_CODE, "requirements": ""},
    "Hello World": {"code": HELLO_WORLD_CODE, "requirements": ""},
}


class AppGallery(pn.viewable.Viewer):
    selection = param.Selector(objects=list(GALLERY_ENTRIES))

    def __init__(self, **params):
        super().__init__(**params)
        self._panel = pn.widgets.RadioBoxGroup.from_param(
            self.param.selection,
            sizing_mode="stretch_width",
            orientation="vertical",
            margin=(20, 5, 10, 5),
        )

    def __panel__(self):
        return self._panel

    @property
    def code(self):
        return GALLERY_ENTRIES[self.selection]["code"]

    @property
    def requirements(self):
        return GALLERY_ENTRIES[self.selection]["requirements"]


class AppActions(param.Parameterized):
    convert = param.Event()
    save = param.Event()
    open = param.Event()
    copy = param.Event()
    new = param.Event()

    _state = param.ClassSelector(class_=AppState)
    gallery = param.ClassSelector(class_=AppGallery)
    jsactions = param.ClassSelector(class_=JSActions)

    last_conversion = param.Date()
    last_published = param.Date()

    def __init__(self, state: AppState, **params):
        if not "gallery" in params:
            params["gallery"] = AppGallery()

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
    def _convert(self):
        self._convert_apps(
            source=self._state.converted_source_dir,
            target=self._state.converted_target_dir,
        )
        self.last_conversion = dt.datetime.now()
        time.sleep(0.25)

    @pn.depends("save", watch=True)
    def _save(self):
        self._convert_apps(
            source=self._state.saved_source_dir, target=self._state.saved_target_dir
        )
        self.last_published = dt.datetime.now()

    @pn.depends("open", watch=True)
    def _open(self):
        print("open")
        self.jsactions.url = self._state.saved_url
        self.jsactions.open = True
        print("opened")

    @pn.depends("copy", watch=True)
    def _copy(self):
        print("copy")
        self.jsactions.url = self._state.saved_url
        self.jsactions.copy = True

    @pn.depends("new", watch=True)
    def _new(self):
        self._state.code = self.gallery.code
        self._state.requirements = self.gallery.requirements
        self._state.project = "new"
        self.convert = True


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


state = AppState()
actions = AppActions(state=state)

configuration_pane = pn.Param(
    state,
    parameters=["user", "project", "requirements", "build_index", "build_pwa"],
    sizing_mode="stretch_width",
    name="configuration.json",
    show_name=False,
)

code_editor = pn.widgets.Ace.from_param(
    state.param.code,
    language="python",
    theme="monokai",
    sizing_mode="stretch_both",
    name="app.py",
)
editor = pn.Tabs(code_editor, configuration_pane, sizing_mode="stretch_both")
new_button = pn.widgets.Button.from_param(
    actions.param.new, sizing_mode="stretch_width", button_type="primary", name="Create"
)
new_tab = pn.Column(
    actions.gallery, new_button, sizing_mode="stretch_width", name="New"
)
faq_text = """
# Frequently Asked Questions

## What is the purpose of the sharing service?

The purpose of this project is to make it easy for you, me and the rest of the Panel community to
share Panel apps.

## What are my rights when using the sharing service?

By using this project you consent to making your project publicly available and
[MIT licensed](https://opensource.org/licenses/MIT).

On the other hand I cannot guarentee the persisting of your project. Use at your own risk.

## How do I add more files to a project?

You cannot do this as that would complicate this free and personal project.

What you can do is 

- Package your python code into a python package that you share on pypi and add it to the
`requirements`
- Store your other files somewhere public. For example on Github.

## What are the most useful resources for Panel data apps?

- [Panel](https://holoviz.panel.org) | [WebAssembly User Guide](https://pyviz-dev.github.io/panel/user_guide/Running_in_Webassembly.html) | [Community Forum](https://discourse.holoviz.org/) | [Github Code](https://github.com/holoviz/panel) | [Github Issues](https://github.com/holoviz/panel/issues) | [Twitter](https://mobile.twitter.com/panel_org) | [LinkedIn](https://www.linkedin.com/company/79754450)
- [Awesome Panel](https://awesome-panel.org) | [Github Code](https://github.com/marcskovmadsen/awesome-panel) | [Github Issues](https://github.com/MarcSkovMadsen/awesome-panel/issues)
- Marc Skov Madsen | [Twitter](https://twitter.com/MarcSkovMadsen) | [LinkedIn](https://www.linkedin.com/in/marcskovmadsen/)
- Sophia Yang | [Twitter](https://twitter.com/sophiamyang) | [Medium](https://sophiamyang.medium.com/)
- [Pyodide](https://pyodide.org) | [FAQ](https://pyodide.org/en/stable/usage/faq.html)
- [PyScript](https://pyscript.net/) | [FAQ](https://docs.pyscript.net/latest/reference/faq.html)

## How did you make the Panel Sharing service?

With Panel of course. Check out the code on
[Github](https://github.com/marcskovmadsen/awesome-panel)
"""

faq_tab = pn.pane.Markdown(faq_text, name="FAQ", sizing_mode="stretch_both")

convert_button = pn.widgets.Button.from_param(
    actions.param.convert,
    name="▶️ CONVERT",
    sizing_mode="stretch_width",
    align="end",
    button_type="success",
)
publish_button = pn.widgets.Button.from_param(
    actions.param.save,
    name="💾 PUBLISH",
    sizing_mode="stretch_width",
    align="end",
    button_type="success",
)
open_button = pn.widgets.Button.from_param(
    actions.param.open,
    name="🚪 OPEN PUBLIC LINK",
    sizing_mode="stretch_width",
    align="end",
    button_type="success",
)
copy_link = pn.widgets.Button.from_param(
    actions.param.copy,
    name="🔗 COPY PUBLIC LINK",
    sizing_mode="stretch_width",
    align="end",
    button_type="success",
)
download_saved_files = pn.widgets.FileDownload(
    filename="download.zip",
    disabled=True,
    button_type="success",
    sizing_mode="stretch_width",
)

actions_pane = pn.Row(
    actions.jsactions,
    convert_button,
    publish_button,
    copy_link,
    open_button,
    download_saved_files,
    sizing_mode="stretch_width",
    margin=(20, 5, 10, 5),
)
editor_tab = pn.Column(actions_pane, editor, sizing_mode="stretch_both", name="Edit")
source_pane = pn.Tabs(new_tab, editor_tab, faq_tab, sizing_mode="stretch_both", active=1)
iframe_pane = pn.pane.HTML(sizing_mode="stretch_both")


@pn.depends(actions.param.last_conversion, watch=True)
def _update_iframe_pane(last_conversion=None):
    iframe_pane.object = ""
    iframe_pane.object = to_iframe(
        state.converted_url + f"?last_conversion={last_conversion}"
    )
    pn.state.notifications.success("Converted")


@pn.depends(actions.param.last_published, watch=True)
def _notify_about_publish(last_published=None):
    pn.state.notifications.success("Published")


actions.convert = True
_update_iframe_pane()

target_pane = pn.Column(
    pn.panel(iframe_pane, sizing_mode="stretch_both"), sizing_mode="stretch_both"
)

template = pn.template.FastGridTemplate(
    site="Panel",
    title="Sharing",
    theme_toggle=False,
    prevent_collision=True,
    save_layout=True,
)
template.main[0:5, 0:6] = source_pane
template.main[0:5, 6:12] = pn.panel(target_pane, sizing_mode="stretch_both")
template.servable()
