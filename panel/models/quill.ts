import type * as p from "@bokehjs/core/properties"
import {div} from "@bokehjs/core/dom"

import {HTMLBox, HTMLBoxView} from "./layout"

export class QuillInputView extends HTMLBoxView {
  declare model: QuillInput

  protected container: HTMLDivElement
  protected _editor: HTMLDivElement
  protected _editing: boolean
  protected _toolbar: HTMLDivElement | null

  quill: any

  override connect_signals(): void {
    super.connect_signals()

    const {disabled, visible, text, mode, toolbar, placeholder} = this.model.properties
    this.on_change(disabled, () => {
      this.quill.enable(!this.model.disabled)
    })
    this.on_change(visible, () => {
      if (this.model.visible) {
        this.container.style.visibility = "visible"
      }
    })
    this.on_change(text, () => {
      if (this._editing) {
        return
      }
      this._editing = true
      this.quill.enable(false)
      this.quill.setContents([])
      this.quill.clipboard.dangerouslyPasteHTML(this.model.text)
      this.quill.enable(!this.model.disabled)
      this._editing = false
    })
    this.on_change(placeholder, () => {
      this.quill.root.setAttribute("data-placeholder", this.model.placeholder)
    })
    this.on_change([mode, toolbar], () => {
      this.render()
      this._layout_toolbar()
    })
  }

  _layout_toolbar(): void {
    if (this._toolbar == null) {
      this.el.style.removeProperty("padding-top")
    } else {
      const height = this._toolbar.getBoundingClientRect().height + 1
      this.el.style.paddingTop = `${height}px`
      this._toolbar.style.marginTop = `${-height}px`
    }
  }

  override render(): void {
    super.render()
    this.container = div({style: {visibility: "hidden"}})
    this.shadow_el.appendChild(this.container)
    const theme = (this.model.mode === "bubble") ? "bubble" : "snow"
    this.watch_stylesheets()
    this.quill = new (window as any).Quill(this.container, {
      modules: {
        toolbar: this.model.toolbar,
      },
      readOnly: true,
      placeholder: this.model.placeholder,
      theme,
    })

    // Apply ShadowDOM patch found at:
    // https://github.com/quilljs/quill/issues/2961#issuecomment-1775999845

    const hasShadowRootSelection = !!((document.createElement("div").attachShadow({mode: "open"}) as any).getSelection)
    // Each browser engine has a different implementation for retrieving the Range
    const getNativeRange = (rootNode: any) => {
      try {
        if (hasShadowRootSelection) {
          // In Chromium, the shadow root has a getSelection function which returns the range
          return rootNode.getSelection().getRangeAt(0)
        } else {
          const selection = window.getSelection()
          if ((selection as any).getComposedRanges) {
            // Webkit range retrieval is done with getComposedRanges (see: https://bugs.webkit.org/show_bug.cgi?id=163921)
            return (selection as any).getComposedRanges(rootNode)[0]
          } else {
            // Gecko implements the range API properly in Native Shadow: https://developer.mozilla.org/en-US/docs/Web/API/Selection/getRangeAt
            return (selection as any).getRangeAt(0)
          }
        }
      } catch {
        return null
      }
    }

    /**
     * Original implementation uses document.active element which does not work in Native Shadow.
     * Replace document.activeElement with shadowRoot.activeElement
     **/
    this.quill.selection.hasFocus = () => {
      const rootNode = (this.quill.root.getRootNode() as ShadowRoot)
      return rootNode.activeElement === this.quill.root
    }

    /**
     * Original implementation uses document.getSelection which does not work in Native Shadow.
     * Replace document.getSelection with shadow dom equivalent (different for each browser)
     **/
    this.quill.selection.getNativeRange = () => {
      const rootNode = (this.quill.root.getRootNode() as ShadowRoot)
      const range = getNativeRange(rootNode)
      return !!range ? this.quill.selection.normalizeNative(range) : null
    }

    /**
     * Original implementation relies on Selection.addRange to programmatically set the range, which does not work
     * in Webkit with Native Shadow. Selection.addRange works fine in Chromium and Gecko.
     **/
    this.quill.selection.setNativeRange = (startNode: Element, startOffset: number, endNode: any = undefined, endOffset: any = undefined, force: boolean = false) => {
      endNode = endNode === undefined ? startNode : endNode
      endOffset = endOffset === undefined ? startOffset : endOffset
      force = force || false

      if (startNode != null && (this.quill.selection.root.parentNode == null || startNode.parentNode == null || endNode.parentNode == null)) {
        return
      }
      const selection = document.getSelection()
      if (selection == null) {
        return
      }
      if (startNode != null) {
        if (!this.quill.selection.hasFocus()) {
          this.quill.selection.root.focus()
        }
        const native = (this.quill.selection.getNativeRange() || {}).native
        if (native == null || force || startNode !== native.startContainer || startOffset !== native.startOffset || endNode !== native.endContainer || endOffset !== native.endOffset) {
          if (startNode.tagName == "BR") {
            startOffset = Array.prototype.indexOf.call(startNode.parentNode?.childNodes ?? [], startNode)
            startNode = startNode.parentNode as any
          }
          if (endNode.tagName == "BR") {
            endOffset = Array.prototype.indexOf(endNode.parentNode?.childNodes ?? [], endNode)
            endNode = endNode.parentNode
          }
          selection.setBaseAndExtent(startNode, startOffset, endNode, endOffset)
        }
      } else {
        selection.removeAllRanges()
        this.quill.selection.root.blur()
        document.body.focus()
      }
    }

    this._editor = (this.shadow_el.querySelector(".ql-editor") as HTMLDivElement)
    this._toolbar = (this.shadow_el.querySelector(".ql-toolbar") as HTMLDivElement)

    const delta = this.quill.clipboard.convert({html: this.model.text})
    this.quill.setContents(delta)

    this.quill.on("text-change", () => {
      if (this._editing) {
        return
      }
      this._editing = true
      this.model.text = this.quill.getSemanticHTML()
      this._editing = false
    })
    if (!this.model.disabled) {
      this.quill.enable(!this.model.disabled)
    }

    document.addEventListener("selectionchange", (..._args: any[]) => {
      // Update selection and some other properties
      this.quill.selection.update()
    })
  }

  override style_redraw(): void {
    if (this.model.visible) {
      this.container.style.visibility = "visible"
    }

    const delta = this.quill.clipboard.convert({html: this.model.text})
    this.quill.setContents(delta)

    this.invalidate_layout()
  }

  override after_layout(): void {
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

export interface QuillInput extends QuillInput.Attrs { }

export class QuillInput extends HTMLBox {
  declare properties: QuillInput.Props

  constructor(attrs?: Partial<QuillInput.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.quill"

  static {
    this.prototype.default_view = QuillInputView

    this.define<QuillInput.Props>(({Any, Str}) => ({
      mode:         [ Str, "toolbar" ],
      placeholder:  [ Str,        "" ],
      text:         [ Str,        "" ],
      toolbar:      [ Any,         null ],
    }))

    this.override<QuillInput.Props>({
      height: 300,
    })
  }
}
