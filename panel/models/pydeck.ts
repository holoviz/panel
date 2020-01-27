import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"

import {PanelHTMLBoxView, set_size} from "./layout"

import GL from '@luma.gl/constants';

const deck = (window as any).deck;
const mapboxgl = (window as any).mapboxgl;
const loaders = (window as any).loaders;
const {CSVLoader, Tile3DLoader} = loaders;
const createDeck = deck.createDeck;

function extractClasses() {
  // Get classes for registration from standalone deck.gl
  const classesDict: any = {};
  const classes = Object.keys(deck).filter(x => x.charAt(0) === x.charAt(0).toUpperCase());
  for (const cls of classes) {
    classesDict[cls] = deck[cls];
  }
  return classesDict;
}

export class PyDeckPlotView extends PanelHTMLBoxView {
  model: PyDeckPlot
  jsonConverter: any

  connect_signals(): void {
    super.connect_signals()
    const {json_input, mapbox_api_key, tooltip, _render_count} = this.model.properties;
    this.on_change([json_input, mapbox_api_key, tooltip, _render_count], () => { this.render() })
  }

  initialize(): void {
    super.initialize()
    if (deck.JSONConverter) {
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

  updateDeck(inputJSON: any, deckgl: any): void {
    const results = this.jsonConverter.convert(inputJSON);
    deckgl.setProps(results);
  }

  createDeck({mapboxApiKey, container, jsonInput, handleClick} : any): void {
    let deckgl;
    try {
      const props = this.jsonConverter.convert(jsonInput);
      deckgl = new deck.DeckGL({
        ...props,
        map: mapboxgl,
        mapboxApiAccessToken: mapboxApiKey,
        onClick: handleClick,
        container
      });
    } catch (err) {
      // This will fail in node tests
      // eslint-disable-next-line
      console.error(err);
    }
    return deckgl;
  }

  render(): void {
    super.render()
    const container = div({class: "deckgl"});
    set_size(container, this.model)

    const jsonInput = JSON.parse(this.model.json_input);
    const MAPBOX_API_KEY = this.model.mapbox_api_key;
    const tooltip = this.model.tooltip;
    if (createDeck) {
      createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container: container,
        jsonInput,
        tooltip
      });
    } else {
      this.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container: container,
        jsonInput
      });
    }
    this.el.appendChild(container);
  }
}

export namespace PyDeckPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    json_input: p.Property<string>
    mapbox_api_key: p.Property<string>
    tooltip: p.Property<boolean>
    _render_count: p.Property<number>
  }
}

export interface PyDeckPlot extends PyDeckPlot.Attrs { }

export class PyDeckPlot extends HTMLBox {
  properties: PyDeckPlot.Props

  constructor(attrs?: Partial<PyDeckPlot.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.pydeck"

  static init_PyDeckPlot(): void {
    this.prototype.default_view = PyDeckPlotView;

    this.define<PyDeckPlot.Props>({
      json_input: [p.String],
      mapbox_api_key: [p.String],
      tooltip: [p.Boolean],
      _render_count: [p.Number, 0],
    })

    this.override({
      height: 400,
      width: 600
    });
  }
}
