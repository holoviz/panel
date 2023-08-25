import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {HTMLBox, HTMLBoxView, set_size} from "./layout"
import {Attrs} from "@bokehjs/core/types"

const THEMES: any = {
  'material-dark': 'Material Dark',
  'material': 'Material Light',
  'vaporwave': 'Vaporwave',
  'solarized': 'Solarized',
  'solarized-dark': 'Solarized Dark',
  'monokai': 'Monokai'
}

const PLUGINS: any = {
  'datagrid': 'Datagrid',
  'd3_x_bar': 'X Bar',
  'd3_y_bar': 'Y Bar',
  'd3_xy_line': 'X/Y Line',
  'd3_y_line': 'Y Line',
  'd3_y_area': 'Y Area',
  'd3_y_scatter': 'Y Scatter',
  'd3_xy_scatter': 'X/Y Scatter',
  'd3_treemap': 'Treemap',
  'd3_candlestick': 'Candlestick',
  'd3_sunburst': 'Sunburst',
  'd3_heatmap': 'Heatmap',
  'd3_ohlc': 'OHLC'
}

function objectFlip(obj: any) {
  const ret: any = {};
  Object.keys(obj).forEach(key => {
    ret[obj[key]] = key;
  });
  return ret;
}

const PLUGINS_REVERSE = objectFlip(PLUGINS)
const THEMES_REVERSE = objectFlip(THEMES)

export class PerspectiveClickEvent extends ModelEvent {
  constructor(readonly config: any, readonly column_names: string[], readonly row: any[]) {
    super()
  }

  protected get event_values(): Attrs {
    return {model: this.origin, config: this.config, column_names: this.column_names, row: this.row}
  }

  static {
    this.prototype.event_name = "perspective-click"
  }
}

export class PerspectiveView extends HTMLBoxView {
  model: Perspective
  perspective_element: any
  table: any
  worker: any
  _updating: boolean = false
  _config_listener: any = null
  _current_config: any = null
  _loaded: boolean = false

