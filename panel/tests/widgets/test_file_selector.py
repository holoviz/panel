import os

import pytest
import s3fs

from panel.models.widgets import DoubleClickEvent
from panel.widgets import FileSelector, FileTree


@pytest.fixture
def test_dir(tmp_path):
    test_dir = tmp_path / 'test_dir'
    subdir1 = test_dir / 'subdir1'
    subdir2 = test_dir / 'subdir2'
    a = subdir1 / "a"
    b = subdir1 / "b"

    subdir1.mkdir(parents=True)
    subdir2.mkdir(parents=True)
    a.write_text("")
    b.write_text("")

    yield str(test_dir)


def test_file_selector_init(test_dir):
    selector = FileSelector(test_dir)

    assert selector._selector.options == {
        '\U0001f4c1subdir1': os.path.join(test_dir, 'subdir1'),
        '\U0001f4c1subdir2': os.path.join(test_dir, 'subdir2')
    }


def test_file_selector_address_bar(test_dir):
    selector = FileSelector(test_dir)

    selector._directory.value = os.path.join(test_dir, 'subdir1')

    assert not selector._go.disabled

    selector._go.clicks = 1

    assert selector._cwd == os.path.join(test_dir, 'subdir1')
    assert selector._go.disabled
    assert selector._forward.disabled
    assert not selector._back.disabled
    assert selector._selector.options == {
        '⬆ ..': '..',
        'a': os.path.join(test_dir, 'subdir1', 'a'),
        'b': os.path.join(test_dir, 'subdir1', 'b'),
    }

    selector._up.clicks = 1

    selector._selector._lists[False].value = ['subdir1']

    assert selector._directory.value == os.path.join(test_dir, 'subdir1')

    selector._selector._lists[False].value = []

    assert selector._directory.value == test_dir


def test_file_selector_back_and_forward(test_dir):
    selector = FileSelector(test_dir)

    selector._directory.value = os.path.join(test_dir, 'subdir1')
    selector._go.clicks = 1

    assert selector._cwd == os.path.join(test_dir, 'subdir1')
    assert not selector._back.disabled
    assert selector._forward.disabled

    selector._back.clicks = 1

    assert selector._cwd == test_dir
    assert selector._back.disabled
    assert not selector._forward.disabled

    selector._forward.clicks = 1

    assert selector._cwd == os.path.join(test_dir, 'subdir1')


def test_file_selector_up(test_dir):
    selector = FileSelector(test_dir)

    selector._directory.value = os.path.join(test_dir, 'subdir1')
    selector._go.clicks = 1

    assert selector._cwd == os.path.join(test_dir, 'subdir1')

    selector._up.clicks = 1

    assert selector._cwd == test_dir


def test_file_selector_select_files(test_dir):
    selector = FileSelector(test_dir)

    selector._directory.value = os.path.join(test_dir, 'subdir1')
    selector._go.clicks = 1

    selector._selector._lists[False].value = ['a']
    selector._selector._buttons[True].clicks = 1

    assert selector.value == [os.path.join(test_dir, 'subdir1', 'a')]

    selector._selector._lists[False].value = ['b']
    selector._selector._buttons[True].clicks = 2

    assert selector.value == [
        os.path.join(test_dir, 'subdir1', 'a'),
        os.path.join(test_dir, 'subdir1', 'b')
    ]

    selector._selector._lists[True].value = ['a', 'b']
    selector._selector._buttons[False].clicks = 2

    assert selector.value == []


def test_file_selector_only_files(test_dir):
    selector = FileSelector(test_dir, only_files=True)

    selector._selector._lists[False].value = ['\U0001f4c1subdir1']
    selector._selector._buttons[True].clicks = 1

    assert selector.value == []
    assert selector._selector._lists[False].options == ['\U0001f4c1subdir1', '\U0001f4c1subdir2']


def test_file_selector_file_pattern(test_dir):
    selector = FileSelector(test_dir, file_pattern='a')

    selector._directory.value = os.path.join(test_dir, 'subdir1')
    selector._go.clicks = 1

    assert selector._selector._lists[False].options == ['⬆ ..', 'a']


def test_file_selector_double_click_up(test_dir):
    selector = FileSelector(test_dir)

    selector._directory.value = os.path.join(test_dir, 'subdir1')
    selector._go.clicks = 1

    assert selector._directory.value == os.path.join(test_dir, 'subdir1')

    selector._select_and_go(DoubleClickEvent(option='⬆ ..', model=None))

    assert selector._directory.value == test_dir

def test_file_selector_cannot_select_up(test_dir):
    selector = FileSelector(test_dir)

    selector._directory.value = os.path.join(test_dir, 'subdir1')
    selector._go.clicks = 1

    selector._selector._lists[False].value = ['⬆ ..']
    selector._selector._buttons[True].param.trigger('clicks')

    assert not selector._selector._lists[False].value
    assert not selector._selector._lists[True].options
    assert not selector.value

def test_file_selector_multiple_across_dirs(test_dir):
    selector = FileSelector(test_dir)

    selector._selector._lists[False].value = ['\U0001f4c1subdir2']
    selector._selector._buttons[True].clicks = 1

    assert selector.value == [os.path.join(test_dir, 'subdir2')]

    selector._directory.value = os.path.join(test_dir, 'subdir1')
    selector._go.clicks = 1

    selector._selector._lists[False].value = ['a']
    selector._selector._buttons[True].clicks = 2

    assert selector.value == [os.path.join(test_dir, 'subdir2'),
                              os.path.join(test_dir, 'subdir1', 'a')]

    selector._selector._lists[True].value = ['\U0001f4c1'+os.path.join('..', 'subdir2')]
    selector._selector._buttons[False].clicks = 1

    assert selector._selector.options == {
        '⬆ ..': '..',
        'a': os.path.join(test_dir, 'subdir1', 'a'),
        'b': os.path.join(test_dir, 'subdir1', 'b'),
    }
    assert selector._selector._lists[False].options == ['⬆ ..', 'b']
    assert selector.value == [os.path.join(test_dir, 'subdir1', 'a')]


def test_filetree_local(test_dir):
    tree = FileTree(directory=test_dir)
    assert len(tree._nodes) == 1
    node = tree._nodes[0]
    assert os.path.abspath(node['id']) == os.path.abspath(test_dir)
    assert node['text'] == 'test_dir'
    assert node['icon'] == 'jstree-folder'
    assert node['type'] == 'folder'
    assert node['state']['opened']
    assert len(node['children']) == 2
    assert node['children'][0]['text'] == 'subdir1'
    assert node['children'][1]['text'] == 'subdir2'


def test_filetree_s3(test_dir):
    fs = s3fs.S3FileSystem(anon=True)
    url = 's3://datasets.holoviz.org'

    tree = FileTree(directory=url, fs=fs)
    assert len(tree._nodes) == 1
    node = tree._nodes[0]
    assert os.path.abspath(node['id']) == os.path.abspath(url)
    assert node['text'] == 'datasets.holoviz.org'
    assert node['icon'] == 'jstree-folder'
    assert node['type'] == 'folder'
    assert node['state']['opened']

    names = map(os.path.basename, fs.ls(url))
    for child, name in zip(node['children'], names, strict=True):
        assert child["text"] == name
