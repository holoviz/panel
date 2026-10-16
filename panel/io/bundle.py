"""
Bundles Pyodide and the Python dependencies of a converted application
next to it, so it can be served without access to a CDN or PyPI.

Dependencies are resolved by running micropip inside Pyodide under
node and freezing the resulting environment into a lockfile, which
the converted application then loads its packages from.
"""
from __future__ import annotations

import filecmp
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import typing as t

from urllib.parse import urlparse

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_wheel_filename

from .. import config
from .convert import PYODIDE_VERSION
from .resources import CDN_DIST, DIST_DIR, JS_VERSION

if t.TYPE_CHECKING:
    from collections.abc import Iterable

BUNDLE_DIR = 'pyodide'

STATIC_DIR = 'static'

PANEL_ROOT = f'{STATIC_DIR}/panel/'

PANEL_DIST = f'{PANEL_ROOT}{JS_VERSION}/dist/'

# Assets Panel references while rendering in the browser, which
# therefore do not show up in the converted HTML.
PANEL_RUNTIME_ASSETS = (
    'css', 'images', 'bundled/theme', 'bundled/font-awesome',
    *(f'bundled/{p.name}' for p in (DIST_DIR / 'bundled').glob('*template'))
)

CDN_ASSET_RE = re.compile(re.escape(CDN_DIST) + r'''([^"'\s)?#]+)''')

EXTENSION_ASSET_RE = re.compile(r'''(?<![\w/.-])static/extensions/([^/"'\s]+)/([^"'\s)?#]+)''')

RESOLVE_ATTEMPTS = 3

PYODIDE_CORE_FILES = (
    'pyodide.js', 'pyodide.mjs', 'pyodide.asm.mjs', 'pyodide.asm.wasm',
    'python_stdlib.zip'
)

RESOLVE_SCRIPT = """
import fs from "node:fs";
import { loadPyodide } from "pyodide";

const [specFile, lockFile] = process.argv.slice(2);
const { requirements, wheels } = JSON.parse(fs.readFileSync(specFile, "utf-8"));

const pyodide = await loadPyodide();
pyodide.FS.mkdirTree("/bundle_wheels");
for (const [name, path] of Object.entries(wheels)) {
  pyodide.FS.writeFile(`/bundle_wheels/${name}`, fs.readFileSync(path));
}
await pyodide.loadPackage("micropip");
pyodide.globals.set("requirements", pyodide.toPy(requirements));
const lock = await pyodide.runPythonAsync(`
import micropip
await micropip.install(list(requirements), keep_going=True)
micropip.freeze()
`);
fs.writeFileSync(lockFile, lock);
"""


def _cache_dir() -> pathlib.Path:
    try:
        import platformdirs
        root = platformdirs.user_cache_path()
    except ImportError:
        root = pathlib.Path.home() / '.cache'
    return root / 'holoviz' / 'panel.pyodide' / PYODIDE_VERSION


def _dist_url(compiled: bool = False) -> str:
    root = config.pyodide_cdn_root.rstrip('/')
    return f'{root}/{PYODIDE_VERSION}/{"pyc" if compiled else "full"}/'


def _executable(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(
            f'Bundling a Pyodide application requires {name!r} to be '
            'installed and available on the PATH.'
        )
    return path


def ensure_node_env() -> pathlib.Path:
    """
    Installs the pyodide npm package matching the Pyodide version
    converted apps are built against into a cache directory.

    Returns
    -------
    The directory containing the node environment.
    """
    env_dir = _cache_dir() / 'node'
    if not (env_dir / 'node_modules' / 'pyodide' / 'package.json').is_file():
        env_dir.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [_executable('npm'), 'install', '--prefix', str(env_dir), '--no-audit',
             '--no-fund', f'pyodide@{PYODIDE_VERSION.lstrip("v")}'],
            capture_output=True, text=True
        )
        if proc.returncode:
            raise RuntimeError(f'Failed to install pyodide with npm:\n{proc.stderr}')
    script = env_dir / 'resolve.mjs'
    if not script.is_file() or script.read_text(encoding='utf-8') != RESOLVE_SCRIPT:
        script.write_text(RESOLVE_SCRIPT, encoding='utf-8')
    return env_dir


def requirement_name(requirement: str) -> str:
    """
    Returns the canonical package name of a micropip requirement,
    which may be a requirement specifier or a URL to a wheel.
    """
    path = urlparse(requirement).path
    if path.endswith('.whl'):
        return canonicalize_name(parse_wheel_filename(os.path.basename(path))[0])
    return canonicalize_name(Requirement(requirement).name)


