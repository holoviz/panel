import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {isArray} from "@bokehjs/core/util/types"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {Attrs} from "@bokehjs/core/types"

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
  timeout: number
  model: VizzuChart
  vizzu_view: any
  last_updated: number
  update: any = {}

  connect_signals(): void {
    if (this.timeout)
      clearTimeout(this.timeout)
    super.connect_signals()
    const update = () => {
      const now = Date.now()
      const diff = now-this.last_updated
      if (!this.valid_config) {
	return
      } else if (diff < this.model.duration)
	setTimeout(update, diff)
      else {
	const update = {config: this.model.config, data: this.data(), style: this.model.style}
	this.vizzu_view.animate(update, this.model.duration+'ms')
	this.last_updated = now
      }
    }
    this.connect(this.model.properties.config.change, update)
    this.connect(this.model.source.properties.data.change, update)
    this.connect(this.model.source.streaming, update)
    this.connect(this.model.source.patching, update)
    this.connect(this.model.properties.style.change, update)
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

  private data(): any {
    const series = []
    for (const column of this.model.columns) {
      let array = [...this.model.source.get_array(column.name)]
      if (column.type === 'datetime' || column.type == 'date')
	column.type = 'measure'
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
    this.vizzu_view = new (window as any).Vizzu(this.container)
    this.vizzu_view.initializing.then((chart: any) => {
      chart.on('click', (event: any) => {
	this.model.trigger_event(new VizzuEvent(event.data))
      })
    })
    this.vizzu_view.animate({data: this.data()})
    this.vizzu_view.animate({config: this.model.config, style: this.model.style})
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

    this.define<VizzuChart.Props>(({Any, Array, Number, Ref}) => ({
      animation:   [ Any,                     {} ],
      config:      [ Any,                     {} ],
      columns:     [ Array(Any),              [] ],
      source:      [ Ref(ColumnDataSource),      ],
      duration:    [ Number,                 500 ],
      style:       [ Any,                     {} ],
    }))
  }
}
