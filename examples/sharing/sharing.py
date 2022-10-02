# Serve with panel serve examples/sharing/sharing.py --autoreload --static-dirs apps=apps/shared/target tmp-apps=apps/development/target
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

from pathlib import Path
from typing import Any, Dict

import param

import panel as pn

from panel.io.convert import convert_apps
from models import AppState
import config
import logging

def exception_handler(ex):
    logging.exception("Error", exc_info=ex)
    if pn.state.notifications and ex:
        pn.state.notifications.error(f"Error. {ex}")

pn.extension("ace", notifications=True, exception_handler=exception_handler)

APPS = "apps"
APP_FILE = "app.py"
ARGUMENT = "config"

CONVERTED_APPS = pathlib.Path("apps/converted").absolute()
SAVED_APPS = pathlib.Path("apps/saved").absolute()

(CONVERTED_APPS / "target").mkdir(parents=True, exist_ok="ok")
(SAVED_APPS / "target").mkdir(parents=True, exist_ok="ok")




class JSActions(pn.reactive.ReactiveHTML):
    developer_url = param.String()
    shared_url = param.String()

    # .event cannot trigger on js side. Thus I use Integer
    open_developer_link = param.Integer()
    open_shared_link = param.Integer()
    copy_shared_link = param.Integer()

    _template = """<div id="jsaction" style="height:0px;width:0px"></div>"""
    _scripts = {
        "open_developer_link": "url=window.location.href.replace('theme=default','').replace('/sharing','/') +  data.developer_url;console.log(url);window.open(url, '_blank')",
        "open_shared_link": "url=window.location.href.replace('theme=default','').replace('/sharing','/') +  data.shared_url;console.log(url);window.open(url, '_blank')",
        "copy_shared_link": "url=window.location.href.replace('theme=default','').replace('/sharing','/') +  data.shared_url;console.log(url);navigator.clipboard.writeText(url)",
    }

    

