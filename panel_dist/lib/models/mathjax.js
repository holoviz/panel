import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
export class MathJaxView extends PanelMarkupView {
    static __name__ = "MathJaxView";
    connect_signals() {
        super.connect_signals();
        const { text } = this.model.properties;
        this.on_change(text, () => this.render());
    }
    render() {
        super.render();
        const text = this.model.text;
        const tex_parts = this.provider.MathJax.find_tex(text);
        const processed_text = [];
        let last_index = 0;
        for (const part of tex_parts) {
            processed_text.push(text.slice(last_index, part.start.n));
            processed_text.push(this.provider.MathJax.tex2svg(part.math, { display: part.display }).outerHTML);
            last_index = part.end.n;
        }
        if (last_index < text.length) {
            processed_text.push(text.slice(last_index));
        }
        this.container.innerHTML = processed_text.join("");
    }
}
export class MathJax extends Markup {
    static __name__ = "MathJax";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.mathjax";
    static {
        this.prototype.default_view = MathJaxView;
    }
}
//# sourceMappingURL=mathjax.js.map