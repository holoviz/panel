import panel as pn

pn.extension(sizing_mode="stretch_width")

picker = pn.widgets.ColorPicker(name="Base Color", value="#3b82f6")
steps = pn.widgets.RadioButtonGroup(name="Shades", options=["5", "7", "9"], value="7")

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def generate_palette(color, n):
    r, g, b = hex_to_rgb(color)
    n = int(n)
    swatches = ""
    for i in range(n):
        f = i / (n - 1) if n > 1 else 0.5
        cr = int(255 + (r - 255) * f)
        cg = int(255 + (g - 255) * f)
        cb = int(255 + (b - 255) * f)
        hx = f"#{cr:02x}{cg:02x}{cb:02x}"
        text_col = "#fff" if (cr * 0.299 + cg * 0.587 + cb * 0.114) < 150 else "#000"
        swatches += (
            f'<div style="background:{hx};color:{text_col};padding:12px 16px;'
            f'border-radius:6px;text-align:center;font-size:13px;font-family:monospace;">'
            f'{hx}</div>'
        )
    return pn.pane.HTML(
        f'<div style="display:grid;grid-template-columns:repeat({n},1fr);gap:6px;">{swatches}</div>'
    )

pn.Column(
    "# Color Palette Generator",
    pn.Row(picker, steps),
    pn.bind(generate_palette, picker, steps),
).servable()