GALLERY_ENTRIES = {
    "Default": {"code": config.CODE, "requirements": ""},
    "Hello World": {"code": config.HELLO_WORLD_CODE, "requirements": ""},
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

    open_developer_link = param.Event()
    open_shared_link = param.Event()
    copy_shared_link = param.Event()
    
    new = param.Event()

    _state = param.ClassSelector(class_=AppState)
    gallery = param.ClassSelector(class_=AppGallery)
    jsactions = param.ClassSelector(class_=JSActions)

    development_src = param.String()
    shared_src = param.String()
    shared = param.Event()
    
    def __init__(self, state: AppState, **params):
        if not "gallery" in params:
            params["gallery"] = AppGallery()
        if not "jsactions" in params:
            params["jsactions"]=JSActions()
        super().__init__(_state=state, **params)
            
    def _get_random_key(self):
        return str(uuid.uuid4()) 

    @pn.depends("convert", watch=True)
    def _convert(self):
        key = self._get_random_key()
        self._state.site.development_storage[key]=self._state.project
        self.development_src = self._state.site.get_development_src(key)

    @property
    def _shared_key(self):
        return self._state.site.get_shared_key(user=self._state.user, project=self._state.project)
    
    @pn.depends("save", watch=True)
    def _save(self):
        key = self._shared_key
        self._state.site.shared_storage[key]=self._state.project
        self.shared_src = self._state.site.get_shared_src(key)
        self.shared=True

    @pn.depends("open_developer_link", watch=True)
    def _open_developer_link(self):
        print("opening_developer_link", self.development_src)
        self.jsactions.developer_url = self.development_src
        if self.jsactions.developer_url:
            self.jsactions.open_developer_link+=1
        else:
            raise ValueError("No developer link")
        print("opened_developer_link")
    
    @pn.depends("open_shared_link", watch=True)
    def _open_shared_link(self):
        print("opening_shared_link", self.shared_src)
        self.jsactions.shared_url = self.shared_src
        if self.jsactions.shared_url:
            self.jsactions.open_shared_link += 1
        else:
            raise ValueError("no shared link to open")
        print("opened_shared_link")
        
    @pn.depends("copy_shared_link", watch=True)
    def _copy_shared_link(self):
        print("copying_shared_link")
        self.jsactions.shared_url = self.shared_src
        if self.jsactions.shared_url:
            self.jsactions.copy_shared_link += 1
        else:
            raise ValueError("No shared link to copy")
        print("copy_shared_link")

    @pn.depends("new", watch=True)
    def _new(self):
        self._state.project.code = self.gallery.code
        self._state.requirements = self.gallery.requirements
        self._state.project = "new"
        self.convert = True

    def download_callback(self):
        key = self._shared_key
        return self._state.site.shared_storage.get_zipped_folder(key=key)
        
        
        


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


def to_html_file_name(app_name):
    return app_name.replace(".py", ".html").replace(".ipynb", ".html")


def serve_html(app_html):
    template = app_html.read_text()
    pn.Template(template).servable()


def to_iframe(src):
    return f"""<iframe frameborder="0" title="panel app" style="width: 100%;height:100%";flex-grow: 1" src="{src}" allow="accelerometer;autoplay;camera;document-domain;encrypted-media;fullscreen;gamepad;geolocation;gyroscope;layout-animations;legacy-image-formats;microphone;oversized-images;payment;publickey-credentials-get;speaker-selection;sync-xhr;unoptimized-images;unsized-media;screen-wake-lock;web-share;xr-spatial-tracking"></iframe>"""

state = AppState()
actions = AppActions(state=state)

configuration_tab = pn.Column(pn.Param(state.param.user, parameters="name"), state.project.param.name, name="Configure")

code_tab = pn.widgets.Ace.from_param(
    state.project.repository.param.code,
    language="python",
    theme="monokai",
    sizing_mode="stretch_both",
    name="app.py",
)
readme_tab = pn.widgets.Ace.from_param(
    state.project.repository.param.readme,
    language="markdown",
    theme="monokai",
    sizing_mode="stretch_both",
    name="readme.md",
)
@pn.depends(dataurl=state.project.repository.param.thumbnail)
def thumbnail_tab(dataurl):
    return pn.pane.HTML(f"""<img src={dataurl} style="height:100%;width:100%"></img>""", max_width=700, name="thumbnail.png", sizing_mode="scale_width")
requirements_tab = pn.widgets.Ace.from_param(
    state.project.repository.param.requirements,
    language="txt",
    theme="monokai",
    sizing_mode="stretch_both",
    name="requirements.txt",
)
file_tabs = pn.Tabs(code_tab, readme_tab, ("thumbnail.png", thumbnail_tab), requirements_tab, sizing_mode="stretch_both")
new_button = pn.widgets.Button.from_param(
    actions.param.new, sizing_mode="stretch_width", button_type="primary", name="Create"
)
new_tab = pn.Column(
    actions.gallery, new_button, sizing_mode="stretch_width", name="New"
)

faq_tab = pn.pane.Markdown(state.site.faq, name="FAQ", sizing_mode="stretch_both")
about_tab = pn.pane.Markdown(state.site.about, name="About", sizing_mode="stretch_both")

convert_button = pn.widgets.Button.from_param(
    actions.param.convert,
    name="▶️ CONVERT",
    sizing_mode="stretch_width",
    align="end",
    button_type="success",
)
open_developer_link_button = pn.widgets.Button.from_param(
    actions.param.open_developer_link,
    name="🔗 OPEN",
    width=125,
    sizing_mode="fixed",
    align="end",
    button_type="light",
)
share_button = pn.widgets.Button.from_param(
    actions.param.save,
    name="💾 SHARE",
    sizing_mode="stretch_width",
    align="end",
    button_type="success",
)
open_shared_link_button = pn.widgets.Button.from_param(
    actions.param.open_shared_link,
    name="🔗 OPEN",
    width=125,
    sizing_mode="fixed",
    align="end",
    button_type="light",
)
copy_shared_link_button = pn.widgets.Button.from_param(
    actions.param.copy_shared_link,
    name="✂️ COPY",
    width=125,
    sizing_mode="fixed",
    align="end",
    button_type="light",
)
download_saved_files = pn.widgets.FileDownload(
    callback=actions.download_callback,
    filename="saved.zip",
    width=125,
    button_type="light",
    sizing_mode="fixed",
    label="📁 DOWNLOAD",
)

actions_pane = pn.Row(
    actions.jsactions,
    convert_button,
    open_developer_link_button,
    share_button,
    open_shared_link_button,
    copy_shared_link_button,
    download_saved_files,
    sizing_mode="stretch_width",
    margin=(20, 5, 10, 5),
)
editor_tab = pn.Column(actions_pane, file_tabs, sizing_mode="stretch_both", name="Edit")
source_pane = pn.Tabs(new_tab, configuration_tab, editor_tab, faq_tab, about_tab, sizing_mode="stretch_both", active=2)
iframe_pane = pn.pane.HTML(sizing_mode="stretch_both")


@pn.depends(actions.param.development_src, watch=True)
def _update_iframe_pane(development_src):
    iframe_pane.object = ""
    iframe_pane.object = to_iframe(src=development_src)
    pn.state.notifications.success("Converted")


@pn.depends(actions.param.shared, watch=True)
def _notify_about_publish(_):
    pn.state.notifications.success("Shared")


actions.convert = True
# _update_iframe_pane()

target_pane = pn.Column(
    pn.panel(iframe_pane, sizing_mode="stretch_both"), sizing_mode="stretch_both"
)

template = pn.template.FastGridTemplate(
    site=state.site.name,
    title=state.site.title,
    theme_toggle=False,
    prevent_collision=True,
    save_layout=True,
)
template.main[0:5, 0:6] = source_pane
template.main[0:5, 6:12] = pn.panel(target_pane, sizing_mode="stretch_both")
template.servable()
