import { Tooltip, TooltipView } from "@bokehjs/models/ui/tooltip"
import { TablerIcon, TablerIconView } from "@bokehjs/models/ui/icons/tabler_icon";
import { SVGIcon, SVGIconView } from "@bokehjs/models/ui/icons/svg_icon";
import { Control, ControlView } from '@bokehjs/models/widgets/control';
import type { IterViews } from '@bokehjs/core/build_views';
import * as p from "@bokehjs/core/properties";
import { build_view } from '@bokehjs/core/build_views';
import { ButtonClick } from "@bokehjs/core/bokeh_events"
import type { EventCallback } from "@bokehjs/model"

export class ClickableIconView extends ControlView {
  model: ClickableIcon;
  icon_view: TablerIconView | SVGIconView;
  was_svg_icon: boolean

  protected tooltip: TooltipView | null

  public *controls() { }

  override remove(): void {
    this.tooltip?.remove()
    this.icon_view?.remove();
    super.remove();
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize();

    this.was_svg_icon = this.is_svg_icon(this.model.icon)
    this.icon_view = await this.build_icon_model(this.model.icon, this.was_svg_icon);
    const { tooltip } = this.model
    if (tooltip != null)
      this.tooltip = await build_view(tooltip, { parent: this })
  }

  override *children(): IterViews {
    yield* super.children();
    yield this.icon_view;
    if (this.tooltip != null)
      yield this.tooltip
  }

  is_svg_icon(icon: string): boolean {
    return icon.trim().startsWith('<svg');
  }

  connect_signals(): void {
    super.connect_signals();
    const { icon, active_icon, disabled, value, size } = this.model.properties;
    this.on_change([active_icon, icon, value], () => this.update_icon());
    this.on_change(disabled, () => this.update_cursor());
    this.on_change(size, () => this.update_size());
  }

  render(): void {
    super.render();
    this.icon_view.render();
    this.update_icon()
    this.update_cursor()
    this.shadow_el.appendChild(this.icon_view.el);

    const toggle_tooltip = (visible: boolean) => {
      this.tooltip?.model.setv({
        visible,
      })
    }
    let timer: number
    this.el.addEventListener("mouseenter", () => {
      timer = setTimeout(() => toggle_tooltip(true), this.model.tooltip_delay)
    })
    this.el.addEventListener("mouseleave", () => {
      clearTimeout(timer)
      toggle_tooltip(false)
    })
  }

  update_cursor(): void {
    this.icon_view.el.style.cursor = this.model.disabled ? 'not-allowed' : 'pointer';
  }

  update_size(): void {
    this.icon_view.model.size = this.calculate_size();
  }

  async build_icon_model(icon: string, is_svg_icon: boolean): Promise<TablerIconView | SVGIconView> {
    const size = this.calculate_size();
    let icon_model;
    if (is_svg_icon) {
      icon_model = new SVGIcon({ svg: icon, size: size });
    } else {
      icon_model = new TablerIcon({ icon_name: icon, size: size });
    }
    const icon_view = await build_view(icon_model, { parent: this });
    icon_view.el.addEventListener('click', () => this.click());
    return icon_view;
  }

  async update_icon(): Promise<void> {
    const icon = this.model.value ? this.get_active_icon() : this.model.icon;
    this.class_list.toggle("active", this.model.value);
    const is_svg_icon = this.is_svg_icon(icon)

    if (this.was_svg_icon !== is_svg_icon) {
      // If the icon type has changed, we need to rebuild the icon view
      // and invalidate the old one.
      const icon_view = await this.build_icon_model(icon, is_svg_icon);
      icon_view.render();
      this.icon_view.remove();
      this.icon_view = icon_view;
      this.was_svg_icon = is_svg_icon;
      this.update_cursor();
      this.shadow_el.appendChild(this.icon_view.el);
    }
    else if (is_svg_icon) {
      (this.icon_view as SVGIconView).model.svg = icon;
    } else {
      (this.icon_view as TablerIconView).model.icon_name = icon;
    }
    this.icon_view.el.style.lineHeight = '0';
  }

  get_active_icon(): string {
    return this.model.active_icon !== '' ? this.model.active_icon : `${this.model.icon}-filled`;
  }

  calculate_size(): string {
    if (this.model.size !== null)
      return this.model.size
    const maxWidth = this.model.width ?? 15;
    const maxHeight = this.model.height ?? 15;
    const size = Math.max(maxWidth, maxHeight);
    return `${size}px`;
  }

  click(): void {
    this.model.trigger_event(new ButtonClick())
  }
}

export namespace ClickableIcon {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = Control.Props & {
    active_icon: p.Property<string>;
    icon: p.Property<string>;
    size: p.Property<string | null>;
    value: p.Property<boolean>;
    tooltip: p.Property<Tooltip | null>
    tooltip_delay: p.Property<number>
  };
}

export interface ClickableIcon extends ClickableIcon.Attrs { }

export class ClickableIcon extends Control {
  properties: ClickableIcon.Props;
  declare __view_type__: ClickableIconView
  static __module__ = "panel.models.icon";

  constructor(attrs?: Partial<ClickableIcon.Attrs>) {
    super(attrs);
  }

  static {
    this.prototype.default_view = ClickableIconView;

    this.define<ClickableIcon.Props>(({ Nullable, Ref, Number, String, Bool }) => ({
      active_icon: [String, ""],
      icon: [String, "heart"],
      size: [Nullable(String), null],
      value: [Bool, false],
      tooltip: [Nullable(Ref(Tooltip)), null],
      tooltip_delay: [Number, 500],
    }));
  }

  on_click(callback: EventCallback<ButtonClick>): void {
    this.on_event(ButtonClick, callback)
  }
}
