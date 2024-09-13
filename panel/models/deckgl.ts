import {div} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import {isNumber} from "@bokehjs/core/util/types"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"

import {debounce} from  "debounce"

import {transform_cds_to_records} from "./data"
import {set_size} from "./layout"
import {GL} from "./lumagl"
import {makeTooltip} from "./tooltips"

function extractClasses() {
  // Get classes for registration from standalone deck.gl
  const classesDict: any = {}
  const deck = (window as any).deck
  const classes = Object.keys(deck).filter(x => x.charAt(0) === x.charAt(0).toUpperCase())
  for (const cls of classes) {
    classesDict[cls] = deck[cls]
  }
  const carto = (window as any).CartoLibrary
  const layers = Object.keys(carto.CARTO_LAYERS).filter(x => x.endsWith("Layer"))
  for (const layer of layers) {
    classesDict[layer] = carto.CARTO_LAYERS[layer]
  }
  return classesDict
}

function extractFunctions() {
  const carto = (window as any).CartoLibrary
  const sources = Object.keys(carto.CARTO_SOURCES).filter(x => x.toLowerCase().endsWith("source"))
  const functionDict: any = {}
  for (const src of sources) {
    functionDict[src] = carto.CARTO_SOURCES[src]
  }
  return functionDict
}

export class DeckGLPlotView extends LayoutDOMView {
  declare model: DeckGLPlot

  jsonConverter: any
  deckGL: any
  _connected: any[]
  _map: any
  _layer_map: any
  _view_cb: any
  _initialized: boolean = false

  override connect_signals(): void {
    super.connect_signals()
    const {data, mapbox_api_key, tooltip, configuration, layers, initialViewState, data_sources} = this.model.properties
    this.on_change([mapbox_api_key, tooltip, configuration], () => this.render())
    this.on_change([data, initialViewState], () => this.updateDeck())
    this.on_change([layers], () => this._update_layers())
    this.on_change([data_sources], () => this._connect_sources(true))
    this._layer_map = {}
    this._connected = []
    this._connect_sources()
  }

  override remove(): void {
    this.deckGL.finalize()
    super.remove()
  }

  _update_layers(): void {
    this._layer_map = {}
    this._update_data(true)
  }

  _connect_sources(render: boolean = false): void {
    for (const cds of this.model.data_sources) {
      if (this._connected.indexOf(cds) < 0) {
        this.on_change(cds.properties.data, () => this._update_data(true))
        this._connected.push(cds)
      }
    }
    this._update_data(render)
  }

  override initialize(): void {
    super.initialize()
    const view_timeout = this.model.throttle.view || 200
    this._view_cb = debounce((event: any) => this._on_viewState_event(event), view_timeout, false)
    if ((window as any).deck.JSONConverter) {
      const {CSVLoader, Tiles3DLoader} = (window as any).loaders;
      (window as any).loaders.registerLoaders([Tiles3DLoader, CSVLoader])
      const jsonConverterConfiguration: any = {
        classes: extractClasses(),
        functions: extractFunctions(),
        // Will be resolved as `<enum-name>.<enum-value>`
        enumerations: {
          COORDINATE_SYSTEM: (window as any).deck.COORDINATE_SYSTEM,
          GL,
        },
        // Constants that should be resolved with the provided values by JSON converter
        constants: {
          Tiles3DLoader,
        },
      }
      this.jsonConverter = new (window as any).deck.JSONConverter({
        configuration: jsonConverterConfiguration,
      })
    }
  }

  _update_data(render: boolean = true): void {
    let n = 0
    for (const layer of this.model.layers) {
      let cds
      n += 1
      if ((n-1) in this._layer_map) {
        cds = this.model.data_sources[this._layer_map[n-1]]
      } else if (!isNumber(layer.data)) {
        continue
      } else {
        this._layer_map[n-1] = layer.data
        cds = this.model.data_sources[layer.data]
      }
      layer.data = transform_cds_to_records(cds)
    }
    if (render) {
      this.updateDeck()
    }
  }

  _on_click_event(event: any): void {
    const click_state: any = {
      coordinate: event.coordinate,
      lngLat: event.coordinate,
      index: event.index,
    }
    if (event.layer) {
      click_state.layer = event.layer.id
    }
    this.model.clickState = click_state
  }

  _on_hover_event(event: any): void {
    if (event.coordinate == null) {
      return
    }
    const hover_state: any = {
      coordinate: event.coordinate,
      lngLat: event.coordinate,
      index: event.index,
    }
    if (event.layer) {
      hover_state.layer = event.layer.id
    }
    this.model.hoverState = hover_state
  }

  _on_viewState_event(event: any): void {
    const view_state = {...event.viewState}
    delete view_state.normalize
    for (const p in view_state) {
      if (p.startsWith("transition")) {
        delete view_state[p]
      }
    }
    const viewport = new (window as any).deck.WebMercatorViewport(view_state)
    view_state.nw = viewport.unproject([0, 0])
    view_state.se = viewport.unproject([viewport.width, viewport.height])
    this.model.viewState = view_state
  }

