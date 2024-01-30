# Build a Report

In this section we will build a *Wind Turbine Report*. We will

- layout and style the report nicely.
- export the report to static `.html` and distribute it via email.

:::{note}
When I ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Create the Report

Run the code code below

```{pyodide}
import panel as pn
import pandas as pd
import altair as alt

pn.extension("vega", sizing_mode="stretch_width")

# Extract Data

TEXT ="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
Proin scelerisque in arcu tristique sollicitudin. Aliquam ornare bibendum blandit."""* 10

df = pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

# Transform Data

count = len(df)
total_capacity = df.t_cap.sum()
avg_capacity = df.t_cap.mean() / 10**3
avg_rotor_diameter = df.t_rd.mean()
top_manufacturers = (
    df.groupby("t_manu").p_cap.sum().sort_values().iloc[-10:].index.to_list()
)
example_df = df.dropna().sample(5).iloc[:5,:13].reset_index(drop=True)

# Plot Data

df = df[df.t_manu.isin(top_manufacturers)]
fig = (
    alt.Chart(
        df.sample(5000),
        title="Capacity by Manufacturer",
    )
    .mark_circle(size=8)
    .encode(
        y="t_manu:N",
        x="p_cap:Q",
        yOffset="jitter:Q",
        color=alt.Color("t_manu:N").legend(None),
        tooltip=["t_manu", "p_cap"],
    )
    .transform_calculate(jitter="sqrt(-2*log(random()))*cos(2*PI*random())")
    .properties(
        height=400,
        width="container",
    )
)

## Build components: display, layout and style the objects

BRAND_COLOR = "teal"
BRAND_TEXT_ON_COLOR = "white"

CARD_STYLE = {
  "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
  "padding": "10px",
  "border-radius": "5px"
}

header = pn.Row(
    pn.pane.Markdown(
        "# Wind Turbine Report", styles={"color": BRAND_TEXT_ON_COLOR}, margin=(5, 20)
    ),
    styles={"background": BRAND_COLOR},
)
indicators = pn.FlexBox(
    pn.indicators.Number(
        value=total_capacity / 1e6,
        name="Total Capacity (TW)",
        format="{value:,.0f}",
        styles=CARD_STYLE,
    ),
    pn.indicators.Number(
        value=avg_capacity,
        name="Avg. Capacity (MW)",
        format="{value:,.1f}",
        styles=CARD_STYLE,
    ),
    pn.indicators.Number(
        value=avg_rotor_diameter,
        name="Avg. Rotor Diameter (m)",
        format="{value:,.0f}",
        styles=CARD_STYLE,
    ),
    pn.indicators.Number(
        value=avg_rotor_diameter,
        name="Avg. Rotor Diameter (m)",
        format="{value:,.0f}",
        styles=CARD_STYLE,
    ),
    pn.indicators.Number(
        value=count,
        name="Count",
        format="{value:,.0f}",
        styles=CARD_STYLE,
    ),
    margin=(20, 5),
)

plot = pn.pane.Vega(
    fig,
    styles=CARD_STYLE,
    margin=10,
)

table = pn.pane.DataFrame(example_df, styles=CARD_STYLE)

## Put the components together

main = pn.Column(
    "# Summary",
    indicators,
    TEXT,
    "## Manufacturer Capacities",
    plot,
    "## Turbine Examples",
    table,
)

main_container = pn.Row(
    main,
    max_width=1024,
    styles={"margin-right": "auto", "margin-left": "auto", "margin-top": "10px", "margin-bottom": "20px"},
)
report = pn.Column(header, main_container, sizing_mode="stretch_width")

## Export and save it

report.save("report.html")

report.servable()
```

If you ran this in a notebook or Python file your report will be saved to the file `report.html`.

## Distribute the report

Attach the `report.html` file generated in the previous section to an email and send it to your self. When you receive the email, then open the `report.html` attachment.

🥳 Congrats. You are now able to create and distribute interactive reports based on DataFrames and any of your favorite plotting libraries. That is an amazing achievement.

## Break it down

We will now break down the example together to get a better understanding of the code.

COMING UP.

## Recap

In this section we have built a *Wind Turbine Report* with a nice user experience, exported it to `.html` and distributed it via email.

## Resources

### How-to

- [Embed State](../../how_to/export/embedding.md)
- [Save app to file](../../how_to/export/saving.md)
