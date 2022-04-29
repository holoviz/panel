import {Grid, ContentBox, Sizeable} from "@bokehjs/core/layout"
import {div, size, children, display, undisplay, position, scroll_size} from "@bokehjs/core/dom"
import {sum, remove_at} from "@bokehjs/core/util/array"
import * as p from "@bokehjs/core/properties"
import {Tabs as  BkTabs, TabsView as BkTabsView} from "@bokehjs/models/layouts/tabs"
import {LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"

import * as tabs from "@bokehjs/styles/tabs.css"
import * as buttons from "@bokehjs/styles/buttons.css"
import * as menus from "@bokehjs/styles/menus.css"


function show(element: HTMLElement): void {
  element.style.visibility = ""
  element.style.opacity = ""
}

function hide(element: HTMLElement): void {
  element.style.visibility = "hidden"
  element.style.opacity = "0"
}

export class TabsView extends BkTabsView {
  model: Tabs

  connect_signals(): void {
    super.connect_signals()
    let view: any = this
    while (view != null) {
      if (view.model.type.endsWith('Tabs')) {
	view.connect(view.model.properties.active.change, () => this.update_zindex())
      }
      view = view.parent || view._parent // Handle ReactiveHTML
    }
  }

  get is_visible(): boolean {
    let parent: any = this.parent
    let current_view: any = this
    while (parent != null) {
      if (parent.model.type.endsWith('Tabs')) {
	if (parent.child_views.indexOf(current_view) !== parent.model.active) {
	  return false
        }
      }
      current_view = parent
      parent = parent.parent || parent._parent // Handle ReactiveHTML
    }
    return true
  }

  override _update_layout(): void {
    const loc = this.model.tabs_location
    const vertical = loc == "above" || loc == "below"

    // XXX: this is a hack, this should be handled by "fit" policy in grid layout
    const {scroll_el, headers_el} = this
    this.header = new class extends ContentBox {
      protected override _measure(viewport: Sizeable) {
        const min_headers = 3

        const scroll = size(scroll_el)
        const headers = children(headers_el).slice(0, min_headers).map((el) => size(el))

        const {width, height} = super._measure(viewport)
        if (vertical) {
          const min_width = scroll.width + sum(headers.map((size) => size.width))
          return {width: viewport.width != Infinity ? viewport.width : min_width, height}
        } else {
          const min_height = scroll.height + sum(headers.map((size) => size.height))
          return {width, height: viewport.height != Infinity ? viewport.height : min_height}
        }
      }
    }(this.header_el)

    let {width_policy, height_policy} = this.model
    if (width_policy == "auto")
      width_policy = this._width_policy()
    if (height_policy == "auto")
      height_policy = this._height_policy()

    const {sizing_mode} = this.model
    if (sizing_mode != null) {
      if (sizing_mode == "fixed")
        width_policy = height_policy = "fixed"
      else if (sizing_mode == "stretch_both")
        width_policy = height_policy = "max"
      else if (sizing_mode == "stretch_width")
        width_policy = "max"
      else if (sizing_mode == "stretch_height")
        height_policy = "max"
    }

    if (vertical)
      this.header.set_sizing({width_policy: width_policy, height_policy: "fixed"})
    else
      this.header.set_sizing({width_policy: "fixed", height_policy: height_policy})

    let row = 1
    let col = 1
    switch (loc) {
      case "above": row -= 1; break
      case "below": row += 1; break
      case "left":  col -= 1; break
      case "right": col += 1; break
    }

    const header = {layout: this.header, row, col}

    const panels = this.child_views.map((child_view) => {
      return {layout: child_view.layout, row: 1, col: 1}
    })

    this.layout = new Grid([header, ...panels])
    this.layout.set_sizing(this.box_sizing())
  }

  update_zindex(): void {
    const {child_views} = this
    for (const child_view of child_views) {
      if (child_view != null && child_view.el != null)
        child_view.el.style.zIndex = ""
    }
    if (this.is_visible) {
      const active = child_views[this.model.active]
      if (active != null && active.el != null)
        active.el.style.zIndex = "1"
    }
  }

  override update_position(): void {
    super.update_position()

    this.header_el.style.position = "absolute" // XXX: do it in position()
    position(this.header_el, this.header.bbox)

    const loc = this.model.tabs_location
    const vertical = loc == "above" || loc == "below"

    const scroll_el_size = size(this.scroll_el)
    const headers_el_size = scroll_size(this.headers_el)
    if (vertical) {
      const {width} = this.header.bbox
      if (headers_el_size.width > width) {
        this.wrapper_el.style.maxWidth = `${width - scroll_el_size.width}px`
        display(this.scroll_el)
        this.do_scroll(this.model.active)
      } else {
        this.headers_el.style.left = '0px'
        this.wrapper_el.style.maxWidth = ""
        undisplay(this.scroll_el)
      }
    } else {
      const {height} = this.header.bbox
      if (headers_el_size.height > height) {
        this.wrapper_el.style.maxHeight = `${height - scroll_el_size.height}px`
        display(this.scroll_el)
        this.do_scroll(this.model.active)
      } else {
        this.headers_el.style.top = '0px'
        this.wrapper_el.style.maxHeight = ""
        undisplay(this.scroll_el)
      }
    }

    const {child_views} = this
    for (const child_view of child_views) {
      hide(child_view.el)
      child_view.el.style.removeProperty('zIndex');
    }

    const tab = child_views[this.model.active]
    if (tab != null)
      show(tab.el)
  }

  override render(): void {
    LayoutDOMView.prototype.render.call(this)

    let {active} = this.model

    const headers = this.model.tabs.map((tab, i) => {
      const el = div({class: [tabs.tab, i == active ? tabs.active : null]}, tab.title)
      el.addEventListener("click", (event) => {
        if (this.model.disabled)
          return
        if (event.target == event.currentTarget)
          this.change_active(i)
      })
      if (tab.closable) {
        const close_el = div({class: tabs.close})
        close_el.addEventListener("click", (event) => {
          if (event.target == event.currentTarget) {
            this.model.tabs = remove_at(this.model.tabs, i)

            const ntabs = this.model.tabs.length
            if (this.model.active > ntabs - 1)
              this.model.active = ntabs - 1
          }
        })
        el.appendChild(close_el)
      }
      if (this.model.disabled || tab.disabled) {
        el.classList.add(tabs.disabled)
      }
      return el
    })
    this.headers_el = div({class: [tabs.headers]}, headers)
    this.wrapper_el = div({class: tabs.headers_wrapper}, this.headers_el)

    this.left_el = div({class: [buttons.btn, buttons.btn_default], disabled: ""}, div({class: [menus.caret, tabs.left]}))
    this.right_el = div({class: [buttons.btn, buttons.btn_default]}, div({class: [menus.caret, tabs.right]}))

    this.left_el.addEventListener("click", () => this.do_scroll("left"))
    this.right_el.addEventListener("click", () => this.do_scroll("right"))

    this.scroll_el = div({class: buttons.btn_group}, this.left_el, this.right_el)

    const loc = this.model.tabs_location
    this.header_el = div({class: [tabs.tabs_header, tabs[loc]]}, this.scroll_el, this.wrapper_el)
    this.el.appendChild(this.header_el)

    this.update_zindex()
    if (active === -1 && this.model.tabs.length)
      this.model.active = 0
  }

  on_active_change(): void {
    const i = this.model.active

    const headers = children(this.headers_el)
    for (const el of headers)
      el.classList.remove(tabs.active)

    headers[i].classList.add(tabs.active)

    const {child_views} = this
    for (const child_view of child_views) {
      hide(child_view.el)
    }

    show(child_views[i].el)
  }

}

export namespace Tabs {
  export type Attrs = p.AttrsOf<Props>

  export type Props = BkTabs.Props & {
  }
}

export interface Tabs extends BkTabs.Attrs {}

export class Tabs extends BkTabs {
  properties: Tabs.Props

  constructor(attrs?: Partial<Tabs.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.tabs"

  static init_Tabs(): void {
    this.prototype.default_view = TabsView

    this.define<Tabs.Props>(({}) => ({
    }))
  }
}
