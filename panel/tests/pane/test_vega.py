import sys

from copy import deepcopy
from unittest.mock import patch

import pytest

from packaging.version import Version

try:
    import altair as alt
    altair_version = Version(alt.__version__)
except Exception:
    alt = None  # type: ignore

altair_available = pytest.mark.skipif(alt is None, reason="requires altair")

import numpy as np
import pandas as pd

import panel as pn

from panel.models.vega import VegaPlot
from panel.pane import PaneBase, Vega
from panel.pane.image import PDF, SVG, Image
from panel.pane.markup import HTML

try:
    import vl_convert as vlc  # type: ignore[import-untyped]
except ImportError:
    vlc = None

blank_schema = {'$schema': ''}

vega4_config = {'view': {'continuousHeight': 300, 'continuousWidth': 400}}
vega5_config = {'view': {'continuousHeight': 300, 'continuousWidth': 300}}

vega_example = {
    'config': {
        'mark': {'tooltip': None},
        'view': {'height': 300, 'width': 400}
    },
    'data': {'values': [{'x': 'A', 'y': 5},
                        {'x': 'B', 'y': 3},
                        {'x': 'C', 'y': 6},
                        {'x': 'D', 'y': 7},
                        {'x': 'E', 'y': 2}]},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'},
                 'y': {'type': 'quantitative', 'field': 'y'}},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json'
}

vega_df_example = {
    'config': {
        'mark': {'tooltip': None},
        'view': {'height': 300, 'width': 400}
    },
    'data': {'values': pd.DataFrame({'x': ['A', 'B', 'C', 'D', 'E'], 'y': [5, 3, 6, 7, 2]})},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'},
                 'y': {'type': 'quantitative', 'field': 'y'}},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json'
}

vega4_selection_example = {
    'config': {'view': {'continuousWidth': 300, 'continuousHeight': 300}},
    'data': {'url': 'https://raw.githubusercontent.com/vega/vega/master/docs/data/penguins.json'},
    'mark': {'type': 'point'},
    'encoding': {
        'color': {
            'condition': {
                'selection': 'brush',
                'field': 'Species',
                'type': 'nominal'
            },
            'value': 'lightgray'},
        'x': {
            'field': 'Beak Length (mm)',
            'scale': {'zero': False},
            'type': 'quantitative'
        },
        'y': {
            'field': 'Beak Depth (mm)',
            'scale': {'zero': False},
            'type': 'quantitative'}
    },
    'height': 250,
    'selection': {'brush': {'type': 'interval'}},
    'width': 250,
    '$schema': 'https://vega.github.io/schema/vega-lite/v4.17.0.json'
}

vega5_selection_example = {
    'config': {'view': {'continuousWidth': 300, 'continuousHeight': 300}},
    'data': {'url': 'https://raw.githubusercontent.com/vega/vega/master/docs/data/penguins.json'},
    'mark': {'type': 'point'},
    'encoding': {
        'color': {
            'condition': {
                'param': 'brush',
                'field': 'Species',
                'type': 'nominal'
            },
            'value': 'lightgray'},
        'x': {
            'field': 'Beak Length (mm)',
            'scale': {'zero': False},
            'type': 'quantitative'
        },
        'y': {
            'field': 'Beak Depth (mm)',
            'scale': {'zero': False},
            'type': 'quantitative'}
    },
    'height': 250,
    'params': [{'name': 'brush', 'select': {'type': 'interval'}}],
    'width': 250,
    '$schema': 'https://vega.github.io/schema/vega-lite/v5.6.1.json'
}

vega_inline_example = {
    'config': {
        'view': {'width': 400, 'height': 300},
        'mark': {'tooltip': None}},
    'data': {'name': 'data-2f2c0ff233b8675aa09202457ebe7506',
             'format': {'property': 'features', 'type': 'json'}},
    'mark': 'geoshape',
    'encoding': {
        'color': {
            'type': 'quantitative',
            'field': 'properties.percent_no_internet'
        }
    },
    'projection': {'type': 'albersUsa'},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json',
    'datasets': {
        'data-2f2c0ff233b8675aa09202457ebe7506': {
            'type': 'FeatureCollection',
            'features': [
                {'id': '0',
                 'type': 'Feature',
                 'properties': {
                     'name': 'Autauga County, Alabama',
                     'percent_no_internet': 0.2341122827016244,
                     'percent_no_internet_normalized': 0.2589760005042632},
                 'geometry': {
                     'type': 'Polygon',
                     'coordinates': [[[-86.411786, 32.706342],
                                      [-86.411786, 32.410587],
                                      [-86.499417, 32.344863],
                                      [-86.817079, 32.339387],
                                      [-86.915664, 32.662526],
                                      [-86.411786, 32.706342]]]
                 }
                }
            ]
        }
    }
}

