from __future__ import division

import numpy as np

from bokeh.core.properties import Dict, String, List, Any, Instance
from bokeh.models import LayoutDOM, ColumnDataSource

from .panels import PanelBase

JS_CODE = """
import * as p from "core/properties"
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"

export class PlotlyPlotView extends LayoutDOMView

  initialize: (options) ->
    super(options)

    url = "https://cdn.plot.ly/plotly-latest.min.js"

    if !window.Plotly?
      script = document.createElement('script')
      script.src = url
      script.async = false
      script.onreadystatechange = script.onload = () => @_init()
      document.querySelector("head").appendChild(script)
    else
      @_init()

  get_width: () ->
    return @model.data.layout.width

  get_height: () ->
    return @model.data.layout.height

  _init: () ->
    @_plot()
    @connect(@model.change, @_plot)

  _plot: () ->
    for i in [0...@model.data.data.length]
      trace = @model.data.data[i]
      cds = @model.data_sources[i]
      for column in cds.columns()
        shape = cds._shapes[column]
        array = cds.get_array(column)
        if shape.length > 1
          arrays = []
          for i in [0...shape[0]]
            arrays.push(array.slice(i*shape[1], (i+1)*shape[1]))
          array = arrays
        trace[column] = array
    Plotly.react(@el, @model.data.data, @model.data.layout)

export class PlotlyPlot extends LayoutDOM
  default_view: PlotlyPlotView
  type: "PlotlyPlot"

  @define {
    data: [ p.Any         ]
    data_sources: [ p.Array  ]
  }
"""


class PlotlyPlot(LayoutDOM):

    __implementation__ = JS_CODE

    data = Dict(String, Any)

    data_sources = List(Instance(ColumnDataSource))


class PlotlyPanel(PanelBase):
    """
    PlotlyPanel allos rendering a plotly Figure.

    For efficiency any array objects found inside a Figure are added
    to a ColumnDataSource which allows using binary transport to sync
    the figure on bokeh server and via Comms.
    """

    _updates = True

    def __init__(self, object, layout=None, **params):
        import plotly.graph_objs as go
        if not isinstance(object, go.Figure):
            object = go.Figure(data=object, layout=layout)
        super(PlotlyPanel, self).__init__(object, **params)

    @classmethod
    def applies(cls, obj):
        return ((isinstance(obj, list) and all(cls.applies(o) for o in obj)) or
                hasattr(obj, 'to_plotly_json'))

    def _get_model(self, doc, root, parent=None, comm=None, rerender=False):
        """
        Should return the bokeh model to be rendered.
        """
        json = self.object.to_plotly_json()
        traces = json['data']
        sources = []
        for trace in traces:
            data = {}
            for key, value in list(trace.items()):
                if isinstance(value, np.ndarray):
                    data[key] = trace.pop(key)
            sources.append(ColumnDataSource(data))
        model = PlotlyPlot(data=json, data_sources=sources)
        if rerender:
            return model, None
        self._link_object(model, doc, root, parent, comm)
        return model


    def _update(self, model):
        json = self.object.to_plotly_json()
        traces = json['data']
        new_sources = []
        for i, trace in enumerate(traces):
            if i < len(model.data_sources):
                cds = model.data_sources[i]
            else:
                cds = ColumnDataSource()
                new_sources.append(cds)
            data = {}
            for key, value in list(trace.items()):
                if isinstance(value, np.ndarray):
                    data[key] = trace.pop(key)
            cds.data = data
        model.data = json
        if new_sources:
            model.data_sources += new_sources
            
