import * as p from "@bokehjs/core/properties"
import {Markup, MarkupView} from "@bokehjs/models/widgets/markup"
import JSONFormatter from "json-formatter-js"

export class JSONView extends MarkupView {
  model: JSON

  connect_signals(): void {
    super.connect_signals()
	this.connect(this.model.change, () => {
      this.render()
      this.root.compute_layout() // XXX: invalidate_layout?
    })
  }

  render(): void {
    super.render();
	const text = this.model.text.replace(/(\r\n|\n|\r)/gm, "").replace("'", '"')
    let json;
	try {
	  json = window.JSON.parse(text)
	} catch(err) {
	  json = {}
	}
	const config = {hoverPreviewEnabled: this.model.hover, theme: this.model.theme}
	const formatter = new JSONFormatter(json, this.model.depth, config)
	const rendered = formatter.render()
	const style = "border-radius: 5px; padding: 10px;";
	if (this.model.theme == "dark")
      rendered.style.cssText = "background-color: rgb(30, 30, 30);" + style
    else
      rendered.style.cssText = style
	this.markup_el.appendChild(rendered)
  }
}

export namespace JSON {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Markup.Props & {
    depth: p.Property<number>
    hover: p.Property<boolean> 
    theme: p.Property<string>  
  }
}

export interface JSON extends JSON.Attrs {}

export class JSON extends Markup {
  properties: JSON.Props

  constructor(attrs?: Partial<JSON.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.markup"

  static init_JSON(): void {
    this.prototype.default_view = JSONView
    this.define<JSON.Props>({
	  depth: [p.Number, 1],
      hover: [p.Boolean, false],
      theme: [p.String, 'light'],
    })
  }
}
