import { Column, ColumnView } from "./column";
import * as p from "@bokehjs/core/properties";

export class LogView extends ColumnView {
  model: Log;

  connect_signals(): void {
    super.connect_signals();

    const { children, loaded_entries, scroll_load_threshold } = this.model.properties;

    this.on_change(children, () => this.handle_new_entries());
    this.on_change(loaded_entries, () => this.hide_unloaded_entries());
    this.on_change(scroll_load_threshold, () => this.trigger_load_entries());
  }

  get unloaded_entries(): number {
    return this.model.children.length - this.model.loaded_entries;
  }

  handle_new_entries(): void {
    this.model.loaded_entries = Math.min(this.model.children.length, this.model.loaded_entries);
    this.hide_unloaded_entries();
    this.trigger_load_entries();
  }

  hide_unloaded_entries(): void {
    for (let i = 0; i < this.unloaded_entries; i++) {
      this.model.children[i].visible = false;
    }
  }

  show_loaded_entries(): void {
    for (let i = this.unloaded_entries; i < this.model.children.length; i++) {
      this.model.children[i].visible = true;
    }
  }

  trigger_load_entries(): void {
    if (this.el.scrollTop < this.model.scroll_load_threshold && this.model.loaded_entries < this.model.children.length) {
      const entriesToAdd = Math.min(this.model.entries_per_load, this.unloaded_entries);
      this.model.loaded_entries += entriesToAdd;

      const initialHeight = this.el.scrollHeight;
      this.show_loaded_entries();
      const newHeight = this.el.scrollHeight;
      const heightDifference = newHeight - initialHeight;
      this.model.scroll_position = Math.round(heightDifference);
    }
  }

  render(): void {
    super.render()
    this.hide_unloaded_entries()
    this.el.addEventListener("scroll", () => {
      this.trigger_load_entries();
    });
  }

  after_render(): void {
    super.after_render()
  }
}

export namespace Log {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = Column.Props & {
    min_entries: p.Property<number>;
    loaded_entries: p.Property<number>;
    entries_per_load: p.Property<number>;
    scroll_load_threshold: p.Property<number>;
  };
}

export interface Log extends Log.Attrs { }

export class Log extends Column {
  properties: Log.Props;

  constructor(attrs?: Partial<Log.Attrs>) {
    super(attrs);
  }

  static __module__ = "panel.models.layout";

  static {
    this.prototype.default_view = LogView;

    this.define<Log.Props>(({ Int }) => ({
      min_entries: [Int, 20],
      loaded_entries: [Int, 20],
      entries_per_load: [Int, 20],
      scroll_load_threshold: [Int, 40],
    }));
  }
}
