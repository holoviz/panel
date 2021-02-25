import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"

import {transform_cds_to_records} from "./data"
import {PanelHTMLBoxView, set_size} from "./layout"
import {makeTooltip} from "./tooltips"

import GL from '@luma.gl/constants';

function extractClasses() {
  // Get classes for registration from standalone deck.gl
  const classesDict: any = {};
  const deck = (window as any).deck;
  const classes = Object.keys(deck).filter(x => x.charAt(0) === x.charAt(0).toUpperCase());
  for (const cls of classes) {
    classesDict[cls] = deck[cls];
  }
  return classesDict;
}

export class DeckGLPlotView extends PanelHTMLBoxView {
  model: DeckGLPlot
  jsonConverter: any
  deckGL: any
  _connected: any[]
  _layer_map: any

  connect_signals(): void {
    super.connect_signals()
    const {data, mapbox_api_key, tooltip, layers, initialViewState, data_sources} = this.model.properties
    this.on_change([mapbox_api_key, tooltip], () => this.render())
    this.on_change([data, initialViewState], () => this.updateDeck())
    this.on_change([layers], () => this._update_layers())
    this.on_change([data_sources], () => this._connect_sources(true))
    this._layer_map = {}
    this._connected = []
    this._connect_sources()
  }

  _update_layers(): void {
    this._layer_map = {}
    this._update_data(true)
  }

  _connect_sources(render: boolean = false): void {
    for (const cds of this.model.data_sources) {
      if (this._connected.indexOf(cds) < 0) {
        this.connect(cds.properties.data.change, () => this._update_data(true))
        this._connected.push(cds)
      }
    }
    this._update_data(render)
  }

  initialize(): void {
    super.initialize()
    if ((window as any).deck.JSONConverter) {
      const {CSVLoader, Tile3DLoader} = (window as any).loaders;
      (window as any).loaders.registerLoaders([Tile3DLoader, CSVLoader]);
      const jsonConverterConfiguration: any = {
        classes: extractClasses(),
        // Will be resolved as `<enum-name>.<enum-value>`
        enumerations: {
          COORDINATE_SYSTEM: (window as any).deck.COORDINATE_SYSTEM,
          GL
        },
        // Constants that should be resolved with the provided values by JSON converter
        constants: {
          Tile3DLoader
        }
      };
      this.jsonConverter = new (window as any).deck.JSONConverter({
        configuration: jsonConverterConfiguration
      });
    }
  }

  _update_data(render: boolean = true): void {
    let n = 0;
    for (const layer of this.model.layers) {
      let cds;
      n += 1;
      if ((n-1) in this._layer_map) {
        cds = this.model.data_sources[this._layer_map[n-1]]
      } else if (typeof layer.data != "number")
        continue
      else {
        this._layer_map[n-1] = layer.data
        cds = this.model.data_sources[layer.data]
      }
      layer.data = transform_cds_to_records(cds);
    }
    if (render)
      this.updateDeck()
  }

  _on_click_event(event: any): void {
    const clickState = {
      coordinate: event.coordinate,
      lngLat: event.lngLat,
      index: event.index
    }
    this.model.clickState = clickState
  }

  _on_hover_event(event: any): void {
    if (event.coordinate == null)
      return
    const hoverState = {
      coordinate: event.coordinate,
      lngLat: event.lngLat,
      index: event.index
    }
    this.model.hoverState = hoverState
  }

  _on_viewState_event(event: any): void {
    this.model.viewState = event.viewState
  }

  getData(): any {
    const data = {
      ...this.model.data,
      layers: this.model.layers,
      initialViewState: this.model.initialViewState,
      onViewStateChange: (event: any) => this._on_viewState_event(event),
      onClick: (event: any) => this._on_click_event(event),
      onHover: (event: any) => this._on_hover_event(event)
    }
    return data
  }

  updateDeck(): void {
    if (!this.deckGL) { this.render(); return; }
    const data = this.getData()
    if ((window as any).deck.updateDeck) {
      (window as any).deck.updateDeck(data, this.deckGL)
    } else {
      const results = this.jsonConverter.convert(data);
      this.deckGL.setProps(results);
    }
  }

  createDeck({mapboxApiKey, container, jsonInput, tooltip} : any): void {
    let deckgl;
    try {
      const props = this.jsonConverter.convert(jsonInput);
      const getTooltip = makeTooltip(tooltip, props.layers);
      deckgl = new (window as any).deck.DeckGL({
        ...props,
        map: (window as any).mapboxgl,
        mapboxApiAccessToken: mapboxApiKey,
        container,
        getTooltip
      });
    } catch (err) {
      console.error(err);
    }
    return deckgl;
  }

  render(): void {
    super.render()
    const container = div({class: "deckgl"});
    set_size(container, this.model)

    const MAPBOX_API_KEY = this.model.mapbox_api_key;
    const tooltip = this.model.tooltip;
    const data = this.getData();

    if ((window as any).deck.createDeck) {
      this.deckGL = (window as any).deck.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container: container,
        jsonInput: data,
        tooltip
      });
    } else {
      this.deckGL = this.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container: container,
        jsonInput: data,
        tooltip
      });
    }
    this.el.appendChild(container);
  }
}

export namespace DeckGLPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    data_sources: p.Property<ColumnDataSource[]>
    initialViewState: p.Property<any>
    layers: p.Property<any[]>
    mapbox_api_key: p.Property<string>
    tooltip: p.Property<any>
    clickState: p.Property<any>
    hoverState: p.Property<any>
    viewState: p.Property<any>
  }
}

export interface DeckGLPlot extends DeckGLPlot.Attrs { }

export class DeckGLPlot extends HTMLBox {
  properties: DeckGLPlot.Props

  constructor(attrs?: Partial<DeckGLPlot.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.deckgl"

  static init_DeckGLPlot(): void {
    this.prototype.default_view = DeckGLPlotView;      

    this.define<DeckGLPlot.Props>(({Any, Array, String, Ref}) => ({
      data:             [ Any                              ],
      data_sources:     [ Array(Ref(ColumnDataSource)), [] ],
      clickState:       [ Any,                          {} ],
      hoverState:       [ Any,                          {} ],
      initialViewState: [ Any,                          {} ],
      layers:           [ Array(Any),                   [] ],
      mapbox_api_key:   [ String,                       '' ],
      tooltip:          [ Any,                          {} ],
      viewState:        [ Any,                          {} ],
    }))

    this.override<DeckGLPlot.Props>({
      height: 400,
      width: 600
    });
  }
}
