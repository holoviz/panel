import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {div} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {HTMLBox, HTMLBoxView, set_size} from "./layout"
import type {Attrs} from "@bokehjs/core/types"

import perspective_css from "styles/models/perspective.css"

const THEMES: any = {
  "pro-dark": "Pro Dark",
  pro: "Pro Light",
  vaporwave: "Vaporwave",
  solarized: "Solarized",
  "solarized-dark": "Solarized Dark",
  monokai: "Monokai",
}

const PLUGINS: any = {
  datagrid: "Datagrid",
  d3_x_bar: "X Bar",
  d3_y_bar: "Y Bar",
  d3_xy_line: "X/Y Line",
  d3_y_line: "Y Line",
  d3_y_area: "Y Area",
  d3_y_scatter: "Y Scatter",
  d3_xy_scatter: "X/Y Scatter",
  d3_treemap: "Treemap",
  d3_candlestick: "Candlestick",
  d3_sunburst: "Sunburst",
  d3_heatmap: "Heatmap",
  d3_ohlc: "OHLC",
}

function objectFlip(obj: any) {
  const ret: any = {}
  Object.keys(obj).forEach(key => {
    ret[obj[key]] = key
  })
  return ret
}

const PLUGINS_REVERSE = objectFlip(PLUGINS)
const THEMES_REVERSE = objectFlip(THEMES)

export class PerspectiveClickEvent extends ModelEvent {
  constructor(readonly config: any, readonly column_names: string[], readonly row: any[]) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, config: this.config, column_names: this.column_names, row: this.row}
  }

  static {
    this.prototype.event_name = "perspective-click"
  }
}

export class PerspectiveView extends HTMLBoxView {
  declare model: Perspective

  perspective_element: any
  table: any
  worker: any
  _updating: boolean = false
  _config_listener: any = null
  _current_config: any = null
  _current_plugin: string | null = null
  _loaded: boolean = false
  _plugin_configs: any = new Map()

  override connect_signals(): void {
    super.connect_signals()

    this.connect(this.model.source.properties.data.change, () => this.setData())
    this.connect(this.model.source.streaming, () => this.stream())
    this.connect(this.model.source.patching, () => this.patch())

    const {
      schema, columns, expressions, split_by, group_by,
      aggregates, filters, sort, plugin, selectable, editable, theme,
      title, settings,
    } = this.model.properties

    const not_updating = (fn: () => void) => {
      return () => {
        if (this._updating) {
          return
        }
        fn()
      }
    }

    this.on_change(schema, () => {
      this.worker.table(this.model.schema).then((table: any) => {
        this.table = table
        this.table.update(this.data)
        this.perspective_element.load(this.table)
      })
    })
    this.on_change(columns, not_updating(() => {
      this.perspective_element.restore({columns: this.model.columns})
    }))
    this.on_change(expressions, not_updating(() => {
      this.perspective_element.restore({expressions: this.model.expressions})
    }))
    this.on_change(split_by, not_updating(() => {
      this.perspective_element.restore({split_by: this.model.split_by})
    }))
    this.on_change(group_by, not_updating(() => {
      this.perspective_element.restore({group_by: this.model.group_by})
    }))
    this.on_change(aggregates, not_updating(() => {
      this.perspective_element.restore({aggregates: this.model.aggregates})
    }))
    this.on_change(filters, not_updating(() => {
      this.perspective_element.restore({filter: this.model.filters})
    }))
    this.on_change(settings, not_updating(() => {
      this.perspective_element.restore({settings: this.model.settings})
    }))
    this.on_change(title, not_updating(() => {
      this.perspective_element.restore({title: this.model.title})
    }))
    this.on_change(sort, not_updating(() => {
      this.perspective_element.restore({sort: this.model.sort})
    }))
    this.on_change(plugin, not_updating(() => {
      this.perspective_element.restore({plugin: PLUGINS[this.model.plugin], ...settings})
    }))
    this.on_change(selectable, not_updating(() => {
      this.perspective_element.restore({plugin_config: {...this._current_config, selectable: this.model.selectable}})
    }))
    this.on_change(editable, not_updating(() => {
      this.perspective_element.restore({plugin_config: {...this._current_config, editable: this.model.editable}})
    }))
    this.on_change(theme, not_updating(() => {
      this.perspective_element.restore({theme: THEMES[this.model.theme as string]}).catch(() => {})
    }))
  }

  override disconnect_signals(): void {
    if (this._config_listener != null) {
      this.perspective_element.removeEventListener("perspective-config-update", this._config_listener)
    }
    this._config_listener = null
    super.disconnect_signals()
  }

