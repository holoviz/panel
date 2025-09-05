import {Column, ColumnView} from "./column"
import {ModelEvent, server_event} from "@bokehjs/core/bokeh_events"
import type * as p from "@bokehjs/core/properties"
import type {Attrs} from "@bokehjs/core/types"
import {build_views} from "@bokehjs/core/build_views"
import type {UIElementView} from "@bokehjs/models/ui/ui_element"
import {ColumnView as BkColumnView} from "@bokehjs/models/layouts/column"

@server_event("scroll_latest_event")
export class ScrollLatestEvent extends ModelEvent {
  constructor(readonly model: Feed, readonly rerender: boolean, readonly scroll_limit?: number | null) {
    super()
    this.origin = model
    this.rerender = rerender
    this.scroll_limit = scroll_limit
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, rerender: this.rerender, scroll_limit: this.scroll_limit}
  }

  static override from_values(values: object) {
    const {model, rerender, scroll_limit} = values as {model: Feed, rerender: boolean, scroll_limit?: number}
    return new ScrollLatestEvent(model, rerender, scroll_limit)
  }
}

export class FeedView extends ColumnView {
  declare model: Feed
  _intersection_observer: IntersectionObserver
  _last_visible: UIElementView | null
  _rendered: boolean = false
  _sync: boolean
  _reference: number | null = null
  _reference_view: UIElementView | null = null

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

      if (visible.length > 0) {
        const refs = this.child_models.map((model) => model.id)
        const indices = visible.map((ref) => refs.indexOf(ref))
        this._last_visible = this.child_views[Math.min(...indices)]
      } else {
        this._last_visible = null
      }
    }, {
      root: this.el,
      threshold: 0.01,
    })
  }

  override connect_signals(): void {
    super.connect_signals()
    this.model.on_event(ScrollLatestEvent, (event: ScrollLatestEvent) => {
      this.scroll_to_latest(event.scroll_limit)
      if (event.rerender) {
        this._rendered = false
      }
    })
  }

  get node_map(): any {
    const nodes = new Map()
    for (const view of this.child_views) {
      nodes.set(view.el, view.model)
    }
    return nodes
  }

  override async update_children(): Promise<void> {
    const last = this._last_visible
    const scroll_top = this.el.scrollTop
    this._reference_view = last
    this._reference = last?.el.offsetTop || 0
    this._sync = false
    const created = await this.build_child_views()
    const created_children = new Set(created)
    const createdLength = created.length
    const views_length = this.child_views.length

    // Check whether we simply have to prepend or append items
    // instead of removing and reordering them
    const is_prepended = created.every((view, index) => view === this.child_views[index])
    const is_appended = created.every((view, index) => view === this.child_views[views_length - createdLength + index])
    const reorder = !(is_prepended || is_appended)
    if (reorder) {
      // First remove and then either reattach existing elements or render and
      // attach new elements, so that the order of children is consistent, while
      // avoiding expensive re-rendering of existing views.
      for (const child_view of this.child_views) {
        child_view.el.remove()
      }
    }
    const prepend: Element[] = []
    for (const child_view of this.child_views) {
      const is_new = created_children.has(child_view)
      const target = this.shadow_el
      if (reorder) {
        if (is_new) {
          child_view.render_to(target)
        } else {
          target.append(child_view.el)
        }
      } else {
        if (is_new) {
          child_view.render()
          child_view.r_after_render()
          if (is_appended) {
            target.append(child_view.el)
          } else if (is_prepended) {
            prepend.push(child_view.el)
          }
        }
      }
    }
    if (is_prepended) {
      this.shadow_el.prepend(...prepend)
    }
    this.r_after_render()
    this._update_children()
    this.invalidate_layout()
    this._sync = true

    // Ensure we adjust the scroll position in case we prepended items
    if (is_prepended) {
      requestAnimationFrame(() => {
        const after_offset = this._reference_view?.el.offsetTop || 0
        const offset = (after_offset-(this._reference || 0))
        this.el.scrollTo({top: scroll_top + offset, behavior: "smooth"})
      })
    }
  }

  override async build_child_views(): Promise<UIElementView[]> {
    const {created, removed} = await build_views(this._child_views, this.child_models, {parent: this})

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
      this._resize_observer.observe(view.el, {box: "border-box"})
      this._intersection_observer.observe(view.el)
    }

    return created
  }

  override _update_layout(): void {
    super._update_layout()
    this.style.append(":host > div", {max_height: "unset"})
  }

  override render(): void {
    this._rendered = false
    super.render()
  }

  override trigger_auto_scroll(): void {}

  override after_render(): void {
    BkColumnView.prototype.after_render.call(this)
    requestAnimationFrame(() => {
      if (this.model.scroll_position) {
        this.scroll_to_position()
      }
      if (this.model.view_latest && !this._rendered) {
        this.scroll_to_latest()
      }
      this.toggle_scroll_button()
      this._rendered = true
    })
  }
}

export namespace Feed {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Column.Props & {
    visible_children: p.Property<string[]>
  }
}

export interface Feed extends Feed.Attrs { }

export class Feed extends Column {
  declare properties: Feed.Props

  constructor(attrs?: Partial<Feed.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.feed"

  static {
    this.prototype.default_view = FeedView

    this.define<Feed.Props>(({List, Str}) => ({
      visible_children: [List(Str), []],
    }))
  }
}
