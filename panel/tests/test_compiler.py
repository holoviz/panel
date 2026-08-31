import pytest

from panel import compiler
from panel.io.resources import CDN_DIST
from panel.theme.bootstrap import Bootstrap


@pytest.fixture
def no_download(monkeypatch):
    def _fail(url):
        raise AssertionError(f'Unexpected download of {url}')
    monkeypatch.setattr(compiler, '_download', _fail)


def test_write_bundled_files_skips_panel_cdn(no_download):
    compiler.write_bundled_files('Bootstrap', [f'{CDN_DIST}bundled/jquery/jquery.min.js'])


def test_write_bundled_files_rejects_error_response(monkeypatch):
    class Response:
        ok = False
        status_code = 404

    monkeypatch.setattr(compiler, '_download', lambda url: (Response(), None))
    with pytest.raises(ConnectionError, match='status 404'):
        compiler.write_bundled_files('KaTeX', ['https://cdn.example.org/katex/missing.css'])


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


def test_design_cdn_resources_are_not_refetched(no_download):
    resources = Bootstrap._resources
    urls = [
        url for kind in ('css', 'js') for url in resources.get(kind, {}).values()
        if url.startswith(CDN_DIST)
    ]
    assert urls
    compiler.write_bundled_files('Bootstrap', urls)
