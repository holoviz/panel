import { ClickableIcon, ClickableIconView } from "./icon";
import * as p from "@bokehjs/core/properties";


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
