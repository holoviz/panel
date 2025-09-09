import * as DOM from "@bokehjs/core/dom";
import { Container } from "@bokehjs/core/layout/grid";
import { GridAlignmentLayout } from "@bokehjs/models/layouts/alignments";
import { LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
import { Column, ColumnView } from "./column";
import card_css from "../styles/models/card.css";
const CHEVRON_RIGHT = `
<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-chevron-right"><path stroke="none" d="M0 0h12v12H0z" fill="none"/><path d="M9 6l6 6l-6 6" /></svg>
`;
const CHEVRON_DOWN = `
<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-chevron-down"><path stroke="none" d="M0 0h12v12H0z" fill="none"/><path d="M6 9l6 6l6 -6" /></svg>
`;
export class CardView extends ColumnView {
    static __name__ = "CardView";
    button_el;
    header_el;
    collapsed_style = new DOM.InlineStyleSheet();
    connect_signals() {
        super.connect_signals();
        const { active_header_background, collapsed, header_background, header_color, hide_header } = this.model.properties;
        this.on_change(collapsed, () => this._collapse());
        this.on_change([header_color, hide_header], () => this.render());
        this.on_change([active_header_background, collapsed, header_background], () => {
            const header_background = this.header_background;
            if (header_background == null) {
                return;
            }
            this.child_views[0].el.style.backgroundColor = header_background;
            this.header_el.style.backgroundColor = header_background;
        });
    }
    stylesheets() {
        return [...super.stylesheets(), card_css];
    }
    *_stylesheets() {
        yield* super._stylesheets();
        yield this.collapsed_style;
    }
    get header_background() {
        let header_background = this.model.header_background;
        if (!this.model.collapsed && this.model.active_header_background) {
            header_background = this.model.active_header_background;
        }
        return header_background;
    }
    render() {
        this.empty();
        if (this.model.collapsed) {
            this.collapsed_style.replace(":host", {
                height: "fit-content",
                flex: "none",
            });
        }
        this._update_stylesheets();
        this._update_css_classes();
        this._apply_styles();
        this._apply_visible();
        this.class_list.add(...this.css_classes());
        const { button_css_classes, header_color, header_tag, header_css_classes } = this.model;
        const header_background = this.header_background;
        const header = this.child_views[0];
        let header_el;
        if (this.model.collapsible) {
            this.button_el = DOM.button({ class: header_css_classes });
            const icon = DOM.div({ class: button_css_classes });
            icon.innerHTML = this.model.collapsed ? CHEVRON_RIGHT : CHEVRON_DOWN;
            this.button_el.appendChild(icon);
            this.button_el.style.backgroundColor = header_background != null ? header_background : "";
            header.el.style.backgroundColor = header_background != null ? header_background : "";
            this.button_el.appendChild(header.el);
            this.button_el.addEventListener("click", (e) => this._toggle_button(e));
            header_el = this.button_el;
        }
        else {
            header_el = DOM.create_element(header_tag, { class: header_css_classes });
            header_el.style.backgroundColor = header_background != null ? header_background : "";
            header_el.appendChild(header.el);
        }
        this.header_el = header_el;
        if (!this.model.hide_header) {
            header_el.style.color = header_color != null ? header_color : "";
            this.shadow_el.appendChild(header_el);
            header.render();
            header.r_after_render();
        }
        if (this.model.collapsed) {
            return;
        }
        for (const child_view of this.child_views.slice(1)) {
            this.shadow_el.appendChild(child_view.el);
            child_view.render();
            child_view.r_after_render();
        }
    }
    async update_children() {
        await this.build_child_views();
        this.render();
        this.invalidate_layout();
    }
    _update_layout() {
        super._update_layout();
        this.style.append(":host", {
            flex_direction: this._direction,
            gap: DOM.px(this.model.spacing),
        });
        const layoutable = new Container();
        let r0 = 0;
        let c0 = 0;
        for (let i = 0; i < this.child_views.length; i++) {
            const view = this.child_views[i];
            if (!(view instanceof LayoutDOMView)) {
                continue;
            }
            const is_row = i == 0;
            const sizing = view.box_sizing();
            const flex = (() => {
                const policy = is_row ? sizing.width_policy : sizing.height_policy;
                const size = is_row ? sizing.width : sizing.height;
                const basis = size != null ? DOM.px(size) : "auto";
                switch (policy) {
                    case "auto":
                    case "fixed": return `0 0 ${basis}`;
                    case "fit": return "1 1 auto";
                    case "min": return "0 1 auto";
                    case "max": return "1 0 0px";
                }
            })();
            const align_self = (() => {
                const policy = is_row ? sizing.height_policy : sizing.width_policy;
                switch (policy) {
                    case "auto":
                    case "fixed":
                    case "fit":
                    case "min": return is_row ? sizing.valign : sizing.halign;
                    case "max": return "stretch";
                }
            })();
            view.parent_style.append(":host", { flex, align_self });
            // undo `width/height: 100%` and let `align-self: stretch` do the work
            if (is_row) {
                if (sizing.height_policy == "max") {
                    view.parent_style.append(":host", { height: "auto" });
                }
            }
            else {
                if (sizing.width_policy == "max") {
                    view.parent_style.append(":host", { width: "auto" });
                }
            }
            if (view.layout != null) {
                layoutable.add({ r0, c0, r1: r0 + 1, c1: c0 + 1 }, view);
                if (is_row) {
                    c0 += 1;
                }
                else {
                    r0 += 1;
                }
            }
        }
        if (layoutable.size != 0) {
            this.layout = new GridAlignmentLayout(layoutable);
            this.layout.set_sizing();
        }
        else {
            delete this.layout;
        }
    }
    _toggle_button(e) {
        for (const path of e.composedPath()) {
            if (path instanceof HTMLInputElement) {
                return;
            }
        }
        this.model.collapsed = !this.model.collapsed;
    }
    _collapse() {
        for (const child_view of this.child_views.slice(1)) {
            if (this.model.collapsed) {
                this.shadow_el.removeChild(child_view.el);
                child_view.model.visible = false;
            }
            else {
                child_view.render();
                child_view.after_render();
                this.shadow_el.appendChild(child_view.el);
                child_view.model.visible = true;
            }
        }
        if (this.model.collapsed) {
            this.collapsed_style.replace(":host", {
                height: "fit-content",
                flex: "none",
            });
        }
        else {
            this.collapsed_style.clear();
        }
        this.button_el.children[0].innerHTML = this.model.collapsed ? CHEVRON_RIGHT : CHEVRON_DOWN;
        this.invalidate_layout();
    }
    _create_element() {
        return DOM.create_element(this.model.tag, { class: this.css_classes() });
    }
}
export class Card extends Column {
    static __name__ = "Card";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.layout";
    static {
        this.prototype.default_view = CardView;
        this.define(({ List, Bool, Nullable, Str }) => ({
            active_header_background: [Nullable(Str), null],
            button_css_classes: [List(Str), []],
            collapsed: [Bool, true],
            collapsible: [Bool, true],
            header_background: [Nullable(Str), null],
            header_color: [Nullable(Str), null],
            header_css_classes: [List(Str), []],
            header_tag: [Str, "div"],
            hide_header: [Bool, false],
            tag: [Str, "div"],
        }));
    }
}
//# sourceMappingURL=card.js.map