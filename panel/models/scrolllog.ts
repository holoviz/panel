import { Column, ColumnView } from "@bokehjs/models/layouts/column";
import * as DOM from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties";

export class ScrollLogView extends ColumnView {
  model: ScrollLog;
  scroll_down_arrow_el: HTMLElement;

  scroll_to_bottom(): void {
    this.el.scrollTop = this.el.scrollHeight;
  }

  connect_signals(): void {
    super.connect_signals();

    const { autoscroll } = this.model.properties;

    if (autoscroll) {
      this.on_change(this.model.properties.children, () => {
        this.scroll_to_bottom();
      });
    }
  }

  render(): void {
    super.render()
    this.empty()
    this._update_stylesheets()
    this._update_css_classes()
    this._apply_styles()
    this._apply_visible()

    this.class_list.add(...this.css_classes())
    this.el.style.overflowY = "auto"
    this.el.style.height = "300px"

    this.scroll_down_arrow_el = DOM.createElement('div', { class: 'scroll-down-arrow' });
    this.scroll_down_arrow_el.textContent = '⬇';
    this.shadow_el.appendChild(this.scroll_down_arrow_el);

    this.scroll_down_arrow_el.addEventListener("click", () => {
      this.scroll_to_bottom();
    });

    this.el.addEventListener("scroll", () => {
      const scrollThreshold = 20;
      const scrollDistanceFromBottom = this.el.scrollHeight - this.el.scrollTop - this.el.clientHeight;

      this.scroll_down_arrow_el.classList.toggle(
        "visible", scrollDistanceFromBottom >= scrollThreshold
      )
    });

    for (const child_view of this.child_views.slice(1)) {
      this.shadow_el.appendChild(child_view.el)
      child_view.render()
      child_view.after_render()
    }
  }

  after_render(): void {
    super.after_render()
    this.scroll_to_bottom();
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
