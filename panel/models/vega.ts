import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {isArray} from "@bokehjs/core/util/types"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"
import {Attrs} from "@bokehjs/core/types"

import {set_size} from "./layout"

import {debounce} from  "debounce"


export class VegaEvent extends ModelEvent {
  constructor(readonly data: any) {
    super()
  }

  protected get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }

  static {
    this.prototype.event_name = "vega_event"
  }
}

export class VegaPlotView extends LayoutDOMView {
  model: VegaPlot
  vega_view: any
  container: HTMLDivElement
  _callbacks: string[]
  _connected: string[]
  _replot: any
  _resize: any
  _rendered: boolean = false

  connect_signals(): void {
    super.connect_signals()
    const {data, show_actions, theme} = this.model.properties
    this._replot = debounce(() => this._plot(), 20)
    this.on_change([data, show_actions, theme], () => {
      this._replot()
    })
    this.connect(this.model.properties.data_sources.change, () => this._connect_sources())
    this.connect(this.model.properties.events.change, () => {
      for (const event of this.model.events) {
        if (this._callbacks.indexOf(event) > -1)
          continue
        this._callbacks.push(event)
        const callback = (name: string, value: any) => this._dispatch_event(name, value)
        const timeout = this.model.throttle[event] || 20
        this.vega_view.addSignalListener(event, debounce(callback, timeout, false))
      }
    })
    this._connected = []
    this._connect_sources()
  }

  _connect_sources(): void {
    for (const ds in this.model.data_sources) {
      const cds = this.model.data_sources[ds]
      if (this._connected.indexOf(ds) < 0) {
        this.connect(cds.properties.data.change, () => this._replot())
        this._connected.push(ds)
      }
    }
  }

  override remove(): void {
    if (this.vega_view) {
      this.vega_view.finalize()
    }
    super.remove()
  }

  _dispatch_event(name: string, value: any): void {
    if ('vlPoint' in value && value.vlPoint.or != null) {
      const indexes = []
      for (const index of value.vlPoint.or) {
        if (index._vgsid_ !== undefined) {  // If "_vgsid_" property exists
          indexes.push(index._vgsid_);
        } else {  // If "_vgsid_" property doesn't exist
          // Iterate through all properties in the "index" object
          for (const key in index) {
            if (index.hasOwnProperty(key)) {  // To ensure key comes from "index" object itself, not its prototype
              indexes.push({[key]: index[key]});  // Push a new object with this key-value pair into the array
            }
          }
        }
      }
      value = indexes
    }
    this.model.trigger_event(new VegaEvent({type: name, value: value}))
  }

  _fetch_datasets() {
    const datasets: any = {}
    for (const ds in this.model.data_sources) {
      const cds = this.model.data_sources[ds];
      const data: any = []
      const columns = cds.columns()
      for (let i = 0; i < cds.get_length(); i++) {
        const item: any = {}
        for (const column of columns) {
          item[column] = cds.data[column][i]
        }
        data.push(item)
      }
      datasets[ds] = data;
    }
    return datasets
  }

  get child_models(): LayoutDOM[] {
    return []
  }

  render(): void {
    super.render()
    this._rendered = false
    this.container = div()
    set_size(this.container, this.model)
    this._callbacks = []
    this._plot()
    this.shadow_el.append(this.container)
  }

  _plot(): void {
    const data = this.model.data
    if ((data == null) || !(window as any).vegaEmbed)
      return
    if (this.model.data_sources && (Object.keys(this.model.data_sources).length > 0)) {
      const datasets = this._fetch_datasets()
      if ('data' in datasets) {
        data.data['values'] = datasets['data']
        delete datasets['data']
      }
      if (data.data != null) {
        const data_objs = isArray(data.data) ? data.data : [data.data]
        for (const d of data_objs) {
          if (d.name in datasets) {
            d['values'] = datasets[d.name]
            delete datasets[d.name]
          }
        }
      }
      this.model.data['datasets'] = datasets
    }
    const config: any = {actions: this.model.show_actions, theme: this.model.theme};

    (window as any).vegaEmbed(this.container, this.model.data, config).then((result: any) => {
      this.vega_view = result.view
      this._resize = debounce(() => this.resize_view(result.view), 50)
      const callback = (name: string, value: any) => this._dispatch_event(name, value)
      for (const event of this.model.events) {
        this._callbacks.push(event)
        const timeout = this.model.throttle[event] || 20
        this.vega_view.addSignalListener(event, debounce(callback, timeout, false))
      }
    })
  }

  after_layout(): void {
    super.after_layout()
    if (this.vega_view != null) {
      this._resize()
    }
  }

  resize_view(view: any): void {
    const canvas = view._renderer.canvas()
    if (!this._rendered && canvas !== null) {
      for (const listener of view._eventListeners) {
	if (listener.type === 'resize')
	  listener.handler(new Event('resize'))
      }
      this._rendered = true
    }
  }
}

export namespace VegaPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = LayoutDOM.Props & {
    data: p.Property<any>
    data_sources: p.Property<any>
    events: p.Property<string[]>
    show_actions: p.Property<boolean>
    theme: p.Property<string | null>
    throttle: p.Property<any>
  }
}

export interface VegaPlot extends VegaPlot.Attrs {}

export class VegaPlot extends LayoutDOM {
  properties: VegaPlot.Props

  constructor(attrs?: Partial<VegaPlot.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.vega"

  static {
    this.prototype.default_view = VegaPlotView

    this.define<VegaPlot.Props>(({Any, Array, Boolean, Nullable, String}) => ({
      data:         [ Any,                {} ],
      data_sources: [ Any,                {} ],
      events:       [ Array(String),      [] ],
      show_actions: [ Boolean,         false ],
      theme:        [ Nullable(String), null ],
      throttle:     [ Any,                {} ]
    }))
  }
}
