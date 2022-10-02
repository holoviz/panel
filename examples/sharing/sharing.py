# Serve with panel serve examples/sharing/sharing.py --autoreload --static-dirs apps=apps/saved/target tmp-apps=apps/converted/target
from __future__ import annotations

import base64
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import uuid

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict

import param

import panel as pn

from panel.io.convert import convert_apps

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

THUMBNAIL_DATA_URL = """data:image/png;base64,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IDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAACpRfx/59g1bsDfGW0AAAAASUVORK5CYII="""


class AppState(param.Parameterized):
    user = param.String("guest", constant=True)
    project = param.String("new")
    
    code = param.String(default=DEFAULT_CODE)
    readme = param.String("# Introduction\n\nThis purpose of this project ...")
    thumbnail = param.String(THUMBNAIL_DATA_URL)
    requirements = param.String()

    def to_dict(self):
        requirements = self.requirements or []
        return {
            APPS: [self.app_file],
            "source": {self.app_file: self.code},
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
        "open": "url=window.location.href.replace('theme=default','').replace('/sharing','/') +  data.url;window.open(url, '_blank')",
        "copy": "url=window.location.href.replace('theme=default','').replace('/sharing','/') +  data.url;navigator.clipboard.writeText(url)",
    }


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
        if not "jsactions" in params:
            params["jsactions"]=JSActions()
        super().__init__(_state=state, **params)

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
            command = f"panel convert app.py --to pyodide-worker --out {target.absolute()}"
            result = subprocess.run(command, shell=True)
            # For some unknown reason this produces .html files that do not work
            # I can see that it includes traces of ace and JSActions in the produced .html file.
            # Its unfortunate as it runs very, very fast.
            # convert_apps(**config)
            

    @pn.depends("convert", watch=True)
    def _convert(self):
        self._convert_apps(
            source=self._state.converted_source_dir,
            target=self._state.converted_target_dir,
        )
        self.last_conversion = dt.datetime.now()        

    @pn.depends("save", watch=True)
    def _save(self):
        self._convert_apps(
            source=self._state.saved_source_dir, target=self._state.saved_target_dir
        )
        self.last_published = dt.datetime.now()

    @pn.depends("open", watch=True)
    def _open(self):
        self.jsactions.url = self._state.saved_url
        self.jsactions.open = True
        
    @pn.depends("copy", watch=True)
    def _copy(self):
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

configuration_tab = pn.Param(
    state,
    parameters=["user", "project", "requirements"],
    sizing_mode="stretch_width",
    name="configuration.json",
    show_name=False,
)

code_tab = pn.widgets.Ace.from_param(
    state.param.code,
    language="python",
    theme="monokai",
    sizing_mode="stretch_both",
    name="app.py",
)
readme_tab = pn.widgets.Ace.from_param(
    state.param.readme,
    language="markdown",
    theme="monokai",
    sizing_mode="stretch_both",
    name="readme.md",
)
@pn.depends(dataurl=state.param.thumbnail)
def thumbnail_tab(dataurl):
    return pn.pane.HTML(f"""<img src={dataurl} style="height:100%;width:100%"></img>""", max_width=700, name="thumbnail.png", sizing_mode="scale_width")
file_tabs = pn.Tabs(code_tab, readme_tab, ("thumbnail.png", thumbnail_tab), configuration_tab, sizing_mode="stretch_both")
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
editor_tab = pn.Column(actions_pane, file_tabs, sizing_mode="stretch_both", name="Edit")
source_pane = pn.Tabs(new_tab, editor_tab, faq_tab, sizing_mode="stretch_both", active=1)
iframe_pane = pn.pane.HTML(sizing_mode="stretch_both")


@pn.depends(actions.param.last_conversion, watch=True)
def _update_iframe_pane(last_conversion):
    iframe_pane.object = ""
    iframe_pane.object = to_iframe(
        state.converted_url + f"?last_conversion={last_conversion}"
    )
    pn.state.notifications.success("Converted")


@pn.depends(actions.param.last_published, watch=True)
def _notify_about_publish(last_published=None):
    pn.state.notifications.success("Published")


actions.convert = True
# _update_iframe_pane()

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