gdf_example = {
    'config': {'view': {'continuousWidth': 400, 'continuousHeight': 300}},
    'data': {'name': 'data-778223ce4ff5da49611148b060c0cd3d'},
    'mark': {'type': 'geoshape', 'fill': 'lightgray', 'stroke': 'white'},
    'height': 600,
    'projection': {'reflectY': True, 'type': 'identity'},
    'width': 800,
    '$schema': 'https://vega.github.io/schema/vega-lite/v4.0.0.json',
    'datasets': {
        'data-778223ce4ff5da49611148b060c0cd3d': [
            {
                'bid': 'SR01-01',
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [[120.0, 855.0],
                         [120.0, 925.0],
                         [20.0, 925.0],
                         [20.0, 855.0],
                         [120.0, 855.0]]
                    ]
                }
            },
            {
                'bid': 'SR02-02',
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [[120.0, 940.0],
                         [120.0, 1010.0],
                         [20.0, 1010.0],
                         [20.0, 940.0],
                         [120.0, 940.0]]
                    ]
                }
            },
            {
                'bid': 'SR03-03',
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [[240.0, 940.0],
                         [240.0, 1010.0],
                         [140.0, 1010.0],
                         [140.0, 940.0],
                         [240.0, 940.0]]
                    ]
                }
            }
        ]
    }
}

datasets_example = {'$schema': 'https://vega.github.io/schema/vega-lite/v6.json',
  'width': 700,
  'height': 400,
  'title': {'text': 'Total Admissions by State',
   'subtitle': 'Illinois has the highest admissions by a large margin'},
  'data': {'url': 'https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json',
   'format': {'type': 'topojson', 'feature': 'states'}},
  'transform': [{'lookup': 'properties.name',
    'from': {'data': {'name': 'total_admissions_by_state_uiuc_students'},
     'key': 'State',
     'fields': ['Total_Admissions']}}],
  'projection': {'type': 'albersUsa'},
  'mark': 'geoshape',
  'encoding': {'color': {'field': 'Total_Admissions',
    'type': 'quantitative',
    'scale': {'scheme': 'blues'},
    'legend': {'title': 'Total Admissions'}},
   'tooltip': [{'field': 'properties.name',
     'type': 'nominal',
     'title': 'State'},
    {'field': 'Total_Admissions',
     'type': 'quantitative',
     'format': ',',
     'title': 'Total Admissions'}]},
  'datasets': {'total_admissions_by_state_uiuc_students': pd.DataFrame(
      {'State': ['Alabama', 'Alaska', 'Arizona'],
       'Total_Admissions': [1106.0, 328.0, 1438.0]}
  )}
}

def test_get_vega_pane_type_from_dict():
    assert PaneBase.get_pane_type(vega_example) is Vega


@pytest.mark.parametrize('example', [vega_example, vega_df_example])
def test_vega_pane(document, comm, example):
    pane = pn.panel(example)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    expected = dict(vega_example, data={})

    assert dict(model.data, **blank_schema) == dict(expected, **blank_schema)
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['A', 'B', 'C', 'D', 'E']))
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    point_example = dict(deepcopy(vega_example), mark='point')
    point_example['data']['values'][0]['x'] = 'C'
    pane.object = point_example
    point_example = dict(point_example, data={})
    assert model.data == point_example
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['C', 'B', 'C', 'D', 'E']))
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    pane._cleanup(model)
    assert pane._models == {}


def test_vega_geometry_data(document, comm):
    pane = pn.panel(gdf_example)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    # Ensure geometries are not packed into CDS
    assert model.data_sources == {}


def test_vega_pane_inline(document, comm):
    pane = pn.panel(vega_inline_example)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    assert dict(model.data, **blank_schema) == dict(vega_inline_example, **blank_schema)
    assert model.data_sources == {}

    pane._cleanup(model)
    assert pane._models == {}


def test_vega_lite_4_selection_spec(document, comm):
    vega = Vega(vega4_selection_example)
    assert vega._selections == {'brush': 'interval'}

def test_vega_lite_5_selection_spec(document, comm):
    vega = Vega(vega5_selection_example)
    assert vega._selections == {'brush': 'interval'}

