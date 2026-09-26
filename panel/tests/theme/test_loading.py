import json

import pytest

from panel.config import config
from panel.io.convert import loading_resources as _convert_resources
from panel.io.loading import (
    loading_css, loading_css_classes, loading_options, loading_resources,
    start_loading_spinner, stop_loading_spinner,
)
from panel.io.resources import CDN_DIST
from panel.layout import Column
from panel.theme import Material
from panel.theme.base import Design
from panel.widgets import TextInput


class LoadingDesign(Design):

    _loading_options = {
        'spinner': 'material',
        'color': '#ff0000'
    }


@pytest.fixture
def default_loading_config():
    """
    Ensures the loading config is at its defaults, i.e. the Design
    declared options win.
    """
    with config.set(**{
        name: config.param[name].default for name in
        ('loading_spinner', 'loading_color', 'loading_max_height')
    }):
        yield


def test_loading_options_defaults():
    assert Design.loading_options() == {
        'spinner': config.loading_spinner,
        'color': config.loading_color,
        'max_height': config.loading_max_height
    }


def test_loading_options_design_defaults(default_loading_config):
    assert LoadingDesign.loading_options() == {
        'spinner': 'material', 'color': '#ff0000', 'max_height': 300
    }


def test_loading_options_user_wins():
    with config.set(loading_spinner='dots', loading_color='#00ff00'):
        assert LoadingDesign.loading_options() == {
            'spinner': 'dots', 'color': '#00ff00', 'max_height': 300
        }


def test_loading_css_classes(default_loading_config):
    assert Design.loading_css_classes() == ['pn-loading', 'pn-arc']
    assert LoadingDesign.loading_css_classes() == ['pn-loading', 'pn-material']


def test_material_design_declares_material_spinner(default_loading_config):
    assert Material.loading_options()['spinner'] == 'material'


def test_module_level_helpers_follow_design(default_loading_config):
    with config.set(design=None):
        assert loading_options()['spinner'] == 'arc'
        assert loading_css_classes() == ['pn-loading', 'pn-arc']
    with config.set(design=LoadingDesign):
        assert loading_options()['spinner'] == 'material'
        assert loading_css_classes() == ['pn-loading', 'pn-material']
        assert '#ff0000' in loading_css()


def test_loading_resources_linked(default_loading_config):
    resources = loading_resources()
    assert resources['css'] == [f'{CDN_DIST}css/loading.css']
    assert len(resources['raw_css']) == 1
    assert 'pn-loading' in resources['raw_css'][0]


def test_loading_resources_without_base():
    resources = loading_resources(include_base=False)
    assert resources['css'] == []
    assert len(resources['raw_css']) == 1


def test_loading_resources_inlined(default_loading_config):
    with config.set(design=LoadingDesign):
        resources = loading_resources(inline=True)
    assert resources['css'] == []
    base = resources['raw_css'][0]
    assert '../assets/material_spinner.svg' not in base
    assert 'data:image/svg+xml;base64,' in base
    # Other spinners are not inlined
    assert '../assets/arc_spinner.svg' in base


def test_loading_resources_inlined_dist_path():
    resources = loading_resources(inline=True, dist_path='static/extensions/panel/')
    base = resources['raw_css'][0]
    assert '../assets' not in base
    assert 'static/extensions/panel/assets/arc_spinner.svg' in base


def test_start_stop_loading_spinner_uses_design(default_loading_config):
    with config.set(design=LoadingDesign):
        obj = Column()
        start_loading_spinner(obj)
        assert obj.css_classes == ['pn-loading', 'pn-material']
        stop_loading_spinner(obj)
    assert obj.css_classes == []


def test_start_loading_spinner_prefers_component_design(default_loading_config):
    obj = Column(design=LoadingDesign)
    start_loading_spinner(obj)
    assert obj.css_classes == ['pn-loading', 'pn-material']
    stop_loading_spinner(obj)
    assert obj.css_classes == []


def test_component_loading_stylesheet_uses_design(default_loading_config):
    widget = TextInput(design=LoadingDesign)
    properties = widget._process_param_change({'stylesheets': []})
    assert '#ff0000' in properties['stylesheets'][0]


def test_jslink_loading_uses_design(default_loading_config):
    from panel.links import JSLinkCallbackGenerator

    generator = JSLinkCallbackGenerator
    with config.set(design=LoadingDesign):
        code = generator._get_code(generator, None, TextInput(), 'value', None, 'loading')
    assert json.dumps(['pn-loading', 'pn-material']) in code


@pytest.mark.skipif(
    _convert_resources.__module__ != 'panel.io.convert',
    reason='panel.io.convert.loading_resources was replaced by another library'
)
def test_convert_loading_resources(default_loading_config):
    from bokeh.core.templates import FILE

    resources = _convert_resources(FILE, False)
    assert len(resources) == 2
    assert resources[0] == (
        f'<link rel="stylesheet" href="{CDN_DIST}css/loading.css" type="text/css" />'
    )
    assert resources[1].startswith('<style type="text/css">')

    # A Panel template already loads the base stylesheet
    resources = _convert_resources(None, False)
    assert len(resources) == 1
    assert resources[0].startswith('<style type="text/css">')
