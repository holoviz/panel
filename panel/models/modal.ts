import type * as p from "@bokehjs/core/properties"
import {Column as BkColumn, ColumnView as BkColumnView} from "@bokehjs/models/layouts/column"
import {div, button} from "@bokehjs/core/dom"

export class ModalView extends BkColumnView {
  declare model: Modal

  modal: any
  dialog: any
  content: any

  override initialize(): void {
    super.initialize()
  }

  override connect_signals(): void {
    super.connect_signals()
    const {} = this.model.properties
    this.on_change([], () => { this.update() })
  }

  //        "render": """
  //        fast_el = document.getElementById("body-design-provider")
  //        if (fast_el!==null){
  //          fast_el.append(pnx_dialog_style)
  //          fast_el.append(pnx_dialog)
  //        }
  //        self.show_close_button()
  //        self.init_modal()
  //        """,
  //        "init_modal": """
  //state.modal = new A11yDialog(pnx_dialog)
  //state.modal.on('show', function (element, event) {data.is_open=true})
  //state.modal.on('hide', function (element, event) {data.is_open=false})
  //if (data.is_open==true){state.modal.show()}
  //""",
  //        "is_open": """\
  //if (data.is_open==true){state.modal.show();view.invalidate_layout()} else {state.modal.hide()}""",
  //        "show_close_button": """
  //if (data.show_close_button){pnx_dialog_close.style.display = " block"}else{pnx_dialog_close.style.display = "none"}
  //""",
  override render(): void {
    super.render()
    const container = div({style: {display: "contents"}})
    this.dialog = div({
      id: "pnx_dialog",
      class: "dialog-container bk-root",
      "aria-hidden": "true",
    } as any)
    const dialog_overlay = div({
      class: "dialog-overlay",
      "data-a11y-dialog-hide": "",
    } as any)
    this.content = div({
      id: "pnx_dialog_content",
      class: "dialog-content",
      role: "document",
    } as any)
    const dialog_close = button({
      content: "Close",
      id: "pnx_dialog_close",
      "data-a11y-dialog-hide": "",
      class: "pnx-dialog-close",
      ariaLabel: "Close this dialog window",
      style: {
        backgroundColor: "red",
      },
    } as any)

    container.append(this.dialog)
    this.dialog.append(dialog_overlay)
    this.dialog.append(this.content)
    this.content.append(dialog_close)
    this.shadow_el.append(container)

    this.modal = new (window as any).A11yDialog(this.dialog)
    this.update()
    this.modal.on("show", (_element: any, _event: any) => { this.model.is_open = true })
    this.modal.on("hide", (_element: any, _event: any) => { this.model.is_open = true })
    this.modal.show()
  }

  update(): void {
    const test = div({
      id: "pnx_modal_object",
      class: "dialog-content",
      role: "document",
    } as any)
    test.innerText = "Hello world2"
    this.content.append(test)
  }
}

export namespace Modal {
  export type Attrs = p.AttrsOf<Props>

  export type Props = BkColumn.Props & {
    is_open: p.Property<boolean>
    show_close_button: p.Property<boolean>
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
    }))
  }
}