def altair_example():
    import altair as alt
    data = alt.Data(values=[{'x': 'A', 'y': 5},
                            {'x': 'B', 'y': 3},
                            {'x': 'C', 'y': 6},
                            {'x': 'D', 'y': 7},
                            {'x': 'E', 'y': 2}])
    chart = alt.Chart(data).mark_bar().encode(
        x='x:O',  # specify ordinal data
        y='y:Q',  # specify quantitative data
    )
    return chart

@altair_available
def test_get_vega_pane_type_from_altair():
    assert PaneBase.get_pane_type(altair_example()) is Vega

@altair_available
def test_altair_pane(document, comm):
    pane = Vega(altair_example())

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    expected = dict(vega_example, data={})
    if altair_version >= Version('5.0.0rc1'):
        expected['mark'] = {'type': 'bar'}
        expected['config'] = vega5_config
    elif altair_version >= Version('4.0.0'):
        expected['config'] = vega4_config
    assert dict(model.data, **blank_schema) == dict(expected, **blank_schema)

    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['A', 'B', 'C', 'D', 'E']))
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    chart = altair_example()
    chart.mark = 'point'
    chart.data.values[0]['x'] = 'C'
    pane.object = chart
    point_example = dict(vega_example, data={},  mark='point')
    if altair_version >= Version('5.0.0rc1'):
        point_example['mark'] = {'type': 'point'}
        point_example['config'] = vega5_config
    elif altair_version >= Version('4.0.0'):
        point_example['config'] = vega4_config
    assert dict(model.data, **blank_schema) == dict(point_example, **blank_schema)
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['C', 'B', 'C', 'D', 'E']))
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    pane._cleanup(model)
    assert pane._models == {}

def test_vega_can_instantiate_empty_with_sizing_mode(document, comm):
    pane = Vega(sizing_mode="stretch_width")
    pane.get_root(document, comm=comm)


def test_vega_can_support_datasets_with_pandas(document, comm):
    pane = Vega(datasets_example)
    pane.get_root(document, comm=comm)


