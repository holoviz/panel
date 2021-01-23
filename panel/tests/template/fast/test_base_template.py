# We use the FastListTemplate to test the general properties of BaseTemplate

from panel.template.fast import FastListTemplate
from panel.template.fast.fast_list_template import DarkTheme

def test_constructor_theme_str():
    """We provide the user an easy way to specify the template"""
    template = FastListTemplate(theme="dark")
    assert template.theme==DarkTheme

def test_constructor_theme_class():
    template = FastListTemplate(theme=DarkTheme)
    assert template.theme==DarkTheme
