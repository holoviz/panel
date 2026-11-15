import pathlib

from io import StringIO

import pytest

from panel.io.convert import BOKEH_VERSION, collect_python_requirements
from panel.io.mime_render import (
    WriteCallbackStream, exec_with_return, find_requirements, format_mime,
)


class HTML:
    def __init__(self, html):
        self.html = html
    def _repr_html_(self):
        return self.html

class Javascript:
    def __init__(self, js):
        self.js = js
    def _repr_javascript_(self):
        return self.js

class Markdown:
    def __init__(self, md):
        self.md = md
    def _repr_markdown_(self):
        return self.md

class PNG:
    def _repr_png_(self):
        with open(pathlib.Path(__file__).parent.parent / 'test_data' / 'logo.png', 'rb') as f:
            return f.read()

def test_convert_requirements_use_native_http():
    requirements = collect_python_requirements('', ['requests'], panel_version='1.10.0')
    assert requirements == [f'bokeh=={BOKEH_VERSION}', 'panel==1.10.0', 'requests']

def test_find_imports_stdlibs():
    code = """
    import os
    import base64
    import pathlib
    import random
    from datetime import datetime, timedelta
    """
    assert find_requirements(code) == []

def test_find_import_stdlibs_multiline():
    code = """
    import re, io, time
    """
    assert find_requirements(code) == []

def test_find_import_imports_multiline():
    code = """
    import numpy, scipy
    """
    assert find_requirements(code) == ['numpy', 'scipy']

def test_find_import_replacement():
    code = """
    import transformers_js
    """
    assert find_requirements(code) == ['transformers-js-py']

@pytest.fixture
def namespace_packages(tmp_path, monkeypatch):
    for name, module_file in (
        ('test-rpc', 'panel_test_namespace/api/rpc/__init__.py'),
        ('test-utilities', 'panel_test_namespace/api/utilities.py'),
    ):
        module = tmp_path / module_file
        module.parent.mkdir(parents=True, exist_ok=True)
        module.touch()
        dist_info = tmp_path / f"{name.replace('-', '_')}-1.0.dist-info"
        dist_info.mkdir()
        (dist_info / 'METADATA').write_text(f'Name: {name}\nVersion: 1.0\n', encoding='utf-8')
        (dist_info / 'RECORD').write_text(f'{module_file},,\n', encoding='utf-8')
    monkeypatch.syspath_prepend(str(tmp_path))

@pytest.mark.parametrize(('code', 'expected'), [
    ('import panel_test_namespace.api.rpc', ['test-rpc']),
    ('from panel_test_namespace.api import rpc as r, utilities', ['test-rpc', 'test-utilities']),
    ('from panel_test_namespace.api.rpc import connect', ['test-rpc']),
    ('import panel_test_namespace.api', ['panel_test_namespace']),
    ('from panel_test_namespace.api import unavailable', ['panel_test_namespace']),
    ('from .api import rpc', []),
])
def test_find_namespace_requirements(namespace_packages, code, expected):
    assert find_requirements(code) == expected

def test_convert_namespace_requirements(namespace_packages):
    code = StringIO("""
    import panel_test_namespace.api.rpc
    import panel_test_namespace.api.utilities
    from panel_test_namespace.api import rpc
    """)
    assert collect_python_requirements(code, panel_version='1.10.0') == [
        f'bokeh=={BOKEH_VERSION}', 'panel==1.10.0', 'test-rpc', 'test-utilities',
    ]

def test_exec_with_return_multi_line():
    assert exec_with_return('a = 1\nb = 2\na + b') == 3

def test_exec_with_return_no_return():
    assert exec_with_return('a = 1') is None

def test_exec_with_return_None():
    assert exec_with_return('None') is None

def test_exec_captures_print():
    def capture_stdout(stdout):
        assert stdout == 'foo'
    stdout = WriteCallbackStream(capture_stdout)
    assert exec_with_return('print("foo")', stdout=stdout) is None
    assert stdout.getvalue() == 'foo'

def test_exec_captures_error():
    def capture_stderr(stderr):
        print()  # noqa: T201
    stderr = WriteCallbackStream(capture_stderr)
    assert exec_with_return('raise ValueError("bar")', stderr=stderr) is None
    assert 'ValueError: bar' in stderr.getvalue()

def test_format_mime_None():
    assert format_mime(None) == ('None', 'text/plain')

def test_format_mime_str():
    assert format_mime('foo') == ('foo', 'text/plain')

def test_format_mime_str_with_escapes():
    assert format_mime('foo>bar') == ('foo&gt;bar', 'text/plain')

def test_format_mime_repr_html():
    assert format_mime(HTML('<b>BOLD</b>')) == ('<b>BOLD</b>', 'text/html')

def test_format_mime_repr_javascript():
    assert format_mime(Javascript('1+1')) == ('<script>1+1</script>', 'text/html')

def test_format_mime_repr_markdown():
    assert format_mime(Markdown('**BOLD**')) == ('<p><strong>BOLD</strong></p>', 'text/html')

def test_format_mime_repr_png():
    img, mime_type = format_mime(PNG())
    assert mime_type == 'text/html'
    assert img.startswith('<img src="data:image/png')

def test_format_mime_type():
    string, mime_type = format_mime(HTML)
    assert mime_type == 'text/plain'
    assert string == '&lt;class &#x27;panel.tests.io.test_mime_render.HTML&#x27;&gt;'
