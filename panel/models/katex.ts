import type * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelMarkupView} from "./layout"

export class KaTeXView extends PanelMarkupView {
  declare model: KaTeX

  override connect_signals(): void {
    super.connect_signals()

    const {text} = this.model.properties
    this.on_change(text, () => this.render())
  }

  override render(): void {
    super.render()
    this.container.innerHTML = this.model.text
    if (!(window as any).renderMathInElement) {
      return
    }
    (window as any).renderMathInElement(this.shadow_el, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "\\[", right: "\\]", display: true},
        {left: "$", right: "$", display: false},
        {left: "\\(", right: "\\)", display: false},
      ],
    })
  }
}

export namespace KaTeX {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Markup.Props & {
    text: p.Property<string>
  }
}

export interface KaTeX extends KaTeX.Attrs {}

export class KaTeX extends Markup {
  declare properties: KaTeX.Props

  constructor(attrs?: Partial<KaTeX.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.katex"

  static {
    this.prototype.default_view = KaTeXView
  }
}
