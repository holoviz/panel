import * as p from "@bokehjs/core/properties"
import {Markup, MarkupView} from "@bokehjs/models/widgets/markup"

import {Layoutable} from "@bokehjs/core/layout/layoutable"
import {Size, SizeHint, Sizeable} from "@bokehjs/core/layout/types"
import {sized, content_size, extents} from "@bokehjs/core/dom"


function htmlDecode(input: string): string | null {
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
}

export class CachedVariadicBox extends Layoutable {
  _cache: {[key: string]: Size}

  constructor(readonly el: HTMLElement) {
    super()
    this._cache = {};
  }

  protected _measure(viewport: Size): SizeHint {
    const key = [viewport.width, viewport.height]
    const key_str = key.toString()
    if (key_str in this._cache)
      return this._cache[key_str]
    const bounded = new Sizeable(viewport).bounded_to(this.sizing.size)
    const size = sized(this.el, bounded, () => {
      const content = new Sizeable(content_size(this.el))
      const {border, padding} = extents(this.el)
      return content.grow_by(border).grow_by(padding).map(Math.ceil)
    })
    this._cache[key_str] = size;
    return size;
  }
}

export class HTMLView extends MarkupView {
  model: HTML

  _update_layout(): void {
    this.layout = new CachedVariadicBox(this.el)
    this.layout.set_sizing(this.box_sizing())
  }

  render(): void {
    super.render()
    const html = htmlDecode(this.model.text);
    if (!html) {
      this.markup_el.innerHTML = '';
      return;
    }
    this.markup_el.innerHTML = html
    Array.from(this.markup_el.querySelectorAll("script")).forEach( oldScript => {
      const newScript = document.createElement("script");
      Array.from(oldScript.attributes)
        .forEach( attr => newScript.setAttribute(attr.name, attr.value) );
      newScript.appendChild(document.createTextNode(oldScript.innerHTML));
      if (oldScript.parentNode)
        oldScript.parentNode.replaceChild(newScript, oldScript);
    });
  }
}

export namespace HTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props
}

export interface HTML extends HTML.Attrs {}

export class HTML extends Markup {
  properties: HTML.Props

  constructor(attrs?: Partial<HTML.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.markup"

  static init_HTML(): void {
    this.prototype.default_view = HTMLView
  }
}
