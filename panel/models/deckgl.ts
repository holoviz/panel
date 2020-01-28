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

  connect_signals(): void {
    super.connect_signals()
    const {json_input, mapbox_api_key, tooltip} = this.model.properties;
    this.on_change([json_input, mapbox_api_key, tooltip], () => { this.render() })
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

  updateDeck(inputJSON: any, deckgl: any): void {
    const results = this.jsonConverter.convert(inputJSON);
    deckgl.setProps(results);
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

    if (deck.createDeck) {
      deck.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container: container,
        jsonInput,
        tooltip
      });
    } else {
      this.createDeck({
        mapboxApiKey: MAPBOX_API_KEY,
        container: container,
        jsonInput,
		tooltip
      });
    }
    this.el.appendChild(container);
  }
}

export namespace DeckGLPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    json_input: p.Property<string>
    mapbox_api_key: p.Property<string>
    tooltip: p.Property<boolean>
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
      json_input: [p.String],
      mapbox_api_key: [p.String],
      tooltip: [p.Boolean],
    })

    this.override({
      height: 400,
      width: 600
    });
  }
}
