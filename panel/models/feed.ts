import { Column, ColumnView } from "./column";
import * as p from "@bokehjs/core/properties";
import { build_views } from "@bokehjs/core/build_views"
import { UIElementView } from "@bokehjs/models/ui/ui_element"
import { ModelEvent } from "@bokehjs/core/bokeh_events"
import type { EventCallback } from "@bokehjs/model"


export class ScrollButtonClick extends ModelEvent {
  static {
    this.prototype.event_name = "scroll_button_click"
  }
}


export class FeedView extends ColumnView {
  model: Feed;
  _intersection_observer: IntersectionObserver
  _last_visible: UIElementView | null
  _sync: boolean

  override initialize(): void {
    super.initialize()
    this._sync = true
    this._intersection_observer = new IntersectionObserver((entries) => {
      const visible = [...this.model.visible_children]
      const nodes = this.node_map

      for (const entry of entries) {
        const id = nodes.get(entry.target).id
        if (entry.isIntersecting) {
          if (!visible.includes(id)) {
            visible.push(id)
          }
        } else if (visible.includes(id)) {
          visible.splice(visible.indexOf(id), 1)
        }
      }

      if (this._sync) {
        this.model.visible_children = visible
      }

      if (visible.length) {
        const refs = this.child_models.map((model) => model.id)
        const indices = visible.map((ref) => refs.indexOf(ref))
        this._last_visible = this.child_views[Math.min(...indices)]
      } else {
        this._last_visible = null
      }
    }, {
      root: this.el,
      threshold: .01
    })
  }

  get node_map(): any {
    const nodes = new Map()
    for (const view of this.child_views) {
      nodes.set(view.el, view.model)
    }
    return nodes
  }

  async update_children(): Promise<void> {
    this._sync = false
    await super.update_children()
    this._sync = true
    this._last_visible?.el.scrollIntoView(true)
  }

  async build_child_views(): Promise<UIElementView[]> {
    const { created, removed } = await build_views(this._child_views, this.child_models, { parent: this })

    const visible = this.model.visible_children
    for (const view of removed) {
      if (visible.includes(view.model.id)) {
        visible.splice(visible.indexOf(view.model.id), 1)
      }
      this._resize_observer.unobserve(view.el)
      this._intersection_observer.unobserve(view.el)
    }
    this.model.visible_children = [...visible]

    for (const view of created) {
      this._resize_observer.observe(view.el, { box: "border-box" })
      this._intersection_observer.observe(view.el)
    }

    return created
  }

  scroll_to_latest(emit_event: boolean = true): void {
    if (emit_event) {
      this.model.trigger_event(new ScrollButtonClick())
    }
    super.scroll_to_latest()
  }

  trigger_auto_scroll(): void {
    const limit = this.model.auto_scroll_limit
    const within_limit = this.distance_from_latest <= limit
    if (limit == 0 || !within_limit)
      return

    this.scroll_to_latest(false)
  }
}

export namespace Feed {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = Column.Props & {
    visible_children: p.Property<string[]>;
  };
}

export interface Feed extends Feed.Attrs { }

export class Feed extends Column {
  properties: Feed.Props;

  constructor(attrs?: Partial<Feed.Attrs>) {
    super(attrs);
  }

  static __module__ = "panel.models.feed";

  static {
    this.prototype.default_view = FeedView;

    this.define<Feed.Props>(({ List, Str }) => ({
      visible_children: [List(Str), []],
    }));
  }

  on_click(callback: EventCallback<ScrollButtonClick>): void {
    this.on_event(ScrollButtonClick, callback)
  }
}
