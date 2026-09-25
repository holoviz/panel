"""
Cross-links Panel's component gallery with the panel-material-ui gallery.

Panel 1.10 ships ``panel.ui``, a namespace where most component names resolve to
Material implementations from panel-material-ui and the rest to the classic
components. For the names that exist in both implementations a reference page
documents only half of what a user can get, so this extension adds a banner
pointing at the other one.

Both halves of the banner set are derived at build time: the Material names from
the imports in ``panel/ui``, the target pages from panel-material-ui's
intersphinx inventory. Neither is written down here, so the banners cannot drift
out of sync with the namespace or with the other site's section layout.

The reciprocal banner is added by ``doc/_ext/classic_reference.py`` in
panel-material-ui.
"""
from __future__ import annotations

import ast
import pathlib

from sphinx.util import logging

logger = logging.getLogger(__name__)

INVENTORY = 'panel_material_ui'

# Module a classic component is imported from, by gallery section.
CLASSIC_MODULES = {
    'chat': 'pn.chat',
    'indicators': 'pn.indicators',
    'layouts': 'pn.layout',
    'panes': 'pn.pane',
    'templates': 'pn.template',
    'widgets': 'pn.widgets',
}

BANNER = """
:::{{admonition}} Material version available
:class: tip

`pn.ui.{name}` resolves to the Material Design implementation of this component,
documented in the {{external+{inventory}:doc}}`panel-material-ui reference <{target}>`.
This page documents {classic}.
:::
"""

_cache: dict[str, object] = {}


def material_names() -> set[str]:
    """
    Names that ``panel.ui`` resolves to a panel-material-ui component.

    Read from the source of ``panel/ui`` rather than by importing it, since
    importing ``panel.ui`` selects the Material design for the whole docs build.
    """
    if 'names' in _cache:
        return _cache['names']
    import panel
    ui = pathlib.Path(panel.__file__).parent / 'ui'
    names: set[str] = set()
    for path in sorted(ui.rglob('*.py')):
        for node in ast.parse(path.read_text(encoding='utf-8')).body:
            if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('panel_material_ui'):
                names.update(alias.asname or alias.name for alias in node.names)
    if not names:
        logger.warning(
            'No panel-material-ui imports found in %s, Material reference '
            'banners will not be added.', ui
        )
    _cache['names'] = names
    return names


def material_pages(env) -> dict[str, str]:
    """Reference page docnames on the panel-material-ui site, by component name."""
    if 'pages' in _cache:
        return _cache['pages']
    inventories = getattr(env, 'intersphinx_named_inventory', {})
    if INVENTORY not in inventories:
        logger.warning(
            'No %r intersphinx inventory, Material reference banners will not '
            'be added. Is the site reachable?', INVENTORY
        )
    pages = {}
    for docname in inventories.get(INVENTORY, {}).get('std:doc', {}):
        parts = docname.split('/')
        if len(parts) == 3 and parts[0] == 'reference' and parts[2] != 'index':
            pages[parts[2]] = docname
    _cache['pages'] = pages
    return pages


def banner_line(lines: list[str]) -> int:
    """
    Line the banner is inserted at, after the title and the download links
    nbsite writes above the first thematic break.
    """
    for i, line in enumerate(lines[:8]):
        if line.strip() == '---':
            return i + 1
    for i, line in enumerate(lines[:4]):
        if line.startswith('# '):
            return i + 1
    return 0


def add_material_banner(app, docname, source):
    parts = docname.split('/')
    if len(parts) != 3 or parts[0] != 'reference':
        return
    _, section, name = parts
    if name not in material_names():
        return
    pages = material_pages(app.env)
    if name not in pages:
        return
    module = CLASSIC_MODULES.get(section)
    classic = f'the classic `{module}.{name}`' if module else f'the classic {name}'
    banner = BANNER.format(
        classic=classic, name=name, inventory=INVENTORY, target=pages[name]
    )
    lines = source[0].split('\n')
    at = banner_line(lines)
    source[0] = '\n'.join(lines[:at] + banner.split('\n') + lines[at:])
    logger.debug('[material_reference] linked %s to %s', docname, pages[name])


def clear_cache(app):
    _cache.clear()


def report(app):
    """
    Logs the number of components that will be cross-linked, so that a build
    which silently stops linking them is visible in the log. Runs late so that
    intersphinx has loaded its inventories.
    """
    names, pages = material_names(), material_pages(app.env)
    linked = [
        path.stem for path in pathlib.Path(app.srcdir).glob('reference/*/*.md')
        if path.stem in names and path.stem in pages
    ]
    log = logger.info if linked else logger.warning
    log('Cross-linking %d reference pages to their Material version.', len(linked))


def setup(app):
    app.connect('builder-inited', clear_cache)
    app.connect('builder-inited', report, priority=900)
    app.connect('source-read', add_material_banner)
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
