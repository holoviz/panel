import { div } from "@bokehjs/core/dom";
import { isArray, isObject } from "@bokehjs/core/util/types";
import { ColumnDataSource } from "@bokehjs/models/sources/column_data_source";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { debounce } from "debounce";
import { HTMLBox, HTMLBoxView } from "./layout";
export class VizzuEvent extends ModelEvent {
    data;
    static __name__ = "VizzuEvent";
    event_name = "vizzu_event";
    publish = true;
    constructor(data) {
        super();
        this.data = data;
    }
    get event_values() {
        return { model: this.origin, data: this.data };
    }
}
const VECTORIZED_PROPERTIES = ["x", "y", "color", "label", "lightness", "size", "splittedBy", "dividedBy"];
export class VizzuChartView extends HTMLBoxView {
    static __name__ = "VizzuChartView";
    container;
    update = [];
    vizzu_view;
    _animating = false;
    connect_signals() {
        super.connect_signals();
        const update = debounce(() => {
            if (!this.valid_config) {
                console.warn("Vizzu config not valid given current data.");
                return;
            }
            else if ((this.update.length === 0) || this._animating) {
                return;
            }
            else {
                let change = {};
                for (const prop of this.update) {
                    if (prop === "config") {
                        change = { ...change, config: this.config() };
                    }
                    else if (prop === "data") {
                        change = { ...change, data: this.data() };
                    }
                    else {
                        change = { ...change, style: this.model.style };
                    }
                }
                this._animating = true;
                this.vizzu_view.animate(change, `${this.model.duration}ms`).then(() => {
                    this._animating = false;
                    if (this.update.length > 0) {
                        update();
                    }
                });
                this.update = [];
            }
        }, 20);
        const update_prop = (prop) => {
            if (!this.update.includes(prop)) {
                this.update.push(prop);
            }
            update();
        };
        const { config, tooltip, style } = this.model.properties;
        this.on_change(config, () => update_prop("config"));
        this.on_change(this.model.source.properties.data, () => update_prop("data"));
        this.connect(this.model.source.streaming, () => update_prop("data"));
        this.connect(this.model.source.patching, () => update_prop("data"));
        this.on_change(tooltip, () => {
            this.vizzu_view.feature("tooltip", this.model.tooltip);
        });
        this.on_change(style, () => update_prop("style"));
    }
    get valid_config() {
        const columns = this.model.source.columns();
        if ("channels" in this.model.config) {
            for (const col of Object.values(this.model.config.channels)) {
                if (isArray(col)) {
                    for (const c of col) {
                        if (col != null && !columns.includes(c)) {
                            return false;
                        }
                    }
                }
                else if (isObject(col)) {
                    for (const prop of Object.keys(col)) {
                        for (const c of col[prop]) {
                            if (col != null && !columns.includes(c)) {
                                return false;
                            }
                        }
                    }
                }
                else if (col != null && !columns.includes(col)) {
                    return false;
                }
            }
        }
        else {
            for (const prop of VECTORIZED_PROPERTIES) {
                if (prop in this.model.config && !columns.includes(this.model.config[prop])) {
                    return false;
                }
            }
        }
        return true;
    }
    config() {
        let config = { ...this.model.config };
        if ("channels" in config) {
            config.channels = { ...config.channels };
        }
        if (config.preset != undefined) {
            config = window.Vizzu.presets[config.preset](config);
        }
        return config;
    }
    data() {
        const series = [];
        for (const column of this.model.columns) {
            let array = [...this.model.source.get_array(column.name)];
            if (column.type === "datetime" || column.type == "date") {
                column.type = "dimension";
            }
            if (column.type === "dimension") {
                array = array.map(String);
            }
            series.push({ ...column, values: array });
        }
        return { series };
    }
    render() {
        super.render();
        this.container = div({ style: { display: "contents" } });
        this.shadow_el.append(this.container);
        const state = { config: this.config(), data: this.data(), style: this.model.style };
        this.vizzu_view = new window.Vizzu(this.container, state);
        this._animating = true;
        this.vizzu_view.initializing.then((chart) => {
            chart.on("click", (event) => {
                this.model.trigger_event(new VizzuEvent({ ...event.target, ...event.detail }));
            });
            chart.feature("tooltip", this.model.tooltip);
            this._animating = false;
        });
    }
    remove() {
        if (this.vizzu_view) {
            this.vizzu_view.detach();
        }
        super.remove();
    }
}
export class VizzuChart extends HTMLBox {
    static __name__ = "VizzuChart";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.vizzu";
    static {
        this.prototype.default_view = VizzuChartView;
        this.define(({ Any, List, Bool, Float, Ref }) => ({
            animation: [Any, {}],
            config: [Any, {}],
            columns: [List(Any), []],
            source: [Ref(ColumnDataSource)],
            duration: [Float, 500],
            style: [Any, {}],
            tooltip: [Bool, false],
        }));
    }
}
//# sourceMappingURL=vizzu.js.map