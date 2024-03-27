import { div } from "@bokehjs/core/dom";
import { isNumber } from "@bokehjs/core/util/types";
import { ColumnDataSource } from "@bokehjs/models/sources/column_data_source";
import { debounce } from "debounce";
import { transform_cds_to_records } from "./data";
import { LayoutDOM, LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
import { makeTooltip } from "./tooltips";
import GL from "@luma.gl/constants";
function extractClasses() {
    // Get classes for registration from standalone deck.gl
    const classesDict = {};
    const deck = window.deck;
    const classes = Object.keys(deck).filter(x => x.charAt(0) === x.charAt(0).toUpperCase());
    for (const cls of classes) {
        classesDict[cls] = deck[cls];
    }
    return classesDict;
}
export class DeckGLPlotView extends LayoutDOMView {
    static __name__ = "DeckGLPlotView";
    jsonConverter;
    deckGL;
    _connected;
    _layer_map;
    connect_signals() {
        super.connect_signals();
        const { data, mapbox_api_key, tooltip, layers, initialViewState, data_sources } = this.model.properties;
        this.on_change([mapbox_api_key, tooltip], () => this.render());
        this.on_change([data, initialViewState], () => this.updateDeck());
        this.on_change([layers], () => this._update_layers());
        this.on_change([data_sources], () => this._connect_sources(true));
        this._layer_map = {};
        this._connected = [];
        this._connect_sources();
    }
    remove() {
        this.deckGL.finalize();
        super.remove();
    }
    _update_layers() {
        this._layer_map = {};
        this._update_data(true);
    }
    _connect_sources(render = false) {
        for (const cds of this.model.data_sources) {
            if (this._connected.indexOf(cds) < 0) {
                this.on_change(cds.properties.data, () => this._update_data(true));
                this._connected.push(cds);
            }
        }
        this._update_data(render);
    }
    initialize() {
        super.initialize();
        if (window.deck.JSONConverter) {
            const { CSVLoader, Tiles3DLoader } = window.loaders;
            window.loaders.registerLoaders([Tiles3DLoader, CSVLoader]);
            const jsonConverterConfiguration = {
                classes: extractClasses(),
                // Will be resolved as `<enum-name>.<enum-value>`
                enumerations: {
                    COORDINATE_SYSTEM: window.deck.COORDINATE_SYSTEM,
                    GL,
                },
                // Constants that should be resolved with the provided values by JSON converter
                constants: {
                    Tiles3DLoader,
                },
            };
            this.jsonConverter = new window.deck.JSONConverter({
                configuration: jsonConverterConfiguration,
            });
        }
    }
    _update_data(render = true) {
        let n = 0;
        for (const layer of this.model.layers) {
            let cds;
            n += 1;
            if ((n - 1) in this._layer_map) {
                cds = this.model.data_sources[this._layer_map[n - 1]];
            }
            else if (!isNumber(layer.data)) {
                continue;
            }
            else {
                this._layer_map[n - 1] = layer.data;
                cds = this.model.data_sources[layer.data];
            }
            layer.data = transform_cds_to_records(cds);
        }
        if (render) {
            this.updateDeck();
        }
    }
    _on_click_event(event) {
        const click_state = {
            coordinate: event.coordinate,
            lngLat: event.coordinate,
            index: event.index,
        };
        if (event.layer) {
            click_state.layer = event.layer.id;
        }
        this.model.clickState = click_state;
    }
    _on_hover_event(event) {
        if (event.coordinate == null) {
            return;
        }
        const hover_state = {
            coordinate: event.coordinate,
            lngLat: event.coordinate,
            index: event.index,
        };
        if (event.layer) {
            hover_state.layer = event.layer.id;
        }
        this.model.hoverState = hover_state;
    }
    _on_viewState_event(event) {
        const view_state = { ...event.viewState };
        delete view_state.normalize;
        for (const p in view_state) {
            if (p.startsWith("transition")) {
                delete view_state[p];
            }
        }
        const viewport = new window.deck.WebMercatorViewport(view_state);
        view_state.nw = viewport.unproject([0, 0]);
        view_state.se = viewport.unproject([viewport.width, viewport.height]);
        this.model.viewState = view_state;
    }
    get child_models() {
        return [];
    }
    getData() {
        const view_timeout = this.model.throttle.view || 200;
        const hover_timeout = this.model.throttle.hover || 100;
        const view_cb = debounce((event) => this._on_viewState_event(event), view_timeout, false);
        const hover_cb = debounce((event) => this._on_hover_event(event), hover_timeout, false);
        const data = {
            ...this.model.data,
            layers: this.model.layers,
            initialViewState: this.model.initialViewState,
            onViewStateChange: view_cb,
            onClick: (event) => this._on_click_event(event),
            onHover: hover_cb,
        };
        return data;
    }
    updateDeck() {
        if (!this.deckGL) {
            this.render();
            return;
        }
        const data = this.getData();
        if (window.deck.updateDeck) {
            window.deck.updateDeck(data, this.deckGL);
        }
        else {
            const results = this.jsonConverter.convert(data);
            this.deckGL.setProps(results);
        }
    }
    createDeck({ mapboxApiKey, container, jsonInput, tooltip }) {
        let deckgl;
        try {
            const props = this.jsonConverter.convert(jsonInput);
            const getTooltip = makeTooltip(tooltip, props.layers);
            deckgl = new window.deck.DeckGL({
                ...props,
                map: window.mapboxgl,
                mapboxApiAccessToken: mapboxApiKey,
                container,
                getTooltip,
                width: "100%",
                height: "100%",
            });
        }
        catch (err) {
            console.error(err);
        }
        return deckgl;
    }
    render() {
        super.render();
        const container = div({ class: "deckgl" });
        const MAPBOX_API_KEY = this.model.mapbox_api_key;
        const tooltip = this.model.tooltip;
        const data = this.getData();
        if (window.deck.createDeck) {
            this.deckGL = window.deck.createDeck({
                mapboxApiKey: MAPBOX_API_KEY,
                container,
                jsonInput: data,
                tooltip,
            });
        }
        else {
            this.deckGL = this.createDeck({
                mapboxApiKey: MAPBOX_API_KEY,
                container,
                jsonInput: data,
                tooltip,
            });
        }
        this.shadow_el.appendChild(container);
    }
    after_layout() {
        super.after_layout();
        this.deckGL.redraw(true);
    }
}
export class DeckGLPlot extends LayoutDOM {
    static __name__ = "DeckGLPlot";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.deckgl";
    static {
        this.prototype.default_view = DeckGLPlotView;
        this.define(({ Any, List, Str, Ref }) => ({
            data: [Any],
            data_sources: [List(Ref(ColumnDataSource)), []],
            clickState: [Any, {}],
            hoverState: [Any, {}],
            initialViewState: [Any, {}],
            layers: [List(Any), []],
            mapbox_api_key: [Str, ""],
            throttle: [Any, {}],
            tooltip: [Any, true],
            viewState: [Any, {}],
        }));
        this.override({
            height: 400,
            width: 600,
        });
    }
}
//# sourceMappingURL=deckgl.js.map