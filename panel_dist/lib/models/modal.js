var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var ModalDialogEvent_1;
import { Column as BkColumn, ColumnView as BkColumnView } from "@bokehjs/models/layouts/column";
import { div, button } from "@bokehjs/core/dom";
import { ModelEvent, server_event } from "@bokehjs/core/bokeh_events";
import { UIElementView } from "@bokehjs/models/ui/ui_element";
import { isNumber } from "@bokehjs/core/util/types";
import { LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
import modal_css from "../styles/models/modal.css";
let ModalDialogEvent = class ModalDialogEvent extends ModelEvent {
    static { ModalDialogEvent_1 = this; }
    static __name__ = "ModalDialogEvent";
    open;
    constructor(open) {
        super();
        this.open = open;
    }
    get event_values() {
        return { open: this.open };
    }
    static from_values(values) {
        const { open } = values;
        return new ModalDialogEvent_1(open);
    }
};
ModalDialogEvent = ModalDialogEvent_1 = __decorate([
    server_event("modal-dialog-event")
], ModalDialogEvent);
export { ModalDialogEvent };
export class ModalView extends BkColumnView {
    static __name__ = "ModalView";
    modal;
    close_button;
    connect_signals() {
        super.connect_signals();
        const { show_close_button } = this.model.properties;
        this.on_change([show_close_button], this.update_close_button);
        this.model.on_event(ModalDialogEvent, (event) => {
            event.open ? this.modal.show() : this.modal.hide();
        });
    }
    render() {
        UIElementView.prototype.render.call(this);
        this.class_list.add(...this.css_classes());
        this.create_modal();
    }
    stylesheets() {
        return [...super.stylesheets(), modal_css];
    }
    async update_children() {
        await LayoutDOMView.prototype.update_children.call(this);
    }
    create_modal() {
        const dialog = div({
            id: "pnx_dialog",
            class: "dialog-container bk-root",
            style: { display: "none" },
        });
        const dialog_overlay = div({ class: "dialog-overlay" });
        if (this.model.background_close) {
            dialog_overlay.setAttribute("data-a11y-dialog-hide", "");
        }
        const { height, width, min_height, min_width, max_height, max_width } = this.model;
        const content = div({
            id: "pnx_dialog_content",
            class: "dialog-content",
            role: "document",
            style: {
                height: isNumber(height) ? `${height}px` : height,
                width: isNumber(width) ? `${width}px` : width,
                min_height: isNumber(min_height) ? `${min_height}px` : min_height,
                min_width: isNumber(min_width) ? `${min_width}px` : min_width,
                max_height: isNumber(max_height) ? `${max_height}px` : max_height,
                max_width: isNumber(max_width) ? `${max_width}px` : max_width,
                overflow: "auto",
            },
        });
        for (const child_view of this.child_views) {
            const target = child_view.rendering_target() ?? content;
            child_view.render_to(target);
        }
        this.close_button = button({
            id: "pnx_dialog_close",
            "data-a11y-dialog-hide": "",
            class: "pnx-dialog-close",
            ariaLabel: "Close this dialog window",
        });
        this.close_button.innerHTML = "&#x2715";
        dialog.append(dialog_overlay);
        dialog.append(content);
        content.append(this.close_button);
        this.shadow_el.append(dialog);
        let first_open = false;
        this.modal = new A11yDialog(dialog);
        this.update_close_button();
        this.modal.on("show", () => {
            this.model.open = true;
            dialog.style.display = "";
            if (!first_open) {
                requestAnimationFrame(() => { this.invalidate_layout(); });
                first_open = true;
            }
        });
        this.modal.on("hide", () => {
            this.model.open = false;
            dialog.style.display = "none";
        });
        if (this.model.open) {
            this.modal.show();
        }
    }
    update_close_button() {
        if (this.model.show_close_button) {
            this.close_button.style.display = "block";
        }
        else {
            this.close_button.style.display = "none";
        }
    }
}
export class Modal extends BkColumn {
    static __name__ = "Modal";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.modal";
    static {
        this.prototype.default_view = ModalView;
        this.define(({ Bool }) => ({
            open: [Bool, false],
            show_close_button: [Bool, true],
            background_close: [Bool, true],
        }));
    }
}
//# sourceMappingURL=modal.js.map