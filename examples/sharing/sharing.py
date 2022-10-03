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
import components
from utils import exception_handler

pn.extension("ace", notifications=True, exception_handler=exception_handler)

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


state = AppState()
state.convert()

new_project_tab = components.NewProject()
configuration_tab = components.settings_editor(state)

build_and_share = components.BuildAndShare(state=state)
repository_editor = components.RepositoryEditor(project=state.project)
editor_tab = pn.Column(build_and_share, repository_editor, sizing_mode="stretch_both", name="Edit")

source_pane = pn.Tabs(
    new_project_tab,
    configuration_tab,
    editor_tab,
    components.faq,
    components.about,
    sizing_mode="stretch_both",
    active=2,
)

iframe_pane = pn.bind(components.iframe, state.param.development_url)

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
template.main[0:5, 6:12] = target_pane
template.servable()
