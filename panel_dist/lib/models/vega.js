import { div } from "@bokehjs/core/dom";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { isArray } from "@bokehjs/core/util/types";
import { LayoutDOM, LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
import { set_size } from "./layout";
import { debounce } from "debounce";
export class VegaEvent extends ModelEvent {
    data;
    static __name__ = "VegaEvent";
    constructor(data) {
        super();
        this.data = data;
    }
    get event_values() {
        return { model: this.origin, data: this.data };
    }
    static {
        this.prototype.event_name = "vega_event";
    }
}
export class VegaPlotView extends LayoutDOMView {
    static __name__ = "VegaPlotView";
    vega_view;
    container;
    _callbacks;
    _connected;
    _replot;
    _resize;
    _rendered = false;
    connect_signals() {
        super.connect_signals();
        const { data, show_actions, theme, data_sources, events } = this.model.properties;
        this._replot = debounce(() => this._plot(), 20);
        this.on_change([data, show_actions, theme], () => {
            this._replot();
        });
        this.on_change(data_sources, () => this._connect_sources());
        this.on_change(events, () => {
            for (const event of this.model.events) {
                if (this._callbacks.indexOf(event) > -1) {
                    continue;
                }
                this._callbacks.push(event);
                const callback = (name, value) => this._dispatch_event(name, value);
                const timeout = this.model.throttle[event] || 20;
                this.vega_view.addSignalListener(event, debounce(callback, timeout, false));
            }
        });
        this._connected = [];
        this._connect_sources();
    }
    _connect_sources() {
        for (const ds in this.model.data_sources) {
            const cds = this.model.data_sources[ds];
            if (this._connected.indexOf(ds) < 0) {
                this.connect(cds.properties.data.change, () => this._replot());
                this._connected.push(ds);
            }
        }
    }
    remove() {
        if (this.vega_view) {
            this.vega_view.finalize();
        }
        super.remove();
    }
    _dispatch_event(name, value) {
        if ("vlPoint" in value && value.vlPoint.or != null) {
            const indexes = [];
            for (const index of value.vlPoint.or) {
                if (index._vgsid_ !== undefined) { // If "_vgsid_" property exists
                    indexes.push(index._vgsid_);
                }
                else { // If "_vgsid_" property doesn't exist
                    // Iterate through all properties in the "index" object
                    for (const key in index) {
                        if (index.hasOwnProperty(key)) { // To ensure key comes from "index" object itself, not its prototype
                            indexes.push({ [key]: index[key] }); // Push a new object with this key-value pair into the array
                        }
                    }
                }
            }
            value = indexes;
        }
        this.model.trigger_event(new VegaEvent({ type: name, value }));
    }
    _fetch_datasets() {
        const datasets = {};
        for (const ds in this.model.data_sources) {
            const cds = this.model.data_sources[ds];
            const data = [];
            const columns = cds.columns();
            for (let i = 0; i < cds.get_length(); i++) {
                const item = {};
                for (const column of columns) {
                    item[column] = cds.data[column][i];
                }
                data.push(item);
            }
            datasets[ds] = data;
        }
        return datasets;
    }
    get child_models() {
        return [];
    }
    render() {
        super.render();
        this._rendered = false;
        this.container = div();
        set_size(this.container, this.model);
        this._callbacks = [];
        this._plot();
        this.shadow_el.append(this.container);
    }
    _plot() {
        const data = this.model.data;
        if ((data == null) || !window.vegaEmbed) {
            return;
        }
        if (this.model.data_sources && (Object.keys(this.model.data_sources).length > 0)) {
            const datasets = this._fetch_datasets();
            if ("data" in datasets) {
                data.data.values = datasets.data;
                delete datasets.data;
            }
            if (data.data != null) {
                const data_objs = isArray(data.data) ? data.data : [data.data];
                for (const d of data_objs) {
                    if (d.name in datasets) {
                        d.values = datasets[d.name];
                        delete datasets[d.name];
                    }
                }
            }
            this.model.data.datasets = datasets;
        }
        const config = { actions: this.model.show_actions, theme: this.model.theme };
        window.vegaEmbed(this.container, this.model.data, config).then((result) => {
            this.vega_view = result.view;
            this._resize = debounce(() => this.resize_view(result.view), 50);
            const callback = (name, value) => this._dispatch_event(name, value);
            for (const event of this.model.events) {
                this._callbacks.push(event);
                const timeout = this.model.throttle[event] || 20;
                this.vega_view.addSignalListener(event, debounce(callback, timeout, false));
            }
        });
    }
    after_layout() {
        super.after_layout();
        if (this.vega_view != null) {
            this._resize();
        }
    }
    resize_view(view) {
        const canvas = view._renderer.canvas();
        if (!this._rendered && canvas !== null) {
            for (const listener of view._eventListeners) {
                if (listener.type === "resize") {
                    listener.handler(new Event("resize"));
                }
            }
            this._rendered = true;
        }
    }
}
export class VegaPlot extends LayoutDOM {
    static __name__ = "VegaPlot";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.vega";
    static {
        this.prototype.default_view = VegaPlotView;
        this.define(({ Any, List, Bool, Nullable, Str }) => ({
            data: [Any, {}],
            data_sources: [Any, {}],
            events: [List(Str), []],
            show_actions: [Bool, false],
            theme: [Nullable(Str), null],
            throttle: [Any, {}],
        }));
    }
}
//# sourceMappingURL=vega.js.map