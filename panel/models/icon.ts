import { TablerIcon, TablerIconView } from "@bokehjs/models/ui/icons/tabler_icon";
import { SVGIcon, SVGIconView } from "@bokehjs/models/ui/icons/svg_icon";
import { Control, ControlView } from '@bokehjs/models/widgets/control';
import type { IterViews } from '@bokehjs/core/build_views';
import * as p from "@bokehjs/core/properties";
import { build_view } from '@bokehjs/core/build_views';

export class ClickableIconView extends ControlView {
  model: ClickableIcon;
  icon_view: TablerIconView | SVGIconView;
  was_svg_icon: boolean

  public *controls() { }

  override remove(): void {
    this.icon_view?.remove();
    super.remove();
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize();

    this.was_svg_icon = this.is_svg_icon(this.model.icon)
    this.icon_view = await this.build_icon_model(this.model.icon, this.was_svg_icon);
  }

  override *children(): IterViews {
    yield* super.children();
    yield this.icon_view;
  }

  is_svg_icon(icon: string): boolean {
    return icon.trim().startsWith('<svg');
  }

  toggle(): void { }

  connect_signals(): void {
    super.connect_signals();
    const { icon, active_icon, disabled } = this.model.properties;
    this.on_change([active_icon, icon], () => this.update_icon());
    this.on_change(disabled, () => this.update_cursor());
  }

  render(): void {
    super.render();
    this.icon_view.render();
    this.update_icon()
    this.update_cursor()
    this.shadow_el.appendChild(this.icon_view.el);
  }

  update_cursor(): void {
    this.icon_view.el.style.cursor = this.model.disabled ? 'not-allowed' : 'pointer';
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
    icon_view.el.addEventListener('click', () => this.toggle());
    return icon_view;
  }

  get_icon(): string {
    return this.model.icon;
  }

  async update_icon(): Promise<void> {
    const icon = this.get_icon();
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
}

export namespace ClickableIcon {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = Control.Props & {
    active_icon: p.Property<string>;
    icon: p.Property<string>;
    size: p.Property<string | null>;
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

    this.define<ClickableIcon.Props>(({ Nullable, String }) => ({
      active_icon: [String, ""],
      icon: [String, "heart"],
      size: [Nullable(String), null],
    }));
  }
}

// ToggleIcon

export class ToggleIconView extends ClickableIconView {
  model: ToggleIcon;

  public *controls() { }

  toggle(): void {
    if (this.model.disabled) {
      return;
    }
    this.model.value = !this.model.value;
    this.update_icon()
  }

  get_icon(): string {
    return this.model.value ? this.get_active_icon() : this.model.icon;
  }

  connect_signals(): void {
    super.connect_signals();
    const { value } = this.model.properties;
    this.on_change(value, () => this.update_icon());
  }
}

export namespace ToggleIcon {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = ClickableIcon.Props & {
    value: p.Property<boolean>;
  };
}

export interface ToggleIcon extends ToggleIcon.Attrs { }

export class ToggleIcon extends ClickableIcon {
  properties: ToggleIcon.Props;
  declare __view_type__: ToggleIconView
  static __module__ = "panel.models.icon";

  constructor(attrs?: Partial<ToggleIcon.Attrs>) {
    super(attrs);
  }

  static {
    this.prototype.default_view = ToggleIconView;

    this.define<ToggleIcon.Props>(({ Boolean }) => ({
      value: [Boolean, false],
    }));
  }
}

// ButtonIcon

export class ButtonIconView extends ClickableIconView {
  model: ButtonIcon;
  _value: boolean;
  _click_listener: any

  public *controls() { }

  toggle(): void {
    if (this.model.disabled) {
      return;
    }
    const updateState = (value: boolean, disabled: boolean) => {
      this._value = value;
      this.model.disabled = disabled;
      this.update_icon();
    };
    updateState(true, true);

    new Promise(resolve => setTimeout(resolve, this.model.active_duration))
      .then(() => {
        updateState(false, false);
      });
  }

  update_cursor(): void {
    this.icon_view.el.style.cursor = this.model.disabled ? 'default' : 'pointer';
  }

  get_icon(): string {
    return this._value ? this.get_active_icon() : this.model.icon;
  }

  render(): void {
    super.render();
    this._click_listener = this.increment_clicks.bind(this)
    this.icon_view.el.addEventListener("click", this._click_listener)
  }

  increment_clicks() : void {
    this.model.clicks = this.model.clicks + 1
  }

  connect_signals(): void {
    super.connect_signals();
  }
}

export namespace ButtonIcon {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = ClickableIcon.Props & {
    clicks: p.Property<number>;
    active_duration: p.Property<number>;
  };
}

export interface ButtonIcon extends ButtonIcon.Attrs { }

export class ButtonIcon extends ClickableIcon {
  properties: ButtonIcon.Props;
  declare __view_type__: ButtonIconView
  static __module__ = "panel.models.icon";

  constructor(attrs?: Partial<ButtonIcon.Attrs>) {
    super(attrs);
  }

  static {
    this.prototype.default_view = ButtonIconView;

    this.define<ButtonIcon.Props>(({ Int }) => ({
      clicks: [Int, 0],
      active_duration: [Int, 75],
    }));
  }
}
