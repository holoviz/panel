"""
Tests the components panel.ui implements itself or takes from panel-material-ui
in place of the classic ones.
"""
import pytest

import panel as pn


def test_material_replacements(panel_ui):
    import panel_material_ui as pmui

    assert panel_ui.StaticText is pmui.StaticText
    assert panel_ui.FloatPanel is pmui.FloatPanel
    assert type(panel_ui.ToggleGroup(options=['a'])) is pmui.CheckButtonGroup
    assert type(panel_ui.ToggleGroup(options=['a'], behavior='radio', widget_type='box')) is pmui.RadioBoxGroup


def test_generated_widgets_map_to_material_replacements(panel_ui):
    mapping = panel_ui.MaterialUIDesign.component_mapping

    assert mapping[pn.widgets.StaticText] is panel_ui.StaticText
    assert mapping[pn.widgets.ToggleGroup] is panel_ui.ToggleGroup


def test_modal_keeps_classic_defaults(panel_ui):
    modal = panel_ui.Modal('Content')

    assert modal.background_close
    assert modal.close_on_click
    assert modal.show_close_button


@pytest.mark.parametrize('param_name', ['background_close', 'close_on_click'])
def test_modal_background_close_aliases_close_on_click(panel_ui, param_name):
    modal = panel_ui.Modal('Content', **{param_name: False})
    assert not modal.background_close and not modal.close_on_click

    modal.param.update(**{param_name: True})
    assert modal.background_close and modal.close_on_click


def test_modal_background_close_is_not_synced(panel_ui, document, comm):
    model = panel_ui.Modal('Content', background_close=False).get_root(document, comm=comm)

    assert model.data.close_on_click is False
    assert 'background_close' not in model.data.properties()


def test_modal_show_hide_toggle(panel_ui):
    modal = panel_ui.Modal('Content')

    modal.show()
    assert modal.open
    modal.hide()
    assert not modal.open
    modal.toggle()
    assert modal.open


def test_modal_create_button(panel_ui):
    modal = panel_ui.Modal('Content')
    button = modal.create_button('toggle', label='Toggle')

    assert isinstance(button, panel_ui.Button)
    button.clicks += 1
    assert modal.open
    button.clicks += 1
    assert not modal.open

    with pytest.raises(TypeError, match='Invalid action'):
        modal.create_button('close')
