import * as p from "core/properties"
import {clone} from "core/util/object"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"


function isPlainObject (obj: any) {
	return Object.prototype.toString.call(obj) === '[object Object]';
}

interface PlotlyHTMLElement extends HTMLElement {
    on(event: 'plotly_relayout', callback: (eventData: any) => void): void;
    on(event: 'plotly_restyle', callback: (eventData: any) => void): void;
    on(event: 'plotly_click', callback: (eventData: any) => void): void;
    on(event: 'plotly_hover', callback: (eventData: any) => void): void;
    on(event: 'plotly_clickannotation', callback: (eventData: any) => void): void;
    on(event: 'plotly_selected', callback: (eventData: any) => void): void;
    on(event: 'plotly_deselect', callback: () => void): void;
    on(event: 'plotly_unhover', callback: () => void): void;
}

const filterEventData = (gd: any, eventData: any, event: string) => {
    // Ported from dash-core-components/src/components/Graph.react.js
    let filteredEventData: {[k: string]: any} = Array.isArray(eventData)? []: {};

    if (event === "click" || event === "hover" || event === "selected") {
        const points = [];

        if (eventData === undefined || eventData === null) {
            return null;
        }

        /*
         * remove `data`, `layout`, `xaxis`, etc
         * objects from the event data since they're so big
         * and cause JSON stringify ciricular structure errors.
         *
         * also, pull down the `customdata` point from the data array
         * into the event object
         */
        const data = gd.data;

        for (let i = 0; i < eventData.points.length; i++) {
            const fullPoint = eventData.points[i];

            let pointData: {[k: string]: any} = {};
            for (let property in fullPoint) {
              const val = fullPoint[property];
              if (fullPoint.hasOwnProperty(property) &&
                  !Array.isArray(val) && !isPlainObject(val))  {

                pointData[property] = val;
              }
            }

            if (fullPoint !== undefined && fullPoint !== null) {
              if(fullPoint.hasOwnProperty("curveNumber") &&
                  fullPoint.hasOwnProperty("pointNumber") &&
                  data[fullPoint["curveNumber"]].hasOwnProperty("customdata")) {

                pointData["customdata"] =
                    data[fullPoint["curveNumber"]].customdata[
                        fullPoint["pointNumber"]
                    ]
              }

              // specific to histogram. see https://github.com/plotly/plotly.js/pull/2113/
              if (fullPoint.hasOwnProperty('pointNumbers')) {
                  pointData["pointNumbers"] = fullPoint.pointNumbers;
              }
            }

            points[i] = pointData;
        }
        filteredEventData["points"] = points;
    } else if (event === 'relayout' || event === 'restyle') {
        /*
         * relayout shouldn't include any big objects
         * it will usually just contain the ranges of the axes like
         * "xaxis.range[0]": 0.7715822247381828,
         * "xaxis.range[1]": 3.0095292008680063`
         */
        for (let property in eventData) {
              if (eventData.hasOwnProperty(property))  {
                filteredEventData[property] = eventData[property];
              }
        }
    }
    if (eventData.hasOwnProperty('range')) {
        filteredEventData["range"] = eventData["range"];
    }
    if (eventData.hasOwnProperty('lassoPoints')) {
        filteredEventData["lassoPoints"] = eventData["lassoPoints"];
    }
    return filteredEventData;
};

export class PlotlyPlotView extends HTMLBoxView {
  model: PlotlyPlot
  _connected: string[]

  connect_signals(): void {
    super.connect_signals();
    this.connect(this.model.properties.data.change, this.render);
    this.connect(this.model.properties.layout.change, this._relayout);
    this.connect(this.model.properties.config.change, this.render);
    this.connect(this.model.properties.data_sources.change, () => this._connect_sources());

    // Python -> JavaScript messages
    this.connect(this.model.properties._py2js_addTraces.change, this.do_addTraces);
    this.connect(this.model.properties._py2js_restyle.change, this.do_restyle);
    this.connect(this.model.properties._py2js_relayout.change, this.do_relayout);
    this.connect(this.model.properties._py2js_update.change, this.do_update);
    this.connect(this.model.properties._py2js_animate.change, this.do_animate);
    this.connect(this.model.properties._py2js_deleteTraces.change, this.do_deleteTraces);
    this.connect(this.model.properties._py2js_moveTraces.change, this.do_moveTraces);

    this._connected = [];
    this._connect_sources();
  }

