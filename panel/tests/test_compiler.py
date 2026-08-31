import json

import pytest

from bokeh.model import Model

from panel import compiler
from panel.config import config
from panel.io.resources import CDN_DIST
from panel.theme.bootstrap import Bootstrap

NPM_CDN = config.npm_cdn.rstrip('/')


@pytest.fixture
def no_download(monkeypatch):
    def _fail(url):
        raise AssertionError(f'Unexpected download of {url}')
    monkeypatch.setattr(compiler, '_download', _fail)


@pytest.fixture(autouse=True)
def clean_licenses():
    compiler._LICENSE_SOURCES.clear()
    yield
    compiler._LICENSE_SOURCES.clear()


def test_write_bundled_files_skips_panel_cdn(no_download):
    compiler.write_bundled_files('Bootstrap', [f'{CDN_DIST}bundled/jquery/jquery.min.js'])


def test_write_bundled_files_rejects_error_response(monkeypatch):
    class Response:
        ok = False
        status_code = 404

    monkeypatch.setattr(compiler, '_download', lambda url: (Response(), None))
    with pytest.raises(ConnectionError, match='status 404'):
        compiler.write_bundled_files('KaTeX', [f'{NPM_CDN}/katex@0.16.22/dist/missing.css'])


@pytest.mark.parametrize('content, expected', [
    # The comment on its own line, and appended to the last rule, which is
    # what minified CSS does.
    ('code()\n//# sourceMappingURL=lib.min.js.map',
     'code()\n//# sourceMappingURL=https://cdn.example.org/a/lib.min.js.map'),
    ('a{}/*# sourceMappingURL=lib.css.map */',
     'a{}/*# sourceMappingURL=https://cdn.example.org/a/lib.css.map */'),
    ('code()\n//@ sourceMappingURL=lib.js.map',
     'code()\n//@ sourceMappingURL=https://cdn.example.org/a/lib.js.map'),
    # jsdelivr serves some maps from a hashed root path.
    ('code()\n//# sourceMappingURL=/sm/abc123.map',
     'code()\n//# sourceMappingURL=https://cdn.example.org/sm/abc123.map'),
    # An inline map needs nothing fetched, and an absolute url already
    # resolves wherever the file ends up.
    ('code()\n//# sourceMappingURL=data:application/json;base64,e30=',
     'code()\n//# sourceMappingURL=data:application/json;base64,e30='),
    ('code()\n//# sourceMappingURL=https://other.example/lib.js.map',
     'code()\n//# sourceMappingURL=https://other.example/lib.js.map'),
])
def test_rewrite_source_map_url(content, expected):
    base = 'https://cdn.example.org/a/lib.min.js'
    assert compiler._rewrite_source_map_url(content, base) == expected


@pytest.mark.parametrize('content', [
    # The strings and regexes bundlers carry in order to handle the comment
    # themselves must not be mistaken for the comment. Both of these are
    # real: the first is in ace's coffee worker, the second in babel.
    'var k="//# sourceMappingURL=data:application/json;base64,"+i,L=1',
    'return /(?:\\/\\/[@#][ \\t]+sourceMappingURL=([^\\s\'"]+?)[ \\t]*$)/gm',
    'var r="sourceMappingURL="+e;return"//# "+r',
])
def test_rewrite_source_map_url_ignores_code(content):
    assert compiler._rewrite_source_map_url(content, 'https://cdn.example.org/a/lib.js') == content


def test_rewrite_source_map_url_strips_without_base():
    """
    A file out of a tarball has no url to resolve against, and a comment
    pointing at a map that was not bundled is a 404 on every page load.
    """
    assert compiler._rewrite_source_map_url('a{}/*# sourceMappingURL=a.css.map */', None) == 'a{}'
    assert compiler._rewrite_source_map_url('code()\n//# sourceMappingURL=a.js.map', None) == 'code()\n'


@pytest.mark.parametrize('tarball, expected', [
    ({'tar': 'https://registry.npmjs.org/bootstrap/-/bootstrap-5.3.0-alpha1.tgz', 'src': 'package/dist'},
     'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/'),
    ({'tar': 'https://registry.npmjs.org/ace-builds/-/ace-builds-1.40.1.tgz', 'src': 'package/src-min-noconflict/'},
     'https://cdn.jsdelivr.net/npm/ace-builds@1.40.1/src-min-noconflict/'),
    ({'tar': 'https://registry.npmjs.org/@scope/pkg/-/pkg-1.2.3.tgz', 'src': 'package'},
     'https://cdn.jsdelivr.net/npm/@scope/pkg@1.2.3/'),
    ({'zip': 'https://use.fontawesome.com/releases/v5.15.4/fontawesome-free-5.15.4-web.zip'}, None),
])
def test_npm_cdn_dir(tarball, expected):
    assert compiler._npm_cdn_dir(tarball) == expected


