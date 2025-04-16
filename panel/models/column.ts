import {ModelEvent, server_event} from "@bokehjs/core/bokeh_events"
import {div} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import type {Attrs} from "@bokehjs/core/types"
import type {EventCallback} from "@bokehjs/model"
import {Column as BkColumn, ColumnView as BkColumnView} from "@bokehjs/models/layouts/column"

export class ScrollButtonClick extends ModelEvent {
  static {
    this.prototype.event_name = "scroll_button_click"
  }
}

@server_event("scroll_to")
export class ScrollToEvent extends ModelEvent {
  constructor(readonly model: Column, readonly index: any) {
    super()
    this.index = index
    this.origin = model
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, index: this.index}
  }

  static override from_values(values: object) {
    const {model, index} = values as {model: Column, index: any}
    return new ScrollToEvent(model, index)
  }
}

export class ColumnView extends BkColumnView {
  declare model: Column
  _updating: boolean = false

  scroll_down_button_el: HTMLElement

  override connect_signals(): void {
    super.connect_signals()

    const {children, scroll_position, scroll_button_threshold} = this.model.properties

    this.on_change(children, () => this.trigger_auto_scroll())
    this.on_change(scroll_position, () => this.scroll_to_position())
    this.on_change(scroll_button_threshold, () => this.toggle_scroll_button())
    this.model.on_event(ScrollToEvent, (event: ScrollToEvent) => this.scroll_to_index(event.index))
  }

  get distance_from_latest(): number {
    return this.el.scrollHeight - this.el.scrollTop - this.el.clientHeight
  }

  scroll_to_index(index: number): void {
    if (index === null) {
      return
    }

    if (index >= this.model.children.length) {
      console.warn(`Invalid scroll index: ${index}`)
      return
    }

    // Get the child view at the specified index
    const childView = this.child_views[index]
    if (!childView) {
      console.warn(`Child view not found for index: ${index}`)
      return
    }

    // Get the top position of the child element relative to the column
    const childEl = childView.el
    const childRect = childEl.getBoundingClientRect()
    const columnRect = this.el.getBoundingClientRect()
    const relativeTop = childRect.top - columnRect.top + this.el.scrollTop

    // Scroll to the child's position
    this.model.scroll_position = Math.round(relativeTop)
  }

  scroll_to_position(): void {
    if (this._updating) {
      return
    }
    requestAnimationFrame(() => {
      this.el.scrollTo({top: this.model.scroll_position, behavior: "instant"})
    })
  }

  scroll_to_latest(scroll_limit: number | null = null): void {
    if (scroll_limit !== null) {
      const within_limit = this.distance_from_latest <= scroll_limit
      if (!within_limit) {
        return
      }
    }

    requestAnimationFrame(() => {
      this.model.scroll_position = Math.round(this.el.scrollHeight)
    })
  }

  trigger_auto_scroll(): void {
    const limit = this.model.auto_scroll_limit
    if (limit == 0) {
      return
    }
    const within_limit = this.distance_from_latest <= limit
    if (!within_limit) {
      return
    }

    this.scroll_to_latest()
  }

  record_scroll_position(): void {
    this._updating = true
    this.model.scroll_position = Math.round(this.el.scrollTop)
    this._updating = false
  }

  toggle_scroll_button(): void {
    const threshold = this.model.scroll_button_threshold
    if (!this.scroll_down_button_el || threshold === 0) {
      return
    }
    const exceeds_threshold = this.distance_from_latest >= threshold
    this.scroll_down_button_el.classList.toggle("visible", exceeds_threshold)
  }

  override render(): void {
    super.render()
    this.scroll_down_button_el = div({class: "scroll-button"})
    this.shadow_el.appendChild(this.scroll_down_button_el)
    this.el.addEventListener("scroll", () => {
      this.record_scroll_position()
      this.toggle_scroll_button()
    })
    this.scroll_down_button_el.addEventListener("click", () => {
      this.scroll_to_latest()
      this.model.trigger_event(new ScrollButtonClick())
    })
  }

