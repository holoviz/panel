import * as p from "@bokehjs/core/properties";
import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
import { htmlDecode } from "./html";

export class PDFView extends PanelMarkupView {
  model: PDF;

  connect_signals(): void {
    super.connect_signals();
    const p = this.model.properties;
    const { text, width, height, embed, start_page } = p;
    this.on_change([text, width, height, embed, start_page], () => {
      this.update();
    });
  }

  render(): void {
    super.render();
    this.update();
  }

  update(): void {
    if (this.model.embed) {
      const blob = this.convert_base64_to_blob();
      const url = URL.createObjectURL(blob);
      const w = this.model.width || "100%";
      const h = this.model.height || "100%";
      this.container.innerHTML = `<embed src="${url}#page=${this.model.start_page}" type="application/pdf" width="${w}" height="${h}"></embed>`;
    } else {
      const html = htmlDecode(this.model.text);
      this.container.innerHTML = html || "";
    }
  }

  protected convert_base64_to_blob(): Blob {
    const byteCharacters = atob(this.model.text);
    const sliceSize = 512;
    var byteArrays = [];
    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
      const slice = byteCharacters.slice(offset, offset + sliceSize);
      const byteNumbers = new Uint8Array(slice.length);
      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }
      byteArrays.push(byteNumbers);
    }
    return new Blob(byteArrays, { type: "application/pdf" });
  }
}

export namespace PDF {
  export type Attrs = p.AttrsOf<Props>;

  export type Props = Markup.Props & {
    embed: p.Property<boolean>;
    start_page: p.Property<Number>;
  };
}

export interface PDF extends PDF.Attrs {}

export class PDF extends Markup {
  properties: PDF.Props;

  constructor(attrs?: Partial<PDF.Attrs>) {
    super(attrs);
  }

  static __module__ = "panel.models.markup";

  static {
    this.prototype.default_view = PDFView;
    this.define<PDF.Props>(({ Number, Boolean }) => ({
      embed: [Boolean, true],
      start_page: [Number, 1],
    }));
  }
}
