import asyncio
import threading

from .state import state


class StoppableThread(threading.Thread):
    """Thread class with a stop() method."""

    def __init__(self, io_loop, **kwargs):
        super().__init__(**kwargs)
        # Backward compatibility to handle Tornado IOLoop
        if hasattr(io_loop, 'asyncio_loop'):
            io_loop = io_loop.asyncio_loop
        self.asyncio_loop = io_loop
        self.server_id = kwargs.get('kwargs', {}).get('server_id')
        self._shutdown_task = None

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
            if bokeh_server is not None and hasattr(bokeh_server, 'stop'):
                # Handle tornado server
                try:
                    bokeh_server.stop()
                except Exception:
                    pass
            if hasattr(self, '_target'):
                del self._target, self._args, self._kwargs # type: ignore
            else:
                del self._Thread__target, self._Thread__args, self._Thread__kwargs # type: ignore

    def stop(self) -> None:
        if not self.is_alive():
            return
        elif self.server_id and self.server_id in state._servers:
            server, _, _ = state._servers[self.server_id]
            if hasattr(server, 'should_exit'):
                server.should_exit = True
                while self.is_alive():
                    continue
                return
        if self._shutdown_task:
            raise RuntimeError("Thread already stopping")
        self._shutdown_task = asyncio.run_coroutine_threadsafe(self._shutdown(), self.asyncio_loop)

    async def _shutdown(self):
        cur_task = asyncio.current_task()
        tasks = [t for t in asyncio.all_tasks() if t is not cur_task]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.asyncio_loop.stop()
        self._shutdown_task = None
