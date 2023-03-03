import * as p from "@bokehjs/core/properties"
import { div } from "@bokehjs/core/dom"

import {HTMLBox, HTMLBoxView} from "./layout"

export class QuillInputView extends HTMLBoxView {
  override model: QuillInput
  protected container: HTMLDivElement
  protected _editor: HTMLDivElement
  protected _editing: boolean
  protected _toolbar: HTMLDivElement | null

  quill: any

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.disabled.change, () => this.quill.enable(!this.model.disabled))
    this.connect(this.model.properties.text.change, () => {
      if (this._editing)
        return
      this._editing = true
      this.quill.enable(false)
      this.quill.setContents([])
      this.quill.clipboard.dangerouslyPasteHTML(this.model.text)
      this.quill.enable(!this.model.disabled)
      this._editing = false
    })
    const {mode, toolbar, placeholder} = this.model.properties
    this.on_change([placeholder], () => {
      this.quill.root.setAttribute('data-placeholder', this.model.placeholder)
    })
    this.on_change([mode, toolbar], () => {
      this.render()
      this._layout_toolbar()
    })
  }

  _layout_toolbar(): void {
    if (this._toolbar == null) {
      this.el.style.removeProperty('padding-top')
    } else {
      const height = this._toolbar.getBoundingClientRect().height + 1
      this.el.style.paddingTop = height + "px"
      this._toolbar.style.marginTop = -height + "px"
    }
  }

  render(): void {
    super.render()
    this.container = div({})
    this.shadow_el.appendChild(this.container)
    const theme = (this.model.mode === 'bubble') ? 'bubble' : 'snow'
    this.quill = new (window as any).Quill(this.container, {
      modules: {
        toolbar: this.model.toolbar
      },
      readOnly: true,
      placeholder: this.model.placeholder,
      theme: theme
    });
    this._editor = (this.shadow_el.querySelector('.ql-editor') as HTMLDivElement)
    this._toolbar = (this.shadow_el.querySelector('.ql-toolbar') as HTMLDivElement)
    this.quill.clipboard.dangerouslyPasteHTML(this.model.text)
    this.quill.on('text-change', () => {
      if (this._editing)
        return
      this._editing = true
      this.model.text = this._editor.innerHTML
      this._editing = false
    });
    if (!this.model.disabled)
      this.quill.enable(!this.model.disabled)

    document.addEventListener("selectionchange", (..._args: any[]) => {
      // Update selection and some other properties
      this.quill.selection.update()
    });
  }

  after_layout(): void {
    super.after_layout()
    this._layout_toolbar()
  }
}

export namespace QuillInput {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    mode:        p.Property<string>
    placeholder: p.Property<string>
    text:        p.Property<string>
    toolbar:     p.Property<any>
  }
}

export interface QuillInput extends QuillInput.Attrs {}

export class QuillInput extends HTMLBox {
  properties: QuillInput.Props

  constructor(attrs?: Partial<QuillInput.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.quill"

  static {
    this.prototype.default_view = QuillInputView

    this.define<QuillInput.Props>(({Any, String}) => ({
      mode:         [ String, 'toolbar' ],
      placeholder:  [ String,        '' ],
      text:         [ String,        '' ],
      toolbar:      [ Any,         null ],
    }))

    this.override<QuillInput.Props>({
      height: 300
    })
  }
}