def resolve_requirements(requirements: list[str]) -> dict[str, t.Any]:
    """
    Resolves requirements into a Pyodide lockfile, containing only
    the requested packages and their dependencies.

    Arguments
    ---------
    requirements: list[str]
        Requirement specifiers, URLs or `file:` paths of wheels.

    Returns
    -------
    The lockfile contents, where packages from the Pyodide
    distribution reference the node cache, wheels from PyPI or
    other URLs their remote location and local wheels the path
    they were installed from.
    """
    env_dir = ensure_node_env()
    wheels, micropip_reqs = {}, []
    for req in requirements:
        parsed = urlparse(req)
        if parsed.scheme == 'file':
            name = os.path.basename(parsed.path)
            wheels[name] = parsed.path
            micropip_reqs.append(f'emfs:/bundle_wheels/{name}')
        else:
            micropip_reqs.append(req)

    with tempfile.TemporaryDirectory() as tmp:
        spec_file = pathlib.Path(tmp) / 'spec.json'
        lock_file = pathlib.Path(tmp) / 'lock.json'
        spec_file.write_text(json.dumps({'requirements': micropip_reqs, 'wheels': wheels}))
        # Retry since fetches from node fail intermittently
        for _ in range(RESOLVE_ATTEMPTS):
            proc = subprocess.run(
                [_executable('node'), str(env_dir / 'resolve.mjs'), str(spec_file), str(lock_file)],
                capture_output=True, text=True, cwd=env_dir
            )
            if not proc.returncode:
                break
        else:
            # Skip the minified source lines node prints alongside errors
            output = '\n'.join(
                line for line in (proc.stderr or proc.stdout).splitlines() if len(line) < 500
            )
            raise RuntimeError(f'Failed to resolve requirements {requirements!r}:\n{output}')
        lock = json.loads(lock_file.read_text(encoding='utf-8'))

    available: dict[str, t.Any] = {canonicalize_name(name): pkg for name, pkg in lock['packages'].items()}
    packages: dict[str, t.Any] = {}
    active: set[str] = set()

    # Pyodide deadlocks loading packages with cyclic dependencies (e.g.
    # panel <-> panel-material-ui), so edges back into the current
    # traversal path are dropped; their targets are loaded regardless.
    def visit(name: str) -> None:
        pkg = dict(available[name])
        file_name = os.path.basename(urlparse(pkg['file_name']).path)
        if file_name in wheels:
            pkg['file_name'] = wheels[file_name]
        packages[name] = pkg
        active.add(name)
        depends = []
        for dep in map(canonicalize_name, pkg['depends']):
            if dep in active:
                continue
            depends.append(dep)
            if dep not in packages:
                visit(dep)
        pkg['depends'] = depends
        active.remove(name)

    for req in requirements:
        if (name := requirement_name(req)) not in packages:
            visit(name)
    return {'info': lock['info'], 'packages': dict(sorted(packages.items()))}


def _sha256(path: pathlib.Path) -> str:
    sha = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            sha.update(chunk)
    return sha.hexdigest()


def _fetch(source: str | pathlib.Path, dest: pathlib.Path, sha256: str | None = None) -> None:
    """
    Copies or downloads a file, skipping it if the destination
    already exists with the expected hash or content. Writes are
    atomic so apps converted in parallel can share a bundle directory.
    """
    if dest.is_file():
        if sha256 is not None:
            if _sha256(dest) == sha256:
                return
        elif not isinstance(source, pathlib.Path) or filecmp.cmp(source, dest, shallow=False):
            return
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=dest.parent, prefix=f'.{dest.name}')
    tmp = pathlib.Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as out:
            if isinstance(source, pathlib.Path):
                with open(source, 'rb') as f:
                    shutil.copyfileobj(f, out)
            else:
                import requests
                with requests.get(source, stream=True, timeout=60) as response:
                    response.raise_for_status()
                    for chunk in response.iter_content(1 << 20):
                        out.write(chunk)
        if sha256 is not None and (actual := _sha256(tmp)) != sha256:
            raise ValueError(
                f'Hash mismatch for {source}: expected {sha256}, got {actual}.'
            )
        # mkstemp creates files only readable by the owner
        os.chmod(tmp, 0o644)
        os.replace(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)


def _distribution_lock(env_dir: pathlib.Path, compiled: bool) -> dict[str, t.Any]:
    if not compiled:
        lock_path = env_dir / 'node_modules' / 'pyodide' / 'pyodide-lock.json'
    else:
        lock_path = _cache_dir() / 'pyc-lock.json'
        _fetch(_dist_url(compiled=True) + 'pyodide-lock.json', lock_path)
    return json.loads(lock_path.read_text(encoding='utf-8'))


def bundle_pyodide(dest_path: str | os.PathLike, compiled: bool = False) -> pathlib.Path:
    """
    Writes the Pyodide runtime into the bundle directory.

    Arguments
    ---------
    dest_path: str | os.PathLike
        The directory the converted applications are written to.
    compiled: bool
        Whether to bundle the compiled (pyc) Pyodide distribution.

    Returns
    -------
    The bundle directory.
    """
    env_dir = ensure_node_env()
    bundle_dir = pathlib.Path(dest_path) / BUNDLE_DIR
    bundle_dir.mkdir(parents=True, exist_ok=True)
    node_dist = env_dir / 'node_modules' / 'pyodide'
    for name in PYODIDE_CORE_FILES:
        source: str | pathlib.Path = _dist_url(compiled) + name if compiled else node_dist / name
        _fetch(source, bundle_dir / name)
    return bundle_dir


