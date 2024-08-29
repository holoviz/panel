import pytest

from panel.io.compile import packages_from_code


def test_packages_from_code_simple():
    code, pkgs = packages_from_code('import * from "https://esm.sh/confetti-canvas@1.0.0"')
    assert code == 'import * from "confetti-canvas"'
    assert pkgs == {'confetti-canvas': '^1.0.0'}

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
