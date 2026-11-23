import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {div} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import {isPlainObject} from "@bokehjs/core/util/types"
import {clone} from "@bokehjs/core/util/object"
import {is_equal} from "@bokehjs/core/util/eq"
import type {Attrs} from "@bokehjs/core/types"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"

import {debounce} from  "debounce"

import {HTMLBox, HTMLBoxView, set_size} from "./layout"
import {convertUndefined, deepCopy, get, reshape, throttle} from "./util"

import plotly_css from "styles/models/plotly.css"

const FORBIDDEN_KEYS = new Set(["__proto__", "prototype", "constructor"])

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null
}

function isSafePath(path: string[]): boolean {
  return path.every((part) => part.length > 0 && !FORBIDDEN_KEYS.has(part))
}

function getSafeParent(obj: unknown, path: string[]): Record<string, unknown> | null {
  let current: unknown = obj

  for (const key of path) {
    if (!isRecord(current) || FORBIDDEN_KEYS.has(key) || !Object.hasOwn(current, key)) {
      return null
    }
    current = current[key]
  }

  return isRecord(current) ? current : null
}

export class PlotlyEvent extends ModelEvent {
  constructor(readonly data: any) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }

  static {
    this.prototype.event_name = "plotly_event"
  }
}

interface PlotlyHTMLElement extends HTMLDivElement {
  _fullLayout: any
  _hoverdata: any
  layout: any
  on(event: "plotly_relayout", callback: (eventData: any) => void): void
  on(event: "plotly_relayouting", callback: (eventData: any) => void): void
  on(event: "plotly_restyle", callback: (eventData: any) => void): void
  on(event: "plotly_click", callback: (eventData: any) => void): void
  on(event: "plotly_doubleclick", callback: (eventData: any) => void): void
  on(event: "plotly_hover", callback: (eventData: any) => void): void
  on(event: "plotly_clickannotation", callback: (eventData: any) => void): void
  on(event: "plotly_selected", callback: (eventData: any) => void): void
  on(event: "plotly_deselect", callback: () => void): void
  on(event: "plotly_unhover", callback: () => void): void
}

const decodeUndefined = (obj: any): any => {
  if (obj === "_undefined_") {
    return undefined
  } else if (Array.isArray(obj)) {
    return obj.map(decodeUndefined)
  } else if (isPlainObject(obj)) {
    return Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, decodeUndefined(v)]))
  }
  return obj
}

type PlotlyUpdate = {[key: string]: unknown}

/**
 * A relayout, or a restyle of a single trace, sent before the plot rendered.
 * Applied in order once plotted, they leave the plot as it would be had they
 * been applied as they arrived.
 */
type PendingUpdate = {kind: "relayout", data: PlotlyUpdate} | {kind: "restyle", trace: number, data: PlotlyUpdate}

const is_descendant = (key: string, of: string): boolean => {
  return key.startsWith(`${of}.`) || key.startsWith(`${of}[`)
}

const parent_path = (key: string): string => {
  const index = Math.max(key.lastIndexOf("."), key.lastIndexOf("["))
  return index < 0 ? "" : key.slice(0, index)
}

/**
 * The array an item-level key such as `annotations[0]` writes to. Plotly
 * treats such a write as an insert (or, with null, a removal) that shifts
 * the items after it, so it is never superseded and orders later writes.
 */
const item_array = (key: string): string | null => {
  return key.endsWith("]") ? key.slice(0, key.lastIndexOf("[")) : null
}

const within = (key: string, path: string): boolean => key == path || is_descendant(key, path)

/**
 * Whether `key` must be applied after `other` rather than together with it:
 * keys under a written ancestor, keys next to a sibling such as
 * `xaxis.range` and `xaxis.autorange` that Plotly resolves together, and
 * keys in an array that an item-level write shifts.
 */
const conflicts = (key: string, other: string): boolean => {
  if (is_descendant(key, other) || is_descendant(other, key)) {
    return true
  }
  const key_array = item_array(key)
  const other_array = item_array(other)
  if ((key_array != null && within(other, key_array)) || (other_array != null && within(key, other_array))) {
    return true
  }
  const parent = parent_path(key)
  return parent !== "" && parent === parent_path(other)
}

