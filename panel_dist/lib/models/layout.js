import { div } from "@bokehjs/core/dom";
import { isArray } from "@bokehjs/core/util/types";
import { WidgetView } from "@bokehjs/models/widgets/widget";
import { LayoutDOM, LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
export class PanelMarkupView extends WidgetView {
    static __name__ = "PanelMarkupView";
    container;
    _initialized_stylesheets;
    connect_signals() {
        super.connect_signals();
        const { width, height, min_height, max_height, margin, sizing_mode } = this.model.properties;
        this.on_change([width, height, min_height, max_height, margin, sizing_mode], () => {
            set_size(this.el, this.model);
            set_size(this.container, this.model, false);
        });
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        if (this.provider.status == "not_started" || this.provider.status == "loading") {
            this.provider.ready.connect(() => {
                if (this.contains_tex_string(this.model.text)) {
                    this.render();
                }
            });
        }
    }
    watch_stylesheets() {
        this._initialized_stylesheets = {};
        for (const sts of this._applied_stylesheets) {
            const style_el = sts.el;
            if (style_el instanceof HTMLLinkElement) {
                this._initialized_stylesheets[style_el.href] = false;
                style_el.addEventListener("load", () => {
                    this._initialized_stylesheets[style_el.href] = true;
                    if (Object.values(this._initialized_stylesheets).every(Boolean)) {
                        this.style_redraw();
                    }
                });
            }
        }
        if (Object.keys(this._initialized_stylesheets).length === 0) {
            this.style_redraw();
        }
    }
    style_redraw() {
    }
    has_math_disabled() {
        return this.model.disable_math || !this.contains_tex_string(this.model.text);
    }
    render() {
        super.render();
        set_size(this.el, this.model);
        this.container = div();
        set_size(this.container, this.model, false);
        this.shadow_el.appendChild(this.container);
        if (this.provider.status == "failed" || this.provider.status == "loaded") {
            this._has_finished = true;
        }
    }
}
export function set_size(el, model, adjustMargin = true) {
    let width_policy = model.width != null ? "fixed" : "fit";
    let height_policy = model.height != null ? "fixed" : "fit";
    const { sizing_mode, margin } = model;
    if (sizing_mode != null) {
        if (sizing_mode == "fixed") {
            width_policy = height_policy = "fixed";
        }
        else if (sizing_mode == "stretch_both") {
            width_policy = height_policy = "max";
        }
        else if (sizing_mode == "stretch_width") {
            width_policy = "max";
        }
        else if (sizing_mode == "stretch_height") {
            height_policy = "max";
        }
        else {
            switch (sizing_mode) {
                case "scale_width":
                    width_policy = "max";
                    height_policy = "min";
                    break;
                case "scale_height":
                    width_policy = "min";
                    height_policy = "max";
                    break;
                case "scale_both":
                    width_policy = "max";
                    height_policy = "max";
                    break;
                default:
                    throw new Error("unreachable");
            }
        }
    }
    let wm, hm;
    if (!adjustMargin) {
        hm = wm = 0;
    }
    else if (isArray(margin)) {
        if (margin.length === 4) {
            hm = margin[0] + margin[2];
            wm = margin[1] + margin[3];
        }
        else {
            hm = margin[0] * 2;
            wm = margin[1] * 2;
        }
    }
    else if (margin == null) {
        hm = wm = 0;
    }
    else {
        wm = hm = margin * 2;
    }
    if (width_policy == "fixed" && model.width) {
        el.style.width = `${model.width}px`;
    }
    else if (width_policy == "max") {
        el.style.width = wm ? `calc(100% - ${wm}px)` : "100%";
    }
    if (model.min_width != null) {
        el.style.minWidth = `${model.min_width}px`;
    }
    if (model.max_width != null) {
        el.style.maxWidth = `${model.max_width}px`;
    }
    if (height_policy == "fixed" && model.height) {
        el.style.height = `${model.height}px`;
    }
    else if (height_policy == "max") {
        el.style.height = hm ? `calc(100% - ${hm}px)` : "100%";
    }
    if (model.min_height != null) {
        el.style.minHeight = `${model.min_height}px`;
    }
    if (model.max_width != null) {
        el.style.maxHeight = `${model.max_height}px`;
    }
}
export class HTMLBoxView extends LayoutDOMView {
    static __name__ = "HTMLBoxView";
    _initialized_stylesheets;
    connect_signals() {
        super.connect_signals();
        const { width, height, min_height, max_height, margin, sizing_mode } = this.model.properties;
        this.on_change([width, height, min_height, max_height, margin, sizing_mode], () => {
            set_size(this.el, this.model);
        });
    }
    render() {
        super.render();
        set_size(this.el, this.model);
    }
    watch_stylesheets() {
        this._initialized_stylesheets = {};
        for (const sts of this._applied_stylesheets) {
            const style_el = sts.el;
            if (style_el instanceof HTMLLinkElement) {
                this._initialized_stylesheets[style_el.href] = false;
                style_el.addEventListener("load", () => {
                    this._initialized_stylesheets[style_el.href] = true;
                    if (Object.values(this._initialized_stylesheets).every(Boolean)) {
                        this.style_redraw();
                    }
                });
            }
        }
    }
    style_redraw() {
    }
    get child_models() {
        return [];
    }
}
export class HTMLBox extends LayoutDOM {
    static __name__ = "HTMLBox";
    constructor(attrs) {
        super(attrs);
    }
}
//# sourceMappingURL=layout.js.map