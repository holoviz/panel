import type * as p from "@bokehjs/core/properties"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {div} from "@bokehjs/core/dom"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {Attrs} from "@bokehjs/core/types"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"

import {ID} from "./util"
import jstree_css from "styles/models/jstree.css"

type Node = {
  [key: string]: any
}

declare function jQuery(...args: any[]): any

export class NodeEvent extends ModelEvent {
  constructor(readonly data: any) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }

  static {
    this.prototype.event_name = "node_event"
  }
}

export class jsTreeView extends LayoutDOMView {
  declare model: jsTree
  protected _container: HTMLDivElement
  protected _id: any
  protected _jstree: any

  override connect_signals(): void {
    super.connect_signals()
    const {nodes, value, checkbox, show_icons, show_dots, multiple} = this.model.properties
    this.on_change(nodes, () => this._jstree.jstree(true).load_node("#", () => {
      this._jstree.jstree(true).refresh({
        skip_loading: false,
        forget_state: true,
      })
      this._update_selection_from_value()
    }))
    this.on_change(value, () => this._update_selection_from_value())
    this.on_change(checkbox, () => this.setCheckboxes())
    this.on_change(show_icons, () => this._setShowIcons())
    this.on_change(show_dots, () => this._setShowDots())
    this.on_change(multiple, () => this._setMultiple())
  }

  get child_models(): LayoutDOM[] {
    return []
  }

  get plugins(): string[] {
    const plugins = [...this.model.plugins]
    if (this.model.checkbox && !this.model.plugins.includes("checkbox")) {
      plugins.push("checkbox")
    }
    if (this.model.checkbox && !this.model.plugins.includes("sort")) {
      plugins.push("sort")
    }

    if (!this.model.plugins.includes("types")) {
      plugins.push("types")
    }
    return plugins
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), jstree_css]
  }

  override render(): void {
    super.render()
    this._id = ID()
    this._container = div({id: this._id, style: "overflow: auto; minHeight: 200px; minWidth: 200px;"})
    this.shadow_el.appendChild(this._container)
    this._jstree = jQuery(this._container).jstree({
      checkbox: {
        three_state: this.model.cascade,
        cascade: this.model.cascade ? "undetermined" : "down+undetermined",
      },
      core: {
        data: (obj: Node, callback: (nodes: Node[]) => void) => {
          if (obj.id == "#") {
            callback(this.model.nodes)
          } else {
            this.model.trigger_event(new NodeEvent({type: "open", node: obj}))
            new Promise((resolve) => {
              const loop = () => {
                const nodes = this.model._new_nodes
                if (nodes != null) {
                  obj.new_nodes = nodes
                  callback(obj.children_nodes)
                  this.model._new_nodes = null
                  resolve(this.model.nodes)
                } else {
                  setTimeout(loop, 10)
                }
              }
              loop()
            }).catch(() => console.warn("Failed to fetch nodes"))
          }
        },
        check_callback: true,
        multiple: this.model.multiple,
        themes: {
          dots: this.model.show_dots,
          icons: this.model.show_icons,
          stripes: this.model.show_stripes,
        },
      },
      plugins: this.plugins,
      sort: (n1: string, n2: string) => {
        const n1_folder = n1.endsWith("/")
        const n2_folder = n2.endsWith("/")
        if (n1_folder && !n2_folder) {
          return -1
        } else if (!n1_folder && n2_folder) {
          return 1
        }
        return n1 > n2 ? 1 : -1
      },
    })
    this.init_callbacks()
  }

  init_callbacks(): void {
    this._jstree.on("activate_node.jstree", ({}, data: any) => this.selectNodeFromEditor({}, data))
    this._jstree.on("refresh.jstree", ({}, {}) => this._update_selection_from_value())
    this._jstree.on("before_open.jstree", (_: any, data: any) => this._listen_for_node_open(data))
  }

  selectNodeFromEditor({}, data: any): void {
    this.model.value = data.instance.get_selected()
  }

  _update_selection_from_value(): void {
    this._jstree.jstree(true).deselect_all(true)
    this._jstree.jstree(true).select_node(this.model.value, true, true)
  }

  _setShowIcons(): void {
    if (this.model.show_icons) {
      this._jstree.jstree(true).show_icons()
    } else {
      this._jstree.jstree(true).hide_icons()
    }
  }

  _setShowDots(): void {
    // console.log("setShowDots")
    if (this.model.show_dots) {
      this._jstree.jstree(true).show_dots()
    } else {
      this._jstree.jstree(true).hide_dots()
    }
  }

  setCheckboxes(): void {
    if (this.model.checkbox) {
      this._jstree.jstree(true).show_checkboxes()
    } else {
      this._jstree.jstree(true).hide_checkboxes()
    }
  }

  _setMultiple(): void {
    this._jstree.jstree(true).settings.core.multiple = this.model.multiple
  }

  _listen_for_node_open(data: any): void {
    data.node.children_nodes = []
    let request_load = false
    for (const child of data.node.children) {
      const child_node = data.instance.get_node(child)
      if (child_node.original.type === "folder" && !child_node.children.length) {
        request_load = true
      }
      data.node.children_nodes.push(child_node)
    }
    if (request_load) {
      data.instance.load_node(data.node.id, (node: Node) => {
        for (const new_node of node.new_nodes) {
          this._jstree.jstree(true).create_node(new_node.parent, new_node)
        }
        delete node.new_nodes
      })
    }
  }
}

export namespace jsTree {
  export type Attrs = p.AttrsOf<Props>
  export type Props = LayoutDOM.Props & {
    plugins: p.Property<any>
    cascade: p.Property<boolean>
    checkbox: p.Property<boolean>
    drag_and_drop: p.Property<boolean>
    multiple: p.Property<boolean>
    nodes: p.Property<any>
    show_icons: p.Property<boolean>
    show_dots: p.Property<boolean>
    show_stripes: p.Property<boolean>
    sort: p.Property<boolean>
    value: p.Property<any>
    _new_nodes: p.Property<any[] | null>
  }
}

export interface jsTree extends jsTree.Attrs {}

export class jsTree extends LayoutDOM {
  declare properties: jsTree.Props

  constructor(attrs?: Partial<jsTree.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.jstree"

  static {
    this.prototype.default_view = jsTreeView

    this.define<jsTree.Props>(({List, Any, Bool, Nullable}) => ({
      _new_nodes:    [ Nullable(List(Any)), [] ],
      cascade:       [ Bool,  true ],
      checkbox:      [ Bool,  true ],
      drag_and_drop: [ Bool, false ],
      nodes:         [ List(Any), [] ],
      plugins:       [ List(Any), [] ],
      multiple:      [ Bool,  true ],
      show_icons:    [ Bool,  true ],
      show_dots:     [ Bool, false ],
      show_stripes:  [ Bool, false ],
      sort:          [ Bool,  true ],
      value:         [ List(Any), [] ],
    }))
  }
}
