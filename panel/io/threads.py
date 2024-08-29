import asyncio
import threading


class StoppableThread(threading.Thread):
    """Thread class with a stop() method."""

    def __init__(self, io_loop, **kwargs):
        super().__init__(**kwargs)
        # Backward compatibility to handle Tornado IOLoop
        if hasattr(io_loop, 'asyncio_loop'):
            io_loop = io_loop.asyncio_loop
        self.asyncio_loop = io_loop
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
            if hasattr(bokeh_server, 'stop'):
                # Handle tornado server
                try:
                    bokeh_server.stop()
                except Exception:
                    pass
            elif hasattr(bokeh_server, 'shutdown'):
                # Handle uvicorn server
                try:
                    self.asyncio_loop.run_until_complete(bokeh_server.shutdown())
                except Exception:
                    pass
            if hasattr(self, '_target'):
                del self._target, self._args, self._kwargs # type: ignore
            else:
                del self._Thread__target, self._Thread__args, self._Thread__kwargs # type: ignore

    def stop(self) -> None:
        """Signal to stop the event loop gracefully."""
        if self._shutdown_task:
            raise RuntimeError("Thread already stopping")
        self._shutdown_task = asyncio.run_coroutine_threadsafe(self._shutdown(), self.asyncio_loop)

    async def _shutdown(self):
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.asyncio_loop.stop()
        self._shutdown_task = None
