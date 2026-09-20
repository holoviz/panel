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
  protected _visibility_pending: boolean = false
  protected _visibility_listener: boolean = false
  protected _latest_pending: boolean = false
  _last_visible: UIElementView | null
  _rendered: boolean = false
  _sync: boolean
  _reference: number | null = null
  _reference_view: UIElementView | null = null
  protected _children_update: Promise<void> | null = null
  protected _latest_scroll_pending: boolean = false
  protected _latest_timer: ReturnType<typeof setTimeout> | null = null

  override initialize(): void {
    super.initialize()
    this._sync = true
    // A Feed that does not clip lets an ancestor scroll, and rooting on it
    // would report every child visible until all objects load (#8661).
    const is_scroll_container = this.is_scroll_container
    const root = is_scroll_container ? this.el : null
    this._intersection_observer = new IntersectionObserver((entries) => {
      // Until its stylesheets load the Feed does not clip, so all children intersect.
      // Before the initial scroll to the latest child the top children are
      // visible; reporting them makes the server load the wrong range.
      if (this._latest_pending || (is_scroll_container && getComputedStyle(this.el).overflowY === "visible")) {
        this._visibility_pending = true
        return
      }
      const visible = [...this.model.visible_children]
      const nodes = this.node_map

      for (const entry of entries) {
        const id = nodes.get(entry.target)?.id
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
      root,
      threshold: 0.01,
    })
  }

  override connect_signals(): void {
    super.connect_signals()
    this.model.on_event(ScrollLatestEvent, async (event: ScrollLatestEvent) => {
      if (event.rerender) {
        this._rendered = false
      }
      const limit = event.scroll_limit
      if (limit != null && this.distance_from_latest > limit) {
        return
      }
      if (event.rerender) {
        // The children it rerendered may not have arrived yet
        this._latest_scroll_pending = true
      }
      // Until the scroll lands, the children at the old position report as
      // visible and make the server load that range again.
      if (this.is_scroll_container) {
        this._hold_latest()
      }
      await this._children_update
      this._scroll_to_latest_children()
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
    const update = this._rebuild_children()
    this._children_update = update
    try {
      await update
    } finally {
      if (this._children_update === update) {
        this._children_update = null
      }
    }
    if (this._latest_scroll_pending) {
      this._latest_scroll_pending = false
      this._scroll_to_latest_children()
    }
  }

  _scroll_to_latest_children(): void {
    // A Feed that cannot scroll yet reports nothing, so leave the retry to
    // scroll_position rather than holding the visibility.
    if (!this._latest_pending || !this._land_latest_scroll()) {
      this._release_latest()
      this.scroll_to_latest()
    }
  }

  protected async _rebuild_children(): Promise<void> {
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
    // The reference child may have been removed, its offset is then meaningless.
    const reference = this._reference_view
    const reference_top = this._reference || 0
    if (is_prepended && reference != null && this.child_views.includes(reference)) {
      requestAnimationFrame(() => {
        const offset = reference.el.offsetTop - reference_top
        // A scroll to where it already is would cancel one in progress.
        if (offset !== 0) {
          this.el.scrollTo({top: scroll_top + offset, behavior: "smooth"})
        }
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
    if (this.model.view_latest && this.is_scroll_container) {
      this._hold_latest()
    }
    super.render()
    if (!this._visibility_listener) {
      this._visibility_listener = true
      this.shadow_el.addEventListener("load", (event) => {
        if (!(event.target instanceof HTMLLinkElement)) {
          return
        }
        if (this._latest_pending) {
          this._land_latest_scroll()
        } else {
          this._reobserve_children()
        }
      }, true)
    }
  }

  _reobserve_children(force: boolean = false): void {
    if (!this._visibility_pending || (!force && getComputedStyle(this.el).overflowY === "visible")) {
      return
    }
    this._visibility_pending = false
    // An observed child is only reported again once its intersection changes.
    for (const view of this.child_views) {
      this._intersection_observer.unobserve(view.el)
      this._intersection_observer.observe(view.el)
    }
  }

  override trigger_auto_scroll(): void {}

  _hold_latest(): void {
    // Should the Feed never become scrollable, e.g. because a stylesheet
    // failed, release the hold rather than never reporting visibility again.
    this._latest_pending = true
    if (this._latest_timer == null) {
      this._latest_timer = setTimeout(() => this._release_latest(true), 1000)
    }
  }

  _release_latest(force: boolean = false): void {
    if (this._latest_timer != null) {
      clearTimeout(this._latest_timer)
      this._latest_timer = null
    }
    if (this._latest_pending) {
      this._latest_pending = false
      this._reobserve_children(force)
    }
  }

  override remove(): void {
    if (this._latest_timer != null) {
      clearTimeout(this._latest_timer)
      this._latest_timer = null
    }
    super.remove()
  }

  _land_latest_scroll(): boolean {
    // Scroll now rather than frames later via scroll_position, so the
    // children are measured at the latest position.
    this.el.scrollTo({top: this.el.scrollHeight, behavior: "instant"})
    // Until its stylesheets load the scroll is a no-op, so keep waiting.
    if (getComputedStyle(this.el).overflowY === "visible") {
      return false
    }
    this._release_latest()
    return true
  }

  override after_render(): void {
    BkColumnView.prototype.after_render.call(this)
    requestAnimationFrame(() => {
      if (this.model.view_latest && !this._rendered) {
        this._land_latest_scroll()
        this.scroll_to_latest()
      } else if (this.model.scroll_position) {
        this.scroll_to_position()
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
