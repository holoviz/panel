import * as p from "@bokehjs/core/properties"
import * as tabs from "@bokehjs/styles/tabs.css"

import {Tabs as BkTabs, TabsView as BkTabsView} from "@bokehjs/models/layouts/tabs"

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

  override render(): void {
    super.render()
    this.update_zindex()
  }

  update_zindex(): void {
    const {child_views} = this
    for (const child_view of child_views) {
      if (child_view != null && child_view.el != null) {
	console.log(child_view.el)
        child_view.el.style.zIndex = ""
      }
    }
    if (this.is_visible) {
      const active = child_views[this.model.active]
      if (active != null && active.el != null)
        active.el.style.zIndex = "1"
    }
  }

  override _after_layout(): void {
    super._after_layout()

    const {child_views} = this
    for (const child_view of child_views)
      hide(child_view.el)

    const {active} = this.model
    if (active in child_views) {
      const tab = child_views[active]
      show(tab.el)
    }
  }

  update_active(): void {
    const i = this.model.active

    const {header_els} = this
    for (const el of header_els) {
      el.classList.remove(tabs.active)
    }

    if (i in header_els) {
      header_els[i].classList.add(tabs.active)
    }

    const {child_views} = this
    for (const child_view of child_views) {
      hide(child_view.el)
    }

    if (i in child_views) {
      show(child_views[i].el)
    }
  }
}

export namespace Tabs {
  export type Attrs = p.AttrsOf<Props>

  export type Props = BkTabs.Props
}

export interface Tabs extends BkTabs.Attrs {}

export class Tabs extends BkTabs {
  properties: Tabs.Props

  static __module__ = "panel.models.tabs"

  static {
    this.prototype.default_view = TabsView
  }
}
