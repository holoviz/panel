import * as p from "@bokehjs/core/properties"
import {Slider, SliderView} from "@bokehjs/models/widgets/slider"
import {span} from "@bokehjs/core/dom"
import {bk_slider_value} from "@bokehjs/styles/widgets/sliders"

export class PnSliderView extends SliderView {
  model: PnSlider

  connect_signals(): void {
    super.connect_signals()
    this.on_change(this.model.properties.suffix, () => this._update_title())
  }

  render(): void {
    super.render()
    this.title_el.style.width = "100%"
  }

  _update_title(): void {
    super._update_title()
    const hide_header = this.model.title == null || (this.model.title.length == 0 && !this.model.show_value)
    if(this.model.suffix && !hide_header){
      this.title_el.appendChild(
        span({class: bk_slider_value, style: {"position": "absolute", "right": "0px"}},
             `${this.model.suffix}`)
      )
    }
  }
}


export namespace PnSlider {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Slider.Props & {
    suffix: p.Property<string>
  }
}

export interface PnSlider extends PnSlider.Attrs {}

export abstract class PnSlider extends Slider {
  
  properties: PnSlider.Props
  
  constructor(attrs?: Partial<PnSlider.Attrs>) {
    super(attrs)
  }
  
  static __module__ = "panel.models.widgets"
  
  static init_PnSlider(): void {
    this.prototype.default_view = PnSliderView
    
    this.define<PnSlider.Props>({
      suffix: [ p.String, ""],
    })  
  }
}
