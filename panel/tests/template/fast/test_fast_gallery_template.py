import pathlib

from panel.site import Application
from panel.template import FastGalleryTemplate

ROOT = pathlib.Path(__file__).parent
GALLERY_YAML = ROOT.parent.parent / "site" / "gallery.yaml"


def test_get_manual_test_app():
    return FastGalleryTemplate(
        site="Panel",
        site_url="https://awesome-panel.org",
        title="Gallery",
        background_image_url="https://ih1.redbubble.net/image.875683605.8623/ur,mug_lifestyle,tall_portrait,750x1000.jpg",
        applications=Application.read(GALLERY_YAML),
        target="_blank",
        accent_base_color="green",
        footer="Made with &#x1f40d;, &#10084;&#65039; and <fast-anchor href='https://panel.holoviz.org' appearance='hypertext' target='_blank'>Panel</fast-anchor>.",
    )


if __name__.startswith("bokeh"):
    test_get_manual_test_app().servable()
