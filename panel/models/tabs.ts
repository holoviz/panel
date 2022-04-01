import {Grid, ContentBox, Sizeable} from "@bokehjs/core/layout"
import {size, children} from "@bokehjs/core/dom"
import {sum} from "@bokehjs/core/util/array"
import * as p from "@bokehjs/core/properties"

import {Tabs as  BkTabs, TabsView as BkTabsView} from "@bokehjs/models/layouts/tabs"

export class TabsView extends BkTabsView {
  model: Tabs
  
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
