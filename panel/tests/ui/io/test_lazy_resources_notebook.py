"""
Lazy resource loading for notebooks rendered by the Jupyter extension.

``lazy.ipynb`` calls ``pn.extension()`` with no arguments and then renders
one component per cell, so nothing it needs is in the page up front and the
libraries can only arrive at render time. The two cells also have different
loading histories: by the time the second renders, the first has already
put es-module-shims and the registry to work.
"""
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

pytestmark = [pytest.mark.ui, pytest.mark.jupyter]


def _script_count(page, fragment):
    return page.evaluate(
        """(fragment) => document.querySelectorAll(`script[src*="${fragment}"]`).length""",
        fragment
    )


def test_notebook_components_load_resources_on_demand(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/lazy.ipynb")
    page.wait_for_load_state('networkidle')

    expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(1, timeout=30000)
    expect(page.locator('perspective-viewer')).to_have_count(1, timeout=30000)

    assert _script_count(page, 'tabulator.min.js') == 1
    assert _script_count(page, 'perspective-viewer-datagrid.js') == 1
    assert _script_count(page, 'es-module-shims') == 1

    urls = page.evaluate(
        """() => [...document.querySelectorAll('script[src]')].map((el) => el.src)"""
    )
    duplicates = {url for url in urls if urls.count(url) > 1}
    assert not duplicates, f'resources loaded more than once: {sorted(duplicates)}'


def test_notebook_declared_extensions_load_each_module_once(page, jupyter_preview):
    """
    ``eager.ipynb`` declares its extensions, so the autoload script loads the
    libraries up front. A module that is imported for its exported global must
    not get a bare module tag as well.
    """
    page.goto(f"{jupyter_preview}/eager.ipynb")
    page.wait_for_load_state('networkidle')

    expect(page.locator('perspective-viewer')).to_have_count(1, timeout=30000)
    expect(page.locator('.filepond--root')).to_have_count(1, timeout=30000)

    # A module with an exported global is imported by an inline script, so it
    # has no src of its own; one without keeps its bare tag.
    assert _script_count(page, 'perspective-viewer.js') == 0
    assert _script_count(page, 'filepond.esm.min.js') == 0
    assert _script_count(page, 'perspective-viewer-datagrid.js') == 1

    globals_defined = page.evaluate(
        """() => ({perspective: window.perspective != null, filepond: window.FilePond != null})"""
    )
    assert globals_defined == {'perspective': True, 'filepond': True}
