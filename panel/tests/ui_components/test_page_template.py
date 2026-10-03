import pytest

import panel as pn

from panel.config import config
from panel.io.state import state


@pytest.fixture
def page_template(server_document):
    with config.set(template='page'):
        yield


def test_page_template_name_resolves_to_page():
    with config.set(template='page'):
        assert config.template is pn.ui.Page


def test_page_template_servable_targets(page_template):
    main = pn.ui.Markdown('main')
    sidebar = pn.ui.Button(label='sidebar')
    header = pn.ui.Button(label='header')
    contextbar = pn.ui.Markdown('context')

    main.servable(title='My App')
    sidebar.servable(target='sidebar')
    header.servable(target='header')
    contextbar.servable(target='contextbar')

    page = state.template
    assert isinstance(page, pn.ui.Page)
    assert page.title == 'My App'
    assert list(page.main) == [main]
    assert list(page.sidebar) == [sidebar]
    assert list(page.header) == [header]
    assert list(page.contextbar) == [contextbar]


def test_page_template_servable_appends_in_order(page_template):
    first, second = pn.ui.Markdown('a'), pn.ui.Markdown('b')
    first.servable()
    second.servable()
    assert list(state.template.main) == [first, second]


def test_page_template_servable_reassigns_area(page_template):
    page = state.template
    events = []
    page.param.watch(events.append, 'sidebar')
    pn.ui.Button(label='a').servable(target='sidebar')
    assert len(events) == 1


def test_page_template_servable_unknown_target_raises(page_template):
    with pytest.raises(ValueError, match="no 'modal' area"):
        pn.ui.Markdown('x').servable(target='modal')


def test_page_template_servable_page_raises(page_template):
    with pytest.raises(RuntimeError, match='pn.config.template'):
        pn.ui.Page(main=['x']).servable()
