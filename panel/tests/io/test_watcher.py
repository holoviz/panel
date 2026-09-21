import asyncio
import gc
import pathlib

import pytest

from panel.io.state import state
from panel.io.watcher import (
    PathWatcher, current_path_watchers, get_path_watcher,
)
from panel.util.checks import import_available


class Subscriber:

    def __init__(self):
        self.calls = 0
        self.notified = asyncio.Event()

    def _update(self):
        self.calls += 1
        self.notified.set()


class FailingSubscriber(Subscriber):

    def _update(self):
        super()._update()
        raise ValueError('nope')


@pytest.fixture(autouse=True)
def clean_watchers(monkeypatch):
    from panel.io import watcher

    # Native filesystem events are not always delivered in CI containers
    # or sandboxes, so poll instead of relying on the platform backend.
    monkeypatch.setenv('WATCHFILES_FORCE_POLLING', '1')
    watcher._watchers.clear()
    yield
    for path_watcher in watcher._watchers.values():
        if path_watcher._stop_event is not None:
            path_watcher._stop_event.set()
    watcher._watchers.clear()
    state._watch_events.clear()


def test_get_path_watcher_is_shared_per_path(tmp_path):
    path = tmp_path / 'bundle.js'
    watcher = get_path_watcher(path)
    assert get_path_watcher(path) is watcher
    assert get_path_watcher(str(path)) is watcher
    assert get_path_watcher(tmp_path / 'other.js') is not watcher
    assert set(current_path_watchers()) == {path, tmp_path / 'other.js'}


def test_subscribe_and_unsubscribe(tmp_path):
    watcher = get_path_watcher(tmp_path / 'bundle.js')
    sub = Subscriber()

    watcher.subscribe(sub, '_update')
    watcher.subscribe(sub, '_update')
    assert list(watcher._subscribers) == [sub]
    assert watcher._subscribers[sub] == {'_update'}

    watcher.unsubscribe(sub, '_update')
    assert list(watcher._subscribers) == []


def test_subscribers_are_held_weakly(tmp_path):
    watcher = get_path_watcher(tmp_path / 'bundle.js')
    sub = Subscriber()
    watcher.subscribe(sub, '_update')

    del sub
    gc.collect()

    assert list(watcher._subscribers) == []


def test_notify_calls_all_subscribers(tmp_path):
    watcher = get_path_watcher(tmp_path / 'bundle.js')
    subs = [Subscriber() for _ in range(3)]
    for sub in subs:
        watcher.subscribe(sub, '_update')

    watcher._notify()

    assert all(sub.calls == 1 for sub in subs)


def test_notify_isolates_failing_subscriber(tmp_path):
    watcher = get_path_watcher(tmp_path / 'bundle.js')
    failing, working = FailingSubscriber(), Subscriber()
    watcher.subscribe(failing, '_update')
    watcher.subscribe(working, '_update')

    watcher._notify()

    assert failing.calls == 1
    assert working.calls == 1


def test_notify_routes_error_to_exception_handler(tmp_path):
    from panel.config import config

    watcher = get_path_watcher(tmp_path / 'bundle.js')
    failing = FailingSubscriber()
    watcher.subscribe(failing, '_update')
    errors = []

    with config.set(exception_handler=errors.append):
        watcher._notify()

    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)


def test_ensure_running_without_loop_is_noop(tmp_path):
    watcher = get_path_watcher(tmp_path / 'bundle.js')
    watcher.subscribe(Subscriber(), '_update')

    assert not watcher.running


@pytest.mark.skipif(not import_available('watchfiles'), reason='watchfiles is not installed')
async def test_watcher_notifies_on_file_change(tmp_path):
    path = tmp_path / 'bundle.js'
    path.write_text('export default {}')

    watcher = get_path_watcher(path)
    sub = Subscriber()
    watcher.subscribe(sub, '_update')

    assert watcher.running
    assert watcher._stop_event in state._watch_events

    # watchfiles snapshots the path asynchronously, so a change made before
    # it is watching goes unnoticed; keep writing until it is picked up.
    for version in range(20):
        path.write_text(f'export default {{version: {version}}}')
        try:
            await asyncio.wait_for(sub.notified.wait(), timeout=0.5)
            break
        except TimeoutError:
            continue

    assert sub.calls >= 1


@pytest.mark.skipif(not import_available('watchfiles'), reason='watchfiles is not installed')
async def test_watcher_task_is_shared(tmp_path):
    path = tmp_path / 'bundle.js'
    path.write_text('export default {}')

    watcher = get_path_watcher(path)
    first, second = Subscriber(), Subscriber()
    watcher.subscribe(first, '_update')
    task = watcher._task

    watcher.subscribe(second, '_update')

    assert watcher._task is task
    assert len([e for e in state._watch_events if e is watcher._stop_event]) == 1


@pytest.mark.skipif(not import_available('watchfiles'), reason='watchfiles is not installed')
async def test_stopping_watcher_deregisters_event(tmp_path):
    path = tmp_path / 'bundle.js'
    path.write_text('export default {}')

    watcher = get_path_watcher(path)
    sub = Subscriber()
    watcher.subscribe(sub, '_update')
    stop_event = watcher._stop_event

    stop_event.set()
    await watcher._task

    assert stop_event not in state._watch_events
    assert not watcher.running
    assert watcher._stop_event is None


def test_esm_components_share_a_watcher(document, comm, tmp_path):
    from panel.config import config
    from panel.custom import JSComponent

    esm = tmp_path / 'CustomShared.js'
    esm.write_text('export function render() {}')

    class CustomShared(JSComponent):
        _esm = pathlib.Path(esm)

    with config.set(autoreload=True):
        first, second = CustomShared(), CustomShared()
        root = first.get_root(document, comm)
        second.get_root(document, comm)

    watcher = get_path_watcher(esm)
    assert isinstance(watcher, PathWatcher)
    assert current_path_watchers() == {esm: watcher}
    assert set(watcher._subscribers) == {first, second}
    assert first._watching_esm is watcher

    first._cleanup(root)

    assert set(watcher._subscribers) == {second}
    assert first._watching_esm is None
