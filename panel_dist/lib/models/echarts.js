import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { div } from "@bokehjs/core/dom";
import { serializeEvent } from "./event-to-object";
import { HTMLBox, HTMLBoxView } from "./layout";
import { transformJsPlaceholders } from "./util";
const mouse_events = [
    "click", "dblclick", "mousedown", "mousemove", "mouseup", "mouseover", "mouseout",
    "globalout", "contextmenu",
];
const events = [
    "highlight", "downplay", "selectchanged", "legendselectchangedEvent", "legendselected",
    "legendunselected", "legendselectall", "legendinverseselect", "legendscroll", "datazoom",
    "datarangeselected", "timelineplaychanged", "restore", "dataviewchanged", "magictypechanged",
    "geoselectchanged", "geoselected", "geounselected", "axisareaselected", "brush", "brushEnd",
    "rushselected", "globalcursortaken", "rendered", "finished",
];
const all_events = mouse_events.concat(events);
export class EChartsEvent extends ModelEvent {
    type;
    data;
    query;
    static __name__ = "EChartsEvent";
    constructor(type, data, query) {
        super();
        this.type = type;
        this.data = data;
        this.query = query;
    }
    get event_values() {
        return { model: this.origin, type: this.type, data: this.data, query: this.query };
    }
    static {
        this.prototype.event_name = "echarts_event";
    }
}
export class EChartsView extends HTMLBoxView {
    static __name__ = "EChartsView";
    container;
    _chart;
    _callbacks = [];
    _loading_interval = null;
    _loading_timeout = null;
    _loading_el = null;
    connect_signals() {
        super.connect_signals();
        const { width, height, renderer, theme, event_config, js_events, data } = this.model.properties;
        this.on_change(data, () => this._plot());
        this.on_change([width, height], () => this._resize());
        this.on_change([theme, renderer], () => {
            this.render();
            if (this._chart != null) {
                this._chart.resize();
            }
        });
        this.on_change([event_config, js_events], () => this._subscribe());
    }
    render() {
        if (this._chart != null) {
            try {
                window.echarts.dispose(this._chart);
            }
            catch (e) {
                // dispose may fail if echarts was never fully initialized
            }
        }
        this._clear_loading_timer();
        super.render();
        this.container = div({ style: { height: "100%", width: "100%" } });
        this.shadow_el.append(this.container);
        if (window.echarts == null) {
            this._show_loading();
            this._await_echarts();
            return;
        }
        this._init_chart();
    }
    _show_loading() {
        this._loading_el = div({
            style: {
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                width: "100%",
                color: "#888",
                fontSize: "14px",
            },
        });
        this._loading_el.textContent = "Loading ECharts...";
        this.container.append(this._loading_el);
    }
    _hide_loading() {
        if (this._loading_el != null) {
            this._loading_el.remove();
            this._loading_el = null;
        }
    }
    _await_echarts() {
        // Try script onload listener first (event-driven, not polling)
        const script = document.querySelector("script[src*='echarts']");
        if (script != null) {
            const onLoad = () => {
                script.removeEventListener("load", onLoad);
                this._clear_loading_timer();
                this._hide_loading();
                this._init_chart();
            };
            script.addEventListener("load", onLoad);
        }
        // Polling fallback in case script tag isn't found or onload doesn't fire
        this._loading_interval = setInterval(() => {
            if (window.echarts != null) {
                this._clear_loading_timer();
                this._hide_loading();
                this._init_chart();
            }
        }, 50);
        this._loading_timeout = setTimeout(() => {
            this._clear_loading_timer();
            this._hide_loading();
            console.warn("ECharts library failed to load. Ensure you call pn.extension('echarts') " +
                "before using Gauge or ECharts components.");
        }, 10000);
    }
    _clear_loading_timer() {
        if (this._loading_interval != null) {
            clearInterval(this._loading_interval);
            this._loading_interval = null;
        }
        if (this._loading_timeout != null) {
            clearTimeout(this._loading_timeout);
            this._loading_timeout = null;
        }
    }
    _init_chart() {
        if (window.echarts == null) {
            return;
        }
        this._hide_loading();
        const config = { width: this.model.width, height: this.model.height, renderer: this.model.renderer };
        this._chart = window.echarts.init(this.container, this.model.theme, config);
        this._plot();
        this._subscribe();
    }
    remove() {
        this._clear_loading_timer();
        super.remove();
        if (this._chart != null) {
            try {
                window.echarts.dispose(this._chart);
            }
            catch (e) {
                // dispose may fail if echarts was never fully initialized
            }
        }
    }
    after_layout() {
        super.after_layout();
        if (this._chart != null) {
            this._chart.resize();
        }
    }
    _plot() {
        if (window.echarts == null || this._chart == null) {
            return;
        }
        const data = transformJsPlaceholders(this.model.data);
        this._chart.setOption(data, this.model.options);
    }
    _resize() {
        if (this._chart != null) {
            this._chart.resize({ width: this.model.width, height: this.model.height });
        }
    }
    _subscribe() {
        if (window.echarts == null || this._chart == null) {
            return;
        }
        for (const [event_type, callback] of this._callbacks) {
            this._chart.off(event_type, callback);
        }
        this._callbacks = [];
        for (const event_type in this.model.event_config) {
            if (!all_events.includes(event_type)) {
                console.warn(`Could not subscribe to unknown Echarts event: ${event_type}.`);
                continue;
            }
            const queries = this.model.event_config[event_type];
            for (const query of queries) {
                const callback = (event) => {
                    const processed = { ...event };
                    processed.event = serializeEvent(event.event?.event);
                    const serialized = JSON.parse(JSON.stringify(processed));
                    this.model.trigger_event(new EChartsEvent(event_type, serialized, query));
                };
                if (query != null) {
                    this._chart.on(event_type, query, callback);
                }
                else {
                    this._chart.on(event_type, callback);
                }
                this._callbacks.push([event_type, callback]);
            }
        }
        for (const event_type in this.model.js_events) {
            if (!all_events.includes(event_type)) {
                console.warn(`Could not subscribe to unknown Echarts event: ${event_type}.`);
                continue;
            }
            const handlers = this.model.js_events[event_type];
            for (const handler of handlers) {
                const callback = (event) => {
                    handler.callback.execute(this._chart, event);
                };
                if ("query" in handler) {
                    this._chart.on(event_type, handler.query, callback);
                }
                else {
                    this._chart.on(event_type, callback);
                }
                this._callbacks.push([event_type, callback]);
            }
        }
    }
}
export class ECharts extends HTMLBox {
    static __name__ = "ECharts";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.echarts";
    static {
        this.prototype.default_view = EChartsView;
        this.define(({ Any, Str }) => ({
            data: [Any, {}],
            options: [Any, {}],
            event_config: [Any, {}],
            js_events: [Any, {}],
            theme: [Str, "default"],
            renderer: [Str, "canvas"],
        }));
    }
}
//# sourceMappingURL=echarts.js.map