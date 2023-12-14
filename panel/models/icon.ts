import { TablerIcon, TablerIconView } from "@bokehjs/models/ui/icons/tabler_icon";
import { Control, ControlView } from '@bokehjs/models/widgets/control';
import type { IterViews } from '@bokehjs/core/build_views';
import * as p from "@bokehjs/core/properties";
import { build_view } from '@bokehjs/core/build_views';


export class ToggleIconView extends ControlView {
  model: ToggleIcon;
  icon_view: TablerIconView;

  public *controls() { }

  override remove(): void {
    this.icon_view?.remove();
    super.remove();
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize();

    const size = this.calculate_size();
    const icon_model = new TablerIcon({ icon_name: this.model.icon_name, size: size });
    this.icon_view = await build_view(icon_model, { parent: this });

    this.icon_view.el.addEventListener('click', () => this.toggle_value());
    this.icon_view.el.style.cursor = 'pointer';
  }

  override *children(): IterViews {
    yield* super.children();
    yield this.icon_view;
  }

  toggle_value(): void {
    this.model.value = !this.model.value;
    this.update_icon()
  }

  connect_signals(): void {
    super.connect_signals();
    const { icon_name, active_icon_name, value } = this.model.properties;
    this.on_change(icon_name, () => this.update_icon());
    this.on_change(active_icon_name, () => this.update_icon());
    this.on_change(value, () => this.update_icon());
  }

  render(): void {
    super.render();

    this.icon_view.render();
    this.update_icon()
    this.shadow_el.appendChild(this.icon_view.el);
  }

  update_icon(): void {
    const icon_name = this.model.value ? this.get_active_icon_name() : this.model.icon_name;
    this.icon_view.model.icon_name = icon_name;
  }

  get_active_icon_name(): string {
    return this.model.active_icon_name !== '' ? this.model.active_icon_name : `${this.model.icon_name}-filled`;
  }

  calculate_size(): string {
    const maxWidth = this.model.width ?? 15;
    const maxHeight = this.model.height ?? 15;
    const size = Math.max(maxWidth, maxHeight);
    return `${size}px`;
  }
}

export namespace ToggleIcon {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = Control.Props & {
    icon_name: p.Property<string>;
    active_icon_name: p.Property<string>;
    value: p.Property<boolean>;
  };
}

export interface ToggleIcon extends ToggleIcon.Attrs { }

export class ToggleIcon extends Control {
  properties: ToggleIcon.Props;
  declare __view_type__: ToggleIconView
  static __module__ = "panel.models.icon";

  constructor(attrs?: Partial<ToggleIcon.Attrs>) {
    super(attrs);
  }

  static {
    this.prototype.default_view = ToggleIconView;

    this.define<ToggleIcon.Props>(({ String, Boolean }) => ({
      icon_name: [String, "heart"],
      active_icon_name: [String, ""],
      value: [Boolean, false],
    }));
  }
}
