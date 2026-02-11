import panel as pn

pn.extension(sizing_mode="stretch_width")

CONVERSIONS = {
    "Length": {"Meters": 1, "Kilometers": 0.001, "Miles": 0.000621371, "Feet": 3.28084, "Inches": 39.3701},
    "Weight": {"Kilograms": 1, "Grams": 1000, "Pounds": 2.20462, "Ounces": 35.274},
    "Temperature": {"Celsius": None, "Fahrenheit": None, "Kelvin": None},
}

category = pn.widgets.Select(name="Category", options=list(CONVERSIONS.keys()), value="Length")
from_unit = pn.widgets.Select(name="From", options=list(CONVERSIONS["Length"].keys()))
to_unit = pn.widgets.Select(name="To", options=list(CONVERSIONS["Length"].keys()), value="Feet")
value_in = pn.widgets.FloatInput(name="Value", value=1.0, step=0.1)

def update_units(event):
    units = list(CONVERSIONS[category.value].keys())
    from_unit.options = units
    to_unit.options = units
    from_unit.value = units[0]
    to_unit.value = units[1] if len(units) > 1 else units[0]

category.param.watch(update_units, "value")

def convert(val, cat, fr, to):
    if cat == "Temperature":
        c = val if fr == "Celsius" else (val - 32) * 5 / 9 if fr == "Fahrenheit" else val - 273.15
        out = c if to == "Celsius" else c * 9 / 5 + 32 if to == "Fahrenheit" else c + 273.15
    else:
        base = val / CONVERSIONS[cat][fr]
        out = base * CONVERSIONS[cat][to]
    return pn.pane.Markdown(f"### {val:.4g} {fr} = **{out:.4g} {to}**")

pn.Column(
    "# Unit Converter",
    pn.Row(category, value_in),
    pn.Row(from_unit, to_unit),
    pn.bind(convert, value_in, category, from_unit, to_unit),
).servable()
