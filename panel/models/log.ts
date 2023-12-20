import { Column, ColumnView } from "./column";
import * as p from "@bokehjs/core/properties";

export class LogView extends ColumnView {
  model: Log;
  oldScrollHeight: number;

  connect_signals(): void {
    super.connect_signals();

    const { children, scroll_load_threshold } = this.model.properties;

    this.on_change(children, () => this.handle_new_entries());
    this.on_change(scroll_load_threshold, () => this.trigger_load_entries());
  }

  get unloaded_entries(): number {
    return this.model._num_entries - this.model.loaded_entries;
  }

  handle_new_entries(): void {
    this.model.loaded_entries = Math.min(this.model.children.length, this.model.loaded_entries);
    this.trigger_load_entries();
  }

  trigger_load_entries(): void {
    const { scrollTop, scrollHeight } = this.el;
    const { scroll_load_threshold, entries_per_load, _num_entries } = this.model;

    const thresholdMet = scrollTop < scroll_load_threshold
    const hasUnloadedEntries = this.model.loaded_entries < _num_entries
    const notLoading = this.oldScrollHeight != scrollHeight
    if ( thresholdMet && hasUnloadedEntries && notLoading) {
      const entriesToAdd = Math.min(entries_per_load, this.unloaded_entries);

      this.model.loaded_entries += entriesToAdd;
      const heightDifference = scrollHeight - this.oldScrollHeight;
      this.model.scroll_position = Math.max(scrollTop + heightDifference, this.model.scroll_load_threshold);
      this.oldScrollHeight = scrollHeight;
      console.log(this.model.scroll_position, this.model.loaded_entries);
    }
    else if (this.oldScrollHeight == scrollHeight) {
      // If the scrollHeight hasn't changed, then we're at the top of the log
      // which will continuously load entries. We need to wait
      setTimeout(() => this.trigger_load_entries(), 500);
    }
  }

  render(): void {
    super.render()
    this.el.addEventListener("scroll", () => {
      this.trigger_load_entries();
    });
  }

  after_render(): void {
    super.after_render()
    requestAnimationFrame(() => {
      this.oldScrollHeight = this.el.scrollHeight;
    })
  }
}

export namespace Log {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = Column.Props & {
    loaded_entries: p.Property<number>;
    entries_per_load: p.Property<number>;
    scroll_load_threshold: p.Property<number>;
    _num_entries: p.Property<number>;
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
      loaded_entries: [Int, 20],
      entries_per_load: [Int, 20],
      scroll_load_threshold: [Int, 5],
      _num_entries: [Int, 0],
    }));
  }
}
