import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"

export class KaTeXView extends HTMLBoxView {
  model: KaTeX

  initialize(): void {
    super.initialize()
    this.render()
    this.connect(this.model.properties.text.change, this.render)
  }

  render(): void {
    super.render();
	this.el.innerHTML = this.model.text;
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
  export type Props = HTMLBox.Props & {
    text: p.Property<string>
  }
}

export interface KaTeX extends KaTeX.Attrs {}

export class KaTeX extends HTMLBox {
  properties: KaTeX.Props

  constructor(attrs?: Partial<KaTeX.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "KaTeX"
    this.prototype.default_view = KaTeXView

    this.define<KaTeX.Props>({
      text: [ p.String ]
    })
  }
}
KaTeX.initClass()