def test_bundled_resource_tarballs_have_a_cdn_dir():
    """
    Without one the sourcemap comments in bootstrap and jQuery are stripped
    rather than repointed, which loses in-browser debugging for the designs.
    """
    from panel.io.resources import RESOURCE_URLS
    tarballs = {
        name: resource for name, resource in RESOURCE_URLS.items() if 'tar' in resource
    }
    assert tarballs
    assert all(compiler._npm_cdn_dir(resource) for resource in tarballs.values())


@pytest.mark.parametrize('url, expected', [
    (f'{NPM_CDN}/tabulator-tables@6.4.0/dist/js/tabulator.min.js', 'tabulator-tables@6.4.0'),
    (f'{NPM_CDN}/@finos/perspective@3.8.0/dist/cdn/perspective.js', '@finos/perspective@3.8.0'),
    # A range or a bare name is left as declared, so the license comes from
    # whichever release the CDN resolves the code from.
    (f'{NPM_CDN}/filepond@^4/dist/filepond.esm.min.js', 'filepond@^4'),
    (f'{NPM_CDN}/luxon/build/global/luxon.min.js', 'luxon'),
    (f'{NPM_CDN}/vega@6.1.2', 'vega@6.1.2'),
    ('https://registry.npmjs.org/bootstrap/-/bootstrap-5.3.0-alpha1.tgz', 'bootstrap@5.3.0-alpha1'),
    ('https://registry.npmjs.org/@microsoft/fast-components/-/fast-components-2.30.6.tgz',
     '@microsoft/fast-components@2.30.6'),
    ('https://cdn.plot.ly/plotly-3.1.0.min.js', 'plotly.js-dist-min@3.1.0'),
    ('https://api.mapbox.com/mapbox-gl-js/v3.0.1/mapbox-gl.js', 'mapbox-gl@3.0.1'),
])
def test_license_spec(url, expected):
    assert compiler._license_spec(url) == expected


def test_license_spec_rejects_unattributable_url():
    with pytest.raises(ValueError, match='LICENSE_PACKAGES'):
        compiler._license_spec('https://cdn.example.org/somelib/somelib.min.js')


def test_register_license_skips_panel_cdn(no_download):
    compiler._register_license(f'{CDN_DIST}bundled/jquery/jquery.min.js')
    assert not compiler._LICENSE_SOURCES


def test_register_license_ignores_cache_busting_query():
    compiler._register_license(f'{NPM_CDN}/katex@0.16.22/dist/katex.min.css?v=1.10.0')
    assert set(compiler._LICENSE_SOURCES) == {'katex@0.16.22'}


@pytest.fixture
def registered_models():
    """
    Puts Panel's models back into Bokeh's resolver.

    ``bundle_models`` reads the models off the resolver, having imported the
    modules that define them, which is enough in the fresh process a build
    runs in. Under the test suite the ``module_cleanup`` fixture has already
    stripped them out and the imports are no-ops, so it would otherwise walk
    a fraction of the models and collect a fraction of the resources.
    """
    from bokeh.core.has_props import _default_resolver

    from panel.config import panel_extension
    from panel.util import _descendents

    for imp in panel_extension._imports.values():
        if imp.startswith('panel.models'):
            __import__(imp)
    known = dict(_default_resolver._known_models)
    for cls in _descendents(Model):
        _default_resolver._known_models.setdefault(cls.__qualified_model__, cls)
    try:
        yield
    finally:
        _default_resolver._known_models.clear()
        _default_resolver._known_models.update(known)


def test_every_bundled_url_can_be_attributed(monkeypatch, tmp_path, registered_models):
    """
    ``_register_license`` raises for a url it cannot attribute to an npm
    release, so collecting the whole bundle is the check. A dependency taken
    from a CDN that is not npm shaped, or one whose pinned version moves out
    from under ``LICENSE_PACKAGES``, fails here rather than being shipped
    inside the wheel without the terms it is licensed under.
    """
    monkeypatch.setattr(compiler, 'BUNDLE_DIR', tmp_path)
    download_list = []
    compiler.bundle_resource_urls(download_list=download_list)
    compiler.bundle_models(download_list=download_list)
    compiler.bundle_templates(download_list=download_list)
    compiler.bundle_themes(download_list=download_list)

    assert len(compiler._LICENSE_SOURCES) > 40
    # A stale entry is as bad as a missing one, since it pins a version that
    # nothing is bundled from any more.
    assert set(compiler.LICENSE_PACKAGES.values()) <= set(compiler._LICENSE_SOURCES)


