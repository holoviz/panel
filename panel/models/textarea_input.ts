import { TextAreaInput as BkTextAreaInput, TextAreaInputView as BkTextAreaInputView } from "@bokehjs/models/widgets/textarea_input";
import * as p from "@bokehjs/core/properties";

export class TextAreaInputView extends BkTextAreaInputView {
  model: TextAreaInput;
  scroll_down_button_el: HTMLElement;

  connect_signals(): void {
    super.connect_signals();

    const { rows } = this.model.properties;

    this.on_change(rows, () => this.update_rows());
  }

  update_rows(): void {
    if (!this.model.auto_grow) {
      return;
    }

    // Use this.el directly to access the textarea element
    const textarea = this.el as HTMLTextAreaElement;
    const textLines = textarea.value.split("\n");
    const numRows = textLines.length;
    if (numRows > 1) {
      textarea.rows = numRows;
    } else {
      textarea.rows = 1;
    }
  }

  render(): void {
    console.log("TESTING LOG STATEMENT")
    super.render();

    this.el.addEventListener("input", () => {
      this.update_rows();
    });
  }
}

export namespace TextAreaInput {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = BkTextAreaInput.Props & {
    auto_grow: p.Property<boolean>;
  };
}

export interface TextAreaInput extends TextAreaInput.Attrs { }

export class TextAreaInput extends BkTextAreaInput {
  properties: TextAreaInput.Props;

  constructor(attrs?: Partial<TextAreaInput.Attrs>) {
    super(attrs);
  }

  static __module__ = "panel.models.widgets";

  static {
    this.prototype.default_view = TextAreaInputView;

    this.define<TextAreaInput.Props>(({ Boolean }) => ({
      auto_grow: [Boolean, false],
    }));
  }
}
