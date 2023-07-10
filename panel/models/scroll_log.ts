import { Column, ColumnView } from "@bokehjs/models/layouts/column";
import * as p from "@bokehjs/core/properties";

export class ScrollLogView extends ColumnView {
  model: ScrollLog;
  scroll_down_arrow: HTMLElement;

  connect_signals(): void {
    super.connect_signals();

    const { autoscroll } = this.model.properties;

    if (autoscroll) {
      this.on_change(this.model.properties.children, () => {
        this.scroll_to_bottom();
      });
    }

    this.el.addEventListener("scroll", () => {
      const scrollThreshold = 20;
      const scrollDistanceFromBottom =
        this.el.scrollHeight - this.el.scrollTop - this.el.clientHeight;

      this.scroll_down_arrow.classList.toggle(
        "visible", scrollDistanceFromBottom >= scrollThreshold
      )
    });

    this.scroll_down_arrow.addEventListener("click", () => {
      this.scroll_to_bottom();
    });
  }

  scroll_to_bottom(): void {
    this.el.scrollTop = this.el.scrollHeight;
  }
}

export namespace ScrollLog {
  export type Attrs = p.AttrsOf<Props>;

  export type Props = Column.Props & {
    autoscroll: p.Property<boolean>;
  };
}

export interface ScrollLog extends ScrollLog.Attrs { }

export class ScrollLog extends Column {
  properties: ScrollLog.Props;

  constructor(attrs?: Partial<ScrollLog.Attrs>) {
    super(attrs);
  }

  static __module__ = "panel.models.layout";

  static {
    this.prototype.default_view = ScrollLogView;

    this.define<ScrollLog.Props>(({ Boolean }) => ({
      autoscroll: [Boolean, true],
    }));
  }
}
