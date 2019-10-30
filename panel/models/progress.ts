import {VariadicBox} from "@bokehjs/core/layout"
import * as p from "@bokehjs/core/properties"
import {Widget, WidgetView} from "@bokehjs/models/widgets/widget"

export class ProgressView extends WidgetView {
  model: Progress
  protected progressEl: HTMLProgressElement

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.change, () => {
      this.render()
      this.root.compute_layout() // XXX: invalidate_layout?
    })
    this.connect(this.model.properties.value.change, () => this.setValue())
  }

  render(): void {
    super.render()
    const style: any = {...this.model.style, display: "inline-block"}
    this.progressEl = document.createElement('progress')
    this.progressEl.max = 100

    if (!this.model.sizing_mode || this.model.sizing_mode === 'fixed') {
      if (this.model.width)
        this.progressEl.style.width = this.model.width + 'px';
      console.log(this.progressEl.style.width)
    } else if (this.model.sizing_mode == 'stretch_width' ||
               this.model.sizing_mode == 'stretch_both' ||
               this.model.width_policy == 'max' ||
               this.model.width_policy == 'fit') {
      this.progressEl.style.width = '100%'
    }
    if (this.model.value != null)
      this.progressEl.value = this.model.value
    for (const prop in style) {
      this.el.style.setProperty(prop, style[prop]);
    }
    this.el.appendChild(this.progressEl)
  }

  setValue(): void {
    if (this.model.value != null)
      this.progressEl.value = this.model.value
  }

  _update_layout(): void {
    this.layout = new VariadicBox(this.el)
    this.layout.set_sizing(this.box_sizing())
  }

}

export namespace Progress {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Widget.Props & {
    style: p.Property<{[key: string]: string}>
    value: p.Property<number | null>
  }
}

export interface Progress extends Progress.Attrs {}

export class Progress extends Widget {
  properties: Progress.Props

  constructor(attrs?: Partial<Progress.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.widgets"

  static init_Progress(): void {
    this.prototype.default_view = ProgressView
    this.define<Progress.Props>({
      style: [ p.Any, {} ],
      value: [ p.Number, null ],
    })
  }
}