/**
 * Adds an update to the queue, dropping earlier writes it supersedes (the
 * same key or a descendant, up to an item-level write that shifted them)
 * and merging it into the last entry when that entry is of the same kind
 * and target and none of its keys conflict. Apart from item-level writes,
 * every key is then pending at most once, which bounds the queue.
 */
export function queue_update(queue: PendingUpdate[], update: PendingUpdate): PendingUpdate[] {
  const keys = Object.keys(update.data)
  const same_target = (entry: PendingUpdate) => {
    return entry.kind == update.kind && (entry.kind == "relayout" || entry.trace == (update as any).trace)
  }
  for (const k of keys) {
    if (item_array(k) != null) {
      continue
    }
    for (let i = queue.length - 1; i >= 0; i--) {
      const entry = queue[i]
      if (!same_target(entry)) {
        continue
      }
      const entry_keys = Object.keys(entry.data)
      if (entry_keys.some((key) => {
        const array = item_array(key)
        return array != null && is_descendant(k, array)
      })) {
        break
      }
      for (const key of entry_keys) {
        if (within(key, k)) {
          delete entry.data[key]
        }
      }
    }
  }
  const pending = queue.filter((entry) => Object.keys(entry.data).length > 0)
  const last = pending.at(-1)
  if (last != null && same_target(last) && !Object.keys(last.data).some((key) => keys.some((k) => conflicts(k, key)))) {
    Object.assign(last.data, update.data)
  } else {
    pending.push({...update, data: {...update.data}})
  }
  return pending
}

const filterEventData = (gd: any, eventData: any, event: string) => {
  // Ported from dash-core-components/src/components/Graph.react.js
  const filteredEventData: {[k: string]: any} = Array.isArray(eventData)? []: {}

  if (event === "click" || event === "hover" || event === "selected") {
    const points = []

    if (eventData === undefined || eventData === null) {
      return null
    }

    const event_obj = eventData.event
    if (event_obj !== undefined) {
      filteredEventData.device_state = {
        // Keyboard modifiers
        alt: event_obj.altKey,
        ctrl: event_obj.ctrlKey,
        meta: event_obj.metaKey,
        shift: event_obj.shiftKey,
        // Mouse buttons
        button: event_obj.button,
        buttons: event_obj.buttons,
      }
    }

    let selectorObject
    if (eventData.hasOwnProperty("range")) {
      // Box selection
      selectorObject = {
        type: "box",
        selector_state: {
          xrange: eventData.range.x,
          yrange: eventData.range.y,
        },
      }
    } else if (eventData.hasOwnProperty("lassoPoints")) {
      // Lasso selection
      selectorObject = {
        type: "lasso",
        selector_state: {
          xs: eventData.lassoPoints.x,
          ys: eventData.lassoPoints.y,
        },
      }
    } else {
      selectorObject = null
    }
    filteredEventData.selector = selectorObject

    /*
     * remove `data`, `layout`, `xaxis`, etc
     * objects from the event data since they're so big
     * and cause JSON stringify circular structure errors.
     *
     * also, pull down the `customdata` point from the data array
     * into the event object
     */
    const data = gd.data

    for (let i = 0; i < eventData.points.length; i++) {
      const fullPoint = eventData.points[i]

      const pointData: {[k: string]: any} = {}
      for (const property in fullPoint) {
        const val = fullPoint[property]
        // Arrays of primitives (e.g. multicategory x, heatmap pointNumber)
        // are safe; arrays holding objects may be circular or huge.
        const isPrimitiveArray = Array.isArray(val) &&
          val.every((v: any) => v === null || typeof v !== "object")
        if (fullPoint.hasOwnProperty(property) &&
            (isPrimitiveArray || (!Array.isArray(val) && !isPlainObject(val))) &&
            val !== undefined)  {
          pointData[property] = val
        }
      }

      if (fullPoint !== undefined && fullPoint !== null) {
        if (fullPoint.hasOwnProperty("curveNumber") &&
           fullPoint.hasOwnProperty("pointNumber") &&
           data[fullPoint.curveNumber].hasOwnProperty("customdata")) {

          pointData.customdata =
            data[fullPoint.curveNumber].customdata[
              fullPoint.pointNumber
            ]
        }

        // specific to histogram. see https://github.com/plotly/plotly.js/pull/2113/
        if (fullPoint.hasOwnProperty("pointNumbers")) {
          pointData.pointNumbers = fullPoint.pointNumbers
        }
      }

      points[i] = pointData
    }
    filteredEventData.points = points
  } else if (event === "relayout" || event === "restyle") {
    /*
     * relayout shouldn't include any big objects
     * it will usually just contain the ranges of the axes like
     * "xaxis.range[0]": 0.7715822247381828,
     * "xaxis.range[1]": 3.0095292008680063`
     */
    for (const property in eventData) {
      if (eventData.hasOwnProperty(property))  {
        filteredEventData[property] = eventData[property]
      }
    }
  }
  if (eventData.hasOwnProperty("range")) {
    filteredEventData.range = eventData.range
  }
  if (eventData.hasOwnProperty("lassoPoints")) {
    filteredEventData.lassoPoints = eventData.lassoPoints
  }
  return convertUndefined(filteredEventData)
}

