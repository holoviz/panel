import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {isArray, isObject} from "@bokehjs/core/util/types"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {Attrs} from "@bokehjs/core/types"

import {debounce} from  "debounce"

import {HTMLBox, HTMLBoxView} from "./layout"


export class VizzuEvent extends ModelEvent {
  event_name: string = "vizzu_event"
  publish: boolean = true

  constructor(readonly data: any) {
    super()
  }

  protected get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }
}

const VECTORIZED_PROPERTIES = ['x', 'y', 'color', 'label', 'lightness', 'size', 'splittedBy', 'dividedBy']

export class VizzuChartView extends HTMLBoxView {
  container: HTMLDivElement
  model: VizzuChart
  update: string[] = []
  vizzu_view: any
  _animating: boolean = false

  connect_signals(): void {
    super.connect_signals()
    const update = debounce(() => {
      if (!this.valid_config) {
	console.warn('Vizzu config not valid given current data.')
	return
      } else if (!this.update.length || this._animating)
	return
      else {
	let change = {}
	for (const prop of this.update) {
	  if (prop === 'config')
	    change = {...change, config: this.config()}
	  else if (prop === 'data')
	    change = {...change, data: this.data()}
	  else
	    change = {...change, style: this.model.style}
	}
	this._animating = true
	this.vizzu_view.animate(change, this.model.duration+'ms').then(() => {
	  this._animating = false
	  if (this.update.length)
	    update()
	})
	this.update = []
      }
    }, 20)
    const update_prop = (prop: string) => {
      if (!this.update.includes(prop))
	this.update.push(prop)
      update()
    }
    this.connect(this.model.properties.config.change, () => update_prop('config'))
    this.connect(this.model.source.properties.data.change, () => update_prop('data'))
    this.connect(this.model.source.streaming, () => update_prop('data'))
    this.connect(this.model.source.patching, () => update_prop('data'))
    this.connect(this.model.properties.tooltip.change, () => {
      this.vizzu_view.feature('tooltip', this.model.tooltip)
    })
    this.connect(this.model.properties.style.change, () => update_prop('style'))
  }

  get valid_config(): boolean {
    const columns = this.model.source.columns()
    if ('channels' in this.model.config) {
      for (const col of Object.values(this.model.config.channels)) {
	if (isArray(col)) {
	  for (const c of col) {
	    if (col != null && !columns.includes(c as string))
	      return false
	  }
	} else if (isObject(col)) {
	  for (const prop of Object.keys(col)) {
	    for (const c of ((col as any)[prop] as string[])) {
	      if (col != null && !columns.includes(c as string))
		return false
	    }
	  }
	} else if (col != null && !columns.includes(col as string))
	  return false
      }
    } else {
      for (const prop of VECTORIZED_PROPERTIES) {
	if (prop in this.model.config && !columns.includes(this.model.config[prop]))
	  return false
      }
    }
    return true
  }

  private config(): any {
    let config = {...this.model.config}
    if ('channels' in config)
      config['channels'] = {...config.channels}
    if (config.preset != undefined)
      config = (window as any).Vizzu.presets[config.preset](config)
    return config
  }

  private data(): any {
    const series = []
    for (const column of this.model.columns) {
      let array = [...this.model.source.get_array(column.name)]
      if (column.type === 'datetime' || column.type == 'date')
	column.type = 'dimension'
      if (column.type === 'dimension')
	array = array.map(String)
      series.push({...column, values: array})
    }
    return {series}
  }

  render(): void {
    super.render()
    this.container = div({'style': 'display: contents;'})
    this.shadow_el.append(this.container)
    const state = {config: this.config(), data: this.data(), style: this.model.style}
    this.vizzu_view = new (window as any).Vizzu(this.container, state)
    this._animating = true
    this.vizzu_view.initializing.then((chart: any) => {
      chart.on('click', (event: any) => {
	this.model.trigger_event(new VizzuEvent(event.data))
      })
      chart.feature('tooltip', this.model.tooltip)
      this._animating = false
    })
  }

  override remove(): void {
    if (this.vizzu_view) {
      this.vizzu_view.detach()
    }
    super.remove()
  }
}

export namespace VizzuChart {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    animation: p.Property<any>
    config: p.Property<any>
    columns: p.Property<any>
    source: p.Property<ColumnDataSource>
    duration: p.Property<number>
    style: p.Property<any>
    tooltip: p.Property<boolean>
  }
}

export interface VizzuChart extends VizzuChart.Attrs {}

export class VizzuChart extends HTMLBox {
  properties: VizzuChart.Props

  constructor(attrs?: Partial<VizzuChart.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.vizzu"

  static {
    this.prototype.default_view = VizzuChartView

    this.define<VizzuChart.Props>(({Any, Array, Boolean, Number, Ref}) => ({
      animation:   [ Any,                     {} ],
      config:      [ Any,                     {} ],
      columns:     [ Array(Any),              [] ],
      source:      [ Ref(ColumnDataSource),      ],
      duration:    [ Number,                 500 ],
      style:       [ Any,                     {} ],
      tooltip:     [ Boolean,              false ],
    }))
  }
}