  get child_models(): LayoutDOM[] {
    return []
  }

  getData(): any {
    const hover_timeout = this.model.throttle.hover || 100
    const hover_cb = debounce((event: any) => this._on_hover_event(event), hover_timeout, false)
    const data = {
      ...this.model.data,
      layers: this.model.layers,
      initialViewState: this.model.initialViewState,
      onViewStateChange: (event: any) => this._sync_viewstate(event),
      onClick: (event: any) => this._on_click_event(event),
      onHover: hover_cb,
    }
    return data
  }

  _sync_viewstate(event: any): void {
    if (this._map) {
      const {longitude, latitude, ...rest} = event.viewState
      this._map.jumpTo({center: [longitude, latitude], ...rest})
    }
    this._view_cb(event)
  }

  updateDeck(): void {
    if (!this.deckGL) {
      this.render()
      return
    }
    const data = this.getData()
    if ((window as any).deck.updateDeck) {
      (window as any).deck.updateDeck(data, this.deckGL)
    } else {
      const results = this.jsonConverter.convert(data)
      this.deckGL.setProps(results)
    }
  }

  createDeck({mapboxApiKey, container, jsonInput, tooltip}: any): void {
    let deckgl
    try {
      let configuration
      if (this.model.configuration) {
        configuration = eval(`(${  this.model.configuration  })`)
      } else {
        configuration = null
      }
      this.jsonConverter.mergeConfiguration(configuration)
      const props = this.jsonConverter.convert(jsonInput)
      const getTooltip = makeTooltip(tooltip, props.layers)
      if (props.mapStyle === null) {
        props.map = null
      } else if (props.mapStyle.includes("carto")) {
        this._map = new (window as any).maplibregl.Map({
          container,
          style: props.mapStyle,
          interactive: false,
        })
        props.controller = true
        props.map = null
        delete props.mapStyle
      } else {
        props.map = (window as any).mapboxgl
        props.mapboxApiAccessToken = mapboxApiKey
      }
      deckgl = new (window as any).deck.DeckGL({
        ...props,
        container,
        getTooltip,
        height: "100%",
        width: "100%",
      })
    } catch (err) {
      console.error(err)
    }
    return deckgl
  }

  override render(): void {
    super.render()
    const container = div({class: "deckgl"})
    set_size(container, this.model, false)
    const MAPBOX_API_KEY = this.model.mapbox_api_key
    const tooltip = this.model.tooltip
    const data = this.getData()
    if ((window as any).deck.createDeck) {
      this.deckGL = (window as any).deck.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container,
        jsonInput: data,
        tooltip,
      })
    } else {
      this.deckGL = this.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container,
        jsonInput: data,
        tooltip,
      })
    }
    this.shadow_el.appendChild(container)
    this._initialized = false
  }

  resize(): void {
    this.deckGL.redraw(true)
    if (this._map) {
      this._map.resize()
    }
  }

  override after_layout(): void {
    super.after_layout()
    if (!this._initialized) {
      this.resize()
    }
    this._initialized = true
  }

  override after_resize(): void {
    super.after_resize()
    this.resize()
  }
}

export namespace DeckGLPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = LayoutDOM.Props & {
    data: p.Property<any>
    data_sources: p.Property<ColumnDataSource[]>
    initialViewState: p.Property<any>
    layers: p.Property<any[]>
    mapbox_api_key: p.Property<string>
    tooltip: p.Property<any>
    configuration: p.Property<string>
    clickState: p.Property<any>
    hoverState: p.Property<any>
    throttle: p.Property<any>
    viewState: p.Property<any>
  }
}

export interface DeckGLPlot extends DeckGLPlot.Attrs { }

export class DeckGLPlot extends LayoutDOM {
  declare properties: DeckGLPlot.Props

  constructor(attrs?: Partial<DeckGLPlot.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.deckgl"

  static {
    this.prototype.default_view = DeckGLPlotView

    this.define<DeckGLPlot.Props>(({Any, List, Str, Ref}) => ({
      data:             [ Any                              ],
      data_sources:     [ List(Ref(ColumnDataSource)), [] ],
      clickState:       [ Any,                          {} ],
      hoverState:       [ Any,                          {} ],
      initialViewState: [ Any,                          {} ],
      layers:           [ List(Any),                   [] ],
      mapbox_api_key:   [ Str,                       "" ],
      throttle:         [ Any,                          {} ],
      tooltip:          [ Any,                        true ],
      configuration:          [ Str,                        "" ],
      viewState:        [ Any,                          {} ],
    }))

    this.override<DeckGLPlot.Props>({
      height: 400,
      width: 600,
    })
  }
}
