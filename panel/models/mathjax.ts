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
    this.container.innerHTML = this.has_math_disabled() ? this.model.text : this.process_tex(this.model.text)
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