def bundle_requirements(
    requirements: list[str],
    dest_path: str | os.PathLike,
    lock_name: str,
    compiled: bool = False
) -> list[str]:
    """
    Resolves requirements and writes all the packages they require
    and a lockfile referencing them into the bundle directory.

    Arguments
    ---------
    requirements: list[str]
        Requirement specifiers, URLs or `file:` paths of wheels.
    dest_path: str | os.PathLike
        The directory the converted applications are written to.
    lock_name: str
        The filename of the lockfile to write.
    compiled: bool
        Whether to bundle the compiled (pyc) Pyodide distribution.

    Returns
    -------
    The names of the requested packages, to be loaded from the lockfile.
    """
    env_dir = ensure_node_env()
    bundle_dir = bundle_pyodide(dest_path, compiled=compiled)
    node_dist = env_dir / 'node_modules' / 'pyodide'
    node_packages = json.loads((node_dist / 'pyodide-lock.json').read_text(encoding='utf-8'))['packages']
    dist_lock = _distribution_lock(env_dir, compiled)
    dist_packages = dist_lock['packages']
    dist_url = _dist_url(compiled)

    lock = resolve_requirements(requirements)
    for name, pkg in lock['packages'].items():
        file_name = os.path.basename(urlparse(pkg['file_name']).path)
        node_pkg = node_packages.get(name)
        source: str | pathlib.Path
        if node_pkg is not None and node_pkg['file_name'] == file_name:
            pkg = dict(dist_packages[name])
            file_name = pkg['file_name']
            cached = node_dist / file_name
            source = cached if not compiled and cached.is_file() else dist_url + file_name
            sha256 = pkg['sha256']
        elif urlparse(pkg['file_name']).scheme in ('http', 'https'):
            source = pkg['file_name']
            sha256 = pkg.get('sha256') or None
        else:
            source = pathlib.Path(pkg['file_name'])
            sha256 = _sha256(source)
        _fetch(source, bundle_dir / file_name, sha256)
        lock['packages'][name] = dict(
            pkg, file_name=file_name, sha256=sha256 or _sha256(bundle_dir / file_name)
        )

    lock['info'] = dist_lock['info']
    (bundle_dir / lock_name).write_text(json.dumps(lock, indent=2), encoding='utf-8')
    return [requirement_name(req) for req in requirements]


def bundle_files(dest_path: str | os.PathLike) -> Iterable[str]:
    """
    Returns the paths of all bundled files relative to dest_path.
    """
    bundle_dir = pathlib.Path(dest_path) / BUNDLE_DIR
    if not bundle_dir.is_dir():
        return []
    return sorted(
        f'{BUNDLE_DIR}/{f.name}' for f in bundle_dir.iterdir()
        if f.is_file() and not f.name.startswith('.')
    )


def _copy_tree(source: pathlib.Path, dest: pathlib.Path) -> None:
    if not source.exists():
        return
    elif source.is_file():
        _fetch(source, dest)
        return
    for path in source.rglob('*'):
        if path.is_file():
            _fetch(path, dest / path.relative_to(source))


def bundle_assets(html: str, dest_path: str | os.PathLike) -> str:
    """
    Copies the Panel and Bokeh extension assets referenced by a
    converted page next to it and rewrites the references to them.

    Arguments
    ---------
    html: str
        The HTML of the converted page.
    dest_path: str | os.PathLike
        The directory the converted applications are written to.

    Returns
    -------
    The HTML referencing the bundled assets.
    """
    from bokeh.embed.bundle import extension_dirs

    dest = pathlib.Path(dest_path)
    panel_dest = dest / PANEL_DIST
    assets = set(PANEL_RUNTIME_ASSETS)
    for match in CDN_ASSET_RE.finditer(html):
        parts = match.group(1).split('/')
        if parts[0] == 'bundled' and len(parts) > 2:
            depth = 3 if parts[1].startswith('@') and len(parts) > 3 else 2
            assets.add('/'.join(parts[:depth]))
        else:
            assets.add(match.group(1))
    for asset in sorted(assets):
        _copy_tree(DIST_DIR / asset, panel_dest / asset)

    extensions = set()
    for ext, path in EXTENSION_ASSET_RE.findall(html):
        if ext == 'panel':
            _copy_tree(DIST_DIR / path, dest / STATIC_DIR / 'extensions' / ext / path)
        elif ext in extension_dirs:
            extensions.add(ext)
    # Stylesheets reference fonts and images relative to themselves
    for ext in sorted(extensions):
        _copy_tree(pathlib.Path(extension_dirs[ext]), dest / STATIC_DIR / 'extensions' / ext)
    return html.replace(CDN_DIST, f'./{PANEL_DIST}')
