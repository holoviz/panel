from __future__ import absolute_import, division, unicode_literals

from panel.pane import HTML, Markdown, PaneBase, Pane, Str


def test_get_markdown_pane_type():
    assert PaneBase.get_pane_type("**Markdown**") is Markdown


def test_markdown_pane(document, comm):
    pane = Pane("**Markdown**")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("<p><strong>Markdown</strong></p>")

    # Replace Pane.object
    pane.object = "*Markdown*"
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("<p><em>Markdown</em></p>")

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


def test_html_pane(document, comm):
    pane = HTML("<h1>Test</h1>")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "&lt;h1&gt;Test&lt;/h1&gt;"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "&lt;h2&gt;Test&lt;/h2&gt;"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


def test_string_pane(document, comm):
    pane = Str("<h1>Test</h1>")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<pre>&lt;h1&gt;Test&lt;/h1&gt;</pre>"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<pre>&lt;h2&gt;Test&lt;/h2&gt;</pre>"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}