  connect_signals(): void {
    super.connect_signals()

    this.connect(this.model.source.properties.data.change, () => this.setData());
    this.connect(this.model.source.streaming, () => this.stream())
    this.connect(this.model.source.patching, () => this.patch())
    this.connect(this.model.properties.schema.change, () => {
      this.worker.table(this.model.schema).then((table: any) => {
	this.table = table
	this.table.update(this.data)
	this.perspective_element.load(this.table)
      })
    });
    this.connect(this.model.properties.toggle_config.change, () => {
      this.perspective_element.toggleConfig()
    })
    this.connect(this.model.properties.columns.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"columns": this.model.columns})
    })
    this.connect(this.model.properties.expressions.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"expressions": this.model.expressions})
    })
    this.connect(this.model.properties.split_by.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"split_by": this.model.split_by})
    })
    this.connect(this.model.properties.group_by.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"group_by": this.model.group_by})
    })
    this.connect(this.model.properties.aggregates.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"aggregates":this.model.aggregates})
    })
    this.connect(this.model.properties.filters.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"filter": this.model.filters})
    })
    this.connect(this.model.properties.sort.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"sort": this.model.sort})
    })
    this.connect(this.model.properties.plugin.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"plugin": PLUGINS[this.model.plugin as any]})
    })
    this.connect(this.model.properties.selectable.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"plugin_config": {...this._current_config, selectable: this.model.selectable}})
    })
    this.connect(this.model.properties.editable.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"plugin_config": {...this._current_config, editable: this.model.editable}})
    })
    this.connect(this.model.properties.theme.change, () => {
      if (this._updating) return
      this.perspective_element.restore({"theme": THEMES[this.model.theme as string]}).catch(() => {})
    })
  }

  disconnect_signals(): void {
    if (this._config_listener != null)
      this.perspective_element.removeEventListener("perspective-config-update", this._config_listener)
    this._config_listener = null
    super.disconnect_signals()
  }

  override remove(): void {
    this.perspective_element.delete(() => this.worker.terminate())
    super.remove()
  }

  render(): void {
    super.render()
    this.worker = (window as any).perspective.worker();
    const container = div({
      class: "pnx-perspective-viewer",
      style: {
        zIndex: 0,
      }
    })
    container.innerHTML = "<perspective-viewer style='height:100%; width:100%;'></perspective-viewer>";
    this.perspective_element = container.children[0]
    this.perspective_element.resetThemes([...Object.values(THEMES)]).catch(() => {});
    if (this.model.toggle_config)
      this.perspective_element.toggleConfig()
    set_size(container, this.model)
    this.shadow_el.appendChild(container)

    this.worker.table(this.model.schema).then((table: any) => {
      this.table = table
      this.table.update(this.data)
      this.perspective_element.load(this.table)

      const plugin_config = {
	...this.model.plugin_config,
	editable: this.model.editable,
	selectable: this.model.selectable
      }

      this.perspective_element.restore({
	aggregates: this.model.aggregates,
	columns: this.model.columns,
	expressions: this.model.expressions,
	filter: this.model.filters,
	split_by: this.model.split_by,
	group_by: this.model.group_by,
	plugin: PLUGINS[this.model.plugin as any],
	plugin_config: plugin_config,
	sort: this.model.sort,
	theme: THEMES[this.model.theme as any]
      }).catch(() => {});

      this.perspective_element.save().then((config: any) => {
	this._current_config = config
      })
      this._config_listener = () => this.sync_config()
      this.perspective_element.addEventListener("perspective-config-update", this._config_listener)
      this.perspective_element.addEventListener("perspective-click", (event: any) => {
        this.model.trigger_event(new PerspectiveClickEvent(event.detail.config, event.detail.column_names, event.detail.row))
      })
      this._loaded = true
    })
  }

  sync_config(): boolean {
    if (this._updating)
      return true
    this.perspective_element.save().then((config: any) => {
      this._current_config = config
      const props: any =  {}
      for (let option in config) {
        let value = config[option]
        if (value === undefined || (option == 'plugin' && value === "debug") || option === 'settings')
          continue
        if (option === 'filter')
          option = 'filters'
        else if (option === 'plugin')
          value = PLUGINS_REVERSE[value as any]
        else if (option === 'theme')
          value = THEMES_REVERSE[value as any]
        props[option] = value
      }
      this._updating = true
      this.model.setv(props)
      this._updating = false
    })
    return true
  }

  get data(): any {
    const data: any = {}
    for (const column of this.model.source.columns())
      data[column] = this.model.source.get_array(column)
    return data
  }

  setData(): void {
    if (!this._loaded)
      return
    for (const col of this.model.source.columns()) {
      if (!(col in this.model.schema))
	return
    }
    this.table.replace(this.data)
  }

  stream(): void {
    if (this._loaded)
      this.table.replace(this.data)
  }

  patch(): void {
    if (this._loaded)
      this.table.replace(this.data)
  }
}

export namespace Perspective {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    aggregates: p.Property<any>
    split_by: p.Property<any[] | null>
    columns: p.Property<any[]>
    expressions: p.Property<any[] | null>
    editable: p.Property<boolean | null>
    filters: p.Property<any[] | null>
    group_by: p.Property<any[] | null>
    plugin: p.Property<any>
    plugin_config: p.Property<any>
    selectable: p.Property<boolean | null>
    toggle_config: p.Property<boolean>
    schema: p.Property<any>
    sort: p.Property<any[] | null>
    source: p.Property<ColumnDataSource>
    theme: p.Property<any>
  }
}

export interface Perspective extends Perspective.Attrs { }

export class Perspective extends HTMLBox {
  properties: Perspective.Props

  constructor(attrs?: Partial<Perspective.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.perspective"

  static {
    this.prototype.default_view = PerspectiveView

    this.define<Perspective.Props>(({Any, Array, Boolean, Ref, Nullable, String}) => ({
      aggregates:       [ Any,                                 {} ],
      columns:          [ Array(Nullable(String)),             [] ],
      expressions:      [ Nullable(Array(String)),           null ],
      split_by:         [ Nullable(Array(String)),           null ],
      editable:         [ Boolean,                           true ],
      filters:          [ Nullable(Array(Any)),              null ],
      group_by:         [ Nullable(Array(String)),           null ],
      plugin:           [ String,                                 ],
      plugin_config:    [ Any,                                 {} ],
      selectable:       [ Boolean,                           true ],
      schema:           [ Any,                                 {} ],
      toggle_config:    [ Boolean,                           true ],
      sort:             [ Nullable(Array(Array(String))),    null ],
      source:           [ Ref(ColumnDataSource),                  ],
      theme:            [ String,                      'material' ]
    }))
  }
}
