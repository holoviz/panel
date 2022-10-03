import logging
import os

from contextlib import contextmanager
from pathlib import Path

import panel as pn


@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        path.mkdir(parents=True, exist_ok=True)
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def exception_handler(ex):
    logging.exception("Error", exc_info=ex)
    if pn.state.notifications and ex:
        pn.state.notifications.error(f"Error. {ex}")