const _isHidden = (gd: any) => {
  const display = window.getComputedStyle(gd).display
  return !display || display === "none"
}

export class PlotlyPlotView extends HTMLBoxView {
  declare model: PlotlyPlot

  _setViewport: Function
  _settingViewport: boolean = false
  _plotInitialized: boolean = false
  _rendered: boolean = false
  _reacting: boolean = false
  _relayouting: boolean = false
  _model_restyles: number = 0
  _pending_updates: PendingUpdate[] = []
  _hoverdata: any = null
  container: PlotlyHTMLElement
  _end_relayouting = debounce(() => {
    this._relayouting = false
  }, 2000, false)
  _throttled_resize: any
  // Frames handed to Plotly for the current plot
  _frames: any[] | null = null
  _plot_promise: Promise<void> | null = null
  _plot_scheduled: boolean = false
  _new_plot: boolean = false

  override initialize(): void {
    super.initialize()
    this._throttled_resize = throttle(() => this.resize_layout(), 25)
  }

  override connect_signals(): void {
    super.connect_signals()

    const {
      data, data_sources, layout, relayout, restyle, viewport_update_policy,
      viewport_update_throttle, _render_count, frames, viewport,
    } = this.model.properties

    this.on_change([data, data_sources, layout, _render_count], () => {
      // The new state already includes any update sent before render
      this._pending_updates = []
      this._schedule_plot()
    })
    this.on_change(frames, () => {
      this._schedule_plot(true)
    })
    this.on_change(relayout, () => {
      const {relayout} = this.model
      if (relayout == null) {
        return
      }
      this.model.relayout = null
      if (this.container == null) {
        this._pending_updates = queue_update(this._pending_updates, {kind: "relayout", data: relayout})
      } else {
        (window as any).Plotly.relayout(this.container, relayout)
      }
    })
    this.on_change(restyle, () => {
      const {restyle} = this.model
      if (restyle == null) {
        return
      }
      this.model.restyle = null
      const data = decodeUndefined(restyle.data)
      if (this.container == null) {
        this._queue_restyle(data, restyle.traces)
      } else {
        this._restyle(data, restyle.traces)
      }
    })

    this.on_change(viewport_update_policy, () => {
      this._updateSetViewportFunction()
    })
    this.on_change(viewport_update_throttle, () => {
      this._updateSetViewportFunction()
    })
    this.on_change(viewport, () => {
      this._updateViewportFromProperty()
    })
  }

