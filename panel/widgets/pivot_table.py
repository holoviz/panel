"""Implementation of the PerspectiveViewer Web Component"""

import param

from panel.models.pivot_table import PivotTable as _BkPivotTable
from panel.widgets.dataframe_base import DataFrameWithStreamAndPatchBaseWidget

class PivotTable(DataFrameWithStreamAndPatchBaseWidget):  # pylint: disable=abstract-method
    """The PivotTable widget enables exploring large tables of data
    in an interactive pivot table"""

    _widget_type = _BkPivotTable

    # I set this to something > 0. Otherwise the PerspectiveViewer widget will have a height of 0px
    # It will appear as if it does not work.
    height = param.Integer(default=300, bounds=(0, None))
