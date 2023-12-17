"""
Before running this script make sure you have

```bash
git pull
pip install -e . -U
python setup.py develop
```

Then run the script to create/ update the notebooks for Panelite

```bash
python scripts/generate_panelite_content.py
```

Follow the steps in the Panel Jupyterlite guide including

```bash
cd lite
pip install -r requirements.txt -U
jupyter lite build --output-dir ./dist
```

Start the http server

```bash
cd dist
python -m http.server
```

Reset your files as described in https://github.com/jupyterlite/jupyterlite/issues/9#issuecomment-875870620

Run the tests

```bash
pytest scripts/test_panelite/test_panelite.py --headed
```
"""
import pathlib

import pytest

from playwright.sync_api import Page, expect

from scripts.test_panelite.notebooks_with_panelite_issues import (
    NOTEBOOK_ISSUES,
)
from scripts.test_panelite.utils import Retrier

URL = "https://panelite.holoviz.org"
URL = "http://localhost:8000"

PANEL_BASE = pathlib.Path(__file__).parent.parent.parent
FILES = PANEL_BASE / 'lite' / 'files'

def get_panelite_nb_paths():
    nbs = list(FILES.glob('*/*/*.ipynb')) + list(FILES.glob('*/*.*'))
    for nb in nbs:
        path = str(nb).replace("\\", "/").split("files/")[-1]
        if path.endswith(".ipynb") and not ".ipynb_checkpoints" in path:
            yield path
PATHS_WITH_NOTHING_TO_TEST = [
    "gallery/demos/attractors.ipynb",
    "gallery/demos/gapminders.ipynb",
    "gallery/demos/glaciers.ipynb",
    "gallery/demos/nyc_taxi.ipynb",
    "gallery/demos/portfolio-optimizer.ipynb",
]
PATHS = list(path for path in get_panelite_nb_paths() if not path in PATHS_WITH_NOTHING_TO_TEST)
PATHS_WITHOUT_ISSUES = list(path for path in PATHS if path not in NOTEBOOK_ISSUES)
PATHS_WITH_ISSUES = list(path for path in PATHS if path in NOTEBOOK_ISSUES)

def _wait_for_notebook_tab(page, notebook):
    tabs = page.get_by_role("tablist")
    tabs.get_by_text(notebook)

def _select_kernel(page):
    page.get_by_role("button", name="Python (Pyodide)").click()
    page.get_by_role("button", name="Select").filter(has_text="Select").click()

def _run_all_cells(page):
    page.get_by_role("menuitem", name="Run").get_by_text("Run").click()
    page.get_by_text("Run All Cells").nth(2).click()

class RunCells(Exception):
    """Raised if an exception is raised while running all cells"""

def run_notebook(path, page):
    """Opens the notebook and runs all cells"""
    url =URL + f"/lab/index.html?path={path}"
    notebook = path.split("/")[-1]

    retrier = Retrier(retries=3, delay=1)
    while not retrier.accomplished:
        with retrier:
            page.goto(url)
            _wait_for_notebook_tab(page, notebook)
            _select_kernel(page)
            _run_all_cells(page)

            # To wait for * makes tests fail faster
            # The data-status attribute cannot be expected to change within the default timeout
            busy_cells = page.get_by_text("[*]:")
            expect(busy_cells).not_to_have_count(0)

            execution_indicator = page.locator('.jp-Notebook-ExecutionIndicator')
            expect(execution_indicator).to_have_attribute("data-status", "unknown", timeout=10000)
            expect(execution_indicator).to_have_attribute("data-status", "busy", timeout=10000)
            expect(execution_indicator).to_have_attribute("data-status", "idle", timeout=45000)


@pytest.mark.parametrize(["path"], [(path,) for path in PATHS_WITHOUT_ISSUES])
def test_notebooks_without_issues(path, page: Page):
    run_notebook(path, page)
    cells_with_err = page.locator('div[data-mime-type="application/vnd.jupyter.stderr"]')
    if cells_with_err.count()>0:
        raise RunCells(cells_with_err.first.inner_text())

@pytest.mark.xfail
@pytest.mark.parametrize(["path"], [(path,) for path in PATHS_WITH_ISSUES])
def test_notebooks_with_issues(path, page: Page):
    run_notebook(path, page)
    cells_with_err = page.locator('div[data-mime-type="application/vnd.jupyter.stderr"]')
    if cells_with_err.count()>0:
        raise RunCells(cells_with_err.first.inner_text())
