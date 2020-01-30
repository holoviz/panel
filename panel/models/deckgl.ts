import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"

import {PanelHTMLBoxView, set_size} from "./layout"
import {makeTooltip} from "./tooltips"

import GL from '@luma.gl/constants';

const deck = (window as any).deck;
const mapboxgl = (window as any).mapboxgl;
const loaders = (window as any).loaders;

function extractClasses() {
  // Get classes for registration from standalone deck.gl
  const classesDict: any = {};
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

  connect_signals(): void {
    super.connect_signals()
    const {data, mapbox_api_key, tooltip} = this.model.properties
    this.on_change([mapbox_api_key, tooltip], () => this.render())
    this.on_change([data], () => this.updateDeck())
    this.connect(this.model.properties.data_sources.change, () => this._connect_sources(true))
    this._connected = []
    this._connect_sources()
  }

  _connect_sources(update: boolean = false): void {
    for (const cds of this.model.data_sources) {
      if (this._connected.indexOf(cds) < 0) {
        this.connect(cds.properties.data.change, () => this.updateDeck())
        this._connected.push(cds)
      }
    }
    if (update)
      this.updateDeck()
  }

  initialize(): void {
    super.initialize()
    if (deck.JSONConverter) {
	  const {CSVLoader, Tile3DLoader} = loaders
      loaders.registerLoaders([Tile3DLoader, CSVLoader]);
      const jsonConverterConfiguration: any = {
        classes: extractClasses(),
        // Will be resolved as `<enum-name>.<enum-value>`
        enumerations: {
          COORDINATE_SYSTEM: deck.COORDINATE_SYSTEM,
          GL
        },
        // Constants that should be resolved with the provided values by JSON converter
        constants: {
          Tile3DLoader
        }
      };
      this.jsonConverter = new deck.JSONConverter({
        configuration: jsonConverterConfiguration
      });
    }
  }

  _update_data(): void {
    for (const layer of this.model.data.layers) {
      if (typeof layer.data != "number") { continue }
      const cds = this.model.data_sources[layer.data];
      const data: any = []
      const columns = cds.columns()
      for (let i = 0; i < cds.data[columns[0]].length; i++) {
        const item: any = {}
        for (const column of columns) {
          item[column] = cds.data[column][i]
        }
        data.push(item)
      }
      layer.data = data;
    }
  }

  updateDeck(): void {
    this._update_data()
    if (!this.deckGL) { this.render(); return; }
    if (deck.updateDeck) {
      deck.updateDeck(this.model.data, this.deckGL)
    } else {
      const results = this.jsonConverter.convert(this.model.data);
      this.deckGL.setProps(results);
    }
  }

  createDeck({mapboxApiKey, container, jsonInput, tooltip, handleClick} : any): void {
    let deckgl;
    try {
      const props = this.jsonConverter.convert(jsonInput);
      const getTooltip = makeTooltip(tooltip);
      deckgl = new deck.DeckGL({
        ...props,
        map: mapboxgl,
        mapboxApiAccessToken: mapboxApiKey,
        onClick: handleClick,
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
    this._update_data()

    if (deck.createDeck) {
      this.deckGL = deck.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container: container,
        jsonInput: this.model.data,
        tooltip
      });
    } else {
      this.deckGL = this.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container: container,
        jsonInput: this.model.data,
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
    data_sources: p.Property<any[]>
    mapbox_api_key: p.Property<string>
    tooltip: p.Property<boolean>
    _render_count: p.Property<number>
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

    this.define<DeckGLPlot.Props>({
      data: [p.Any],
      data_sources: [ p.Array, [] ],
      mapbox_api_key: [p.String],
      tooltip: [p.Boolean],
    })

    this.override({
      height: 400,
      width: 600
    });
  }
}
