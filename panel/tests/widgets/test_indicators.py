import pytest

from panel.config import config
from panel.widgets.indicators import (
    Dial, Gauge, LinearGauge, Number, Tqdm,
)


def test_number_none(document, comm):
    number = Number(value=None, label='Value')

    model = number.get_root(document, comm)

    assert model.text.endswith("&lt;div style=&quot;font-size: 54pt; color: currentcolor&quot;&gt;-&lt;/div&gt;")

    number.nan_format = 'nan'

    assert model.text.endswith("&lt;div style=&quot;font-size: 54pt; color: currentcolor&quot;&gt;nan&lt;/div&gt;")


def test_number_thresholds(document, comm):
    number = Number(value=0, colors=[(0.33, 'green'), (0.66, 'yellow'), (1, 'red')])

    model = number.get_root(document, comm)

    assert 'green' in model.text

    number.value = 0.5

    assert 'yellow' in model.text

    number.value = 0.7

    assert 'red' in model.text


def test_dial_thresholds(document, comm):
    dial = Dial(value=0, colors=[(0.33, 'green'), (0.66, 'yellow'), (1, 'red')])

    model = dial.get_root(document, comm)

    cds = model.select(name='annulus_source')

    assert ['green', '#e8e8e8'] == cds.data['color']

    dial.value = 50

    assert ['yellow', '#e8e8e8'] == cds.data['color']

    dial.value = 72

    assert ['red', '#e8e8e8'] == cds.data['color']


def test_dial_none(document, comm):
    dial = Dial(value=None, label='Value')

    model = dial.get_root(document, comm)

    cds = model.select(name='annulus_source')

    assert list(cds.data['starts']) == [9.861110273767961, 9.861110273767961]
    assert list(cds.data['ends']) == [9.861110273767961, 5.846852994181004]

    text_cds = model.select(name='label_source')

    assert text_cds.data['text'] == ['Value', '-%', '0%', '100%']

    dial.nan_format = 'nan'

    assert text_cds.data['text'] == ['Value', 'nan%', '0%', '100%']


def test_dial_thresholds_with_bounds(document, comm):
    dial = Dial(value=25, colors=[(0.33, 'green'), (0.66, 'yellow'), (1, 'red')],
                bounds=(25, 75))

    model = dial.get_root(document, comm)

    cds = model.select(name='annulus_source')

    assert ['green', '#e8e8e8'] == cds.data['color']

    dial.value = 50

    assert ['yellow', '#e8e8e8'] == cds.data['color']

    dial.value = 75

    assert ['red', '#e8e8e8'] == cds.data['color']


def test_dial_bounds():
    dial = Dial(bounds=(0, 20))

    with pytest.raises(ValueError):
        dial.value = 100


def test_gauge_bounds():
    dial = Gauge(bounds=(0, 20))

    with pytest.raises(ValueError):
        dial.value = 100


def test_gauge_creation():
    gauge = Gauge(label="Test", value=50, bounds=(0, 100))
    assert gauge.value == 50
    assert gauge.bounds == (0, 100)
    assert gauge.label == "Test"


def test_gauge_colors():
    gauge = Gauge(value=75, colors=[(0.4, 'green'), (0.8, 'yellow'), (1, 'red')])
    assert gauge.colors == [(0.4, 'green'), (0.8, 'yellow'), (1, 'red')]


def test_gauge_custom_opts():
    gauge = Gauge(value=50, custom_opts={'pointer': {'width': 5}})
    assert gauge.custom_opts == {'pointer': {'width': 5}}


def test_gauge_process_param_change():
    gauge = Gauge(label="G", value=50, bounds=(0, 100))
    msg = gauge._process_param_change({
        'value': 50, 'bounds': (0, 100), 'tooltip_format': '{b} : {c}%',
        'show_ticks': True, 'show_labels': True, 'title_size': 18,
        'format': '{value}%', 'start_angle': 225, 'end_angle': -45,
        'num_splits': 10, 'annulus_width': 10,
    })
    assert 'data' in msg
    assert msg['data']['series'][0]['type'] == 'gauge'
    assert msg['data']['series'][0]['data'][0]['value'] == 50
    assert msg['data']['series'][0]['min'] == 0
    assert msg['data']['series'][0]['max'] == 100


