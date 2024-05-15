import * as p from "@bokehjs/core/properties"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import { div } from "@bokehjs/core/dom"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type {Attrs} from "@bokehjs/core/types"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"

import {ID} from "./util"
import jstree_css from "styles/models/jstree.css"

type Node = {
  [key: string]: any;
};

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
  protected _last_selected: string[]

  override initialize(): void {
    super.initialize()
    this._last_selected = []
  }

  override connect_signals(): void {
    super.connect_signals()
    const {nodes, value, _new_nodes, checkbox, show_icons, show_dots, multiple} = this.model.properties
    this.on_change(nodes, () => this._update_tree_from_nodes())
    this.on_change(value, () => this._update_selection_from_value())
    this.on_change(_new_nodes, () => this._update_tree_from_new_nodes())
    this.on_change(checkbox, () => this.setCheckboxes())
    this.on_change(show_icons, () => this._setShowIcons())
    this.on_change(show_dots, () => this._setShowDots())
    this.on_change(multiple, () => this._setMultiple())
  }

  get child_models(): LayoutDOM[] {
    return []
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), jstree_css]
  }

  override render(): void {
    super.render()
    this._id = ID()
    this._container = div({id: this._id, style: "overflow: auto; minHeight: 200px; minWidth: 200px;"},)
    this.shadow_el.appendChild(this._container);

    let kw: {[k: string]: any} = {"checkbox": {
      "three_state": false,
      "cascade": "undetermined"
    }}

    if (this.model.checkbox && !this.model.plugins.includes("checkbox")) {
      this.model.plugins.push("checkbox")
    }
    if (this.model.checkbox && !this.model.plugins.includes("sort")) {
      this.model.plugins.push("sort")
    }

    this._jstree = jQuery(this._container).jstree({
      "core": {
	"data": this.model.nodes,
	"check_callback": true,
        "multiple": this.model.multiple,
        "themes": {
          "dots": this.model.show_dots,
          "icons": this.model.show_icons,
	  "stripes": this.model.show_stripes,
        }
      },
      "plugins": this.model.plugins,
      ...kw
    });
    this.init_callbacks()
  }

  init_callbacks(): void {
    this._jstree.on('refresh.jstree', ({}, {}) => this._update_selection_from_value());
    //this._jstree.on('model.jstree', ({}, {}) => this.onNewData());
    this._jstree.on('activate_node.jstree', ({}, data: any) => this.selectNodeFromEditor({}, data));
    this._jstree.on('before_open.jstree', (e: any, data: any) => this._listen_for_node_open(e, data));
  }

  selectNodeFromEditor({}, data: any): void {
    this.model.value = data.instance.get_selected()
  }

  _update_selection_from_value(): void {
    this._jstree.jstree(true).select_node(this.model.value)
    // We sometimes have to fire this function more than once per value change because of
    // calling jstree.refresh, so we check to see if model.value has really changed
    // by comparing to last_selected
    if (this.model.value != this._last_selected) {
      let deselected = this._last_selected.filter(x => !this.model.value.includes(x));
      this._jstree.jstree(true).deselect_node(deselected)
    }
    // We choose get_selected
    this._last_selected = this.model.value;
  }

  _update_tree_from_new_nodes(): void {
    for (let node of this.model._new_nodes){
      this._jstree.jstree(true).create_node(node["parent"], node, "first")
    }
    this._jstree.jstree(true).settings.core.data = this._jstree.jstree(true).get_json(null, {no_li_attr: true, no_a_attr: true, no_data: true})
    this.model.nodes = this._jstree.jstree(true).settings.core.data
  }

  _update_tree_from_nodes(): void {
    this._jstree.jstree(true).settings.core.data = this.model.nodes;
    // This will redraw the tree if we swap out the data with new data
    // we set forget_state to true, so the current state is not reapplied
    // letting whatever state is set in the new data (open or closed, etc)
    // be the new state
    this._jstree.jstree(true).refresh({
      "skip_loading": false,
      "forget_state": true,
    })

    // selected state is not preserved correctly right now, so we then
    // deselect everything because that is better than getting it wrong
    this._jstree.jstree(true).deselect_all({"supress_event": true})
  }

  _setShowIcons(): void {
    if (this.model.show_icons) {
      this._jstree.jstree(true).show_icons();
    }
    else {
      this._jstree.jstree(true).hide_icons();
    }
  }

  _setShowDots(): void {
    // console.log("setShowDots")
    if (this.model.show_dots) {
      this._jstree.jstree(true).show_dots()
    }
    else {
      this._jstree.jstree(true).hide_dots()
    }
  }

  setCheckboxes(): void {
    if (this.model.checkbox) {
      this._jstree.jstree(true).show_checkboxes()
    }
    else {
      this._jstree.jstree(true).hide_checkboxes()
    }
  }

  _setMultiple(): void {
    this._jstree.jstree(true).settings.core.multiple = this.model.multiple
  }

  _listen_for_node_open(e, data: any): void {
    data.node.children_nodes = []
    for (let child of data.node.children) {
      data.node.children_nodes.push(this._jstree.jstree(true).get_node(child))
    }
    this.model.trigger_event(new NodeEvent({type: 'open', node: data.node}))
  }
}

export namespace jsTree {
  export type Attrs = p.AttrsOf<Props>
  export type Props = LayoutDOM.Props & {
    drag_and_drop: p.Property<boolean>
    plugins: p.Property<any>
    checkbox: p.Property<boolean>
    multiple: p.Property<boolean>
    nodes: p.Property<any>
    show_icons: p.Property<boolean>
    show_dots: p.Property<boolean>
    show_stripes: p.Property<boolean>
    sort: p.Property<boolean>
    value: p.Property<any>
    _new_nodes: p.Property<any>
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

    this.define<jsTree.Props>(({Array, Any, Boolean}) => ({
      _new_nodes:    [ Array(Any), [] ],
      checkbox:      [ Boolean,  true ],
      drag_and_drop: [ Boolean, false ],
      nodes:         [ Array(Any), [] ],
      plugins:       [ Array(Any), [] ],
      multiple:      [ Boolean,  true ],
      show_icons:    [ Boolean,  true ],
      show_dots:     [ Boolean, false ],
      show_stripes:  [ Boolean, false ],
      sort:          [ Boolean,  true ],
      value:         [ Array(Any), [] ],
    }))
  }
}
