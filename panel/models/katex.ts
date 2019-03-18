import * as p from "core/properties"
import {Markup, MarkupView} from "models/widgets/markup"

export class KaTeXView extends MarkupView {
  model: KaTeX

  render(): void {
    super.render();
    this.markup_el.innerHTML = this.model.text;
    if (!(window as any).renderMathInElement) {
      return
    }
    (window as any).renderMathInElement(this.el, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "\\[", right: "\\]", display: true},
        {left: "$", right: "$", display: false},
        {left: "\\(", right: "\\)", display: false}
      ]
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
  properties: KaTeX.Props

  constructor(attrs?: Partial<KaTeX.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "KaTeX"
    this.prototype.default_view = KaTeXView
  }
}
KaTeX.initClass()