  /**
   * Plots once all changes applied in the current task have been
   * processed, waiting for a plot in progress to finish first.
   */
  _schedule_plot(new_plot: boolean = false): void {
    this._new_plot ||= new_plot
    if (this._plot_scheduled) {
      return
    }
    this._plot_scheduled = true
    const run = () => {
      this._plot_scheduled = false
      const replot = this._new_plot
      this._new_plot = false
      this._plot_promise = this.plot(replot)
    }
    (this._plot_promise ?? Promise.resolve()).then(run, run)
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), plotly_css]
  }

  override remove(): void {
    if (this.container != null) {
      (window as any).Plotly.purge(this.container)
    }
    super.remove()
  }

  override render(): void {
    super.render()
    this.container = div() as PlotlyHTMLElement
    set_size(this.container, this.model)
    this._rendered = false
    this.watch_stylesheets()
    this._plot_promise = this.plot(true).then(() => {
      this.shadow_el.appendChild(this.container)
      this._rendered = true
      this.resize_layout()
      if (this.model.relayout != null) {
        (window as any).Plotly.relayout(this.container, this.model.relayout)
        this.model.relayout = null
      }
      return this._apply_pending_updates()
    })
  }

  _restyle(data: PlotlyUpdate, traces: number | number[] | null): Promise<unknown> {
    this._model_restyles += 1
    return (window as any).Plotly.restyle(this.container, data, traces).finally(() => {
      this._model_restyles -= 1
    })
  }

  /**
   * Splits a restyle into one update per trace, resolving values the way
   * Plotly does: arrays are indexed (and wrapped) by position in `traces`,
   * and undefined values leave the trace unchanged.
   */
  _queue_restyle(data: PlotlyUpdate, traces: number | number[] | null): void {
    const ntraces = this.model.data.length
    const indices = traces == null ? [...Array(ntraces).keys()] : Array.isArray(traces) ? traces : [traces]
    indices.forEach((trace, position) => {
      // Plotly ignores negative trace indices
      if (trace < 0) {
        return
      }
      const update: PlotlyUpdate = {}
      for (const [key, value] of Object.entries(data)) {
        const trace_value = Array.isArray(value) ? value[position % value.length] : value
        if (trace_value !== undefined) {
          update[key] = trace_value
        }
      }
      if (Object.keys(update).length > 0) {
        this._pending_updates = queue_update(this._pending_updates, {kind: "restyle", trace, data: update})
      }
    })
  }

  async _apply_pending_updates(): Promise<void> {
    const pending = this._pending_updates
    this._pending_updates = []
    let i = 0
    while (i < pending.length) {
      const entry = pending[i]
      if (entry.kind == "relayout") {
        await (window as any).Plotly.relayout(this.container, entry.data)
        i++
        continue
      }
      // Consecutive restyles of the same keys on different traces go in one call
      const keys = Object.keys(entry.data).join("\0")
      const batch = [entry]
      while (i + batch.length < pending.length) {
        const next = pending[i + batch.length]
        if (next.kind != "restyle" || Object.keys(next.data).join("\0") != keys || batch.some((e) => e.trace == next.trace)) {
          break
        }
        batch.push(next)
      }
      const data = Object.fromEntries(Object.keys(entry.data).map((key) => [key, batch.map((e) => e.data[key])]))
      await this._restyle(data, batch.map((e) => e.trace))
      i += batch.length
    }
  }

  /**
   * The plot size derived from the model and the element, or null while
   * the element is not laid out.
   */
  _plot_size(): [number, number] | null {
    const width = Math.min(this.model.width || this.el.clientWidth, this.model.max_width || Infinity)
    const height = Math.min(this.model.height || this.el.clientHeight, this.model.max_height || Infinity)
    return width > 0 && height > 0 ? [width, height] : null
  }

  override style_redraw(): void {
    this.resize_layout()
  }

  resize_layout(): void {
    if (!this._rendered || this.container == null) {
      return
    }
    const width: number = Math.min(this.model.width || this.el.clientWidth, this.model.max_width || Infinity)
    const height: number = Math.min(this.model.height || this.el.clientHeight, this.model.max_height || Infinity)
    // A relayout resets the hover state, dropping clicks right after it
    const {layout} = this.container
    if (layout != null && layout.width === width && layout.height === height) {
      return
    }
    (window as any).Plotly.relayout(this.container, {width, height})
  }

  override after_layout(): void {
    super.after_layout()
    this._throttled_resize()
  }

  _trace_data(): any {
    const data = []
    for (let i = 0; i < this.model.data.length; i++) {
      data.push(this._get_trace(i, false))
    }
    return data
  }

  _layout_data(): any {
    const newLayout = deepCopy(this.model.layout)
    if (this._relayouting) {
      const {layout} = this.container

      // For each xaxis* and yaxis* property of layout, if the value has a 'range'
      // property then use this in newLayout
      Object.keys(layout).reduce((value: any, key: string) => {
        if (key.slice(1, 5) === "axis" && "range" in value) {
          newLayout[key].range = value.range
        }
      }, {})
    }
    // Sizing the plot up front saves the relayout resize_layout would
    // otherwise issue after every update.
    const size = this._rendered ? this._plot_size() : null
    if (size != null) {
      newLayout.width ??= size[0]
      newLayout.height ??= size[1]
    }
    return newLayout
  }

  _install_callbacks(): void {
    //  - plotly_relayout
    this.container.on("plotly_relayout", (eventData: any) => {
      if (eventData._update_from_property !== true) {
        this.model.relayout_data = filterEventData(
          this.container, eventData, "relayout")

        this._updateViewportProperty()

        this._end_relayouting()
      }
    })

    //  - plotly_relayouting
    this.container.on("plotly_relayouting", () => {
      if (this.model.viewport_update_policy !== "mouseup") {
        this._relayouting = true
        this._updateViewportProperty()
      }
    })

    //  - plotly_restyle
    this.container.on("plotly_restyle", (eventData: any) => {
      // Echoing a restyle sent by Python could arrive after a newer update and revert it
      if (this._model_restyles > 0) {
        return
      }
      this.model.restyle_data = filterEventData(
        this.container, eventData, "restyle")

      this._updateViewportProperty()
    })

    //  - plotly_click
    this.container.on("plotly_click", (eventData: any) => {
      const data = filterEventData(this.container, eventData, "click")
      this.model.trigger_event(new PlotlyEvent({type: "click", data}))
    })

    //  - plotly_doubleclick
    this.container.on("plotly_doubleclick", (eventData: any) => {
      const data = filterEventData(this.container, eventData, "click")
      this.model.trigger_event(new PlotlyEvent({type: "doubleclick", data}))
    })

    //  - plotly_hover
    this.container.on("plotly_hover", (eventData: any) => {
      const data = filterEventData(this.container, eventData, "hover")
      this.model.trigger_event(new PlotlyEvent({type: "hover", data}))
      // Override hoverdata to ensure click event has context
      // see https://github.com/holoviz/panel/pull/6753
      this._hoverdata = this.container._hoverdata = eventData.points
    })

    //  - plotly_selected
    this.container.on("plotly_selected", (eventData: any) => {
      if (eventData === undefined || eventData === null) {
        // filter out the empty events that come from single-click
        return
      }
      const data = filterEventData(this.container, eventData, "selected")
      this.model.trigger_event(new PlotlyEvent({type: "selected", data}))
    })

    //  - plotly_clickannotation
    this.container.on("plotly_clickannotation", (eventData: any) => {
      delete eventData.event
      delete eventData.fullAnnotation
      this.model.trigger_event(new PlotlyEvent({type: "clickannotation", data: eventData}))
    })

    //  - plotly_deselect
    this.container.on("plotly_deselect", () => {
      this.model.trigger_event(new PlotlyEvent({type: "selected", data: null}))
    })

    //  - plotly_unhover
    this.container.on("plotly_unhover", () => {
      this.model.trigger_event(new PlotlyEvent({type: "hover", data: null}))
      // Plotly already stored the new point when moving straight to it
      if (this.container._hoverdata != null) {
        return
      }
      // Override hoverdata to ensure click event has context
      const hoverdata = this.container._hoverdata = this._hoverdata
      setTimeout(() => {
        // Remove hoverdata once events have been processed
        if (this.container._hoverdata === hoverdata) {
          delete this.container._hoverdata
        }
      }, 0)
    })
  }

  async plot(new_plot: boolean=false): Promise<void> {
    if (!(window as any).Plotly || !this.container) {
      return
    }
    const data = this._trace_data()
    const newLayout = this._layout_data()
    const {config, frames} = this.model
    this._reacting = true
    try {
      if (new_plot || !this._plotInitialized) {
        await (window as any).Plotly.newPlot(this.container, {data, layout: newLayout, config, frames})
      } else if (frames !== this._frames) {
        // Passing frames makes react replace the existing ones
        await (window as any).Plotly.react(this.container, {data, layout: newLayout, config, frames})
      } else {
        await (window as any).Plotly.react(this.container, data, newLayout, config)
      }
      this._frames = frames
      this._updateSetViewportFunction()
      this._updateViewportProperty()
      if (!this._plotInitialized) {
        this._install_callbacks()
      } else if (!_isHidden(this.container)) {
        this.resize_layout()
      }
    } finally {
      this._reacting = false
    }
    this._plotInitialized = true
  }

  _get_trace(index: number, update: boolean): any {
    const trace = clone(this.model.data[index]) as any
    const cds = this.model.data_sources[index]
    for (const column of cds.columns()) {
      let array = cds.get_array(column)[0]
      if (array.shape != null && array.shape.length > 1) {
        array = reshape(array, array.shape)
      }

      // Column name used for resolving object data needs to be validated
      // to avoid prototype pollution
      const propPath = column.split(".")
      const prop = propPath[propPath.length - 1]
      const propParent = getSafeParent(trace, propPath.slice(0, -1))
      if (!propParent || !prop || !isSafePath(propPath) || FORBIDDEN_KEYS.has(prop)) {
        console.warn("Attempted prototype pollution detected via Plotly column resolution.")
        continue
      }

      if (update && propPath.length == 1) {
        propParent[prop] = [array]
      } else {
        propParent[prop] = array
      }
    }
    return trace
  }

  _updateViewportFromProperty(): void {
    if (!(window as any).Plotly || this._settingViewport || this._reacting || !this.model.viewport) {
      return
    }

    const fullLayout = this.container._fullLayout

    // Call relayout if viewport differs from fullLayout
    Object.keys(this.model.viewport).reduce((value: any, key: string) => {
      if (!is_equal(get(fullLayout, key), value)) {
        const clonedViewport = deepCopy(this.model.viewport)
        clonedViewport._update_from_property = true
        this._settingViewport = true;
        (window as any).Plotly.relayout(this.el, clonedViewport).then(() => {
          this._settingViewport = false
        })
        return false
      } else {
        return true
      }
    }, {})
  }

  _updateViewportProperty(): void {
    const fullLayout = this.container._fullLayout
    const viewport: any = {}

    // Get range for all xaxis and yaxis properties
    for (const prop in fullLayout) {
      if (!fullLayout.hasOwnProperty(prop)) {
        continue
      }
      const maybe_axis = prop.slice(0, 5)
      if (maybe_axis === "xaxis" || maybe_axis === "yaxis") {
        viewport[`${prop  }.range`] = deepCopy(fullLayout[prop].range)
      }
    }

    if (!is_equal(viewport, this.model.viewport)) {
      this._setViewport(viewport)
    }
  }

  _updateSetViewportFunction(): void {
    if (this.model.viewport_update_policy === "continuous" ||
        this.model.viewport_update_policy === "mouseup") {
      this._setViewport = (viewport: any) => {
        if (!this._settingViewport) {
          this._settingViewport = true
          this.model.viewport = viewport
          this._settingViewport = false
        }
      }
    } else {
      this._setViewport = throttle((viewport: any) => {
        if (!this._settingViewport) {
          this._settingViewport = true
          this.model.viewport = viewport
          this._settingViewport = false
        }
      }, this.model.viewport_update_throttle)
    }
  }
}

