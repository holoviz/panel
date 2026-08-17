import { div, px } from "@bokehjs/core/dom";
import { isArray } from "@bokehjs/core/util/types";
import { unreachable } from "@bokehjs/core/util/assert";
import { WidgetView } from "@bokehjs/models/widgets/widget";
import { LayoutDOM, LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
/**
 * Re-renders a view, including its layout.
 *
 * Bokeh's own `rerender` runs the whole render walk before `update_layout`,
 * which is wrong for anything that is positioned by the layout: `render`
 * re-parents annotation elements into the canvas layers and it is
 * `update_layout` that moves them into their side panels. Measuring in
 * between therefore caches a bbox for the container the element is about to
 * leave, e.g. a legend measuring the full canvas width instead of its side
 * panel. `compute_layout` then sizes the panel from that stale bbox and can
 * squeeze the frame to zero, which poisons everything derived from it (for
 * tile-based plots, a division by zero width puts NaN into the ranges with no
 * recovery path). Updating the layout first means `after_render` measures
 * elements where they will actually live.
 */
export function rerender_view(view) {
    if (view instanceof LayoutDOMView) {
        view.render();
        view.update_layout();
        view.r_after_render();
        view.compute_layout();
    }
    else if (view.rerender) {
        // Can be removed when Bokeh>3.7 (see https://github.com/holoviz/panel/pull/7815)
        view.rerender();
    }
    else {
        view.render();
        view.r_after_render();
    }
}
export class PanelMarkupView extends WidgetView {
    static __name__ = "PanelMarkupView";
    container;
    _initialized_stylesheets;
    _stylesheets_watcher = null;
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
    /**
     * Schedules `style_redraw` for when all applied stylesheets have settled.
     *
     * A stylesheet counts as settled once it has loaded *or* failed: views
     * reveal their container from `style_redraw`, so a stylesheet that never
     * arrives must not hide them forever. Listeners registered by a previous
     * call are cancelled, since the elements they watch have been discarded.
     */
    watch_stylesheets() {
        this._stylesheets_watcher?.abort();
        const { signal } = this._stylesheets_watcher = new AbortController();
        this._initialized_stylesheets = new Map();
        for (const stylesheet of this._applied_stylesheets) {
            // @ts-expect-error: 'el' is protected
            const style_el = stylesheet.el;
            if (style_el instanceof HTMLLinkElement) {
                // A link served from cache may already have loaded, and `load` does
                // not fire again for it, so seed from `sheet` instead of assuming
                // every stylesheet is still pending.
                this._initialized_stylesheets.set(style_el.href, style_el.sheet != null);
                const settled = () => {
                    this._initialized_stylesheets.set(style_el.href, true);
                    if ([...this._initialized_stylesheets.values()].every((v) => v)) {
                        requestAnimationFrame(() => this.style_redraw());
                    }
                };
                style_el.addEventListener("load", settled, { signal });
                style_el.addEventListener("error", settled, { signal });
            }
        }
        if ([...this._initialized_stylesheets.values()].every((v) => v)) {
            this.style_redraw();
        }
    }
    /**
     * Bokeh recreates the stylesheet elements on every update, discarding the
     * ones `watch_stylesheets` listens on, so the watcher has to be re-armed.
     * Skipped until the view has armed it itself, as the update triggered from
     * `super.render()` precedes the creation of `this.container`.
     */
    _update_stylesheets() {
        super._update_stylesheets();
        if (this._stylesheets_watcher != null) {
            this.watch_stylesheets();
        }
    }
    rerender_(view = null) {
        rerender_view(view == null ? this : view);
    }
    style_redraw() { }
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
export function set_size(el, model, adjust_margin = true) {
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
                case "scale_width": {
                    width_policy = "max";
                    height_policy = "min";
                    break;
                }
                case "scale_height": {
                    width_policy = "min";
                    height_policy = "max";
                    break;
                }
                case "scale_both": {
                    width_policy = "max";
                    height_policy = "max";
                    break;
                }
                case "inherit": {
                    break;
                }
                default: {
                    unreachable();
                }
            }
        }
    }
    let wm, hm;
    if (!adjust_margin) {
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
    if (width_policy == "fixed" && model.width != null) {
        el.style.width = px(model.width);
    }
    else if (width_policy == "max") {
        el.style.width = wm != 0 ? `calc(100% - ${px(wm)})` : "100%";
    }
    if (model.min_width != null) {
        el.style.minWidth = px(model.min_width);
    }
    if (model.max_width != null) {
        el.style.maxWidth = px(model.max_width);
    }
    if (height_policy == "fixed" && model.height != null) {
        el.style.height = px(model.height);
    }
    else if (height_policy == "max") {
        el.style.height = hm != 0 ? `calc(100% - ${px(hm)})` : "100%";
    }
    if (model.min_height != null) {
        el.style.minHeight = px(model.min_height);
    }
    if (model.max_height != null) {
        el.style.maxHeight = px(model.max_height);
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
    rerender_(view = null) {
        rerender_view(view == null ? this : view);
    }
    watch_stylesheets() {
        this._initialized_stylesheets = new Map();
        for (const stylesheet of this._applied_stylesheets) {
            // @ts-expect-error: 'el' is protected
            const style_el = stylesheet.el;
            if (style_el instanceof HTMLLinkElement) {
                this._initialized_stylesheets.set(style_el.href, false);
                style_el.addEventListener("load", () => {
                    this._initialized_stylesheets.set(style_el.href, true);
                    if ([...this._initialized_stylesheets.values()].every((v) => v)) {
                        this.style_redraw();
                    }
                });
            }
        }
        // Unconditional: subclasses redraw (and reveal themselves) here even when
        // the stylesheets never load, so this is their only guaranteed redraw.
        requestAnimationFrame(() => this.style_redraw());
    }
    style_redraw() { }
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