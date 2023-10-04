from bokeh.document import Document

from panel.template.fast.grid import FastGridTemplate
from panel.theme.fast import FastDarkTheme


def test_template_theme_parameter():
    template = FastGridTemplate(title="Fast", theme="dark")
    # Not '#3f3f3f' which is for the Vanilla theme

    doc = template.server_doc(Document())
    assert doc.theme._json['attrs']['figure']['background_fill_color'] == "#181818"

    assert isinstance(template._design.theme, FastDarkTheme)
