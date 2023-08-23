import { Column as BkColumn, ColumnView as BkColumnView } from "@bokehjs/models/layouts/column";
import * as DOM from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties";

export class ColumnView extends BkColumnView {
  model: Column;
  scroll_down_button_el: HTMLElement;

  connect_signals(): void {
    super.connect_signals();

    const { children, scroll_position, scroll_button_threshold } = this.model.properties;

    this.on_change(children, () => this.trigger_auto_scroll());
    this.on_change(scroll_position, () => this.scroll_to_position());
    this.on_change(scroll_button_threshold, () => this.toggle_scroll_button())
  }

  get distance_from_latest(): number {
    return this.el.scrollHeight - this.el.scrollTop - this.el.clientHeight;
  }

  scroll_to_position(): void {
    requestAnimationFrame(() => {
      this.el.scrollTop = this.model.scroll_position;
    });
  }

  scroll_to_latest(): void {
    // Waits for the child to be rendered before scrolling
    requestAnimationFrame(() => {
      this.el.scrollTop = this.el.scrollHeight;
    });
  }

  trigger_auto_scroll(): void {
    const limit = this.model.auto_scroll_limit
    const within_limit = this.distance_from_latest <= limit
    if (limit == 0 || !within_limit)
      return

    this.scroll_to_latest()
  }

  record_scroll_position(): void {
    this.model.scroll_position = this.el.scrollTop;
  }

  toggle_scroll_button(): void {
    const threshold = this.model.scroll_button_threshold
    const exceeds_threshold = this.distance_from_latest >= threshold
    if (this.scroll_down_button_el) {
      this.scroll_down_button_el.classList.toggle(
        "visible", threshold !== 0 && exceeds_threshold
      )
    };
  }

  render(): void {
    super.render()
    this.scroll_down_button_el = DOM.createElement('div', { class: 'scroll-button' });
    this.shadow_el.appendChild(this.scroll_down_button_el);
    this.el.addEventListener("scroll", () => {
      this.record_scroll_position();
      this.toggle_scroll_button();
    });
    this.scroll_down_button_el.addEventListener("click", () => {
      this.scroll_to_latest();
    });
  }

  after_render(): void {
    super.after_render()
    requestAnimationFrame(() => {
      if (this.model.scroll_position) {
        this.scroll_to_position();
      }
      if (this.model.view_latest) {
        this.scroll_to_latest();
      }
      this.toggle_scroll_button();
    });
  }
}

export namespace Column {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = BkColumn.Props & {
    scroll_position: p.Property<number>;
    auto_scroll_limit: p.Property<number>;
    scroll_button_threshold: p.Property<number>;
    view_latest: p.Property<boolean>;
  };
}

export interface Column extends Column.Attrs { }

export class Column extends BkColumn {
  properties: Column.Props;

  constructor(attrs?: Partial<Column.Attrs>) {
    super(attrs);
  }

  static __module__ = "panel.models.layout";

  static {
    this.prototype.default_view = ColumnView;

    this.define<Column.Props>(({ Int, Boolean }) => ({
      scroll_position: [Int, 0],
      auto_scroll_limit: [Int, 0],
      scroll_button_threshold: [Int, 0],
      view_latest: [Boolean, false],
    }));
  }
}
