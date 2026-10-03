"""
Tests the components panel.ui implements itself or takes from panel-material-ui
in place of the classic ones, and the Material stylesheets it applies to the
classic components it keeps.
"""
import logging

import pytest

import panel as pn

from panel.io.resources import CDN_DIST, stylesheet_url


@pytest.fixture
def logger():
    return logging.getLogger('panel.callbacks')


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
    assert mapping[pn.widgets.Debugger] is panel_ui.Debugger


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


def test_debugger_is_a_material_card(panel_ui):
    import panel_material_ui as pmui

    debugger = panel_ui.Debugger()

    assert isinstance(debugger, pmui.Card)
    assert debugger.collapsed
    assert debugger.objects == [debugger.terminal]
    assert isinstance(debugger.header, pmui.Row)


def test_debugger_counts_logs(panel_ui, logger):
    debugger = panel_ui.Debugger(level=logging.INFO)
    errors, warnings, infos = debugger._chips.values()

    logger.error('first')
    logger.error('second')
    logger.warning('warning')
    logger.info('info')

    assert (errors.label, warnings.label, infos.label) == ('2 errors', '1 warning', '1 info')
    assert errors.visible and warnings.visible and infos.visible
    assert 'second' in debugger.terminal.output


def test_debugger_level_filters_logs(panel_ui, logger):
    debugger = panel_ui.Debugger()

    logger.info('ignored')
    assert debugger._number_of_infos == 0

    debugger.level = logging.INFO
    logger.info('printed')
    assert debugger._number_of_infos == 1


def test_debugger_clear_acknowledges_logs(panel_ui, logger):
    debugger = panel_ui.Debugger(level=logging.INFO)
    logger.error('error')
    logger.info('info')

    debugger.terminal.clear()

    assert debugger._number_of_errors == debugger._number_of_infos == 0
    assert not any(chip.visible for chip in debugger._chips.values())


def test_debugger_log_file(panel_ui, logger):
    debugger = panel_ui.Debugger(title='Session log')
    logger.error('saved')

    assert 'saved' in debugger._log_file().getvalue()
    assert debugger._save.filename == 'Session log.txt'

    debugger.title = 'Other'
    assert debugger._save.filename == 'Other.txt'
    assert debugger._title.object == 'Other'


def test_debugger_terminal_sizing(panel_ui):
    assert panel_ui.Debugger().terminal.sizing_mode == 'stretch_width'
    assert panel_ui.Debugger().terminal.height == 200
    assert panel_ui.Debugger(height=400).terminal.sizing_mode == 'stretch_both'
    assert panel_ui.Debugger(sizing_mode='stretch_both').terminal.height is None


def test_debugger_ignores_logs_after_its_models_are_destroyed(panel_ui, document, comm, logger):
    debugger = panel_ui.Debugger()
    model = debugger.get_root(document, comm=comm)

    model.destroy()
    logger.error('after destroy')

    assert debugger._number_of_errors == 0


def test_debugger_detaches_handler_on_cleanup(panel_ui, document, comm, logger):
    debugger = panel_ui.Debugger()
    panel_logger = logging.getLogger('panel')
    model = debugger.get_root(document, comm=comm)
    assert debugger.stream_handler in panel_logger.handlers

    debugger._cleanup(model)
    assert debugger.stream_handler not in panel_logger.handlers

    debugger.get_root(document, comm=comm)
    assert debugger.stream_handler in panel_logger.handlers


@pytest.mark.parametrize(('component', 'stylesheet'), [
    ('CodeEditor', 'codeeditor_mui.css'),
    ('FileDropper', 'filedropper_mui.css'),
    ('JSON', 'json_mui.css'),
    ('JSONEditor', 'jsoneditor_mui.css'),
    ('Markdown', 'markdown_mui.css'),
    ('Tabulator', 'tabulator_mui.css'),
    ('Terminal', 'terminal_mui.css'),
    ('TextEditor', 'texteditor_mui.css'),
])
def test_classic_components_get_material_stylesheets(panel_ui, component, stylesheet):
    cls = getattr(panel_ui, component)
    stylesheets = [
        stylesheet_url(s) for s in panel_ui.MaterialUIDesign().params(cls())[0]['stylesheets']
        if not isinstance(s, str)
    ]

    assert f'{CDN_DIST}css/{stylesheet}' in stylesheets
    # The Material stylesheet the MUI overrides build on is kept.
    assert f'{CDN_DIST}bundled/theme/material.css' in stylesheets


def test_tabulator_keeps_material_theme(panel_ui):
    params = panel_ui.MaterialUIDesign().params(panel_ui.Tabulator())[0]

    assert params['theme'] == 'materialize'


def test_widgetbox_disables_its_widgets(panel_ui):
    text, button = panel_ui.TextInput(), panel_ui.Button()
    box = panel_ui.WidgetBox(text, panel_ui.Row(button), disabled=True)
    assert text.disabled and button.disabled

    box.disabled = False
    assert not text.disabled and not button.disabled

    box.disabled = True
    added = panel_ui.Select()
    box.append(added)
    assert added.disabled


def test_widgetbox_keeps_widget_state_when_enabled(panel_ui):
    text = panel_ui.TextInput(disabled=True)
    panel_ui.WidgetBox(text)
    assert text.disabled


def test_widgetbox_disabled_is_not_synced(panel_ui, document, comm):
    model = panel_ui.WidgetBox(disabled=True).get_root(document, comm=comm)
    assert 'disabled' not in model.data.properties()
