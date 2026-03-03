"""
itables Example -- Interactive DataTables
==========================================

This example demonstrates using the itables library's ITable widget
with Panel's AnyWidget pane. itables renders pandas/polars DataFrames
as interactive DataTables (https://datatables.net/) with sorting,
searching, pagination, and row selection.

GitHub: https://github.com/mwouts/itables
Docs:   https://mwouts.github.io/itables/

Required package:
    pip install itables

Run with:
    panel serve research/anywidget/examples/ext_itables.py --port 6111

Testing instructions:
    1. The table should render with 208 rows of country data
    2. Try typing in the search box -- the table should filter rows
    3. Click column headers to sort
    4. Click rows to select them -- selected row indices should update
       in the "Synced State" panel on the right
    5. Use the Panel controls to change the caption and CSS classes
    6. Use the "Update DataFrame" button to swap the table data
"""

import pandas as pd

from itables.sample_dfs import get_countries
from itables.widget import ITable

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def status_banner(color, title, detail=""):
    """Return a Markdown pane with a colored status banner."""
    colors = {
        "green":  ("#d4edda", "#155724", "#28a745"),
        "yellow": ("#fff3cd", "#856404", "#ffc107"),
        "red":    ("#f8d7da", "#721c24", "#dc3545"),
    }
    bg, fg, border = colors[color]
    detail_html = (
        f'<p style="color: {fg}; font-size: 14px; margin: 6px 0 0 0;">{detail}</p>'
        if detail else ""
    )
    return pn.pane.Markdown(f"""
<div style="background-color: {bg}; border: 2px solid {border}; border-radius: 8px; padding: 12px 16px; margin: 8px 0;">
<p style="color: {fg}; font-size: 18px; font-weight: bold; margin: 0;">{title}</p>
{detail_html}
</div>
""")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

countries_df = get_countries()

# A smaller DataFrame for the "swap" demo
sample_df = pd.DataFrame({
    "Language": ["Python", "JavaScript", "Rust", "Go", "TypeScript",
                 "Java", "C++", "Ruby", "Swift", "Kotlin"],
    "Year": [1991, 1995, 2015, 2009, 2012, 1995, 1985, 1995, 2014, 2011],
    "Typing": ["Dynamic", "Dynamic", "Static", "Static", "Static",
               "Static", "Static", "Dynamic", "Static", "Static"],
    "Popularity": [1, 2, 14, 8, 5, 3, 4, 18, 16, 12],
})

# ---------------------------------------------------------------------------
# Widget setup
# ---------------------------------------------------------------------------

# Create the ITable widget with row selection enabled
itable_widget = ITable(
    countries_df,
    caption="World Countries -- Click rows to select",
    select=True,
    classes="display nowrap compact cell-border",
)

# Wrap it with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(itable_widget, sizing_mode="stretch_width")

# Access the Panel component for sync
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

caption_input = pn.widgets.TextInput(
    name="Table Caption",
    value=itable_widget.caption,
    width=300,
)

classes_input = pn.widgets.TextInput(
    name="CSS Classes",
    value=itable_widget.classes,
    width=300,
    placeholder="e.g. display compact stripe hover",
)

# Display for selected rows
selected_display = pn.pane.JSON(
    {"selected_rows": []},
    name="Selected Rows",
    depth=2,
    height=120,
)

# Display for all synced state
state_display = pn.pane.JSON(
    {},
    name="Widget State",
    depth=2,
    height=200,
)

# Button to swap the DataFrame
swap_button = pn.widgets.Button(
    name="Swap to Programming Languages",
    button_type="primary",
    width=280,
)

swap_back_button = pn.widgets.Button(
    name="Swap to Countries",
    button_type="default",
    width=280,
)

# ---------------------------------------------------------------------------
# Sync callbacks
# ---------------------------------------------------------------------------

# Panel -> Widget sync (through component params)
caption_input.param.watch(
    lambda e: setattr(component, 'caption', e.new), "value"
)
classes_input.param.watch(
    lambda e: setattr(component, 'classes', e.new), "value"
)


def update_state_display(*events):
    """Update the state display whenever any component param changes."""
    state_display.object = {
        "caption": component.caption,
        "classes": component.classes,
        "selected_rows": component.selected_rows,
    }
    for event in events:
        if event.name == "selected_rows":
            selected_display.object = {"selected_rows": event.new}
        elif event.name == "caption":
            caption_input.value = event.new
        elif event.name == "classes":
            classes_input.value = event.new


# Widget -> Panel sync (through component param.watch)
component.param.watch(
    update_state_display, ["caption", "classes", "selected_rows"]
)


# DataFrame swap logic
_current_df = {"name": "countries"}


def swap_to_languages(event):
    itable_widget.df = sample_df
    itable_widget.caption = "Programming Languages"
    _current_df["name"] = "languages"


def swap_to_countries(event):
    itable_widget.df = countries_df
    itable_widget.caption = "World Countries -- Click rows to select"
    _current_df["name"] = "countries"


swap_button.on_click(swap_to_languages)
swap_back_button.on_click(swap_to_countries)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# itables -- Interactive DataTables

**itables** renders pandas and polars DataFrames as interactive
[DataTables](https://datatables.net/) with sorting, searching, pagination,
and row selection. It uses the `anywidget` protocol, so it works seamlessly
with Panel's `AnyWidget` pane.

## How to Use

1. **Search:** Type in the search box to filter rows instantly
2. **Sort:** Click any column header to sort ascending/descending
3. **Select rows:** Click a row to select it (shift+click for range, ctrl+click for multi)
4. **Paginate:** Use the page controls at the bottom for large datasets
5. **Change caption/classes:** Use the Panel controls on the right
6. **Swap data:** Click the buttons to switch between datasets
""")

controls = pn.Column(
    pn.pane.Markdown("## Panel Controls"),
    caption_input,
    classes_input,
    pn.pane.Markdown("### Swap DataFrame"),
    swap_button,
    swap_back_button,
    width=320,
)

sync_section = pn.Column(
    pn.pane.Markdown("## Synced State (Live)"),
    pn.pane.Markdown("### Selected Rows"),
    selected_display,
    pn.pane.Markdown("### Full State"),
    state_display,
    width=320,
)

# Trait collision info
collision_info = pn.pane.Markdown("""
## Trait Name Collisions

**No collisions detected.** All public ITable traits (`caption`, `classes`,
`selected_rows`) are safe -- none collide with Bokeh reserved model property
names or Panel component parameter names.

| Trait | Type | Collides? |
|-------|------|-----------|
| `caption` | Unicode | No |
| `classes` | Unicode | No |
| `selected_rows` | List[Int] | No |
| `_style` | Unicode (private) | No |
| `_dt_args` | Dict (private) | No |
""")

pn.Column(
    status_banner(
        "green",
        "WORKS -- Renders, search, sort, pagination, and row selection all functional",
        "Bidirectional sync works for <code>caption</code>, <code>classes</code>, "
        "and <code>selected_rows</code>. DataFrame can be swapped via "
        "<code>widget.df = new_df</code>.",
    ),
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Interactive Table"),
            anywidget_pane,
            min_width=500,
            sizing_mode="stretch_width",
        ),
        pn.Column(
            controls,
            pn.layout.Divider(),
            sync_section,
        ),
    ),
    collision_info,
    max_width=1200,
    styles={"margin": "0 auto"},
).servable()
