import * as p from "@bokehjs/core/properties"
import { div } from "@bokehjs/core/dom"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"

import {PanelHTMLBoxView} from "./layout"

export class QuillInputView extends PanelHTMLBoxView {
  override model: QuillInput
  protected _container: HTMLDivElement
  protected _toolbar: HTMLDivElement
  protected _md: any

  quill: any

  initialize(): void {
    super.initialize()
    this._container = div({})
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.text.change, () => {
      this.quill.setContents([])
      this.quill.clipboard.dangerouslyPasteHTML(this.model.text)
    })
  }

  render(): void {
    super.render()
    this.el.style.paddingTop = "41px"
    this.el.appendChild(this._container)
    this.quill = new (window as any).Quill(this._container, {
      placeholder: this.model.placeholder,
      theme: 'snow'
    });
    this._toolbar = (this.el.children[0] as HTMLDivElement)
    this.quill.clipboard.dangerouslyPasteHTML(this.model.text)
    this.quill.on('text-change', () => {
      this.model.text = this._container.querySelector('.ql-editor').innerHTML
    });
  }

  after_layout(): void {
    super.after_layout()
    this._toolbar.style.marginTop = "-41px"
    this._toolbar.style.height = "40px"
  }
}

export namespace QuillInput {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    placeholder: p.Property<string>
    readonly:    p.Property<boolean>
    text:        p.Property<string>
  }
}

export interface QuillInput extends QuillInput.Attrs {}

export class QuillInput extends HTMLBox {
  properties: QuillInput.Props

  constructor(attrs?: Partial<QuillInput.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.quill"
  
  static init_QuillInput(): void {
    this.prototype.default_view = QuillInputView

    this.define<QuillInput.Props>(({Boolean, String}) => ({
      placeholder:  [ String,       '' ],
      readonly:     [ Boolean,   false ],
      text:         [ String,       '' ],
    }))
  }
}
