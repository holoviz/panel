import { ClickableIcon, ClickableIconView } from "./icon";
import * as p from "@bokehjs/core/properties";


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
      this.increment_clicks();
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

  increment_clicks(): void {
    if (!this.model.disabled) {
      this.model.clicks = this.model.clicks + 1
    }
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
