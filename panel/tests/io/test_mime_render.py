import pathlib

from panel.io.mime_render import (
    WriteCallbackStream, exec_with_return, find_imports, format_mime,
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

def test_find_imports_stdlibs():
    code = """
    import os
    import base64
    import pathlib
    """
    assert find_imports(code) == []

def test_find_import_stdlibs_multiline():
    code = """
    import re, io, time
    """
    assert find_imports(code) == []

def test_find_import_imports_multiline():
    code = """
    import numpy, scipy
    """
    assert find_imports(code) == ['numpy', 'scipy']

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
        print()
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
