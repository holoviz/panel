import * as p from "@bokehjs/core/properties"
import {AbstractIcon, AbstractIconView} from "@bokehjs/models/widgets/abstract_icon"

export class FontAwesomeIconView extends AbstractIconView {
  model: FontAwesomeIcon

  render(): void {
    this.el.innerHTML = '<i class="fas ' + this.model.icon + '"></i>'
  }

  css_classes(): string[] {
    return this.model.css_classes
  }
}

export namespace FontAwesomeIcon {
  export type Attrs = p.AttrsOf<Props>

  export type Props = AbstractIcon.Props & {
    css_classes: p.Property<string[]>
    icon: p.Property<string>
  }
}

export interface FontAwesomeIcon extends FontAwesomeIcon.Attrs {}

export class FontAwesomeIcon extends AbstractIcon {
  properties: FontAwesomeIcon.Props

  static __module__ = "panel.models.icons"

  constructor(attrs?: Partial<FontAwesomeIcon.Attrs>) {
    super(attrs)
  }

  static init_FontAwesomeIcon(): void {
    this.prototype.default_view = FontAwesomeIconView

    this.define<FontAwesomeIcon.Props>({
      css_classes: [ p.Array, []  ],
      icon:        [ p.String, '' ]
	})
  }
}
