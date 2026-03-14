import type * as p from "@bokehjs/core/properties"
import {Column as BkColumn, ColumnView as BkColumnView} from "@bokehjs/models/layouts/column"
import {div, button} from "@bokehjs/core/dom"
import {ModelEvent, server_event} from "@bokehjs/core/bokeh_events"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import type {Attrs} from "@bokehjs/core/types"
import {UIElementView} from "@bokehjs/models/ui/ui_element"
import {isNumber} from "@bokehjs/core/util/types"

import modal_css from "styles/models/modal.css"

declare type A11yDialogView = {
  on(event: string, listener: () => void): void
  show(): void
  hide(): void
}

declare interface A11yDialogInterface { new (container: HTMLElement): A11yDialogView }
declare const A11yDialog: A11yDialogInterface

@server_event("modal-dialog-event")
export class ModalDialogEvent extends ModelEvent {
  constructor(readonly model: Modal, readonly open: boolean) {
    super()
    this.open = open
    this.origin = model
  }

  protected override get event_values(): Attrs {
    return {open: this.open, origin: this.origin}
  }

  static override from_values(values: object) {
    const {open, model} = values as {open: boolean, model: Modal}
    return new ModalDialogEvent(model, open)
  }
}

export class ModalView extends BkColumnView {
  declare model: Modal

  modal: A11yDialogView
  close_button: HTMLButtonElement
  content: HTMLElement

  override connect_signals(): void {
    super.connect_signals()
    const {show_close_button} = this.model.properties
    this.on_change([show_close_button], this.update_close_button)
    this.model.on_event(ModalDialogEvent, (event) => {
      event.open ? this.modal.show() : this.modal.hide()
    })
  }

  override render(): void {
    UIElementView.prototype.render.call(this)
    this.class_list.add(...this.css_classes())
    this.create_modal()
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), modal_css]
  }

  override async update_children(): Promise<void> {
    const created = await this.build_child_views()
    const created_views = new Set(created)

    // Find index up to which the order of the existing views
    // matches the order of the new views so we can skip
    // re-inserting views that are already in the correct position.
    const current_views = Array.from(this.content.children).flatMap(el => {
      const view = this.child_views.find(view => view.el === el)
      return view === undefined ? [] : [view]
    })
    let matching_index = null
    for (let i = 0; i < current_views.length; i++) {
      if (current_views[i] === this.child_views[i]) {
        matching_index = i
      } else {
        break
      }
    }

    for (let i = 0; i < this.child_views.length; i++) {
      const view = this.child_views[i]
      const is_new = created_views.has(view)
      const target = view.rendering_target() ?? this.content
      if (is_new) {
        view.render_to(target)
      } else if (matching_index === null || i > matching_index) {
        target.append(view.el)
      }
    }
    this.r_after_render()
    this._update_children()
    this.invalidate_layout()
  }

  create_modal(): void {
    const dialog = div({
      id: "pnx_dialog",
      class: "dialog-container bk-root",
      style: {display: "none"},
    })

    const dialog_overlay = div({class: "dialog-overlay"})
    if (this.model.background_close) {
      dialog_overlay.setAttribute("data-a11y-dialog-hide", "")
    }

    const {height, width, min_height, min_width, max_height, max_width} = this.model
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
    } as any)
    this.content = content
    for (const child_view of this.child_views) {
      const target = child_view.rendering_target() ?? this.content
      child_view.render_to(target)
    }

    this.close_button = button({
      id: "pnx_dialog_close",
      "data-a11y-dialog-hide": "",
      class: "pnx-dialog-close",
      ariaLabel: "Close this dialog window",
    } as any)
    this.close_button.innerHTML = "&#x2715"

    dialog.append(dialog_overlay)
    dialog.append(content)
    content.append(this.close_button)
    this.shadow_el.append(dialog)
    let first_open = false

    this.modal = new A11yDialog(dialog)
    this.update_close_button()
    this.modal.on("show", () => {
      this.model.open = true
      dialog.style.display = ""
      if (!first_open) {
        requestAnimationFrame(() => { this.invalidate_layout(); dialog.focus() })
        first_open = true
      }
    })
    this.modal.on("hide", () => {
      this.model.open = false
      dialog.style.display = "none"
    })

    if (this.model.open) { this.modal.show() }
  }

  update_close_button(): void {
    if (this.model.show_close_button) {
      this.close_button.style.display = "block"
    } else {
      this.close_button.style.display = "none"
    }
  }
}

export namespace Modal {
  export type Attrs = p.AttrsOf<Props>

  export type Props = BkColumn.Props & {
    open: p.Property<boolean>
    show_close_button: p.Property<boolean>
    background_close: p.Property<boolean>
  }
}

export interface Modal extends Modal.Attrs {}

export class Modal extends BkColumn {
  declare properties: Modal.Props

  constructor(attrs?: Partial<Modal.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.modal"
  static {
    this.prototype.default_view = ModalView
    this.define<Modal.Props>(({Bool}) => ({
      open: [Bool, false],
      show_close_button: [Bool, true],
      background_close: [Bool, true],
    }))
  }
}
