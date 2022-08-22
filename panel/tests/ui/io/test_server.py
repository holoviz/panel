import time

import pytest

pytestmark = pytest.mark.ui

from panel import config, state
from panel.io.server import serve
from panel.template import BootstrapTemplate


def test_server_reuse_sessions(page, port):
    def app(counts=[0]):
        config.reuse_sessions = True
        content = f'# Count {counts[0]}'
        counts[0] += 1
        return content

    serve(app, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    assert page.text_content(".bk.markdown") == 'Count 0'

    page.goto(f"http://localhost:{port}")

    assert page.text_content(".bk.markdown") == 'Count 1'


def test_server_reuse_sessions_with_session_key_func(page, port):
    def app(counts=[0]):
        config.param.update(
            reuse_sessions=True,
            session_key_func = lambda r: (r.path, r.arguments.get('arg', [''])[0])
        )
        title = state.session_args.get('arg', [b''])[0].decode('utf-8')
        content = f"# Count {counts[0]}"
        tmpl = BootstrapTemplate(title=title)
        tmpl.main.append(content)
        counts[0] += 1
        return tmpl

    serve(app, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}/?arg=foo")

    assert page.text_content("title") == 'foo'
    assert page.text_content(".bk.markdown") == 'Count 0'

    page.goto(f"http://localhost:{port}/?arg=bar")

    assert page.text_content("title") == 'bar'
    assert page.text_content(".bk.markdown") == 'Count 1'
