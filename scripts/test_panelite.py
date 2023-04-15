"""
Before running this script make sure you have

```bash
git pull
pip install pytest-retry
pip install -e . -U
python setup.py develop
```

Then run the script to create/ update the notebooks for Panelite

```bash
python scripts/generate_panelite_content.py
```

Run the tests

```bash
pytest scripts/test_panelite.py --headed
```
"""
import pytest

from playwright.sync_api import Page, expect

URL = "https://panelite.holoviz.org"

PATHS = ["Getting_Started.ipynb", "gallery/apis/stocks_altair.ipynb"]

def _wait_for_notebook_tab(page, notebook):
    tabs = page.get_by_role("tablist")
    tabs.get_by_text(notebook)

def _select_kernel(page):
    page.get_by_role("button", name="Python (Pyodide)").click()
    page.get_by_role("button", name="Select").filter(has_text="Select").click()

def _run_all_cells(page):
    page.get_by_role("menuitem", name="Run").get_by_text("Run").click()
    page.get_by_text("Run All Cells").nth(2).click()

@pytest.mark.flaky(retries=2, delay=1)
@pytest.mark.parametrize(["path"], [(path,) for path in PATHS])
def test_homepage_has_Playwright_in_title_and_get_started_link_linking_to_the_intro_page(path, page: Page):
    url =URL + f"/lab/index.html?path={path}"
    notebook = path.split("/")[-1]

    page.goto(url)
    _wait_for_notebook_tab(page, notebook)
    _select_kernel(page)
    _run_all_cells(page)

    # To wait for * makes tests fail faster
    # The data-status attribute cannot be expected to change within the default timeout
    busy_cells = page.get_by_text("[*]:")
    expect(busy_cells).not_to_have_count(0)

    execution_indicator = page.locator('.jp-Notebook-ExecutionIndicator')
    expect(execution_indicator).to_have_attribute("data-status", "busy", timeout=120000)
    expect(execution_indicator).to_have_attribute("data-status", "idle", timeout=60000)

    traceback = page.locator('div[data-mime-type="application/vnd.jupyter.stderr"]')

    expect(traceback).to_have_count(0, timeout=1)
