import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// import { div } from "core/dom"
import * as p from "@bokehjs/core/properties"

export class WebComponentView extends HTMLBoxView {
    model: WebComponent
    webComponentElement: any
    eventsCount: any

    initialize(): void {
        super.initialize()
    }

    connect_signals(): void {
        super.connect_signals()
        this.connect(this.model.properties.innerHTML.change, () => this.render())
        this.connect(this.model.properties.propertiesLastChange.change, () => this.handlePropertiesLastChangeChange())
        this.connect(this.model.properties.eventsToWatch.change, () => this.handleEventsToWatchChange())
    }

    handleEventsToWatchChange(): void {
        console.log("handleEventsToWatchChange")
        console.log(this.model.eventsToWatch);
        // for (let event in this.model.eventsToWatch) {
        //     this.webComponentElement.addEventListener(event, () => { console.log(this.webComponentElement) }, false)
        // }
    }

    render(): void {
        super.render()

        if (this.el.innerHTML !== this.model.innerHTML) {
            var webComponentElementOld: any = null
            if (this.webComponentElement) {
                this.webComponentElement.onchange = null;
                webComponentElementOld = this.webComponentElement;
            }
            this.el.innerHTML = this.model.innerHTML; // Todo: Remove
            this.webComponentElement = this.el.firstElementChild;
            if (!webComponentElementOld) {
                // initializes to the correct properties on first construction
                this.handlePropertiesLastChangeChange();
            }


            this.webComponentElement.onchange = (ev: any) => this.handlePropertiesChange(ev);
            this.eventsCount = {};
            for (let event in this.model.eventsToWatch) {
                this.eventsCount[event] = 0
                this.webComponentElement.addEventListener(event, (ev: Event) => this.eventHandler(ev), false)
            }
        }
    }

    // Todo: Find out if onchange and event listeners should be removed "on destroy"

    // Todo: Set this up
    // handle_innerHTML_change(ev: any): void {
    //     if (this.model.innerHTML !== this.webComponentElement.outerHTML) {
    //         this.model.innerHTML = this.webComponentElement.outerHTML;
    //     }
    // }
    eventHandler(ev: Event): void {
        var event = ev.type;
        this.eventsCount[event] += 1;
        var eventsCountLastChanged: any = {};
        eventsCountLastChanged[event] = this.eventsCount[event]
        this.model.eventsCountLastChange = eventsCountLastChanged;
    }

    handlePropertiesChange(ev: any): void {
        // Todo: remove logging
        var properties_change: any = new Object();
        for (let property in this.model.propertiesToWatch) {
            if (property in ev.detail) {
                properties_change[property] = ev.detail[property];
            }
        }
        if (Object.keys(properties_change).length) {
            this.model.propertiesLastChange = properties_change;
        }
    }

    handlePropertiesLastChangeChange(): void {
        if (!this.webComponentElement) { return; }

        var propertiesLastChange: any = this.model.propertiesLastChange;
        for (let property in this.model.propertiesLastChange) {
            if (property in this.model.propertiesToWatch) {
                var value = propertiesLastChange[property]
                this.webComponentElement[property] = value;
            }
        }

    }
}

export namespace WebComponent {
    export type Attrs = p.AttrsOf<Props>
    // Todo: make property types more specific
    export type Props = HTMLBox.Props & {
        // Todo: should we just use object instead of innerHTML?
        // Just like for the HTML element
        innerHTML: p.Property<string>,
        attributesToWatch: p.Property<any> // A dictionary
        propertiesToWatch: p.Property<p.Any>, // A dictionary
        propertiesLastChange: p.Property<p.Any>, // A dictionary
        eventsToWatch: p.Property<p.Any> // A dictionary
        eventsCountLastChange: p.Property<p.Any> // A Dictionary
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
            attributesToWatch: [p.Any], // A dictionary
            propertiesToWatch: [p.Any], // A dictionary
            propertiesLastChange: [p.Any], // A dictionary
            eventsToWatch: [p.Any], // A dictionary
            eventsCountLastChange: [p.Any] // A list
        })
    }
}