def test_gauge_process_param_change_with_colors():
    gauge = Gauge(label="G", value=75, bounds=(0, 100),
                  colors=[(0.5, 'green'), (1, 'red')])
    msg = gauge._process_param_change({
        'value': 75, 'bounds': (0, 100), 'tooltip_format': '{b} : {c}%',
        'show_ticks': True, 'show_labels': True, 'title_size': 18,
        'format': '{value}%', 'start_angle': 225, 'end_angle': -45,
        'num_splits': 10, 'annulus_width': 10,
        'colors': [(0.5, 'green'), (1, 'red')],
    })
    assert msg['data']['series'][0]['axisLine']['lineStyle']['color'] == [
        (0.5, 'green'), (1, 'red')
    ]


def test_gauge_warns_without_extension(caplog):
    import logging

    from panel.config import panel_extension
    original = list(panel_extension._loaded_extensions)
    try:
        panel_extension._loaded_extensions.clear()
        with caplog.at_level(logging.WARNING):
            Gauge(label="G", value=50, bounds=(0, 100))
        assert "Gauge requires the ECharts library" in caplog.text
    finally:
        panel_extension._loaded_extensions.extend(original)


def test_tqdm_color():
    tqdm = Tqdm()
    tqdm.text_pane.styles={'color': 'green'}
    for _ in tqdm(range(2)):
        pass
    assert tqdm.text_pane.styles["color"]=="green"


@pytest.mark.parametrize(('theme', 'text', 'unfilled'), [
    ('default', 'black', '#e8e8e8'), ('dark', 'white', '#424242')
])
def test_dial_colors_follow_theme(document, comm, theme, text, unfilled):
    with config.set(theme=theme):
        model = Dial(value=25).get_root(document, comm)

    labels = model.select_one({'name': 'label_source'}).data['color']
    annulus = model.select_one({'name': 'annulus_source'}).data['color']
    needle = model.select_one({'name': 'needle_renderer'}).glyph
    assert labels[0] == labels[2] == text
    assert annulus[-1] == unfilled
    assert needle.fill_color == text


def test_dial_explicit_colors_override_theme(document, comm):
    with config.set(theme='dark'):
        model = Dial(value=25, label_color='red', needle_color='blue', unfilled_color='grey').get_root(document, comm)

    assert model.select_one({'name': 'label_source'}).data['color'][0] == 'red'
    assert model.select_one({'name': 'annulus_source'}).data['color'][-1] == 'grey'
    assert model.select_one({'name': 'needle_renderer'}).glyph.fill_color == 'blue'


def test_dial_needle_color_update(document, comm):
    dial = Dial(value=25)
    model = dial.get_root(document, comm)

    dial.needle_color = 'blue'

    assert model.select_one({'name': 'needle_renderer'}).glyph.fill_color == 'blue'
    assert model.select_one({'name': 'needle_hub_renderer'}).glyph.fill_color == 'blue'


def test_dial_is_transparent(document, comm):
    model = Dial(value=25).get_root(document, comm)

    assert model.background_fill_alpha == 0
    assert model.border_fill_alpha == 0


def test_dial_hides_needle_for_none(document, comm):
    dial = Dial(value=None)
    model = dial.get_root(document, comm)
    needle = model.select_one({'name': 'needle_source'})

    assert list(needle.data['radius']) == [0]

    dial.value = 50

    assert list(needle.data['radius']) == [0.9]


@pytest.mark.parametrize(('width', 'height'), [(250, 250), (400, 200), (200, 400)])
def test_dial_ranges_preserve_aspect(document, comm, width, height):
    model = Dial(value=25, width=width, height=height).get_root(document, comm)

    x_span = model.x_range.end - model.x_range.start
    y_span = model.y_range.end - model.y_range.start
    assert x_span/width == pytest.approx(y_span/height)
    assert model.x_range.start < -1 and model.x_range.end > 1
    assert model.y_range.end > 1


def test_dial_ranges_follow_size(document, comm):
    dial = Dial(value=25)
    model = dial.get_root(document, comm)

    dial.width = 500

    x_span = model.x_range.end - model.x_range.start
    y_span = model.y_range.end - model.y_range.start
    assert x_span/500 == pytest.approx(y_span/250)


def test_dial_tick_labels_align_inwards(document, comm):
    model = Dial(value=25).get_root(document, comm)
    labels = model.select_one({'name': 'label_source'}).data

    assert labels['align'] == ['center', 'center', 'left', 'right']
    assert list(labels['rot']) == [0, 0, 0, 0]
    # Value row sits below the min/max labels to avoid overlapping them.
    assert labels['y'][1] < labels['y'][2]


def test_linear_gauge_is_transparent(document, comm):
    model = LinearGauge(value=25).get_root(document, comm)

    assert model.background_fill_alpha == 0
    assert model.border_fill_alpha == 0


def test_gauge_background_is_transparent():
    assert Gauge(value=25)._process_param_change({})['data']['backgroundColor'] == 'transparent'
