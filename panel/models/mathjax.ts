import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelMarkupView} from "./layout"

export class MathJaxView extends PanelMarkupView {
  model: MathJax
  private _hub: any

  initialize(): void {
    super.initialize()
    this._hub = (window as any).MathJax.Hub;
    this._hub.Config({
      tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]}
    });
  }

  render(): void {
    super.render();
    if (!this._hub) { return }
    this.markup_el.innerHTML = this.model.text;
    this._hub.Queue(["Typeset", this._hub, this.markup_el]);
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
  properties: MathJax.Props

  constructor(attrs?: Partial<MathJax.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.mathjax"

  static init_MathJax(): void {
    this.prototype.default_view = MathJaxView
  }
}
