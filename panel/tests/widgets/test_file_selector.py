import os
import shutil

from collections import OrderedDict

import pytest

from panel.widgets import FileSelector

@pytest.yield_fixture
def test_dir():
    test_dir = os.path.expanduser(os.path.join('~','test_dir'))
    os.mkdir(test_dir)
    os.mkdir(os.path.expanduser(os.path.join('~','test_dir','subdir1')))
    with open(os.path.expanduser(os.path.join('~','test_dir','subdir1','a')), 'a'):
        pass
    with open(os.path.expanduser(os.path.join('~','test_dir','subdir1','b')), 'a'):
        pass
    os.mkdir(os.path.expanduser(os.path.join('~','test_dir','subdir2')))
    yield test_dir
    shutil.rmtree(os.path.expanduser(os.path.join('~','test_dir')))


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
        'a': os.path.join(test_dir, 'subdir1', 'a'),
        'b': os.path.join(test_dir, 'subdir1', 'b')
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

    assert selector._selector._lists[False].options == ['a']


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

    assert selector._selector.options == OrderedDict([
        ('a', os.path.join(test_dir, 'subdir1', 'a')),
        ('b', os.path.join(test_dir, 'subdir1', 'b'))
    ])
    assert selector._selector._lists[False].options == ['b']
    assert selector.value == [os.path.join(test_dir, 'subdir1', 'a')]
