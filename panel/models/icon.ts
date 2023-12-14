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

    const icon_model = new TablerIcon({ icon_name: this.model.icon_name });
    this.icon_view = await build_view(icon_model, { parent: this });

    this.icon_view.el.addEventListener('click', () => this.change_input());
    this.icon_view.el.style.cursor = 'pointer';
  }

  override *children(): IterViews {
    yield* super.children();
    yield this.icon_view;
  }

  change_input(): void {
    this.model.value = !this.model.value;
    const icon_name = this.model.value ? this.getIconName() : this.model.icon_name;
    this.icon_view.model.icon_name = icon_name;
  }

  connect_signals(): void {
    super.connect_signals();
  }

  render(): void {
    super.render();

    this.icon_view.render();
    this.shadow_el.appendChild(this.icon_view.el);
  }

  private getIconName(): string {
    return this.model.active_icon_name !== '' ? this.model.active_icon_name : `${this.model.icon_name}-filled`;
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