  _connect_sources(): void {
    for (let i = 0; i < this.model.data.length; i++) {
      const cds = this.model.data_sources[i]
      if (this._connected.indexOf(cds.id) < 0) {
        this.connect(cds.properties.data.change, () => this._restyle(i))
        this._connected.push(cds.id)
      }
    }
  }

  render(): void {
    super.render()
    if (!(window as any).Plotly) { return }
    if (!this.model.data.length && !Object.keys(this.model.layout).length) {
      (window as any).Plotly.purge(this.el);
    }
    const data = [];
    for (let i = 0; i < this.model.data.length; i++) {
      data.push(this._get_trace(i, false));
    }

    (window as any).Plotly.react(this.el, data, this.model.layout, this.model.config);

    // Install callbacks
    //  - plotly_relayout
    (<PlotlyHTMLElement>(this.el)).on('plotly_relayout', (eventData: any) => {
      this.model.relayout_data = filterEventData(
          this.el, eventData, 'relayout');
    });

    //  - plotly_restyle
    (<PlotlyHTMLElement>(this.el)).on('plotly_restyle', (eventData: any) => {
      this.model.restyle_data = filterEventData(
          this.el, eventData, 'restyle');
    });

    //  - plotly_click
    (<PlotlyHTMLElement>(this.el)).on('plotly_click', (eventData: any) => {
      this.model.click_data = filterEventData(
          this.el, eventData, 'click');
    });

    //  - plotly_hover
    (<PlotlyHTMLElement>(this.el)).on('plotly_hover', (eventData: any) => {
      this.model.hover_data = filterEventData(
          this.el, eventData, 'hover');
    });

    //  - plotly_selected
    (<PlotlyHTMLElement>(this.el)).on('plotly_selected', (eventData: any) => {
      this.model.selected_data = filterEventData(
          this.el, eventData, 'selected');
    });

    //  - plotly_clickannotation
    (<PlotlyHTMLElement>(this.el)).on('plotly_clickannotation', (eventData: any) => {
      delete eventData["event"];
      delete eventData["fullAnnotation"];
      this.model.clickannotation_data = eventData
    });

    //  - plotly_deselect
    (<PlotlyHTMLElement>(this.el)).on('plotly_deselect', () => {
      this.model.selected_data = null;
    });

    //  - plotly_unhover
    (<PlotlyHTMLElement>(this.el)).on('plotly_unhover', () => {
      this.model.hover_data = null;
    });
  }

  _get_trace(index: number, update: boolean): any {
    const trace = clone(this.model.data[index]);
    const cds = this.model.data_sources[index];
    for (const column of cds.columns()) {
      const shape: number[] = cds._shapes[column][0];
      let array = cds.get_array(column)[0];
      if (shape.length > 1) {
        const arrays = [];
        for (let s = 0; s < shape[0]; s++) {
          arrays.push(array.slice(s*shape[1], (s+1)*shape[1]));
        }
        array = arrays;
      }
      let prop_path = column.split(".");
      let prop = prop_path[prop_path.length - 1];
      var prop_parent = trace;
      for(let k of prop_path.slice(0, -1)) {
        prop_parent = prop_parent[k]
      }

      if (update) {
        prop_parent[prop] = [array];
      } else {
        prop_parent[prop] = array;
      }
    }
    return trace;
  }

  /**
     * Input a trace index specification and return an Array of trace
     * indexes where:
     *
     *  - null|undefined -> Array of all traces
     *  - Trace index as Number -> Single element array of input index
     *  - Array of trace indexes -> Input array unchanged
     *
     * @param {undefined|null|Number|Array.<Number>} trace_indexes
     * @returns {Array.<Number>}
     *  Array of trace indexes
     * @private
     */
    _normalize_trace_indexes(trace_indexes: any): Array<number> {
        if (trace_indexes === null || trace_indexes === undefined) {
            var numTraces = this.model.data.length;
            trace_indexes = Array.from(Array(numTraces).keys())
        }
        if (!Array.isArray(trace_indexes)) {
            // Make sure idx is an array
            trace_indexes = [trace_indexes];
        }
        return trace_indexes
    }

  _restyle(index: number): void {
    if (!(window as any).Plotly) { return }
    const trace = this._get_trace(index, true);
    (window as any).Plotly.restyle(this.el, trace, index)
  }

  _relayout(): void {
    if (!(window as any).Plotly) { return }
    (window as any).Plotly.relayout(this.el, this.model.layout)
  }