export namespace PlotlyPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any[]>
    frames: p.Property<any[] | null>
    layout: p.Property<any>
    config: p.Property<any>
    data_sources: p.Property<any[]>
    relayout: p.Property<any>
    restyle: p.Property<any>
    relayout_data: p.Property<any>
    restyle_data: p.Property<any>
    viewport: p.Property<any>
    viewport_update_policy: p.Property<string>
    viewport_update_throttle: p.Property<number>
    _render_count: p.Property<number>
  }
}

export interface PlotlyPlot extends PlotlyPlot.Attrs {}

export class PlotlyPlot extends HTMLBox {
  declare properties: PlotlyPlot.Props

  constructor(attrs?: Partial<PlotlyPlot.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.plotly"

  static {
    this.prototype.default_view = PlotlyPlotView

    this.define<PlotlyPlot.Props>(({List, Any, Nullable, Float, Ref, Str}) => ({
      data: [ List(Any), [] ],
      layout: [ Any, {} ],
      config: [ Any, {} ],
      frames: [ Nullable(List(Any)), null ],
      data_sources: [ List(Ref(ColumnDataSource)), [] ],
      relayout: [ Nullable(Any), {} ],
      restyle: [ Nullable(Any), {} ],
      relayout_data: [ Any, {} ],
      restyle_data: [ List(Any), [] ],
      viewport: [ Any, {} ],
      viewport_update_policy: [ Str, "mouseup" ],
      viewport_update_throttle: [ Float, 200 ],
      _render_count: [ Float, 0 ],
    }))
  }
}
