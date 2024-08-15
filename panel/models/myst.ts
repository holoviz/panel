import type * as p from "@bokehjs/core/properties"
import {HTMLView, HTML} from "./html"


export class MySTView extends HTMLView {
  declare model: MyST

  override process_tex(): string {
    const myst = new (window as any).mystjs.MyST()
    const text = myst.render(this.model.text)
    if (this.model.disable_math || !this.contains_tex(text)) {
      return text
    }

    const tex_parts = this.provider.MathJax.find_tex(text)
    const processed_text: string[] = []

    let last_index: number | undefined = 0
    for (const part of tex_parts) {
      processed_text.push(text.slice(last_index, part.start.n))
      processed_text.push(this.provider.MathJax.tex2svg(part.math, {display: part.display}).outerHTML)

      last_index = part.end.n
    }

    if (last_index! < text.length) {
      processed_text.push(text.slice(last_index))
    }

    return processed_text.join("")
  }
}

export namespace MyST {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTML.Props
}

export interface MyST extends MyST.Attrs {}

export class MyST extends HTML {
  declare properties: MyST.Props

  constructor(attrs?: Partial<MyST.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.myst"

  static {
    this.prototype.default_view = MySTView
    this.define<MyST.Props>(({}) => ({}))
  }
}