  override async update_children(): Promise<void> {
    let current_views = [...this.child_views]
    const created = await this.build_child_views()
    const created_children = new Set(created)
    const current_elements = Array.from(this.shadow_el.children).filter(el => {
      return this.child_views.some(view => view.el === el)
    })
    // Generate previous ordering
    current_views = current_views.filter(view => !current_elements.includes(view.el))

    const added = new Set()
    for (let i = 0; i < this.child_views.length; i++) {
      const child_view = this.child_views[i]
      const is_new = created_children.has(child_view)
      const target = child_view.rendering_target()

      if (is_new) {
        child_view.render()
      }

      if (target != null) {
        if (!target.contains(child_view.el)) {
          if (child_view.el.parentNode) {
            child_view.el.remove()
          }
          target.append(child_view.el)
        }
      } else {
	// Compute insertion point for view in previous ordering
        const next_view = current_views.find(view => current_elements.includes(view.el) && !added.has(view))
        if (next_view) {
          this.shadow_el.insertBefore(child_view.el, next_view.el)
        } else {
          this.shadow_el.appendChild(child_view.el)
        }
      }
      added.add(child_view)
    }

    this.r_after_render()
    this._update_children()
    this.invalidate_layout()
  }

  override async update_children(): Promise<void> {
    // Can be removed after https://github.com/bokeh/bokeh/pull/14459 is released
    let current_views = [...this.child_views]
    const created = await this.build_child_views()
    const created_children = new Set(created)

    // The newly generated child_views are added to the shadow_el one-by-one
    // In order to determine the correct ordering we compute the existing
    // order and then either insert each item before an existing node or append it.
    // This ensures correct ordering without removing and then re-adding DOM nodes
    // which can cause issues for certain virtual DOM implementations (e.g. React).
    const current_elements = Array.from(this.shadow_el.children).filter(el => {
      return this.child_views.some(view => view.el === el)
    })
    current_views = current_views.filter(view => !current_elements.includes(view.el))

    const added = new Set()
    for (const child_view of this.child_views) {
      const is_new = created_children.has(child_view)
      const target = child_view.rendering_target()

      if (is_new) {
        child_view.render()
      }

      if (target !== null) {
        if (!target.contains(child_view.el)) {
          if (child_view.el.parentNode !== null) {
            child_view.el.remove()
          }
          target.append(child_view.el)
        }
      } else {
        // Compute insertion point for view in previous ordering
        const next_view = current_views.find(view => current_elements.includes(view.el) && !added.has(view))
        if (next_view === undefined) {
          this.shadow_el.appendChild(child_view.el)
        } else {
          this.shadow_el.insertBefore(child_view.el, next_view.el)
        }
      }
      added.add(child_view)
    }

    this.r_after_render()
    this._update_children()
    this.invalidate_layout()
  }

  override after_render(): void {
    super.after_render()
    requestAnimationFrame(() => {
      if (this.model.scroll_position) {
        this.scroll_to_position()
      }
      if (this.model.view_latest) {
        this.scroll_to_latest()
      }
      this.toggle_scroll_button()
    })
  }
}

export namespace Column {
  export type Attrs = p.AttrsOf<Props>
  export type Props = BkColumn.Props & {
    scroll_position: p.Property<number>
    scroll_index: p.Property<number | null>
    auto_scroll_limit: p.Property<number>
    scroll_button_threshold: p.Property<number>
    view_latest: p.Property<boolean>
  }
}

export interface Column extends Column.Attrs { }

export class Column extends BkColumn {
  declare properties: Column.Props

  constructor(attrs?: Partial<Column.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.layout"

  static {
    this.prototype.default_view = ColumnView

    this.define<Column.Props>(({Int, Bool, Nullable}) => ({
      scroll_position: [Int, 0],
      scroll_index: [Nullable(Int), null],
      auto_scroll_limit: [Int, 0],
      scroll_button_threshold: [Int, 0],
      view_latest: [Bool, false],
    }))
  }

  on_click(callback: EventCallback<ScrollButtonClick>): void {
    this.on_event(ScrollButtonClick, callback)
  }
}
