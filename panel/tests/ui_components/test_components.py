"""
Tests the components panel.ui implements itself or takes from panel-material-ui
in place of the classic ones.
"""
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
