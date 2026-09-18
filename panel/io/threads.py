import asyncio
import logging
import threading
import typing as t

from .state import state

logger = logging.getLogger(__name__)

SHUTDOWN_TIMEOUT = 5


class StoppableThread(threading.Thread):
    """Thread class with a stop() method."""

    def __init__(self, io_loop, owns_loop: bool = False, **kwargs):
        super().__init__(**kwargs)
        # Backward compatibility to handle Tornado IOLoop
        if hasattr(io_loop, 'asyncio_loop'):
            io_loop = io_loop.asyncio_loop
        self.asyncio_loop = io_loop
        self._owns_loop = owns_loop
        self.server_id = kwargs.get('kwargs', {}).get('server_id')
        self._shutdown_task: t.Any | None = None

    def run(self) -> None:
        if hasattr(self, '_target'):
            target, args, kwargs = self._target, self._args, self._kwargs # type: ignore
        else:
            target, args, kwargs = self._Thread__target, self._Thread__args, self._Thread__kwargs # type: ignore
        if not target:
            return
        bokeh_server = None
        try:
            bokeh_server = target(*args, **kwargs)
        finally:
            if (
                bokeh_server is not None and hasattr(bokeh_server, 'stop')
                and not getattr(bokeh_server, '_stopped', False)
            ):
                # Handle tornado server
                try:
                    bokeh_server.stop()
                except Exception:
                    pass
            if self._owns_loop and self.asyncio_loop and not self.asyncio_loop.is_closed():
                try:
                    self._cancel_pending_tasks()
                except Exception:
                    logger.debug('Could not drain pending tasks', exc_info=True)
                finally:
                    try:
                        self.asyncio_loop.close()
                    except Exception:
                        logger.debug('Could not close the event loop', exc_info=True)
            if hasattr(self, '_target'):
                del self._target, self._args, self._kwargs # type: ignore
            else:
                del self._Thread__target, self._Thread__args, self._Thread__kwargs # type: ignore

    def _cancel_pending_tasks(self) -> None:
        # Stopping the server can schedule tasks that never run before the
        # loop is closed, leaving them destroyed while pending.
        loop = self.asyncio_loop
        tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
        if not tasks:
            return
        for task in tasks:
            task.cancel()
        # A task may shield itself from the cancellation, so it is not awaited
        # indefinitely.
        loop.run_until_complete(asyncio.wait(tasks, timeout=SHUTDOWN_TIMEOUT))

    def stop(self) -> None:
        if not self.is_alive():
            return
        elif self.server_id and self.server_id in state._servers:
            server, _, _ = state._servers[self.server_id]
            if hasattr(server, 'should_exit'):
                server.should_exit = True
                self.join()
                return
        if self._shutdown_task:
            raise RuntimeError("Thread already stopping")
        self._shutdown_task = asyncio.run_coroutine_threadsafe(self._shutdown(), self.asyncio_loop)
        self.join()

    async def _shutdown(self):
        # A locked callback cancelled halfway may already have returned a
        # coroutine, which nothing awaits then.
        servers = state._servers.get(self.server_id) if self.server_id else None
        server = servers[0] if servers else None
        if server is not None and not getattr(server, '_stopped', True):
            # Lifecycle hooks and locked callbacks run before the server is
            # stopped, so it may never complete.
            try:
                await asyncio.wait_for(server.stop_async(), SHUTDOWN_TIMEOUT)
            except TimeoutError:
                logger.warning('Server did not stop within %s seconds', SHUTDOWN_TIMEOUT)
            except Exception:
                logger.debug('Could not stop the server', exc_info=True)
        cur_task = asyncio.current_task()
        tasks = [t for t in asyncio.all_tasks() if t is not cur_task]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.asyncio_loop.stop()
        self._shutdown_task = None
