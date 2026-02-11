import panel as pn

pn.extension("echarts", sizing_mode="stretch_width")

speed = pn.widgets.IntSlider(name="Speed", start=0, end=100, value=70)
reliability = pn.widgets.IntSlider(name="Reliability", start=0, end=100, value=85)
comfort = pn.widgets.IntSlider(name="Comfort", start=0, end=100, value=60)
safety = pn.widgets.IntSlider(name="Safety", start=0, end=100, value=90)
efficiency = pn.widgets.IntSlider(name="Efficiency", start=0, end=100, value=75)

def radar_chart(sp, re, co, sa, ef):
    return pn.pane.ECharts({
        "radar": {"indicator": [
            {"name": "Speed", "max": 100}, {"name": "Reliability", "max": 100},
            {"name": "Comfort", "max": 100}, {"name": "Safety", "max": 100},
            {"name": "Efficiency", "max": 100},
        ]},
        "series": [{"type": "radar", "data": [{"value": [sp, re, co, sa, ef], "name": "Score",
            "areaStyle": {"opacity": 0.3}}]}],
    }, height=400)

pn.Column(
    "# Radar Chart",
    pn.Row(speed, reliability, comfort, safety, efficiency),
    pn.bind(radar_chart, speed, reliability, comfort, safety, efficiency),
).servable()
