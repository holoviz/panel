import numpy as np
import pandas as pd

import panel as pn

pn.extension("tabulator", sizing_mode="stretch_width")

np.random.seed(42)
N = 50
df = pd.DataFrame({
    "Name": [f"Item-{i+1:03d}" for i in range(N)],
    "Category": np.random.choice(["Alpha", "Beta", "Gamma", "Delta"], N),
    "Value": np.round(np.random.uniform(10, 100, N), 2),
    "Score": np.random.randint(1, 11, N),
})

cat_filter = pn.widgets.MultiChoice(name="Categories", options=sorted(df["Category"].unique().tolist()), value=[])
range_filter = pn.widgets.RangeSlider(name="Value Range", start=10, end=100, value=(10, 100), step=1)

def filtered_view(cats, vrange):
    out = df.copy()
    if cats:
        out = out[out["Category"].isin(cats)]
    out = out[(out["Value"] >= vrange[0]) & (out["Value"] <= vrange[1])]
    stats = f"**{len(out)} rows** | Mean value: {out['Value'].mean():.1f} | Mean score: {out['Score'].mean():.1f}"
    return pn.Column(
        pn.pane.Markdown(stats),
        pn.widgets.Tabulator(out, height=300, sizing_mode="stretch_width"),
    )

pn.Column(
    "# Data Explorer",
    pn.Row(cat_filter, range_filter),
    pn.bind(filtered_view, cat_filter, range_filter),
).servable()
