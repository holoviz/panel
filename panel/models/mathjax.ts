import * as p from "core/properties"
import {Markup, MarkupView} from "models/widgets/markup"

export class MathJaxView extends MarkupView {
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

  static initClass(): void {
    this.prototype.type = "MathJax"
    this.prototype.default_view = MathJaxView
  }
}
MathJax.initClass()
