import panel as pn

from .pn_model import GBM


def app(doc):
    gbm = GBM()
    row = pn.Row(gbm.param, gbm.update_plot)
    row.server_doc(doc)
