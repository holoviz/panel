import * as p from "@bokehjs/core/properties";
import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";

// TODO:
// some kind of loading icon + placeholder for large files
// better handling of nullvalues
// resizeable
// handle urls

export class PDFView extends PanelMarkupView {
  model: PDF;

  connect_signals(): void {
    super.connect_signals();

    // const p = this.model.properties;
    // const { width, height, file } = p;

    // this.on_change([width, height, file], () => {
    //   this.update();
    // });

    this.connect(this.model.properties.file.change, () => {
      this.update()
    })

    // this.connect(this.model.properties.width.change, () => {
    //   this.render()
    // })

    // this does not seem to work
    // this.connect(this.model.properties.width.change, () => {
    //   this.update()
    // })
  }

  render(): void {
    super.render();
    this.update();
  }

  update(): void {
    const url = this.convert_base64_to_url();

    // This seem very unelegant
    this.markup_el.innerHTML = `<embed src="${url}#page=${this.model.start_page}" type="application/pdf" width="${this.model.width}" height="${this.model.height}"></embed>`;
  }

  protected convert_base64_to_url(): string {
    const byteCharacters = atob(this.model.blob);
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
    const blob = new Blob(byteArrays, { type: "application/pdf" });
    return URL.createObjectURL(blob);
  }
}

export namespace PDF {
  export type Attrs = p.AttrsOf<Props>;

  export type Props = Markup.Props & {
    blob: p.Property<string>;
    file: p.Property<string>;
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

  static init_PDF(): void {
    this.prototype.default_view = PDFView;
    this.define<PDF.Props>(({ String, Number }) => ({
      blob: [String, ""], // Nullable this
      file: [String, ""], // Nullable this
      start_page: [Number, 1],
    }));
  }
}
