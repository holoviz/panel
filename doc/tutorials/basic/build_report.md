# Build a Report

In this section, we will collaboratively create a *Wind Turbine Report*. Together, we will:

- Layout and style the report nicely.
- Export the report to a static `.html` file using the `.save` method.
- Distribute the report via email.

## Create the Report

Copy the code below into a file `app.py`.

```{pyodide}
import panel as pn
import pandas as pd
import altair as alt

pn.extension("vega", sizing_mode="stretch_width")

# Extract Data

TEXT ="""# Wind Turbine

A wind turbine is a device that converts the kinetic energy of wind into \
[electrical energy](https://en.wikipedia.org/wiki/Electrical_energy).

The most visible part of a wind turbine is its *rotor*, which typically consists of two or three long *blades* attached to a central hub. These blades are meticulously designed to efficiently capture the energy of the wind as it passes through them. Through careful aerodynamic engineering, the shape, length, and angle of the blades are optimized to maximize the amount of kinetic energy they can extract from the wind.

As the wind blows, it causes the rotor blades to rotate. This rotational motion is transferred to a generator housed within the turbine's nacelle, a large enclosure situated atop a tall tower. The generator converts the mechanical energy of the rotating blades into electrical energy through the principles of electromagnetic induction. This electricity is then transmitted via cables down the tower and into the electrical grid for distribution to homes, businesses, and industries.

The height of the tower plays a crucial role in the efficiency of a wind turbine. By elevating the rotor assembly high above the ground, turbines can access stronger and more consistent wind speeds, which translates to higher energy production. Taller towers also help minimize the impact of surface friction and turbulence near the ground, allowing the rotor blades to operate more smoothly and efficiently.

Read more [here](https://en.wikipedia.org/wiki/Wind_turbine).
"""

@pn.cache
def get_data():
    return pd.read_csv("https://assets.holoviz.org/panel/tutorials/turbines.csv.gz")

df = get_data()

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

## Build components: display, layout, and style the objects

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
```

Run the code with `python app.py`.

Please verify that the file `report.html` has been created.

Please open the `report.html` file in your browser. It should look like:

```{pyodide}
report
```

:::{note}
The code refers to

- `report.save("report.html")`: Saves the Panel component `report` to the file `report.html`.
:::

:::{note}
With `.save` you can produce *static* reports that display content and have very limited interactivity. It is possible to add more interactivity. Check out the [*Embed State*](../../how_to/export/embedding.md) or [Convert Panel Applications](../../how_to/wasm/convert.md) guides for more detail.
:::

## Distribute the report

Attach the `report.html` file generated in the previous section to an email and send it to yourself. When you receive the email, then open the `report.html` attachment.

🥳 Congrats! Together, we have successfully created and distributed an interactive report based on DataFrames and one of our favorite plotting libraries. This is an amazing achievement!

## Recap

In this section we have built a *Wind Turbine Report* with a nice user experience, exported it to a `.html` file using the `.save` method and distributed it via email.

## Resources

### How-to

- [Embed State](../../how_to/export/embedding.md)
- [Save app to file](../../how_to/export/saving.md)
