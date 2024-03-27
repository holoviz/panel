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
        this.container.innerHTML = this.has_math_disabled() ? this.model.text : this.process_tex(this.model.text);
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