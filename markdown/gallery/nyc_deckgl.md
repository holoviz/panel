# Nyc Deckgl

```python
import panel as pn
import panel_material_ui as pmui
import pandas as pd
import param

pn.extension('deckgl')
```

## Define App

```python
class App(pn.viewable.Viewer):

    data = param.DataFrame(precedence=-1)

    view = param.DataFrame(precedence=-1)

    arc_view = param.DataFrame(precedence=-1)

    radius = param.Integer(default=50, bounds=(20, 1000))

    elevation = param.Integer(default=10, bounds=(0, 50))

    hour = param.Integer(default=0, bounds=(0, 23))

    speed = param.Integer(default=1, bounds=(0, 10), precedence=-1)

    play = param.Event(label='▷')

    def __init__(self, **params):
        self.deck_gl = None
        super().__init__(**params)
        self._update_arc_view()
        self.deck_gl = pn.pane.DeckGL(
            self.spec,
            throttle={'click': 10},
            sizing_mode='stretch_both',
            margin=0
        )
        self.deck_gl.param.watch(self._update_arc_view, 'click_state')
        self._playing = False
        self._cb = pn.state.add_periodic_callback(
            self._update_hour, 1000//self.speed, start=False
        )

    @param.depends('view', 'radius', 'elevation', 'arc_view')
    def spec(self):
        return {
            "initialViewState": {
                "bearing": 0,
                "latitude": 40.7,
                "longitude": -73.9,
                "maxZoom": 15,
                "minZoom": 5,
                "pitch": 40.5,
                "zoom": 11
            },
            "mapStyle": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            "layers": [self.hex_layer, self.arc_layer],
            "views": [
                {"@@type": "MapView", "controller": True}
            ]
        }

    @property
    def hex_layer(self):
        return {
            "@@type": "HexagonLayer",
            "autoHighlight": True,
            "coverage": 1,
            "data": self.data if self.view is None else self.view,
            "elevationRange": [0, 100],
            "elevationScale": self.elevation,
            "radius": self.radius,
            "extruded": True,
            "getPosition": "@@=[pickup_x, pickup_y]",
            "id": "8a553b25-ef3a-489c-bbe2-e102d18a3211"
        }

    @property
    def arc_layer(self):
        return {
            "@@type": "ArcLayer",
            "id": 'arc-layer',
            "data": self.arc_view,
            "pickable": True,
            "getWidth": 2,
            "getSourcePosition": "@@=[pickup_x, pickup_y]",
            "getTargetPosition": "@@=[dropoff_x, dropoff_y]",
            "getSourceColor": [0, 255, 0, 180],
            "getTargetColor": [240, 100, 0, 180]
        }

    def _update_hour(self):
        self.hour = (self.hour+1) % 24

    @param.depends('hour', watch=True, on_init=True)
    def _update_hourly_view(self):
        self.view = self.data[self.data.hour==self.hour]

    @param.depends('view', 'radius', watch=True)
    def _update_arc_view(self, event=None):
        data = self.data if self.view is None else self.view
        lon, lat, = (-73.9857, 40.7484)
        if self.deck_gl:
            lon, lat = self.deck_gl.click_state.get('coordinate', (lon, lat))
        tol = self.radius / 100000
        self.arc_view = data[
            (data.pickup_x>=float(lon-tol)) &
            (data.pickup_x<=float(lon+tol)) &
            (data.pickup_y>=float(lat-tol)) &
            (data.pickup_y<=float(lat+tol))
        ]

    @param.depends('speed', watch=True)
    def _update_speed(self):
        self._cb.period = 1000//self.speed

    @param.depends('play', watch=True)
    def _play_pause(self):
        if self._playing:
            self._cb.stop()
            self.param.play.label = '▷'
            self.param.speed.precedence = -1
        else:
            self._cb.start()
            self.param.play.label = '❚❚'
            self.param.speed.precedence = 1
        self._playing = not self._playing

    @property
    def controls(self):
        return pn.Param(app.param, show_name=False)

    def __panel__(self):
        return pn.Row(
            self.controls,
            self.deck_gl,
            min_height=800,
            sizing_mode='stretch_both',
        )
```

## Display app

```python
df = pd.read_parquet('https://datasets.holoviz.org/nyc_taxi_small/v1/nyc_taxi_small.parq')

app = App(data=df)

app
```

### Served App

```python
if pn.state.served:
    pmui.Page(
        main=[app.deck_gl],
        sidebar=[app.controls],
        sidebar_width=350,
        title='NYC Taxi Deck.GL Explorer',
        sx={".MuiToolbar-root": {"mb": 0}}
    ).servable()
```
