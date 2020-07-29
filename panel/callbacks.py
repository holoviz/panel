"""
Defines callbacks to be executed on a thread or by scheduling it
on a running bokeh server.
"""
import param

from .io.callbacks import PeriodicCallback # noqa

param.main.param.warning(
    "panel.callbacks module is deprecated and has been moved to "
    "panel.io.callbacks. Update your import as it will be removed "
    "in the next minor release."
)
