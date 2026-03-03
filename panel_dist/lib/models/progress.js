import { ImportedStyleSheet } from "@bokehjs/core/dom";
import { HTMLBox, HTMLBoxView } from "./layout";
export class ProgressView extends HTMLBoxView {
    static __name__ = "ProgressView";
    progressEl;
    connect_signals() {
        super.connect_signals();
        const { width, height, height_policy, width_policy, sizing_mode, active, bar_color, css_classes, value, max, } = this.model.properties;
        this.on_change([width, height, height_policy, width_policy, sizing_mode], () => this.rerender_());
        this.on_change([active, bar_color, css_classes], () => this.setCSS());
        this.on_change(value, () => this.setValue());
        this.on_change(max, () => this.setMax());
    }
    render() {
        super.render();
        const style = { ...this.model.styles, display: "inline-block" };
        this.progressEl = document.createElement("progress");
        this.setValue();
        this.setMax();
        // Set styling
        this.setCSS();
        for (const prop in style) {
            this.progressEl.style.setProperty(prop, style[prop]);
        }
        this.shadow_el.appendChild(this.progressEl);
    }
    stylesheets() {
        const styles = super.stylesheets();
        for (const css of this.model.css) {
            styles.push(new ImportedStyleSheet(css));
        }
        return styles;
    }
    setCSS() {
        let css = `${this.model.css_classes.join(" ")} ${this.model.bar_color}`;
        if (this.model.active) {
            css = `${css} active`;
        }
        this.progressEl.className = css;
    }
    setValue() {
        if (this.model.value == null) {
            this.progressEl.value = 0;
        }
        else if (this.model.value >= 0) {
            this.progressEl.value = this.model.value;
        }
        else if (this.model.value < 0) {
            this.progressEl.removeAttribute("value");
        }
    }
    setMax() {
        if (this.model.max != null) {
            this.progressEl.max = this.model.max;
        }
    }
}
export class Progress extends HTMLBox {
    static __name__ = "Progress";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = ProgressView;
        this.define(({ Any, List, Bool, Float, Str }) => ({
            active: [Bool, true],
            bar_color: [Str, "primary"],
            css: [List(Str), []],
            max: [Float, 100],
            value: [Any, null],
        }));
    }
}
//# sourceMappingURL=progress.js.map