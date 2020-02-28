import { HTMLBox, HTMLBoxView } from "models/layouts/html_box"

// import { div } from "core/dom"
import * as p from "core/properties"

export class RadioButtonView extends HTMLBoxView {
    model: RadioButton
    webComponentElement: any

    initialize(): void {
        super.initialize()

        // this.el.innerHTML = this.model.html
        // this.webComponentElement = this.el.firstElementChild;
        // console.log(this.webComponentElement);
        // this.connect(this.webComponentElement.properties["checked"].change, () => this.watch())
    }

    connect_signals(): void {
        super.connect_signals()
        this.connect(this.model.properties.html.change, () => this.render())
    }

    render(): void {
        super.render()

        if (this.el.innerHTML !== this.model.html) {
            this.el.innerHTML = this.model.html; // Todo: Remove
            this.webComponentElement = this.el.firstElementChild;
            console.log(this.webComponentElement);

            // Since far from all web components change the attribute when the corresponding property is changed
            // we need to watch the properties and not the attributes
            // An example is wired-radio from https://www.npmjs.com/package/wired-radio
            // When we click that, the checked property is changed but not the checked attribute
            this.webComponentElement.onchange = (ev: any) => this.watch(ev);
        }
    }

    watch(ev: any): void {
        var change = ev.detail["checked"];
        if (change === true) {
            this.webComponentElement.setAttribute("checked", "")
        } else if (change === false) {
            this.webComponentElement.removeAttribute("checked")
        } else {
            this.webComponentElement.setAttribute("checked", change)
        }

        if (this.model.html !== this.webComponentElement.outerHTML) {
            this.model.html = this.webComponentElement.outerHTML;
        }
    }
}

export namespace RadioButton {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        html: p.Property<string>
    }
}

export interface RadioButton extends RadioButton.Attrs { }

export class RadioButton extends HTMLBox {
    properties: RadioButton.Props

    constructor(attrs?: Partial<RadioButton.Attrs>) {
        super(attrs)
    }

    static init_RadioButton(): void {
        this.prototype.default_view = RadioButtonView;

        this.define<RadioButton.Props>({
            html: [p.String, '<wired-radio id="1" checked>Radio Two</wired-radio>'],
        })
    }
}
