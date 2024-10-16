from typing import (
    TYPE_CHECKING, ClassVar, Mapping, Optional,
)

import param

from ..models import ChartJS as _BkChartJS
from ..util import lazy_load
from .base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm, JupyterComm


class ChartJS(ModelPane):
    # Set the Bokeh model to use
    _widget_type = _BkChartJS

    # Rename Panel Parameters -> Bokeh Model properties
    # Parameters like title that does not exist on the Bokeh model should be renamed to None
    _rename: ClassVar[Mapping[str, str | None]] = {}

    # Parameters to be mapped to Bokeh model properties
    object = param.String(default="Click Me!")
    clicks = param.Integer(default=0)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        self._bokeh_model = lazy_load(
            'panel.models.chartjs', 'ChartJS', isinstance(comm, JupyterComm), root
        )
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('chartjs_event', model=model, doc=doc, comm=comm)
        return model
