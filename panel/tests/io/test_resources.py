import os

from panel.io.resources import PANEL_DIR, resolve_custom_path
from panel.widgets import Button


def test_resolve_custom_path_relative_input():
    assert resolve_custom_path(Button, 'button.py') == (PANEL_DIR / 'widgets' / 'button.py')

def test_resolve_custom_path_relative_input_relative_to():
    assert str(resolve_custom_path(Button, 'button.py', relative=True)) == 'button.py'

def test_resolve_custom_path_relative_level_up_input():
    assert resolve_custom_path(Button, '../reactive.py') == (PANEL_DIR / 'reactive.py')

def test_resolve_custom_path_relative_input_level_up_relative_to():
    assert str(resolve_custom_path(Button, '../reactive.py', relative=True)) == f'..{os.path.sep}reactive.py'

def test_resolve_custom_path_abs_input():
    assert resolve_custom_path(Button, (PANEL_DIR / 'widgets' / 'button.py')) == (PANEL_DIR / 'widgets' / 'button.py')

def test_resolve_custom_path_abs_input_relative_to():
    assert str(resolve_custom_path(Button, (PANEL_DIR / 'widgets' / 'button.py'), relative=True)) == 'button.py'
