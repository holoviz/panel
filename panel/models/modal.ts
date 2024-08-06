import type * as p from "@bokehjs/core/properties"
import {Column as BkColumn, ColumnView as BkColumnView} from "@bokehjs/models/layouts/column"
import {div, button} from "@bokehjs/core/dom"
import {ModelEvent, server_event} from "@bokehjs/core/bokeh_events"
import type {Attrs} from "@bokehjs/core/types"
import {UIElementView} from "@bokehjs/models/ui/ui_element"

type A11yDialogView = {
  on(event: string, listener: () => void): void
  show(): void
  hide(): void
}

type A11yDialog = (container: HTMLElement) => Promise<{view: A11yDialogView}>
declare const A11yDialog: A11yDialog

@server_event("modal-dialog-event")
export class ModalDialogEvent extends ModelEvent {
  open: boolean

  constructor(open: boolean) {
    super()
    this.open = open
  }

  protected override get event_values(): Attrs {
    return {open: this.open}
  }

  static override from_values(values: object) {
    const {open} = values as {open: boolean}
    return new ModalDialogEvent(open)
  }
}

export class ModalView extends BkColumnView {
  declare model: Modal

  modal: A11yDialogView
  close_button: HTMLButtonElement
  modal_children: HTMLElement

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

    for (const child_view of this.child_views) {
      this.modal_children.appendChild(child_view.el)
      child_view.render()
      child_view.after_render()
    }
  }

  override async update_children(): Promise<void> {
    const created = await this.build_child_views()
    const created_children = new Set(created)

    // First remove and then either reattach existing elements or render and
    // attach new elements, so that the order of children is consistent, while
    // avoiding expensive re-rendering of existing views.
    for (const child_view of this.child_views) {
      child_view.el.remove()
    }

    for (const child_view of this.child_views) {
      const is_new = created_children.has(child_view)

      const target = child_view.rendering_target() ?? this.shadow_el
      if (is_new) {
        child_view.render_to(target)
      } else {
        target.append(child_view.el)
      }
    }
    this.r_after_render()

    this._update_children()
    this.invalidate_layout()
  }

  create_modal(): void {
    const container = div({style: {display: "contents"}})
    const dialog = div({
      id: "pnx_dialog",
      class: "dialog-container bk-root",
      "aria-hidden": "true",
    } as any)

    const dialog_overlay = div({class: "dialog-overlay"})
    if (this.model.background_close) {
      dialog_overlay.setAttribute("data-a11y-dialog-hide", "")
    }

    // TODO: Add width and height here
    const content = div({
      id: "pnx_dialog_content",
      class: "dialog-content",
      role: "document",
    } as any)
    this.close_button = button({
      id: "pnx_dialog_close",
      "data-a11y-dialog-hide": "",
      class: "pnx-dialog-close",
      ariaLabel: "Close this dialog window",
    } as any)
    this.modal_children = div({id: "pnx_modal_object"})

    container.append(dialog)
    dialog.append(dialog_overlay)
    dialog.append(content)
    content.append(this.close_button)
    content.append(this.modal_children)
    this.shadow_el.append(container)

    this.modal = new (window as any).A11yDialog(dialog)
    this.update_close_button()
    this.modal.on("show", () => { this.model.is_open = true })
    this.modal.on("hide", () => { this.model.is_open = false })
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
    is_open: p.Property<boolean>
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

  static override __module__ = "panel.models.layout"
  static {
    this.prototype.default_view = ModalView
    this.define<Modal.Props>(({Bool}) => ({
      is_open: [Bool, false],
      show_close_button: [Bool, true],
      background_close: [Bool, true],
    }))
  }
}