  // Python -> JavaScript messages
  do_addTraces(): void {
    let Plotly = (window as any).Plotly;
    let msgData = this.model._py2js_addTraces;

    if (!Plotly || !msgData) { return }

    Plotly.addTraces(this.el, msgData.trace_data)
  }

  do_restyle(): void {
    let Plotly = (window as any).Plotly;
    let msgData = this.model._py2js_restyle;

    if (!Plotly || !msgData) { return }

    let restyleData = msgData.restyle_data;
    let traceIndexes = this._normalize_trace_indexes(msgData.restyle_traces);

    Plotly.restyle(this.el, restyleData, traceIndexes);
  }

  do_relayout(): void {
    let Plotly = (window as any).Plotly;
    let msgData = this.model._py2js_relayout;

    if (!Plotly || !msgData) { return }

    Plotly.relayout(this.el, msgData.relayout_data);
  }

  do_update(): void {
    let Plotly = (window as any).Plotly;
    let msgData = this.model._py2js_update;

    if (!Plotly || !msgData) { return }

    let style = msgData.style_data || {};
    let layout = msgData.layout_data || {};
    let traceIndexes = this._normalize_trace_indexes(msgData.style_traces);

    Plotly.update(this.el, style, layout, traceIndexes);
  }

  do_animate(): void {
    let Plotly = (window as any).Plotly;
    let msgData = this.model._py2js_animate;

    if (!Plotly || !msgData) { return }

    let animationOpts = msgData.animation_opts;
    let styles = msgData.style_data;
    let layout = msgData.layout_data;
    let traceIndexes = this._normalize_trace_indexes(msgData.style_traces);
    let animationData = {
        data: styles,
        layout: layout,
        traces: traceIndexes
    };

    Plotly.animate(this.el, animationData, animationOpts)
  }

  do_deleteTraces(): void {
    let Plotly = (window as any).Plotly;
    let msgData = this.model._py2js_deleteTraces;

    if (!Plotly || !msgData) { return }

    let delete_inds = msgData.delete_inds;

    Plotly.deleteTraces(this.el, delete_inds)
  }

  do_moveTraces(): void {
    let Plotly = (window as any).Plotly;
    let msgData = this.model._py2js_moveTraces;

    if (!Plotly || !msgData) { return }

    let currentInds = msgData.current_trace_inds;
    let newInds = msgData.new_trace_inds;

    Plotly.moveTraces(this.el, currentInds, newInds)
  }
}

export namespace PlotlyPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any[]>
    layout: p.Property<any>
    config: p.Property<any>
    data_sources: p.Property<any[]>
    relayout_data: p.Property<any>
    restyle_data: p.Property<any>
    click_data: p.Property<any>
    hover_data: p.Property<any>
    clickannotation_data: p.Property<any>
    selected_data: p.Property<any>
    _py2js_addTraces: p.Property<any>
    _py2js_deleteTraces: p.Property<any>
    _py2js_moveTraces: p.Property<any>
    _py2js_restyle: p.Property<any>
    _py2js_relayout: p.Property<any>
    _py2js_update: p.Property<any>
    _py2js_animate: p.Property<any>
  }
}

export interface PlotlyPlot extends PlotlyPlot.Attrs {}

export class PlotlyPlot extends HTMLBox {
  properties: PlotlyPlot.Props

  constructor(attrs?: Partial<PlotlyPlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "PlotlyPlot"
    this.prototype.default_view = PlotlyPlotView

    this.define<PlotlyPlot.Props>({
      data: [ p.Array, [] ],
      layout: [ p.Any, {} ],
      config: [ p.Any, {} ],
      data_sources: [ p.Array, [] ],
      relayout_data: [ p.Any, {} ],
      restyle_data: [ p.Array, [] ],
      click_data: [ p.Any, {} ],
      hover_data: [ p.Any, {} ],
      clickannotation_data: [ p.Any, {} ],
      selected_data: [ p.Any, {} ],
      _py2js_addTraces: [ p.Any, {} ],
      _py2js_deleteTraces: [ p.Any, {} ],
      _py2js_moveTraces: [ p.Any, {} ],
      _py2js_restyle: [ p.Any, {} ],
      _py2js_relayout: [ p.Any, {} ],
      _py2js_update: [ p.Any, {} ],
      _py2js_animate: [ p.Any, {} ],
    })
  }
}
PlotlyPlot.initClass()
