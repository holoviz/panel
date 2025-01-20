import os

from pathlib import Path

import pytest

try:
    import s3fs
except Exception:
    s3fs = None

from panel.models.widgets import DoubleClickEvent
from panel.widgets.file_selector import (
    FileSelector, LocalFileProvider, RemoteFileProvider,
)

s3fs_available = pytest.mark.skipif(s3fs is None, reason='s3fs not available')

FILE_PATH = Path(__file__)


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

@pytest.fixture
async def s3_filesystem():
    fs = s3fs.S3FileSystem(anon=True)
    yield fs
    s3 = await fs.get_s3()
    await s3.close()

def test_local_file_provider_is_dir():
    provider = LocalFileProvider()
    assert not provider.isdir(FILE_PATH)
    assert provider.isdir(FILE_PATH.parent)

def test_local_file_provider_ls():
    provider = LocalFileProvider()
    dirs, files = provider.ls(FILE_PATH.parent, '*test_file_selector*')
    assert files == [str(FILE_PATH)]

@s3fs_available
def test_remote_file_provider_is_dir(s3_filesystem):
    provider = RemoteFileProvider(fs=s3_filesystem)
    assert not provider.isdir('s3://datasets.holoviz.org/stocks/v1/stocks.csv')
    assert provider.isdir('s3://datasets.holoviz.org/stocks/v1/')

@s3fs_available
def test_remote_file_provider_ls(s3_filesystem):
    provider = RemoteFileProvider(fs=s3_filesystem)
    dirs, _ = provider.ls('s3://datasets.holoviz.org/stocks/')
    assert dirs == ['s3://datasets.holoviz.org/stocks/v1/']
    _, files = provider.ls('s3://datasets.holoviz.org/stocks/v1')
    assert files == ['s3://datasets.holoviz.org/stocks/v1/stocks.csv']


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
