import * as p from "@bokehjs/core/properties"
import {Slider, SliderView} from "@bokehjs/models/widgets/slider"
import {input, div} from "@bokehjs/core/dom"
import {bk_input, bk_input_group} from "@bokehjs/styles/widgets/inputs"

export class SliderInputView extends SliderView {
  model: SliderInput
  protected input_el: HTMLInputElement
  protected global_group_el: HTMLElement
  protected slider_group_el: HTMLElement
  protected tilte_group_el: HTMLElement

  render(): void {
    super.render()
    const uislider = (this.slider_el as any).noUiSlider
    this.el.removeChild(this.group_el)
    if (this.input_el == null) {
      this.input_el = input({
        type: "text",
        class: bk_input,
        name: this.model.name,
        value: uislider.get(),
      })
    }
    const direction = this.model.orientation == "horizontal" ? "row" : "column"
    this.slider_group_el = div(
      {
        class: bk_input_group,
        style: {
          display: "flex",
          flexDirection: direction,
          alignItems: this.align,
        },
      },
      this.slider_el
    )

    //to not overlap the slider handle
    if (direction == "column") {
      this.slider_group_el.style.paddingTop = "1px"
      this.slider_group_el.style.paddingBottom = "6px"
    } else {
      this.slider_group_el.style.paddingRight = "6px"
    }

    this.tilte_group_el = div(
      {
        class: bk_input_group,
        style: {
          display: "flex",
          flexDirection: "column",
          alignItems: this.align,
        },
      },
      this.title_el,
      this.slider_group_el
    )
    this.global_group_el = div(
      {
        class: bk_input_group,
        style: {
          display: "flex",
          flexDirection: direction,
          alignItems: this.align,
        },
      },
      this.tilte_group_el,
      this.input_el
    )
    this.el.appendChild(this.global_group_el)
    this.el.style.display = "flex"
    this.el.style.flexDirection = direction
    const input_size = this.input_size
    if (input_size.endsWith("%")) {
      this.tilte_group_el.style.width = `${
        100 - Number(input_size.slice(0, -1))
      }%`
    }
    this.input_el.style.width = input_size

    uislider.on("slide", (value: string) => {
      this.input_el.value = value
    })

    this.input_el.addEventListener("change", () => {
      let value = Number(this.input_el.value)
      if (value || value === 0) {
        if (this.model.hard_start != null) {
          if (value < this.model.hard_start) {
            value = this.model.hard_start
            this.input_el.value = this.model.pretty(value)
          }
        }
        if (this.model.hard_end != null) {
          if (value > this.model.hard_end) {
            value = this.model.hard_end
            this.input_el.value = this.model.pretty(value)
          }
        }
        uislider.set(this.input_el.value)
        this.model.value = value
        this.model.value_throttled = value
      }
    })
    this.input_el.value = this.model.pretty(this.model.value)
  }

  private get align(): string {
    if (this.model.align == "center") {
      return "center"
    } else if (this.model.align == "start") {
      return "flex-start"
    } else {
      return "flex-end"
    }
  }

  private get input_size(): string {
    return this.model.input_size ? this.model.input_size : "30%"
  }

  connect_signals(): void {
    super.connect_signals()
    const {value} = this.model.properties
    this.on_change(value, () => {
      this.input_el.value = this.model.value
    })
  }
}

export namespace SliderInput {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Slider.Props & {
    hard_start: p.Property<number | null>
    hard_end: p.Property<number | null>
    input_size: p.Property<string | null>
  }
}

export interface SliderInput extends SliderInput.Attrs {}

export class SliderInput extends Slider {
  properties: SliderInput.Props

  constructor(attrs?: Partial<SliderInput.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.widgets"

  static init_SliderInput(): void {
    this.prototype.default_view = SliderInputView
    this.define<SliderInput.Props>({
      hard_start: [ p.Number, null ],
      hard_end:   [ p.Number, null ],
      input_size: [ p.String, null ],
    })
    this.override({tooltips: false})
  }
}
