from bokeh.document import Document

from panel.template.fast.list import FastListTemplate
from panel.theme.fast import FastDarkTheme
from panel.widgets import Button


def test_template_theme_parameter():
    template = FastListTemplate(title="Fast", theme="dark")
    # Not '#3f3f3f' which is for the Vanilla theme

    doc = template.server_doc(Document())
    assert doc.theme._json['attrs']['figure']['background_fill_color']=="#181818"

    assert isinstance(template._design.theme, FastDarkTheme)


def test_accepts_colors_by_name():
    template = FastListTemplate(
        accent_base_color="red",
        header_background="green",
        header_color="white",
        header_accent_base_color="blue",
    )
    template._update_vars()


def test_accent():
    accent = "yellow"
    template = FastListTemplate(accent=accent)
    assert template.accent_base_color==accent
    assert template.header_background==accent


def test_template_right_sidebar():
    tmpl = FastListTemplate()
    button = Button(name="Click me", button_type="primary")
    tmpl.right_sidebar.append(button)

    assert len(tmpl._render_items) == 5
    assert f"right_nav-{id(button)}" in tmpl._render_items
