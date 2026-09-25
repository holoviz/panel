"""
Shared file watching for the autoreload development loop.

Components that render from the same file, e.g. every component compiled
into a shared ESM bundle, would otherwise each start their own watcher
task. This module hands out one watcher per path and notifies all its
subscribers when the file changes.
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import typing as t
import weakref

from .state import state

_watchers: dict[pathlib.Path, PathWatcher] = {}


class PathWatcher:
    """
    Watches a single path on behalf of any number of subscribers.

    Subscribers are held weakly, so subscribing does not keep a component
    alive; each is notified by calling the method it subscribed with.
    """

    def __init__(self, path: pathlib.Path):
        self.path = path
        self._subscribers: weakref.WeakKeyDictionary[t.Any, set[str]] = weakref.WeakKeyDictionary()
        self._stop_event: asyncio.Event | None = None
        self._task: asyncio.Task | None = None

    def subscribe(self, obj: t.Any, method: str) -> None:
        """
        Subscribes an object to changes of the watched path.

        Parameters
        ----------
        obj: Any
            The object to notify, held weakly.
        method: str
            Name of the method to invoke on the object.
        """
        self._subscribers.setdefault(obj, set()).add(method)
        self._ensure_running()

    def unsubscribe(self, obj: t.Any, method: str | None = None) -> None:
        """
        Unsubscribes an object, either from a single method or entirely.
        """
        if method is None:
            self._subscribers.pop(obj, None)
            return
        methods = self._subscribers.get(obj)
        if methods is None:
            return
        methods.discard(method)
        if not methods:
            self._subscribers.pop(obj, None)

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    def _ensure_running(self) -> None:
        if self.running:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Without a running loop there is nothing to schedule the
            # watcher on, e.g. when rendering to a static file.
            return
        self._stop_event = asyncio.Event()
        # Registering the event lets the server stop the watcher on shutdown
        # alongside its own autoreload watchers.
        state._watch_events.append(self._stop_event)
        # Deliberately not scheduled via state.execute, which would bind the
        # task to whichever Document happens to be rendering; the watcher is
        # shared by all sessions and must outlive any one of them.
        self._task = loop.create_task(self._watch())

    async def _watch(self) -> None:
        import watchfiles
        stop_event = self._stop_event
        try:
            async for changes in watchfiles.awatch(self.path, stop_event=stop_event):
                if await self._is_complete_write(changes, watchfiles):
                    self._notify()
        finally:
            if stop_event in state._watch_events:
                state._watch_events.remove(stop_event)
            self._stop_event = None
            self._task = None

    async def _is_complete_write(self, changes, watchfiles) -> bool:
        """
        Whether any change represents a finished write. Bundlers write
        non-atomically, so a modification event may arrive while the file
        is still missing or only partially written. A write that replaces
        the file atomically is reported as a deletion followed by an
        addition, so additions count as a new version while a deletion on
        its own does not.
        """
        updated = False
        for change, path in changes:
            if change is watchfiles.Change.deleted:
                continue
            for _ in range(5):
                if os.path.exists(path):
                    updated = True
                    break
                await asyncio.sleep(0.1)
        return updated

    def _notify(self) -> None:
        from ..config import config
        for obj, methods in list(self._subscribers.items()):
            for method in list(methods):
                try:
                    getattr(obj, method)()
                except Exception as e:
                    # The watcher is shared, so a failing subscriber must not
                    # tear down reloading for all the others.
                    if config.exception_handler:
                        config.exception_handler(e)
                    else:
                        state.log(
                            f'{type(obj).__name__}.{method} raised {e!r} while '
                            f'handling a change to {self.path}.', level='error'
                        )


def get_path_watcher(path: str | os.PathLike) -> PathWatcher:
    """
    Returns the process-wide watcher for the given path, creating it on
    first use.
    """
    path = pathlib.Path(path).absolute()
    if path not in _watchers:
        _watchers[path] = PathWatcher(path)
    return _watchers[path]


def current_path_watchers() -> dict[pathlib.Path, PathWatcher]:
    """
    Returns the watchers that have been created so far.
    """
    return dict(_watchers)
