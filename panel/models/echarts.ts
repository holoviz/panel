import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {div} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import type {Attrs} from "@bokehjs/core/types"

import {serializeEvent} from "./event-to-object"
import {HTMLBox, HTMLBoxView} from "./layout"
import {transformJsPlaceholders} from "./util"

const mouse_events = [
  "click", "dblclick", "mousedown", "mousemove", "mouseup", "mouseover", "mouseout",
  "globalout", "contextmenu",
]

const events = [
  "highlight", "downplay", "selectchanged", "legendselectchangedEvent", "legendselected",
  "legendunselected", "legendselectall", "legendinverseselect", "legendscroll", "datazoom",
  "datarangeselected", "timelineplaychanged", "restore", "dataviewchanged", "magictypechanged",
  "geoselectchanged", "geoselected", "geounselected", "axisareaselected", "brush", "brushEnd",
  "rushselected", "globalcursortaken", "rendered", "finished",
]

const all_events = mouse_events.concat(events)

const ECHARTS_MAP_CDN = "https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/json/{name}.json"
const _geojson_cache: Map<string, Promise<unknown>> = new Map()

function fetch_geojson(url: string): Promise<unknown> {
  let p = _geojson_cache.get(url)
  if (p == null) {
    p = fetch(url).then((r) => {
      if (!r.ok) {
        throw new Error(`HTTP ${r.status}`)
      }
      return r.json()
    })
    _geojson_cache.set(url, p)
  }
  return p
}

function collect_map_names(data: any): Set<string> {
  const names = new Set<string>()
  const geo = data?.geo
  if (geo != null) {
    const arr = Array.isArray(geo) ? geo : [geo]
    for (const g of arr) {
      if (g?.map) { names.add(g.map) }
    }
  }
  for (const s of (data?.series ?? [])) {
    if (s?.type === "map" && s?.map) { names.add(s.map) }
  }
  return names
}

export class EChartsEvent extends ModelEvent {
  constructor(readonly type: string, readonly data: any, readonly query: string) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, type: this.type, data: this.data, query: this.query}
  }

  static {
    this.prototype.event_name = "echarts_event"
  }
}

export class EChartsView extends HTMLBoxView {
  declare model: ECharts

  container: Element
  _chart: any
  _callbacks: Array<any>[] = []

  override connect_signals(): void {
    super.connect_signals()
    const {width, height, renderer, theme, event_config, js_events, data, geo_data} = this.model.properties
    this.on_change([data, geo_data], () => this._plot())
    this.on_change([width, height], () => this._resize())
    this.on_change([theme, renderer], () => {
      this.render()
      this._chart.resize()
    })
    this.on_change([event_config, js_events], () => this._subscribe())
  }

  override render(): void {
    if (this._chart != null) {
      try {
        (window as any).echarts.dispose(this._chart)
      } catch (e) {}
    }
    super.render()
    this.container = div({style: {height: "100%", width: "100%"}})
    const config = {width: this.model.width, height: this.model.height, renderer: this.model.renderer}
    this._chart = (window as any).echarts.init(
      this.container,
      this.model.theme,
      config,
    )
    this._plot()
    this._subscribe()
    this.shadow_el.append(this.container)
  }

  override remove(): void {
    super.remove()
    if (this._chart != null) {
      (window as any).echarts.dispose(this._chart)
    }
  }

  override after_layout(): void {
    super.after_layout()
    if (this._chart != null) {
      this._chart.resize()
    }
  }

  async _register_maps(): Promise<void> {
    const echarts = (window as any).echarts
    if (echarts == null) {
      return
    }
    const geo_data = this.model.geo_data ?? {}
    const tasks: Promise<unknown>[] = []
    for (const [name, value] of Object.entries(geo_data)) {
      if (typeof value === "string") {
        tasks.push(
          fetch_geojson(value)
            .then((json) => echarts.registerMap(name, json as any))
            .catch((e) => console.warn(
              `ECharts: failed to fetch GeoJSON for map '${name}' from ${value}: ${e}`,
            )),
        )
      } else {
        echarts.registerMap(name, value as any)
      }
    }
    const referenced = collect_map_names(this.model.data)
    for (const name of referenced) {
      if (name in geo_data) {
        continue
      }
      const url = ECHARTS_MAP_CDN.replace("{name}", name)
      tasks.push(
        fetch_geojson(url)
          .then((json) => echarts.registerMap(name, json as any))
          .catch((e) => console.warn(
            `ECharts config references map '${name}' but no GeoJSON ` +
            `was provided and auto-fetch from ${url} failed: ${e}. ` +
            `Pass geo_data={'${name}': geojson_dict} to register map data manually.`,
          )),
      )
    }
    if (tasks.length > 0) {
      await Promise.all(tasks)
    }
  }

  async _plot(): Promise<void> {
    if ((window as any).echarts == null) {
      return
    }
    await this._register_maps()
    const data = transformJsPlaceholders(this.model.data)
    this._chart.setOption(data, this.model.options)
  }

  _resize(): void {
    this._chart.resize({width: this.model.width, height: this.model.height})
  }

  _subscribe(): void {
    if ((window as any).echarts == null) {
      return
    }
    for (const [event_type, callback] of this._callbacks) {
      this._chart.off(event_type, callback)
    }
    this._callbacks = []
    for (const event_type in this.model.event_config) {
      if (!all_events.includes(event_type)) {
        console.warn(`Could not subscribe to unknown Echarts event: ${event_type}.`)
        continue
      }
      const queries = this.model.event_config[event_type]
      for (const query of queries) {
        const callback = (event: any) => {
          const processed = {...event}
          processed.event = serializeEvent(event.event?.event)
          const serialized = JSON.parse(JSON.stringify(processed))
          this.model.trigger_event(new EChartsEvent(event_type, serialized, query))
        }
        if (query != null) {
          this._chart.on(event_type, query, callback)
        } else {
          this._chart.on(event_type, callback)
        }
        this._callbacks.push([event_type, callback])
      }
    }
    for (const event_type in this.model.js_events) {
      if (!all_events.includes(event_type)) {
        console.warn(`Could not subscribe to unknown Echarts event: ${event_type}.`)
        continue
      }
      const handlers = this.model.js_events[event_type]
      for (const handler of handlers) {
        const callback = (event: any) => {
          handler.callback.execute(this._chart, event)
        }
        if ("query" in handler) {
          this._chart.on(event_type, handler.query, callback)
        } else {
          this._chart.on(event_type, callback)
        }
        this._callbacks.push([event_type, callback])
      }
    }
  }
}

export namespace ECharts {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    geo_data: p.Property<any>
    options: p.Property<any>
    event_config: p.Property<any>
    js_events: p.Property<any>
    renderer: p.Property<string>
    theme: p.Property<string>
  }
}

export interface ECharts extends ECharts.Attrs {}

export class ECharts extends HTMLBox {
  declare properties: ECharts.Props

  constructor(attrs?: Partial<ECharts.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.echarts"

  static {
    this.prototype.default_view = EChartsView

    this.define<ECharts.Props>(({Any, Str}) => ({
      data:          [ Any,           {} ],
      geo_data:      [ Any,           {} ],
      options:       [ Any,           {} ],
      event_config:  [ Any,           {} ],
      js_events:     [ Any,           {} ],
      theme:         [ Str,  "default"],
      renderer:      [ Str,   "canvas"],
    }))
  }
}
