import panel as pn

pn.extension(sizing_mode="stretch_width")

a = pn.widgets.FloatInput(name="A", value=10, step=1)
b = pn.widgets.FloatInput(name="B", value=3, step=1)
op = pn.widgets.Select(name="Operator", options=["+", "-", "*", "/"], value="+")

def compute(a, op, b):
    ops = {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b != 0 else float("inf")}
    result = ops[op]
    return pn.pane.Markdown(f"## {a} {op} {b} = **{result:.4g}**")

pn.Column(
    pn.Card(
        pn.Row(a, op, b),
        pn.bind(compute, a, op, b),
        title="Mini Calculator",
    ),
).servable()
