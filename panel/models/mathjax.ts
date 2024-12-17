import type * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelMarkupView} from "./layout"

export class MathJaxView extends PanelMarkupView {
  declare model: MathJax

  override connect_signals(): void {
    super.connect_signals()

    const {text} = this.model.properties
    this.on_change(text, () => this.render())
  }

  override render(): void {
    super.render()
    const text = this.model.text
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

    this.container.innerHTML = processed_text.join("")
  }
}

export namespace MathJax {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Markup.Props & {
    text: p.Property<string>
  }
}

export interface MathJax extends MathJax.Attrs {}

export class MathJax extends Markup {
  declare properties: MathJax.Props

  constructor(attrs?: Partial<MathJax.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.mathjax"

  static {
    this.prototype.default_view = MathJaxView
  }
}