  override remove(): void {
    if (this.perspective_element) {
      this.perspective_element.delete(() => this.worker.terminate())
    }
    super.remove()
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), perspective_css]
  }

  override render(): void {
    super.render()
    this.worker = (window as any).perspective.worker()
    const container = div({
      class: "pnx-perspective-viewer",
      style: {
        zIndex: "0",
      },
    })
    this._current_plugin = this.model.plugin
    container.innerHTML = "<perspective-viewer style='height:100%; width:100%;'></perspective-viewer>"
    this.perspective_element = container.children[0]

    const themesArray = Object.values(THEMES)
    const filteredThemes = themesArray.filter(t => t !== this.model.theme)
    const orderedThemes = [this.model.theme, ...filteredThemes]
    this.perspective_element.resetThemes(orderedThemes).catch(() => {})

    set_size(container, this.model)
    this.shadow_el.appendChild(container)

    this.worker.table(this.model.schema).then((table: any) => {
      this.table = table
      this.table.update(this.data)
      this.perspective_element.load(this.table)

      const plugin_config = {
        ...this.model.plugin_config,
        editable: this.model.editable,
        selectable: this.model.selectable,
      }

      this.perspective_element.restore({
        aggregates: this.model.aggregates,
        columns: this.model.columns,
        columns_config: this.model.columns_config,
        expressions: this.model.expressions,
        filter: this.model.filters,
        split_by: this.model.split_by,
        group_by: this.model.group_by,
        plugin: PLUGINS[this.model.plugin],
        plugin_config,
        settings: this.model.settings,
        sort: this.model.sort,
        theme: THEMES[this.model.theme ],
        title: this.model.title,
      }).catch(() => {})

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
    if (this._updating) {
      return true
    }
    this.perspective_element.save().then((config: any) => {
      if (config.plugin !== this._current_plugin) {
        this._plugin_configs.set(this._current_plugin, {
          columns: this._current_config.columns,
          columns_config: this._current_config.columns_config,
          plugin_config: this._current_config.plugin_config,
        })
        if (this._plugin_configs.has(config.plugin)) {
          const overrides = this._plugin_configs.get(config.plugin)
          this.perspective_element.restore(overrides)
          config = {...config, ...overrides}
        }
      }
      this._current_config = config
      this._current_plugin = config.plugin
      const props: any =  {}
      for (let option in config) {
        let value = config[option]
        if (value === undefined || (option == "plugin" && value === "debug") || option == "version" || this.model.properties.hasOwnProperty(option) === undefined) {
          continue
        }
        if (option === "filter") {
          option = "filters"
        } else if (option === "plugin") {
          value = PLUGINS_REVERSE[value ]
        } else if (option === "theme") {
          value = THEMES_REVERSE[value ]
        }
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
    for (const column of this.model.source.columns()) {
      let array = this.model.source.get_array(column)
      if (this.model.schema[column] == "datetime" && array.includes(-9223372036854776)) {
        array = array.map((v) => v === -9223372036854776 ? null : v)
      }
      data[column] = array
    }
    return data
  }

  setData(): void {
    if (!this._loaded) {
      return
    }
    for (const col of this.model.source.columns()) {
      if (!(col in this.model.schema)) {
        return
      }
    }
    this.table.replace(this.data)
  }

  stream(): void {
    if (this._loaded) {
      this.table.replace(this.data)
    }
  }

  patch(): void {
    if (this._loaded) {
      this.table.replace(this.data)
    }
  }
}

export namespace Perspective {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    aggregates: p.Property<any>
    split_by: p.Property<any[] | null>
    columns: p.Property<any[]>
    columns_config: p.Property<any>
    expressions: p.Property<any>
    editable: p.Property<boolean | null>
    filters: p.Property<any[] | null>
    group_by: p.Property<any[] | null>
    plugin: p.Property<any>
    plugin_config: p.Property<any>
    selectable: p.Property<boolean | null>
    schema: p.Property<any>
    settings: p.Property<boolean>
    sort: p.Property<any[] | null>
    source: p.Property<ColumnDataSource>
    theme: p.Property<any>
    title: p.Property<string | null>
  }
}

export interface Perspective extends Perspective.Attrs { }

export class Perspective extends HTMLBox {
  declare properties: Perspective.Props

  constructor(attrs?: Partial<Perspective.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.perspective"

  static {
    this.prototype.default_view = PerspectiveView

    this.define<Perspective.Props>(({Any, List, Bool, Ref, Nullable, Str}) => ({
      aggregates:       [ Any,                         {} ],
      columns:          [ List(Nullable(Str)),         [] ],
      columns_config:   [ Any,                         {} ],
      expressions:      [ Any,                         {} ],
      split_by:         [ Nullable(List(Str)),       null ],
      editable:         [ Bool,                      true ],
      filters:          [ Nullable(List(Any)),       null ],
      group_by:         [ Nullable(List(Str)),       null ],
      plugin:           [ Str                             ],
      plugin_config:    [ Any,                         {} ],
      selectable:       [ Bool,                      true ],
      settings:         [ Bool,                      true ],
      schema:           [ Any,                         {} ],
      sort:             [ Nullable(List(List(Str))), null ],
      source:           [ Ref(ColumnDataSource)           ],
      theme:            [ Str,                      "pro" ],
      title:            [ Nullable(Str),             null ],
    }))
  }
}
