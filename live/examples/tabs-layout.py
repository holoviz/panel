import panel as pn

pn.extension(sizing_mode="stretch_width")

def card(label, color):
    return pn.pane.HTML(
        f'<div style="background:{color};color:#fff;padding:20px;border-radius:8px;'
        f'text-align:center;font-weight:600;">{label}</div>'
    )

column_tab = pn.Column(card("A", "#3b82f6"), card("B", "#ef4444"), card("C", "#22c55e"))
row_tab = pn.Row(card("X", "#8b5cf6"), card("Y", "#f59e0b"), card("Z", "#06b6d4"))

flexbox_tab = pn.FlexBox(
    *(card(f"Item {i+1}", f"hsl({i*45}, 70%, 55%)") for i in range(6)),
    flex_wrap="wrap", min_height=150,
)

grid_tab = pn.GridBox(
    card("1", "#e11d48"), card("2", "#7c3aed"), card("3", "#0891b2"),
    card("4", "#059669"), card("5", "#d97706"), card("6", "#dc2626"),
    ncols=3,
)

pn.Column(
    "# Layout Showcase",
    pn.Tabs(
        ("Column", column_tab),
        ("Row", row_tab),
        ("FlexBox", flexbox_tab),
        ("GridBox", grid_tab),
    ),
).servable()
