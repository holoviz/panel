import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// import { div } from "core/dom"
import * as p from "@bokehjs/core/properties"

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
            this.webComponentElement.onchange = (ev: any) => this.synchronize(ev);
        }
    }

    synchronize(ev: any): void {
        // Todo: Should depend on attributesWatched list
        for (let attribute in this.model.attributesToWatch) {
            var change = ev.detail[attribute];
            if (change === true) {
                this.webComponentElement.setAttribute(attribute, "")
            } else if (change === false) {
                this.webComponentElement.removeAttribute(attribute)
            } else {
                this.webComponentElement.setAttribute(attribute, change)
            }

            if (this.model.innerHTML !== this.webComponentElement.outerHTML) {
                this.model.innerHTML = this.webComponentElement.outerHTML;
            }
        }
    }
}

export namespace WebComponent {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        innerHTML: p.Property<string>,
        attributesToWatch: p.Property<any> // A dictionary
    }
}

export interface WebComponent extends WebComponent.Attrs { }

export class WebComponent extends HTMLBox {
    properties: WebComponent.Props

    constructor(attrs?: Partial<WebComponent.Attrs>) {
        super(attrs)
    }

    static __module__ = "panel.models.web_component"

    static init_WebComponent(): void {
        this.prototype.default_view = WebComponentView;

        this.define<WebComponent.Props>({
            innerHTML: [p.String, ''],
            attributesToWatch: [p.Any] // A dictionary
        })
    }
}
