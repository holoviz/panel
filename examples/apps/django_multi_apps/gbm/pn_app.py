import panel as pn

from .pn_model import GBM


def app(doc):
    gbm = GBM()
    row = pn.Row(pn.Column(gbm.param, gbm.refresh), gbm.update_plot)
    row.server_doc(doc)
