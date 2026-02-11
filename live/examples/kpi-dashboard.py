import panel as pn

pn.extension("echarts", sizing_mode="stretch_width")

kpi1 = pn.indicators.Number(name="Revenue", value=128500, format="${value:,.0f}", font_size="28pt", title_size="12pt")
kpi2 = pn.indicators.Number(name="Users", value=8420, format="{value:,}", font_size="28pt", title_size="12pt")
kpi3 = pn.indicators.Number(name="Conversion", value=3.4, format="{value}%", font_size="28pt", title_size="12pt")

gauge = pn.indicators.Gauge(name="Target", value=72, bounds=(0, 100), format="{value}%", colors=[(0.4, "#e74c3c"), (0.7, "#f1c40f"), (1, "#2ecc71")])

trend_data = {"x": list(range(12)), "y": [12, 15, 13, 17, 20, 18, 22, 25, 23, 28, 30, 32]}
trend = pn.indicators.Trend(
    name="Monthly Growth", data=trend_data,
    width=300, height=100,
    plot_color="#3b82f6",
)

pn.Column(
    "# KPI Dashboard",
    pn.Row(kpi1, kpi2, kpi3),
    pn.Row(gauge, trend),
).servable()
