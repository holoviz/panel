import {empty} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {Layoutable} from "@bokehjs/core/layout"
import {LayoutDOM, LayoutDOMView} from "@bokehjs/models/layouts/layout_dom"
import {CachedVariadicBox} from "./layout"
import {htmlDecode} from "./html"

function getNodes(node: any) {
  function recursor(n: any) {
    var i, a: any = [];
    if (n.nodeType == 1) {
      a.push(n);
      if (n.childNodes)
         for (i = 0; i < n.childNodes.length; ++i)
           a = a.concat(recursor(n.childNodes[i]));
    }
    return a;
  }
  return recursor(node);
}

export class MicroTemplateView extends LayoutDOMView {
  layout: Layoutable
  model: MicroTemplate
  _prev_sizing_mode: string | null

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.children.change, () => this.rebuild())
  }

  render(): void {
    empty(this.el)
	const decoded = htmlDecode(this.model.html);
    const html = decoded || this.model.html
	this.el.innerHTML = html
	const nodes = getNodes(this.el)
	for (let i = 0; i < this.child_views.length; i++) {
      const view = this.child_views[i]
      for (const node of nodes) {
        if (node.innerHTML && (node.innerHTML == `{${i}}`)) {
          node.innerHTML = ''
          node.appendChild(view.el)
          view.render()
        }
      }
	}
	this.root.compute_layout()
  }

  _update_layout(): void {
    let changed = ((this._prev_sizing_mode !== undefined) &&
                   (this._prev_sizing_mode !== this.model.sizing_mode))
    this._prev_sizing_mode = this.model.sizing_mode;
    this.layout = new CachedVariadicBox(this.el, this.model.sizing_mode, changed)
    this.layout.set_sizing(this.box_sizing())
  }
  
  get child_models(): LayoutDOM[] {
    return this.model.children
  }
}

export namespace MicroTemplate {
  export type Attrs = p.AttrsOf<Props>

  export type Props = LayoutDOM.Props & {
    children: p.Property<LayoutDOM[]>
    html: p.Property<string>
  }
}

export interface MicroTemplate extends MicroTemplate.Attrs {}

export class MicroTemplate extends LayoutDOM {
  properties: MicroTemplate.Props

  constructor(attrs?: Partial<MicroTemplate.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.layout"

  static init_MicroTemplate(): void {
    this.prototype.default_view = MicroTemplateView

    this.define<MicroTemplate.Props>({
      children: [ p.Array,  [] ],
	  html:   [ p.String, ''        ],
    })
  }
}
