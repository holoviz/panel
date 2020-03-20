from bokeh.models import Model
from bokeh.core.properties import String


class CommManager(Model):

    plot_id = String()

    comm_id = String()
