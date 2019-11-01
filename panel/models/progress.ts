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
    this.connect(this.model.properties.active.change, () => this.setCSS())
    this.connect(this.model.properties.bar_color.change, () => this.setCSS())
    this.connect(this.model.properties.css_classes.change, () => this.setCSS())
    this.connect(this.model.properties.value.change, () => this.setValue())
    this.connect(this.model.properties.max.change, () => this.setMax())
  }

  render(): void {
    super.render()
    const style: any = {...this.model.style, display: "inline-block"}
    this.progressEl = document.createElement('progress')
    this.setValue()
    this.setMax()

    // Set styling
    if (!this.model.sizing_mode || this.model.sizing_mode === 'fixed') {
      if (this.model.width)
        this.progressEl.style.width = this.model.width + 'px';
    } else if (this.model.sizing_mode == 'stretch_width' ||
               this.model.sizing_mode == 'stretch_both' ||
               this.model.width_policy == 'max' ||
               this.model.width_policy == 'fit') {
      this.progressEl.style.width = '100%'
    }
    this.setCSS()
    for (const prop in style)
      this.progressEl.style.setProperty(prop, style[prop]);
    this.el.appendChild(this.progressEl)
  }

  setCSS(): void {
    const css = this.model.css_classes.join(" ") + " " + this.model.bar_color;
    if (this.model.active)
      this.progressEl.className = css + " active";
    else
      this.progressEl.className = css;
  }

  setValue(): void {
    if (this.model.value != null)
      this.progressEl.value = this.model.value
  }

  setMax(): void {
    if (this.model.max != null)
      this.progressEl.max = this.model.max
  }

  _update_layout(): void {
    this.layout = new VariadicBox(this.el)
    this.layout.set_sizing(this.box_sizing())
  }
}

export namespace Progress {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Widget.Props & {
    active: p.Property<boolean>
    bar_color: p.Property<string>
    style: p.Property<{[key: string]: string}>
    max: p.Property<number | null>
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
      active:    [ p.Boolean, true ],
      bar_color: [ p.String, 'primary' ],
      style:     [ p.Any, {} ],
      max:       [ p.Number, 100 ],
      value:     [ p.Number, null ],
    })
  }
}
