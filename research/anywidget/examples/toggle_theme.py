"""
Theme toggle anywidget demonstrating Bool traitlet and dynamic CSS.

This example demonstrates:
- Defining a custom anywidget with Bool traitlet
- Dynamic CSS classes based on state
- Rendering a styled toggle switch
- Bidirectional synchronization with Panel checkbox widget

Run with: panel serve research/anywidget/examples/toggle_theme.py
"""
import anywidget
import traitlets

import panel as pn

pn.extension()


class ThemeToggleWidget(anywidget.AnyWidget):
    """A theme toggle widget with light and dark mode."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "theme-container";

        // Toggle switch
        let switchContainer = document.createElement("div");
        switchContainer.className = "switch-container";

        let switchLabel = document.createElement("label");
        switchLabel.className = "switch";

        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = model.get("dark") || false;

        let slider = document.createElement("span");
        slider.className = "slider";

        checkbox.addEventListener("change", () => {
            model.set("dark", checkbox.checked);
            model.save_changes();
            updateTheme();
        });

        switchLabel.appendChild(checkbox);
        switchLabel.appendChild(slider);
        switchContainer.appendChild(switchLabel);

        let switchText = document.createElement("span");
        switchText.className = "switch-text";
        switchText.textContent = "Dark Mode";
        switchContainer.appendChild(switchText);

        container.appendChild(switchContainer);

        // Content area
        let contentArea = document.createElement("div");
        contentArea.className = "content-area";
        contentArea.innerHTML = `
            <h2>Theme Content</h2>
            <p>Toggle the switch above to switch between light and dark themes.</p>
            <p>The entire content area changes appearance based on the selected theme.</p>
        `;

        container.appendChild(contentArea);

        function updateTheme() {
            let isDark = model.get("dark") || false;
            if (isDark) {
                container.classList.remove("theme-light");
                container.classList.add("theme-dark");
            } else {
                container.classList.remove("theme-dark");
                container.classList.add("theme-light");
            }
        }

        model.on("change:dark", () => {
            checkbox.checked = model.get("dark") || false;
            updateTheme();
        });

        updateTheme();
        el.appendChild(container);
    }
    export default { render };
    """

    _css = """
    .theme-container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        padding: 20px;
        border-radius: 8px;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    .theme-light {
        background-color: #f5f5f5;
        color: #333;
    }

    .theme-dark {
        background-color: #333;
        color: #f5f5f5;
    }

    .switch-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }

    .switch {
        position: relative;
        display: inline-block;
        width: 50px;
        height: 28px;
    }

    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: 0.4s;
        border-radius: 28px;
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 22px;
        width: 22px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: 0.4s;
        border-radius: 50%;
    }

    input:checked + .slider {
        background-color: #2196F3;
    }

    input:checked + .slider:before {
        transform: translateX(22px);
    }

    .switch-text {
        font-weight: 500;
        font-size: 15px;
    }

    .content-area {
        padding: 16px;
        border-radius: 6px;
        border: 2px solid currentColor;
    }

    .theme-light .content-area {
        background-color: white;
        border-color: #ddd;
    }

    .theme-dark .content-area {
        background-color: #444;
        border-color: #666;
    }

    .content-area h2 {
        margin-top: 0;
        font-size: 20px;
    }

    .content-area p {
        margin: 8px 0;
        line-height: 1.5;
    }
    """

    dark = traitlets.Bool(False, help="Whether dark mode is enabled").tag(sync=True)


# Create the anywidget instance and wrap it with Panel
widget = ThemeToggleWidget(dark=False)
pane = pn.pane.AnyWidget(widget)

# pane.component is available immediately — use param API
component = pane.component

# Create a Panel checkbox for syncing
dark_mode_checkbox = pn.widgets.Checkbox(name="Dark Mode (Python side)", value=False)

# Bidirectional sync via param API (no widget.observe needed!)
component.param.watch(lambda e: setattr(dark_mode_checkbox, 'value', e.new), ['dark'])
dark_mode_checkbox.param.watch(lambda e: setattr(component, 'dark', e.new), ['value'])

# Layout
header = pn.pane.Markdown("""
# Theme Toggle Example — AnyWidget Pane + Bool Traitlet + Dynamic CSS

This example demonstrates a **Bool traitlet** toggling light/dark themes.
The anywidget renders a CSS toggle switch and a themed content area.
Panel's `AnyWidget` pane extracts the `_css` into `_stylesheets` automatically.

**Try it:**
1. **Click the toggle switch** in the anywidget — the theme changes, and the
   Panel checkbox below updates via traitlet sync.
2. **Check/uncheck the Panel checkbox** — the anywidget theme toggles via
   bidirectional sync.
""")

pn.Column(
    header,
    pn.pane.Markdown("### Anywidget (browser-side toggle + themed content)"),
    pane,
    pn.pane.Markdown("### Panel Widget (Python-side checkbox)"),
    dark_mode_checkbox,
).servable()
