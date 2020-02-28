import { HTMLBox, HTMLBoxView } from "models/layouts/html_box"

// import { div } from "core/dom"
import * as p from "core/properties"

export class WebComponentView extends HTMLBoxView {
    model: WebComponent
    webComponentElement: any

    initialize(): void {
        super.initialize()
    }

    connect_signals(): void {
        super.connect_signals()
        this.connect(this.model.properties.innerHTML.change, () => this.render())
    }

    render(): void {
        super.render()

        if (this.el.innerHTML !== this.model.innerHTML) {
            this.el.innerHTML = this.model.innerHTML; // Todo: Remove
            this.webComponentElement = this.el.firstElementChild;

            // Since far from all web components change the attribute when the corresponding property is changed
            // we need to watch the properties and not the attributes
            // An example is wired-radio from https://www.npmjs.com/package/wired-radio
            // When we click that, the checked property is changed but not the checked attribute
            this.webComponentElement.onchange = (ev: any) => this.watch(ev);
        }
    }

    watch(ev: any): void {
        // Todo: Should depend on attributesWatched list
        var change = ev.detail["checked"];
        if (change === true) {
            this.webComponentElement.setAttribute("checked", "")
        } else if (change === false) {
            this.webComponentElement.removeAttribute("checked")
        } else {
            this.webComponentElement.setAttribute("checked", change)
        }

        if (this.model.innerHTML !== this.webComponentElement.outerHTML) {
            this.model.innerHTML = this.webComponentElement.outerHTML;
        }
    }
}

export namespace WebComponent {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        innerHTML: p.Property<string>
    }
}

export interface WebComponent extends WebComponent.Attrs { }

export class WebComponent extends HTMLBox {
    properties: WebComponent.Props

    constructor(attrs?: Partial<WebComponent.Attrs>) {
        super(attrs)
    }

    static init_WebComponent(): void {
        this.prototype.default_view = WebComponentView;

        this.define<WebComponent.Props>({
            innerHTML: [p.String, '<wired-radio id="1" checked>Radio Two</wired-radio>'],
        })
    }
}
