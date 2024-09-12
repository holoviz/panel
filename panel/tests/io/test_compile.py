import pytest

from panel.io.compile import (
    packages_from_code, packages_from_importmap, replace_imports,
)


def test_packages_from_code_esm_sh():
    code, pkgs = packages_from_code('import * from "https://esm.sh/confetti-canvas@1.0.0"')
    assert code == 'import * from "confetti-canvas"'
    assert pkgs == {'confetti-canvas': '^1.0.0'}

def test_packages_from_code_unpkg():
    code, pkgs = packages_from_code('import * from "https://unpkg.com/esm@3.2.25/esm/loader.js"')
    assert code == 'import * from "esm"'
    assert pkgs == {'esm': '^3.2.25'}

def test_packages_from_code_jsdelivr():
    code, pkgs = packages_from_code('import * as vg from "https://cdn.jsdelivr.net/npm/@uwdata/vgplot@0.8.0/+esm"')
    assert code == 'import * as vg from "@uwdata/vgplot"'
    assert pkgs == {'@uwdata/vgplot': '^0.8.0'}

@pytest.mark.parametrize('dev', ['rc', 'a', 'b'])
def test_packages_from_code_dev(dev):
    code, pkgs = packages_from_code(f'import * from "https://esm.sh/confetti-canvas@1.0.0-{dev}.1"')
    assert code == 'import * from "confetti-canvas"'
    assert pkgs == {'confetti-canvas': f'^1.0.0-{dev}.1'}

@pytest.mark.parametrize('import_code', [
    'import * from "https://esm.sh/chart.js@1.0.0/auto"',
    'import * from "https://esm.sh/chart.js@1.0.0/auto?deps=react"',
    'import * from "https://esm.sh/chart.js@1.0.0&external=react/auto"',
])
def test_packages_from_code_path(import_code):
    code, pkgs = packages_from_code(import_code)
    assert code == 'import * from "chart.js/auto"'
    assert pkgs == {'chart.js': '^1.0.0'}

def test_replace_imports_single_quote():
    assert replace_imports("import {foo} from 'bar'", {'bar': 'pkg-bar'}) == "import {foo} from 'pkg-bar'"

def test_replace_imports_double_quote():
    assert replace_imports('import {foo} from "bar"', {'bar': 'pkg-bar'}) == 'import {foo} from "pkg-bar"'

def test_replace_imports_trailing_slash():
    assert replace_imports('import {foo} from "bar/baz"', {'bar': 'pkg-bar'}) == 'import {foo} from "pkg-bar/baz"'

def test_replace_imports_only_from():
    assert replace_imports('import {bar} from "bar"', {'bar': 'pkg-bar'}) == 'import {bar} from "pkg-bar"'

def test_packages_from_importmap_esm_sh():
    code, packages = packages_from_importmap(
        'import * from "confetti"',
        {'confetti': 'https://esm.sh/confetti-canvas@1.0.0'}
    )
    assert code == 'import * from "confetti-canvas"'
    assert packages == {'confetti-canvas': '^1.0.0'}

def test_packages_from_importmap_unpkg():
    code, pkgs = packages_from_importmap(
        'import * from "esm"',
        {'esm': 'https://unpkg.com/esm@3.2.25/esm/loader.js'}
    )
    assert code == 'import * from "esm"'
    assert pkgs == {'esm': '^3.2.25'}

def test_packages_from_importmap_jsdelivr():
    code, pkgs = packages_from_importmap(
        'import * as vg from "@uwdata/vgplot"',
        {"@uwdata/vgplot": "https://cdn.jsdelivr.net/npm/@uwdata/vgplot@0.8.0/+esm"}
    )
    assert code == 'import * as vg from "@uwdata/vgplot"'
    assert pkgs == {'@uwdata/vgplot': '^0.8.0'}

@pytest.mark.parametrize('dev', ['rc', 'a', 'b'])
def test_packages_from_importmap_dev(dev):
    code, pkgs = packages_from_importmap(
        'import * from "confetti"',
        {'confetti': f'https://esm.sh/confetti-canvas@1.0.0-{dev}.1'}
    )
    assert code == 'import * from "confetti-canvas"'
    assert pkgs == {'confetti-canvas': f'^1.0.0-{dev}.1'}

@pytest.mark.parametrize('url', [
    "https://esm.sh/chart.js@1.0.0/",
    "https://esm.sh/chart.js@1.0.0/?deps=react",
    "https://esm.sh/chart.js@1.0.0&external=react/",
])
def test_packages_from_importmap_path(url):
    code, pkgs = packages_from_importmap('import * from "chart-js/auto"', {'chart-js/': url})
    assert code == 'import * from "chart.js/auto"'
    assert pkgs == {'chart.js': '^1.0.0'}
