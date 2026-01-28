import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
export class KaTeXView extends PanelMarkupView {
    static __name__ = "KaTeXView";
    connect_signals() {
        super.connect_signals();
        const { text } = this.model.properties;
        this.on_change(text, () => this.render());
    }
    render() {
        super.render();
        this.container.innerHTML = this.model.text;
        if (!window.renderMathInElement) {
            return;
        }
        window.renderMathInElement(this.shadow_el, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "\\[", right: "\\]", display: true },
                { left: "$", right: "$", display: false },
                { left: "\\(", right: "\\)", display: false },
            ],
        });
    }
}
export class KaTeX extends Markup {
    static __name__ = "KaTeX";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.katex";
    static {
        this.prototype.default_view = KaTeXView;
    }
}
//# sourceMappingURL=katex.js.map