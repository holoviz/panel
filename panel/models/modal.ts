import type * as p from "@bokehjs/core/properties"
import {Column as BkColumn, ColumnView as BkColumnView} from "@bokehjs/models/layouts/column"
import {div} from "@bokehjs/core/dom"

export class ModalView extends BkColumnView {
  declare model: Modal

  modal: any
  dialog: any

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
    //<div id="pnx_dialog" class="dialog-container bk-root" aria-hidden="true">
    //<div class="dialog-overlay" data-a11y-dialog-hide></div>
    //  <div id="pnx_dialog_content" class="dialog-content" role="document">
    //    <button id="pnx_dialog_close" data-a11y-dialog-hide class="pnx-dialog-close" aria-label="Close this dialog window">
    //      <svg class="svg-icon" viewBox="0 0 20 20">
    //        <path
    //          fill="currentcolor"
    //          d="M15.898,4.045c-0.271-0.272-0.713-0.272-0.986,0l-4.71,4.711L5.493,4.045c-0.272-0.272-0.714-0.272-0.986,0s-0.272,0.714,0,0.986l4.709,4.711l-4.71,4.711c-0.272,0.271-0.272,0.713,0,0.986c0.136,0.136,0.314,0.203,0.492,0.203c0.179,0,0.357-0.067,0.493-0.203l4.711-4.711l4.71,4.711c0.137,0.136,0.314,0.203,0.494,0.203c0.178,0,0.355-0.067,0.492-0.203c0.273-0.273,0.273-0.715,0-0.986l-4.711-4.711l4.711-4.711C16.172,4.759,16.172,4.317,15.898,4.045z"
    //        ></path>
    //      </svg>
    //    </button>
    //    {% for object in objects %}
    //      <div id="pnx_modal_object">${object}</div>
    //    {% endfor %}
    //  </div>
    //</div>
    const container = div({style: {display: "contents"}})
    this.dialog = div({
      id: "pnx_dialog",
      class: "dialog-container bk-root",
      role: "dialog",
      "aria-hidden": "true",
      "aria-modal": "true",
      tabindex: "-1",
    } as any)
    const dialog_overlay = div({
      class: "dialog-overlay",
      "data-a11y-dialog-hide": "",
    } as any)
    const dialog_content = div({
      id: "pnx_dialog_content",
      class: "dialog-content",
      role: "document",
      //"data-a11y-dialog-hide": "true",
    } as any)
    const dialog_close = div({
      id: "pnx_dialog_close",
      "data-a11y-dialog-hide": "",
      class: "pnx-dialog-close",
      ariaLabel: "Close this dialog window",
    } as any)

    container.append(this.dialog)
    this.dialog.append(dialog_overlay)
    this.dialog.append(dialog_content)
    dialog_content.append(dialog_close)
    this.shadow_el.append(container)

    const test = div({
      id: "pnx_modal_object",
      class: "dialog-content",
      role: "document",
    } as any)
    test.innerText = "Hello world"
    dialog_content.append(test)

    this.modal = new (window as any).A11yDialog(this.dialog)
    this.modal.show()
  }

  update(): void { }
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