class TestVegaExport:
    """Tests for Vega.export() method."""

    @pytest.fixture
    def vl_convert(self):
        """Fixture to skip tests if vl_convert is not available."""
        pytest.importorskip('vl_convert')

    def test_export_requires_vl_convert(self):
        """Test that export raises ImportError if vl_convert is not available."""
        pane = Vega(vega_example)
        with patch.dict(sys.modules, {'vl_convert': None}):
            with pytest.raises(ImportError, match='vl-convert-python is required'):
                pane.export('png')

    def test_export_with_dict_spec(self, vl_convert):
        """Test export with a dict specification."""
        pane = Vega(vega_example)

        # Test PNG export returns bytes
        result = pane.export('png')
        assert isinstance(result, bytes)
        assert len(result) > 0

        # Test SVG export returns string
        result = pane.export('svg')
        assert isinstance(result, str)
        assert '<svg' in result.lower()

    @altair_available
    def test_export_with_altair_chart(self, vl_convert):
        """Test export with an Altair chart object."""

        pane = Vega(altair_example())

        # Test PNG export returns bytes
        result = pane.export('png')
        assert isinstance(result, bytes)
        assert len(result) > 0

        # Test SVG export returns string
        result = pane.export('svg')
        assert isinstance(result, str)
        assert '<svg' in result.lower()

    def test_export_png_format(self, vl_convert):
        """Test PNG export format."""
        pane = Vega(vega_example)
        result = pane.export('png')
        assert isinstance(result, bytes)
        # PNG files start with specific magic bytes
        assert result[:8] == b'\x89PNG\r\n\x1a\n'

    def test_export_jpeg_format(self, vl_convert):
        """Test JPEG export format."""
        pane = Vega(vega_example)
        result = pane.export('jpeg')
        assert isinstance(result, bytes)
        # JPEG files start with FFD8
        assert result[:2] == b'\xff\xd8'

    def test_export_svg_format(self, vl_convert):
        """Test SVG export format."""
        pane = Vega(vega_example)
        result = pane.export('svg')
        assert isinstance(result, str)
        assert result.startswith('<svg')
        assert '</svg>' in result

    def test_export_pdf_format(self, vl_convert):
        """Test PDF export format."""
        pane = Vega(vega_example)
        result = pane.export('pdf')
        assert isinstance(result, bytes)
        # PDF files start with %PDF
        assert result.startswith(b'%PDF')

    def test_export_html_format(self, vl_convert):
        """Test HTML export format."""
        pane = Vega(vega_example)
        result = pane.export('html')
        assert isinstance(result, str)
        assert '<html' in result.lower() or '<!doctype' in result.lower()

    def test_export_url_format(self, vl_convert):
        """Test URL export format."""
        pane = Vega(vega_example)
        result = pane.export('url')
        assert isinstance(result, str)
        assert result.startswith('https://')
        assert 'vega.github.io' in result

    def test_export_case_insensitive(self, vl_convert):
        """Test that format is case insensitive."""
        pane = Vega(vega_example)

        # Should handle uppercase
        result_upper = pane.export('PNG')
        assert isinstance(result_upper, bytes)

        result_mixed = pane.export('Svg')
        assert isinstance(result_mixed, str)

    def test_export_invalid_format(self, vl_convert):
        """Test that invalid format raises ValueError."""
        pane = Vega(vega_example)

        with pytest.raises(ValueError, match="Unsupported format 'invalid'"):
            pane.export('invalid')

    def test_export_dimension_handling(self, vl_convert):
        """Test dimension handling: pane params > spec values > defaults (800x600)."""
        # Test 1: Default dimensions when nothing specified
        spec_no_dims = {
            '$schema': 'https://vega.github.io/schema/vega-lite/v5.0.0.json',
            'mark': 'bar',
            'data': {'values': [{'x': 'A', 'y': 5}]},
            'encoding': {'x': {'field': 'x', 'type': 'ordinal'},
                        'y': {'field': 'y', 'type': 'quantitative'}}
        }
        pane = Vega(spec_no_dims)
        result = pane.export('svg')
        assert '800' in result and '600' in result

        # Test 2: Spec dimensions used when pane has none
        spec = dict(vega_example)
        spec['width'] = 500
        spec['height'] = 400
        pane = Vega(spec, width=None, height=None)
        result = pane.export('svg')
        assert '500' in result and '400' in result

        # Test 3: Pane width overrides spec width, spec height preserved
        spec['width'] = 300
        spec['height'] = 250
        pane = Vega(spec, width=700)
        result = pane.export('svg')
        assert '700' in result and '250' in result

        # Test 4: Pane height overrides spec height, spec width preserved
        pane = Vega(spec, height=600)
        result = pane.export('svg')
        assert '300' in result and '600' in result

        # Test 5: Both pane dimensions override spec
        pane = Vega(spec, width=1000, height=800)
        result = pane.export('svg')
        assert '1000' in result and '800' in result

    @altair_available
    def test_export_altair_dimensions(self, vl_convert):
        """Test dimension handling with Altair charts."""
        # Altair chart dimensions in spec
        chart = altair_example()
        chart = chart.properties(width=600, height=400)
        pane = Vega(chart)
        result = pane.export('svg')
        assert '600' in result and '400' in result

        # Pane dimensions override Altair dimensions
        chart = chart.properties(width=300, height=200)
        pane = Vega(chart, width=1000, height=750)
        result = pane.export('svg')
        assert '1000' in result and '750' in result

    def test_export_kwargs_passed_to_vl_convert(self, vl_convert):
        """Test that additional kwargs are passed to vl_convert functions."""
        pane = Vega(vega_example)
        with patch.object(vlc, 'vegalite_to_png', return_value=b'fake_png') as mock_convert:
            result = pane.export('png', scale=2.0)
            assert result == b'fake_png'
            assert mock_convert.call_args[1]['scale'] == 2.0

    @pytest.mark.parametrize('fmt,expected_pane', [
        ('png', Image),
        ('jpeg', Image),
        ('svg', SVG),
        ('pdf', PDF),
        ('html', HTML),
    ])
    def test_export_as_pane(self, vl_convert, fmt, expected_pane):
        """Test export with as_pane=True returns correct pane type."""
        pane = Vega(vega_example)
        result = pane.export(fmt, as_pane=True)
        assert isinstance(result, expected_pane)

    def test_export_as_pane_url(self, vl_convert):
        """Test URL export with as_pane=True returns HTML pane with iframe."""
        pane = Vega(vega_example)
        result = pane.export('url', as_pane=True)
        assert isinstance(result, HTML)
        # Check that the object contains an iframe tag
        assert '<iframe' in result.object.lower()
        assert 'https://' in result.object

    def test_export_as_pane_false_returns_raw_data(self, vl_convert):
        """Test that as_pane=False returns raw data, not panes."""
        pane = Vega(vega_example)

        # PNG returns bytes, not Image pane
        result = pane.export('png', as_pane=False)
        assert isinstance(result, bytes)
        assert not isinstance(result, Image)

        # SVG returns string, not SVG pane
        result = pane.export('svg', as_pane=False)
        assert isinstance(result, str)
        assert not isinstance(result, SVG)