def test_unminified_duplicates():
    names = [
        'tabulator.js', 'tabulator.min.js',
        'bootstrap.css', 'bootstrap.min.css',
        # Only one build published, so there is nothing to drop.
        'quill.js', 'gridstack.min.css',
        # Not a build of the same file.
        'perspective.wasm', 'LICENSE',
    ]
    assert compiler._unminified_duplicates(names) == {'tabulator.js', 'bootstrap.css'}


def test_prune_unminified_duplicates(monkeypatch, tmp_path):
    monkeypatch.setattr(compiler, 'BUNDLE_DIR', tmp_path)
    (tmp_path / 'jquery').mkdir()
    for name in ('jquery/jquery.js', 'jquery/jquery.min.js', 'jquery/LICENSE'):
        (tmp_path / name).write_text('x')
    # The unminified build is only a duplicate of one sitting beside it.
    (tmp_path / 'quill').mkdir()
    (tmp_path / 'quill' / 'quill.js').write_text('x')

    compiler.prune_unminified_duplicates()

    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob('*') if p.is_file()) == [
        'jquery/LICENSE', 'jquery/jquery.min.js', 'quill/quill.js'
    ]


def _license_response(monkeypatch, files):
    class Response:
        def __init__(self, body):
            self.ok = body is not None
            self.content = self.text = body

    monkeypatch.setattr(
        compiler, '_download',
        lambda url: (Response(files.get(url.rsplit('/', 1)[-1])), None)
    )


def test_write_license(monkeypatch, tmp_path):
    monkeypatch.setattr(compiler, 'BUNDLE_DIR', tmp_path)
    monkeypatch.setattr(compiler, 'LICENSE_DIR', tmp_path / 'licenses')
    _license_response(monkeypatch, {
        'package.json': json.dumps({'name': 'notyf', 'version': '3.10.0', 'license': 'MIT'}),
        'LICENSE.md': 'MIT License\n',
    })
    index = []

    compiler._write_license('notyf@3', index)

    assert (tmp_path / 'licenses' / 'notyf@3.10.0.txt').read_text() == 'MIT License\n'
    assert index == [{
        'package': 'notyf',
        'version': '3.10.0',
        'specifier': 'notyf@3',
        'license': 'MIT',
        'source': f'{NPM_CDN}/notyf@3/LICENSE.md',
        'file': 'licenses/notyf@3.10.0.txt',
    }]


def test_write_license_falls_back_to_declared_identifier(monkeypatch, tmp_path):
    """
    npm does not require a package to include its license text, and two of
    the libraries Panel bundles do not.
    """
    monkeypatch.setattr(compiler, 'BUNDLE_DIR', tmp_path)
    monkeypatch.setattr(compiler, 'LICENSE_DIR', tmp_path / 'licenses')
    _license_response(monkeypatch, {'package.json': json.dumps(
        {'name': '@microsoft/fast-components', 'version': '2.30.6', 'license': 'MIT'}
    )})
    index = []

    compiler._write_license('@microsoft/fast-components@2.30.6', index)

    written = (tmp_path / 'licenses' / '@microsoft' / 'fast-components@2.30.6.txt').read_text()
    assert 'distributed under the MIT license' in written
    assert index[0]['source'] is None


def test_write_license_rejects_package_without_any_license(monkeypatch, tmp_path):
    monkeypatch.setattr(compiler, 'LICENSE_DIR', tmp_path / 'licenses')
    _license_response(monkeypatch, {'package.json': json.dumps({'name': 'x', 'version': '1.0.0'})})
    with pytest.raises(ConnectionError, match='nothing to redistribute it under'):
        compiler._write_license('x@1.0.0', [])


def test_design_cdn_resources_are_not_refetched(no_download):
    resources = Bootstrap._resources
    urls = [
        url for kind in ('css', 'js') for url in resources.get(kind, {}).values()
        if url.startswith(CDN_DIST)
    ]
    assert urls
    compiler.write_bundled_files('Bootstrap', urls)
