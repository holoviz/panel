# Build a Report

In this section, we will collaboratively create a *Wind Turbine Report*. Together, we will:

- Layout and style the report nicely.
- Export the report to a static `.html` file using the `.save` method.
- Distribute the report via email.

<video controls="" poster="https://assets.holoviz.org/panel/tutorials/wind_turbine_report.png">
    <source src="https://assets.holoviz.org/panel/tutorials/wind_turbine_report.mp4" type="video/mp4" style="max-height: 400px; max-width: 100%;">
    Your browser does not support the video tag.
</video>

:::::{dropdown} Dependencies

```bash
altair panel
```

:::::

:::::{dropdown} Code

```python
import altair as alt
import pandas as pd
import panel as pn

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
report = pn.Column(header, main_container)

## Export and save it

report.save("report.html")

report.servable() # Added such that the report can be served for development
```

:::::

## Install the dependencies

Please ensure that [Altair](https://altair-viz.github.io/) and [Panel](https://panel.holoviz.org) are installed.

::::{tab-set}

:::{tab-item} pip
:sync: pip

```bash
pip install altair panel
```

:::

:::{tab-item} conda
:sync: conda

```bash
conda install -y -c conda-forge altair panel
```

:::

::::

## Explanation

Let's break down and explain the code:

```{pyodide}
import altair as alt
import pandas as pd
import panel as pn
```

Here, we import the necessary libraries: [Altair](https://altair-viz.github.io/) for data visualization, [Pandas](https://pandas.pydata.org/) for data manipulation, and [Panel](https://panel.holoviz.org) for creating interactive web apps.

```{pyodide}
pn.extension("vega", sizing_mode="stretch_width")
```

Additionally we load the `"vega"` renderer, which enables rendering Altair plots, and set the sizing mode to `"stretch_width"` to make sure the content fills the available horizontal space.

```{pyodide}
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
```

We define a multiline string `TEXT` containing some markdown text describing wind turbines. Then, we define a function `get_data()` decorated with `@pn.cache` to cache the data retrieval operation. This function reads a CSV file containing turbine data from a URL and returns a Pandas DataFrame, which we store in the variable `df`.

```{pyodide}
count = len(df)
total_capacity = df.t_cap.sum()
avg_capacity = df.t_cap.mean() / 10**3
avg_rotor_diameter = df.t_rd.mean()
top_manufacturers = (
    df.groupby("t_manu").p_cap.sum().sort_values().iloc[-10:].index.to_list()
)
example_df = df.dropna().sample(5).iloc[:5,:13].reset_index(drop=True)
```

We calculate various summary statistics from the dataset, such as the total count of turbines, the total capacity, the average capacity (converted to MW), the average rotor diameter, and a list of top manufacturers by total capacity. Additionally, we create an example DataFrame (`example_df`) containing a random sample of turbine data to display in a table later.

```{pyodide}
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
```

We filter the dataset to include only the turbines from the top manufacturers. Then, we create an Altair scatter plot (`fig`) to visualize the capacity of turbines by manufacturer. We encode the manufacturer on the y-axis, the capacity on the x-axis, and use jitter to prevent overplotting. The tooltip shows the manufacturer and capacity when hovering over data points.

```{pyodide}
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
```

Here, we define some styling constants and create a header for the report, which consists of a Markdown title styled with the brand color and a teal background.

```{pyodide}
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
```

We create various components for the report, including a set of indicators (total capacity, average capacity, etc.), a Vega plot (`plot`) displaying the capacity by manufacturer, and a DataFrame (`table`) showing example turbine data.

```{pyodide}
main = pn.Column(
    "# Summary",
    indicators,
    TEXT,
    "## Manufacturer Capacities",
    plot,
    "## Turbine Examples",
    table,
)
```

We assemble the main content of the report (`main`) as a Column layout, including the summary section, the indicators, the Markdown text, the plot, and the table.

```{pyodide}
main_container = pn.Row(
    main,
    max_width=1024,
    styles={"margin-right": "auto", "margin-left": "auto", "margin-top": "10px", "margin-bottom": "20px"},
)
report = pn.Column(header, main_container)
report
```

We create a container (`main_container`) to hold the main content with a maximum width and some margin styling. Then, we compose the entire report (`report`) by combining the header and the main container.

```python
report.save("report.html")
```

Finally, we save the report as an HTML file named "report.html". This HTML file will contain the rendered content of the report, including the header, indicators, text, plot, and table.

:::{note}
With `.save` you can produce *static* reports that display content and have very limited interactivity. It is possible to add more interactivity. Check out the [*Embed State*](../../how_to/export/embedding.md) or [Convert Panel Applications](../../how_to/wasm/convert.md) guides for more detail.
:::

## Run the Code

Run the code with `python app.py`.

Please verify that the file `report.html` has been created.

Please open the `report.html` file in your browser. It should look like:

<video controls="" poster="https://assets.holoviz.org/panel/tutorials/wind_turbine_report.png">
    <source src="https://assets.holoviz.org/panel/tutorials/wind_turbine_report.mp4" type="video/mp4" style="max-height: 400px; max-width: 100%;">
    Your browser does not support the video tag.
</video>

## Distribute the report

Attach the `report.html` file generated in the previous section to an email and send it to yourself. When you receive the email, then open the `report.html` attachment.

🥳 Congrats! Together, we have successfully created and distributed an interactive report based on DataFrames and one of our favorite plotting libraries. This is an amazing achievement!

## Recap

In this section we have built a *Wind Turbine Report* with a nice user experience, exported it to a `.html` file using the `.save` method and distributed it via email.

## Resources

### How-to

- [Embed State](../../how_to/export/embedding.md)
- [Save app to file](../../how_to/export/saving.md)
