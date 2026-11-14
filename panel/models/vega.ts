import {div} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {isArray} from "@bokehjs/core/util/types"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"
import type {Attrs} from "@bokehjs/core/types"
import type {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"

import {set_size} from "./layout"
import type {ResourceSpec} from "./resources"
import {
  await_resources, define_external_resources, load_resources,
  render_resource_error,
} from "./resources"

import {debounce} from  "debounce"

export class VegaEvent extends ModelEvent {
  constructor(readonly data: any) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }

  static {
    this.prototype.event_name = "vega_event"
  }
}

export class VegaPlotView extends LayoutDOMView {
  declare model: VegaPlot

  vega_view: any
  container: HTMLDivElement
  _connected: Set<ColumnDataSource> = new Set()
  _listeners: Set<string> = new Set()
  _dirty_sources: Set<string> = new Set()
  _data_update: Promise<void> | null = null
  _replot: any
  _replot_pending: boolean = false
  _embed_id: number = 0
  _resize: any
  _rendered: boolean = false

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()
    const error = await await_resources(this.model)
    if (error != null) {
      render_resource_error(this, error, LayoutDOMView.prototype.render)
    }
  }

  override connect_signals(): void {
    super.connect_signals()
    const {data, show_actions, theme, data_sources, events} = this.model.properties
    this._replot = debounce(() => this._plot(), 20)
    this.on_change([data, show_actions, theme], () => {
      this._replot_pending = true
      this._replot()
    })
    this.on_change(data_sources, () => this._connect_sources())
    this.on_change(events, () => this._add_listeners())
    this._connect_sources()
  }

  _connect_sources(): void {
    for (const name in this.model.data_sources) {
      const cds = this.model.data_sources[name]
      if (!this._connected.has(cds)) {
        this.connect(cds.properties.data.change, () => this._source_changed(name))
        this._connected.add(cds)
      }
    }
  }

  /**
   * Pushes changed datasets into the existing Vega View rather than
   * recompiling the spec, coalescing changes made in the same patch.
   */
  _source_changed(name: string): void {
    this._dirty_sources.add(name)
    if (this._data_update == null) {
      this._data_update = Promise.resolve().then(() => {
        this._data_update = null
        this._update_data()
      })
    }
  }

  _update_data(): void {
    if (this._dirty_sources.size === 0 || this._replot_pending) {
      this._dirty_sources.clear()
      return
    }
    const view = this.vega_view
    if (view == null) {
      // Applied once the embed in flight resolves, or fetched by render()
      return
    }
    const names = [...this._dirty_sources]
    this._dirty_sources.clear()
    for (const name of names) {
      const cds = this.model.data_sources[name]
      if (cds == null) {
        continue
      }
      const values = this._fetch_dataset(cds)
      const dataset = this._store_values(name, values)
      try {
        view.data(dataset, values)
      } catch {
        // The dataset is not part of the compiled dataflow (e.g. the spec
        // was restructured), so fall back to re-embedding the spec.
        this._replot_pending = true
        this._replot()
        return
      }
    }
    view.runAsync()
  }

  override remove(): void {
    // Also discards the result of an embed still in flight
    this._embed_id++
    this.vega_view?.finalize()
    this.vega_view = null
    super.remove()
  }

  _dispatch_event(name: string, value: any): void {
    if ("vlPoint" in value && value.vlPoint.or != null) {
      const indexes = []
      for (const index of value.vlPoint.or) {
        if (index._vgsid_ !== undefined) {  // If "_vgsid_" property exists
          indexes.push(index._vgsid_)
        } else {  // If "_vgsid_" property doesn't exist
          // Iterate through all properties in the "index" object
          for (const key in index) {
            if (index.hasOwnProperty(key)) {  // To ensure key comes from "index" object itself, not its prototype
              indexes.push({[key]: index[key]})  // Push a new object with this key-value pair into the array
            }
          }
        }
      }
      value = indexes
    }
    this.model.trigger_event(new VegaEvent({type: name, value}))
  }

  _fetch_dataset(cds: any): any[] {
    const data: any = []
    const columns = cds.columns()
    for (let i = 0; i < cds.get_length(); i++) {
      const item: any = {}
      for (const column of columns) {
        item[column] = cds.data[column][i]
      }
      data.push(item)
    }
    return data
  }

  /**
   * Writes the values of a data source into the spec, returning the name
   * of the dataset they end up in once the spec is compiled by Vega.
   */
  _store_values(name: string, values: any[]): string {
    const {data} = this.model
    if (name === "data" && data.data != null && !isArray(data.data)) {
      data.data.values = values
      return data.data.name ?? "source_0"
    }
    if (data.data != null) {
      const data_objs = isArray(data.data) ? data.data : [data.data]
      for (const d of data_objs) {
        if (d.name === name) {
          d.values = values
          return name
        }
      }
    }
    data.datasets = data.datasets ?? {}
    data.datasets[name] = values
    return name
  }

  get child_models(): LayoutDOM[] {
    return []
  }

  override render(): void {
    super.render()
    this._rendered = false
    this.container = div()
    set_size(this.container, this.model)
    this._plot()
    this.shadow_el.append(this.container)
  }

  _plot(): void {
    this._replot_pending = false
    const data = this.model.data
    if ((data == null) || !(window as any).vegaEmbed) {
      return
    }
    for (const name in this.model.data_sources) {
      this._store_values(name, this._fetch_dataset(this.model.data_sources[name]))
    }
    this._dirty_sources.clear()
    const config: any = {actions: this.model.show_actions, theme: this.model.theme}

    // vegaEmbed replaces the container contents but leaves the previous
    // View (and its timers and listeners) running, so finalize it here.
    this.vega_view?.finalize()
    this.vega_view = null
    this._listeners.clear()
    const embed_id = ++this._embed_id;
    (window as any).vegaEmbed(this.container, this.model.data, config).then((result: any) => {
      if (embed_id !== this._embed_id) {
        result.view.finalize()
        return
      }
      this.vega_view = result.view
      this._resize = debounce(() => this.resize_view(result.view), 50)
      this._add_listeners()
      this._update_data()
    })
  }

  _add_listeners(): void {
    const view = this.vega_view
    if (view == null) {
      return
    }
    for (const event of this.model.events) {
      if (this._listeners.has(event)) {
        continue
      }
      this._listeners.add(event)
      const callback = (name: string, value: any) => this._dispatch_event(name, value)
      const timeout = this.model.throttle[event] || 20
      view.addSignalListener(event, debounce(callback, timeout, false))
    }
  }

  override after_layout(): void {
    super.after_layout()
    if (this.vega_view != null) {
      this._resize()
    }
  }

  resize_view(view: any): void {
    const canvas = view._renderer.canvas()
    if (!this._rendered && canvas !== null) {
      for (const listener of view._eventListeners) {
        if (listener.type === "resize") {
          listener.handler(new Event("resize"))
        }
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
    external_resources: p.Property<ResourceSpec | null>
  }
}

export interface VegaPlot extends VegaPlot.Attrs {}

export class VegaPlot extends LayoutDOM {
  declare properties: VegaPlot.Props

  constructor(attrs?: Partial<VegaPlot.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.vega"

  static {
    this.prototype.default_view = VegaPlotView

    this.define<VegaPlot.Props>(({Any, List, Bool, Nullable, Str}) => ({
      data:         [ Any,                {} ],
      data_sources: [ Any,                {} ],
      events:       [ List(Str),      [] ],
      show_actions: [ Bool,         false ],
      theme:        [ Nullable(Str), null ],
      throttle:     [ Any,                {} ],
    }))
    define_external_resources(this)
  }

  override initialize(): void {
    super.initialize()
    load_resources(this)
  }
}
