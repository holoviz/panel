import * as p from "core/properties"
import {Markup, MarkupView} from "models/widgets/markup"

function htmlDecode(input: string): string | null {
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
}

export class HTMLView extends MarkupView {
  model: HTML

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

  static initClass(): void {
    this.prototype.type = "HTML"
    this.prototype.default_view = HTMLView
  }
}
HTML.initClass()
