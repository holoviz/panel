"""
widget-periodictable Example with Bidirectional Sync
=====================================================

This example demonstrates using the widget-periodictable library's PTableWidget
with Panel's AnyWidget pane and bidirectional sync between the widget
and Panel controls.

PTableWidget renders an interactive periodic table where elements can be
clicked to cycle through selection states. Each state has a distinct color,
making it useful for categorizing elements (e.g., "included" vs "excluded"
in a chemical analysis).

GitHub: https://github.com/osscar-org/widget-periodictable
Docs:   https://osscar-org.github.io/widget-periodictable/

Key traitlets:
    - selected_elements (Dict): Maps element symbols to their selection state
    - states (Int): Number of selection states (default 1)
    - disabled (Bool): Whether the widget is disabled
    - disabled_elements (List): Elements that cannot be selected
    - selected_colors (List): Colors for each selection state
    - width (Unicode): Element cell width (collides with Panel's width param,
      renamed to w_width on the component)

Required package:
    pip install widget-periodictable

Run with:
    panel serve research/anywidget/examples/ext_periodictable.py
"""

from widget_periodictable import PTableWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the PTableWidget with multiple selection states
# ---------------------------------------------------------------------------

ptable_widget = PTableWidget(
    states=3,
    selected_colors=[
        "rgb(100,180,255)",   # State 0: blue
        "rgb(100,220,100)",   # State 1: green
        "rgb(255,160,80)",    # State 2: orange
    ],
    border_color="rgb(80,80,80)",
    unselected_color="rgb(240,240,240)",
)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(ptable_widget)

# ---------------------------------------------------------------------------
# 2. Access the component for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Display the selected_elements dict reactively
selection_display = pn.pane.JSON(
    ptable_widget.selected_elements if ptable_widget.selected_elements else {},
    name="Selected Elements",
    depth=2,
)

# Watch for changes to selected_elements on the component
def on_selection_change(*events):
    for event in events:
        if event.name == "selected_elements":
            selection_display.object = event.new if event.new else {}

component.param.watch(on_selection_change, ["selected_elements"])

# ---------------------------------------------------------------------------
# 3. Panel controls for programmatic selection
# ---------------------------------------------------------------------------

select_fe_button = pn.widgets.Button(
    name="Select Fe (Iron) - State 0", button_type="primary", width=250
)
select_noble_button = pn.widgets.Button(
    name="Select Noble Gases - State 1", button_type="success", width=250
)
clear_button = pn.widgets.Button(
    name="Clear All Selections", button_type="danger", width=250
)

def select_fe(event):
    current = dict(component.selected_elements)
    current["Fe"] = 0
    component.selected_elements = current

def select_noble_gases(event):
    current = dict(component.selected_elements)
    for el in ["He", "Ne", "Ar", "Kr", "Xe", "Rn"]:
        current[el] = 1
    component.selected_elements = current

def clear_all(event):
    component.selected_elements = {}

select_fe_button.on_click(select_fe)
select_noble_button.on_click(select_noble_gases)
clear_button.on_click(clear_all)

# States control
states_spinner = pn.widgets.IntInput(
    name="Number of States", value=3, start=1, end=10, step=1, width=200
)

def on_states_change(event):
    component.states = event.new

states_spinner.param.watch(on_states_change, "value")

# Watch for states changes from widget side
component.param.watch(
    lambda e: setattr(states_spinner, 'value', e.new) if e.name == 'states' else None,
    ["states"],
)

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# widget-periodictable -- Interactive Periodic Table

**widget-periodictable** renders a clickable periodic table where elements
can be selected and categorized into multiple states. Each click cycles
an element through the available states.

## How to Use

1. **Click an element** on the periodic table to select it (cycles through states)
2. **Use the buttons** on the right to programmatically select elements
3. **Watch the JSON display** update in real-time as selections change

## Testing Instructions

- Click elements on the table and verify the JSON display updates
- Click "Select Fe (Iron)" and verify Fe appears in the JSON with state 0
- Click "Select Noble Gases" and verify He, Ne, Ar, Kr, Xe, Rn appear with state 1
- Click "Clear All" and verify the JSON becomes empty
- Change the "Number of States" to modify how many states are available
""")

controls = pn.Column(
    pn.pane.Markdown("## Controls"),
    select_fe_button,
    select_noble_button,
    clear_button,
    pn.pane.Markdown("---"),
    states_spinner,
    width=300,
)

data_section = pn.Column(
    pn.pane.Markdown("## Selected Elements (Real-time)"),
    selection_display,
    width=350,
)

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
Interactive periodic table renders correctly. Click elements to cycle through
selection states. Bidirectional sync works for <code>selected_elements</code>,
<code>states</code>, and programmatic selection from Python. The shadow DOM
<code>getElementById</code> patch enables jQuery-based element lookup.
</p>
</div>
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Periodic Table"),
            anywidget_pane,
        ),
        controls,
        data_section,
    ),
    max_width=1200,
).servable()
