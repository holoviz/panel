import type * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelMarkupView} from "./layout"
import {html_decode} from "./html"

export class PDFView extends PanelMarkupView {
  declare model: PDF

  override connect_signals(): void {
    super.connect_signals()
    const {text, width, height, embed, start_page} = this.model.properties
    this.on_change([text, width, height, embed, start_page], () => { this.update() })
  }

  override render(): void {
    super.render()
    this.update()
  }

  update(): void {
    if (this.model.embed) {
      const blob = this.convert_base64_to_blob()
      const url = URL.createObjectURL(blob)
      this.container.innerHTML = `<embed src="${url}#page=${this.model.start_page}" type="application/pdf" width="100%" height="100%"></embed>`
    } else {
      const html = html_decode(this.model.text)
      this.container.innerHTML = html || ""
    }
  }

  protected convert_base64_to_blob(): Blob {
    const byte_characters = atob(this.model.text)
    const slice_size = 512
    const byte_arrays = []
    for (let offset = 0; offset < byte_characters.length; offset += slice_size) {
      const slice = byte_characters.slice(offset, offset + slice_size)
      const byte_numbers = new Uint8Array(slice.length)
      for (let i = 0; i < slice.length; i++) {
        byte_numbers[i] = slice.charCodeAt(i)
      }
      byte_arrays.push(byte_numbers)
    }
    return new Blob(byte_arrays, {type: "application/pdf"})
  }
}

export namespace PDF {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props & {
    embed: p.Property<boolean>
    start_page: p.Property<number>
  }
}

export interface PDF extends PDF.Attrs {}

export class PDF extends Markup {
  declare properties: PDF.Props

  constructor(attrs?: Partial<PDF.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.markup"
  static {
    this.prototype.default_view = PDFView
    this.define<PDF.Props>(({Int, Bool}) => ({
      embed: [Bool, false],
      start_page: [Int, 1],
    }))
  }
}
