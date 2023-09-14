import * as p from "@bokehjs/core/properties"
import { div } from "@bokehjs/core/dom"

import {HTMLBox, HTMLBoxView} from "./layout"

const normalizeNative = (nativeRange: any) => {

  // document.getSelection model has properties startContainer and endContainer
  // shadow.getSelection model has baseNode and focusNode
  // Unify formats to always look like document.getSelection

  if (nativeRange) {

    const range = nativeRange;

    if (range.baseNode) {
      range.startContainer = nativeRange.baseNode;
      range.endContainer = nativeRange.focusNode;
      range.startOffset = nativeRange.baseOffset;
      range.endOffset = nativeRange.focusOffset;

      if (range.endOffset < range.startOffset) {
        range.startContainer = nativeRange.focusNode;
        range.endContainer = nativeRange.baseNode;
        range.startOffset = nativeRange.focusOffset;
        range.endOffset = nativeRange.baseOffset;
      }
    }

    if (range.startContainer) {

      return {
        start: { node: range.startContainer, offset: range.startOffset },
        end: { node: range.endContainer, offset: range.endOffset },
        native: range
      };
    }
  }

  return null
};

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
    this.connect(this.model.properties.visible.change, () => {
      if (this.model.visible)
	this.container.style.visibility = 'visible';
    })
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
    this.container = div({style: "visibility: hidden;"})
    this.shadow_el.appendChild(this.container)
    const theme = (this.model.mode === 'bubble') ? 'bubble' : 'snow'
    this.watch_stylesheets()
    this.quill = new (window as any).Quill(this.container, {
      modules: {
        toolbar: this.model.toolbar
      },
      readOnly: true,
      placeholder: this.model.placeholder,
      theme: theme
    });

    // Hack Quill and replace document.getSelection with shadow.getSelection
    // see https://stackoverflow.com/questions/67914657/quill-editor-inside-shadow-dom/67944380#67944380
    this.quill.selection.getNativeRange = () => {
      const selection = (this.shadow_el as any).getSelection();
      const range = normalizeNative(selection);
      return range;
    };

    this._editor = (this.shadow_el.querySelector('.ql-editor') as HTMLDivElement)
    this._toolbar = (this.shadow_el.querySelector('.ql-toolbar') as HTMLDivElement)

    const delta = this.quill.clipboard.convert(this.model.text);
    this.quill.setContents(delta);

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

  style_redraw(): void {
    if (this.model.visible)
      this.container.style.visibility = 'visible';

    const delta = this.quill.clipboard.convert(this.model.text);
    this.quill.setContents(delta);

    this.invalidate_layout()
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
