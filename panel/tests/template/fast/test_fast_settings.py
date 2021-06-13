import panel as pn
from panel.template.fast import FastListTemplate
from panel.template.fast.settings import (FastDesignProvider,
                                          FastTemplateSettings)


def test_provider_constructor():
    FastDesignProvider(
        background="#000000",
        neutral_color="#ffffff",
        accent_color="#aabbcc",
    )

def test_settings_constructor():
    FastTemplateSettings(FastListTemplate())

def test_create_list_app():
    FastTemplateSettings.create_list_designer()

def test_create_grid_app():
    FastTemplateSettings.create_grid_designer()

if __name__=="__main__":
    pn.config.sizing_mode = "stretch_width"
    pn.serve({
        "fast-list-template": FastTemplateSettings.create_list_designer,
        "fast-grid-template": FastTemplateSettings.create_grid_designer,
    })
