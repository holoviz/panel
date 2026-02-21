"""
AnyWidget with CSS styling example: a styled card component.

This example demonstrates:
- Defining a custom anywidget with inline ES module JavaScript
- Adding CSS styling via the _css attribute
- Bidirectional synchronization with Panel widgets
- Rendering dynamic HTML content

Run with: panel serve research/anywidget/examples/styled_card.py
"""
import anywidget
import traitlets

import panel as pn

pn.extension()


class StyledCardWidget(anywidget.AnyWidget):
    """A card widget with CSS styling and customizable title and content."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "styled-card";

        let heading = document.createElement("h3");
        heading.textContent = model.get("title");

        let paragraph = document.createElement("p");
        paragraph.textContent = model.get("content");

        container.appendChild(heading);
        container.appendChild(paragraph);
        el.appendChild(container);

        // Listen for changes to title from Python side
        model.on("change:title", () => {
            heading.textContent = model.get("title");
        });

        // Listen for changes to content from Python side
        model.on("change:content", () => {
            paragraph.textContent = model.get("content");
        });
    }
    export default { render };
    """

    _css = """
    .styled-card {
        border: 2px solid #2196F3;
        border-radius: 8px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        max-width: 400px;
    }

    .styled-card h3 {
        margin: 0 0 12px 0;
        font-size: 24px;
        font-weight: 600;
        color: #ffffff;
    }

    .styled-card p {
        margin: 0;
        font-size: 16px;
        line-height: 1.5;
        color: rgba(255, 255, 255, 0.95);
    }
    """

    title = traitlets.Unicode("Hello Panel").tag(sync=True)
    content = traitlets.Unicode("AnyWidget + Panel").tag(sync=True)


# Create the anywidget instance and wrap it with Panel
widget = StyledCardWidget()
pane = pn.pane.AnyWidget(widget)

# pane.component is available immediately — use param API
component = pane.component

# Create Panel TextInput widgets to edit title and content
title_input = pn.widgets.TextInput(
    name="Card Title", value=widget.title, width=400
)
content_input = pn.widgets.TextInput(
    name="Card Content", value=widget.content, width=400
)

# Bidirectional sync via param API (no widget.observe needed!)
component.param.watch(lambda e: setattr(title_input, 'value', e.new), ['title'])
title_input.param.watch(lambda e: setattr(component, 'title', e.new), ['value'])

component.param.watch(lambda e: setattr(content_input, 'value', e.new), ['content'])
content_input.param.watch(lambda e: setattr(component, 'content', e.new), ['value'])

# Layout
header = pn.pane.Markdown("""
# Styled Card Example — AnyWidget Pane + CSS

This example demonstrates **CSS styling** with an anywidget.  The card below
is rendered by the anywidget's inline ESM with styles from its `_css` attribute.
Panel's `AnyWidget` pane extracts the CSS into `_stylesheets` automatically.

**Try it:** Edit the title or content in the **Panel TextInput** widgets below —
the styled card updates in real-time via bidirectional traitlet sync.
""")

pn.Column(
    header,
    pn.pane.Markdown("### Panel Widgets (Python-side text inputs)"),
    title_input,
    content_input,
    pn.pane.Markdown("### Anywidget (browser-side styled card)"),
    pane,
).servable()
