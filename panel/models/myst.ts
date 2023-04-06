import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelMarkupView} from "./layout"

export class MySTView extends PanelMarkupView {
  model: MyST

  override render(): void {
    super.render()
    const myst = new (window as any).MyST();
    this.container.innerHTML = myst.render(this.model.text);
  }
}

export namespace MyST {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Markup.Props & {
    text: p.Property<string>
  }
}

export interface MyST extends MyST.Attrs {}

export class MyST extends Markup {
  properties: MyST.Props

  constructor(attrs?: Partial<MyST.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.myst"

  static {
    this.prototype.default_view = MySTView
  }
}
