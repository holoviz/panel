import type * as p from "@bokehjs/core/properties"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {div} from "@bokehjs/core/dom"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {Attrs} from "@bokehjs/core/types"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"

import {convertUndefined, ID} from "./util"
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

function sync_state(node: any, tree: any) {
  const node_json = tree.get_node(node.id)
  if (node_json) {
    node.state = Object.assign({}, node_json.state, (node.state || {}))
    node.state.loading = false
  } else if (!node.state) {
    node.state = {loading: false}
  }
  if (node.children && node.children.length) {
    for (const child of (node.children || [])) {
      sync_state(child, tree)
    }
  }
}

export class jsTreeView extends LayoutDOMView {
  declare model: jsTree
  protected _container: HTMLDivElement
  protected _id: any
  protected _jstree: any
  protected _setting: boolean

  override connect_signals(): void {
    super.connect_signals()
    const {nodes, checked, checkbox, show_icons, show_dots, multiple} = this.model.properties
    this.on_change(nodes, () => {
      const tree = this._jstree.jstree(true)
      for (const node of this.model.nodes) {
        sync_state(node, tree)
      }
      tree.load_node("#", () => {
        tree.refresh({
          skip_loading: false,
          forget_state: false,
        })
        this._update_selection_from_value()
      })
    })
    this.on_change(checked, () => {
      if (!this._setting) {
        this._update_selection_from_value()
      }
    })
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
    if (!this.model.plugins.includes("wholerow")) {
      plugins.push("wholerow")
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
      allow_reselect: true,
      checkbox: {
        three_state: this.model.cascade,
        cascade: this.model.cascade ? "undetermined" : "down+undetermined",
        cascade_to_disabled: false,
        tie_selection: false,
        whole_node: false,
      },
      core: {
        data: (obj: Node, callback: (nodes: Node[]) => void) => {
          if (obj.id == "#") {
            callback(this.model.nodes)
          } else {
            if (obj.children_nodes === undefined) {
              const tree = this._jstree.jstree(true)
              obj.children_nodes = []
              for (const child of obj.children) {
                const child_node = tree.get_node(child)
                obj.children_nodes.push(child_node)
              }
            }
            this.model.trigger_event(new NodeEvent({type: "load", node: convertUndefined(obj)}))
            new Promise((resolve) => {
              const loop = () => {
                const nodes = this.model._new_nodes
                if (nodes != null) {
                  const combined = [...obj.children_nodes]
                  const new_children: any[] = []
                  for (const new_node of nodes) {
                    if (new_node.parent === obj.id) {
                      combined.push(new_node)
                    } else if (!new_children.includes(new_node)) {
                      new_children.push(new_node)
                    }
                  }
                  obj._new_children = new_children
                  callback(combined)
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
    this._jstree.on("dblclick.jstree", (e: MouseEvent) => {
      let target = e.target
      while (!(target === null || !(target instanceof Element) || target.className.includes("jstree-node"))) {
        target = target.parentNode
      }
      if (target && (target instanceof Element) && target.className.includes("jstree-node")) {
        const node = this._jstree.jstree(true).get_node(target)
        this.model.trigger_event(new NodeEvent({type: "click", subtype: "dblclick", node: {id: node.id}}))
      }
    })
    this._jstree.on("select_node.jstree", ({}, data: any) => {
      this.model.trigger_event(new NodeEvent({type: "click", subtype: "click", node: {id: data.node.id}}))
    })
    this._jstree.on("check_node.jstree uncheck_node.jstree", ({}, data: any) => this.selectNodeFromEditor({}, data))
    this._jstree.on("refresh.jstree", ({}, {}) => this._update_selection_from_value())
    this._jstree.on("before_open.jstree", (_: any, data: any) => this._listen_for_node_open(data))
    this._jstree.on("after_close.jstree", (_: any, data: any) => {
      this.model.trigger_event(new NodeEvent({type: "close", node: {id: data.node.id}}))
    })
  }

  selectNodeFromEditor({}, data: any): void {
    this._setting = true
    this.model.checked = data.instance.get_checked()
    this._setting = false
  }

  _update_selection_from_value(): void {
    this._jstree.jstree(true).uncheck_all(true)
    this._jstree.jstree(true).check_node(this.model.checked, true, true)
  }

  _setShowIcons(): void {
    if (this.model.show_icons) {
      this._jstree.jstree(true).show_icons()
    } else {
      this._jstree.jstree(true).hide_icons()
    }
  }

  _setShowDots(): void {
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
    this.model.trigger_event(new NodeEvent({type: "open", node: {id: data.node.id}}))
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
        const tree = this._jstree.jstree(true)
        for (const new_node of node._new_children) {
          const parent = tree.get_node(new_node.parent)
          parent.state.loaded = true
          tree.create_node(new_node.parent, new_node)
        }
        delete node._new_children
      })
    }
  }
}

export namespace jsTree {
  export type Attrs = p.AttrsOf<Props>
  export type Props = LayoutDOM.Props & {
    checked: p.Property<any>
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
      checked:       [ List(Any), [] ],
      drag_and_drop: [ Bool, false ],
      nodes:         [ List(Any), [] ],
      plugins:       [ List(Any), [] ],
      multiple:      [ Bool,  true ],
      show_icons:    [ Bool,  true ],
      show_dots:     [ Bool, false ],
      show_stripes:  [ Bool, false ],
      sort:          [ Bool,  true ],
    }))
  }
}
