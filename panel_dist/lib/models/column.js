var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var ScrollToEvent_1;
import { ModelEvent, server_event } from "@bokehjs/core/bokeh_events";
import { div } from "@bokehjs/core/dom";
import { Column as BkColumn, ColumnView as BkColumnView } from "@bokehjs/models/layouts/column";
export class ScrollButtonClick extends ModelEvent {
    static __name__ = "ScrollButtonClick";
    static {
        this.prototype.event_name = "scroll_button_click";
    }
}
let ScrollToEvent = class ScrollToEvent extends ModelEvent {
    static { ScrollToEvent_1 = this; }
    model;
    index;
    static __name__ = "ScrollToEvent";
    constructor(model, index) {
        super();
        this.model = model;
        this.index = index;
        this.index = index;
        this.origin = model;
    }
    get event_values() {
        return { model: this.origin, index: this.index };
    }
    static from_values(values) {
        const { model, index } = values;
        return new ScrollToEvent_1(model, index);
    }
};
ScrollToEvent = ScrollToEvent_1 = __decorate([
    server_event("scroll_to")
], ScrollToEvent);
export { ScrollToEvent };
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
        this.model.on_event(ScrollToEvent, (event) => this.scroll_to_index(event.index));
    }
    get distance_from_latest() {
        return this.el.scrollHeight - this.el.scrollTop - this.el.clientHeight;
    }
    scroll_to_index(index) {
        if (index === null) {
            return;
        }
        if (index >= this.model.children.length) {
            console.warn(`Invalid scroll index: ${index}`);
            return;
        }
        // Get the child view at the specified index
        const childView = this.child_views[index];
        if (!childView) {
            console.warn(`Child view not found for index: ${index}`);
            return;
        }
        // Get the top position of the child element relative to the column
        const childEl = childView.el;
        const childRect = childEl.getBoundingClientRect();
        const columnRect = this.el.getBoundingClientRect();
        const relativeTop = childRect.top - columnRect.top + this.el.scrollTop;
        // Scroll to the child's position
        this.model.scroll_position = Math.round(relativeTop);
    }
    scroll_to_position() {
        if (this._updating) {
            return;
        }
        requestAnimationFrame(() => {
            this.el.scrollTo({ top: this.model.scroll_position, behavior: "instant" });
        });
    }
    scroll_to_latest(scroll_limit = null) {
        if (scroll_limit !== null) {
            const within_limit = this.distance_from_latest <= scroll_limit;
            if (!within_limit) {
                return;
            }
        }
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
        this.define(({ Int, Bool, Nullable }) => ({
            scroll_position: [Int, 0],
            scroll_index: [Nullable(Int), null],
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