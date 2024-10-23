import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { div } from "@bokehjs/core/dom";
import { Column as BkColumn, ColumnView as BkColumnView } from "@bokehjs/models/layouts/column";
export class ScrollButtonClick extends ModelEvent {
    static __name__ = "ScrollButtonClick";
    static {
        this.prototype.event_name = "scroll_button_click";
    }
}
export class ColumnView extends BkColumnView {
    static __name__ = "ColumnView";
    _updating = false;
    scroll_down_button_el;
    connect_signals() {
        super.connect_signals();
        const { children, scroll_position, scroll_button_threshold } = this.model.properties;
        this.on_change(children, () => this.trigger_auto_scroll());
        this.on_change(scroll_position, () => this.scroll_to_position());
        this.on_change(scroll_button_threshold, () => this.toggle_scroll_button());
    }
    get distance_from_latest() {
        return this.el.scrollHeight - this.el.scrollTop - this.el.clientHeight;
    }
    scroll_to_position() {
        if (this._updating) {
            return;
        }
        requestAnimationFrame(() => {
            this.el.scrollTo({ top: this.model.scroll_position, behavior: "instant" });
        });
    }
    scroll_to_latest() {
        // Waits for the child to be rendered before scrolling
        requestAnimationFrame(() => {
            this.model.scroll_position = Math.round(this.el.scrollHeight);
        });
    }
    trigger_auto_scroll() {
        const limit = this.model.auto_scroll_limit;
        if (limit == 0) {
            return;
        }
        const within_limit = this.distance_from_latest <= limit;
        if (!within_limit) {
            return;
        }
        this.scroll_to_latest();
    }
    record_scroll_position() {
        this._updating = true;
        this.model.scroll_position = Math.round(this.el.scrollTop);
        this._updating = false;
    }
    toggle_scroll_button() {
        const threshold = this.model.scroll_button_threshold;
        if (!this.scroll_down_button_el || threshold === 0) {
            return;
        }
        const exceeds_threshold = this.distance_from_latest >= threshold;
        this.scroll_down_button_el.classList.toggle("visible", exceeds_threshold);
    }
    render() {
        super.render();
        this.scroll_down_button_el = div({ class: "scroll-button" });
        this.shadow_el.appendChild(this.scroll_down_button_el);
        this.el.addEventListener("scroll", () => {
            this.record_scroll_position();
            this.toggle_scroll_button();
        });
        this.scroll_down_button_el.addEventListener("click", () => {
            this.scroll_to_latest();
            this.model.trigger_event(new ScrollButtonClick());
        });
    }
    after_render() {
        super.after_render();
        requestAnimationFrame(() => {
            if (this.model.scroll_position) {
                this.scroll_to_position();
            }
            if (this.model.view_latest) {
                this.scroll_to_latest();
            }
            this.toggle_scroll_button();
        });
    }
}
export class Column extends BkColumn {
    static __name__ = "Column";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.layout";
    static {
        this.prototype.default_view = ColumnView;
        this.define(({ Int, Bool }) => ({
            scroll_position: [Int, 0],
            auto_scroll_limit: [Int, 0],
            scroll_button_threshold: [Int, 0],
            view_latest: [Bool, false],
        }));
    }
    on_click(callback) {
        this.on_event(ScrollButtonClick, callback);
    }
}
//# sourceMappingURL=column.js.map