import type {TooltipView} from "@bokehjs/models/ui/tooltip"
import {Tooltip} from "@bokehjs/models/ui/tooltip"
import type {TablerIconView} from "@bokehjs/models/ui/icons/tabler_icon"
import {TablerIcon} from "@bokehjs/models/ui/icons/tabler_icon"
import type {SVGIconView} from "@bokehjs/models/ui/icons/svg_icon"
import {SVGIcon} from "@bokehjs/models/ui/icons/svg_icon"
import {Control, ControlView} from "@bokehjs/models/widgets/control"
import type {IterViews} from "@bokehjs/core/build_views"
import type * as p from "@bokehjs/core/properties"
import {div} from "@bokehjs/core/dom"
import {build_view} from "@bokehjs/core/build_views"
import {ButtonClick} from "@bokehjs/core/bokeh_events"
import type {EventCallback} from "@bokehjs/model"

export class ClickableIconView extends ControlView {
  declare model: ClickableIcon
  icon_view: TablerIconView | SVGIconView
  label_el: HTMLDivElement
  was_svg_icon: boolean
  row_div: HTMLDivElement

  protected tooltip: TooltipView | null

  public *controls() {}

  override remove(): void {
    this.tooltip?.remove()
    this.icon_view.remove()
    super.remove()
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()

    this.was_svg_icon = this.is_svg_icon(this.model.icon)
    this.label_el = div({class: "bk-IconLabel"}, this.model.title)
    this.label_el.style.fontSize = this.calculate_size(0.6)
    this.icon_view = await this.build_icon_model(this.model.icon, this.was_svg_icon)
    const {tooltip} = this.model
    if (tooltip != null) {
      this.tooltip = await build_view(tooltip, {parent: this})
    }
  }

  override *children(): IterViews {
    yield* super.children()
    yield this.icon_view
    if (this.tooltip != null) {
      yield this.tooltip
    }
  }

  is_svg_icon(icon: string): boolean {
    return icon.trim().startsWith("<svg")
  }

  override connect_signals(): void {
    super.connect_signals()
    const {icon, active_icon, disabled, value, size, tooltip} = this.model.properties
    this.on_change([active_icon, icon, value], () => this.update_icon())
    this.on_change(this.model.properties.title, () => this.update_label())
    this.on_change(disabled, () => this.update_cursor())
    this.on_change(size, () => this.update_size())
    this.on_change(tooltip, () => this.update_tooltip())
  }

  async update_tooltip(): Promise<void> {
    if (this.tooltip != null) {
      this.tooltip.remove()
    }
    const {tooltip} = this.model
    if (tooltip != null) {
      this.tooltip = await build_view(tooltip, {parent: this})
    }
  }

  override render(): void {
    super.render()
    this.icon_view.render()
    this.update_icon()
    this.update_label()
    this.update_cursor()
    this.row_div = div({
      class: "bk-IconRow",
    }, this.icon_view.el, this.label_el)
    this.shadow_el.appendChild(this.row_div)

    const toggle_tooltip = (visible: boolean) => {
      this.tooltip?.model.setv({
        visible,
      })
    }
    let timer: ReturnType<typeof setTimeout> | undefined
    this.el.addEventListener("mouseenter", () => {
      if (timer) {
        clearTimeout(timer)
      }
      timer = setTimeout(() => toggle_tooltip(true), this.model.tooltip_delay)
    })
    this.el.addEventListener("pointerleave", () => {
      clearTimeout(timer)
      timer = undefined
      toggle_tooltip(false)
    })
  }

  update_label(): void {
    this.label_el.innerText = this.model.title
  }

  update_cursor(): void {
    this.icon_view.el.style.cursor = this.model.disabled ? "not-allowed" : "pointer"
  }

  update_size(): void {
    this.icon_view.model.size = this.calculate_size()
    this.label_el.style.fontSize = this.calculate_size(0.6)
  }

  async build_icon_model(icon: string, is_svg_icon: boolean): Promise<TablerIconView | SVGIconView> {
    const size = this.calculate_size()
    const icon_model = (() => {
      if (is_svg_icon) {
        return new SVGIcon({svg: icon, size})
      } else {
        return new TablerIcon({icon_name: icon, size})
      }
    })()
    const icon_view = await build_view(icon_model, {parent: this})
    icon_view.el.addEventListener("click", () => this.click())
    return icon_view
  }

  async update_icon(): Promise<void> {
    const icon = this.model.value ? this.get_active_icon() : this.model.icon
    this.class_list.toggle("active", this.model.value)
    const is_svg_icon = this.is_svg_icon(icon)

    if (this.was_svg_icon !== is_svg_icon) {
      // If the icon type has changed, we need to rebuild the icon view
      // and invalidate the old one.
      const icon_view = await this.build_icon_model(icon, is_svg_icon)
      icon_view.render()
      this.icon_view.remove()
      this.icon_view = icon_view
      this.was_svg_icon = is_svg_icon
      this.update_cursor()
      // We need to re-append the new icon view to the DOM
      this.row_div.insertBefore(this.icon_view.el, this.label_el)
    } else if (is_svg_icon) {
      (this.icon_view as SVGIconView).model.svg = icon
    } else {
      (this.icon_view as TablerIconView).model.icon_name = icon
    }
    this.icon_view.el.style.lineHeight = "0"
  }

  get_active_icon(): string {
    return this.model.active_icon !== "" ? this.model.active_icon : `${this.model.icon}-filled`
  }

  calculate_size(factor: number = 1): string {
    if (this.model.size !== null) {
      return `calc(${this.model.size} * ${factor})`
    }
    const maxWidth = this.model.width ?? 15
    const maxHeight = this.model.height ?? 15
    const size = Math.max(maxWidth, maxHeight) * factor
    return `${size}px`
  }

  click(): void {
    this.model.trigger_event(new ButtonClick())
  }
}

export namespace ClickableIcon {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Control.Props & {
    active_icon: p.Property<string>
    icon: p.Property<string>
    size: p.Property<string | null>
    value: p.Property<boolean>
    title: p.Property<string>
    tooltip: p.Property<Tooltip | null>
    tooltip_delay: p.Property<number>
  }
}

export interface ClickableIcon extends ClickableIcon.Attrs { }

export class ClickableIcon extends Control {
  declare properties: ClickableIcon.Props
  declare __view_type__: ClickableIconView
  static override __module__ = "panel.models.icon"

  constructor(attrs?: Partial<ClickableIcon.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = ClickableIconView

    this.define<ClickableIcon.Props>(({Nullable, Ref, Float, Str, Bool}) => ({
      active_icon: [Str, ""],
      icon: [Str, "heart"],
      size: [Nullable(Str), null],
      value: [Bool, false],
      title: [Str, ""],
      tooltip: [Nullable(Ref(Tooltip)), null],
      tooltip_delay: [Float, 500],
    }))
  }

  on_click(callback: EventCallback<ButtonClick>): void {
    this.on_event(ButtonClick, callback)
  }
}
