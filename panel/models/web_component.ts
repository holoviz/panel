import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// import { div } from "core/dom"
import * as p from "@bokehjs/core/properties"


export class WebComponentView extends HTMLBoxView {
    model: WebComponent
    webComponentElement: any // Element
    eventsCount: any // Dict
    propertyValues: any // Dict

    initialize(): void {
        super.initialize()
    }

    connect_signals(): void {
        super.connect_signals()
        this.connect(this.model.properties.innerHTML.change, () => this.render())
        this.connect(this.model.properties.attributesLastChange.change, () => this.handleAttributesLastChangeChange())
        this.connect(this.model.properties.propertiesLastChange.change, () => this.handlePropertiesLastChangeChange())
        this.connect(this.model.properties.columnDataSource.change, () => this.handleColumnDataSourceChange())
    }

    render(): void {
        super.render()

        if (this.el.innerHTML !== this.model.innerHTML) {
            this.createOrUpdateWebComponentElement()
        }
    }
    private createOrUpdateWebComponentElement() {
        let webComponentElementOld: any = null
        if (this.webComponentElement) {
            this.webComponentElement.onchange = null
            webComponentElementOld = this.webComponentElement
        }

        this.el.innerHTML = this.model.innerHTML
        this.webComponentElement = this.el.firstElementChild
        this.activate_scripts(this.webComponentElement.parentNode)

        // Initialize properties
        this.initPropertyValues()
        if (!webComponentElementOld) {
            this.handlePropertiesLastChangeChange()
        }
        this.handleColumnDataSourceChange()

        // Subscribe to events
        this.webComponentElement.onchange = (ev: any) => this.handlePropertiesChange(ev)
        this.addEventListeners()
        this.addAttributesMutationObserver()
    }

    addAttributesMutationObserver(): void {
        let options = {
            childList: false,
            attributes: true,
            characterData: false,
            subtree: false,
            attributeFilter: Object.keys(this.model.attributesToWatch),
            attributeOldValue: false,
            characterDataOldValue: false
        };

        const this_ = this; // hack
        function handleAttributesChange(_: Array<MutationRecord>): void {
            let attributesLastChange: any = new Object();

            for (let attribute in this_.model.attributesToWatch) {
                const value = this_.webComponentElement.getAttribute(attribute)
                attributesLastChange[attribute] = value;
            }

            if (this_.model.attributesLastChange !== attributesLastChange) {
                this_.model.attributesLastChange = attributesLastChange;
            }
        }

        let observer = new MutationObserver(handleAttributesChange);
        observer.observe(this.webComponentElement, options)
    }


    private addEventListeners() {
        this.eventsCount = {}
        for (let event in this.model.eventsToWatch) {
            this.eventsCount[event] = 0
            this.webComponentElement.addEventListener(event, (ev: Event) => this.eventHandler(ev), false)
        }
    }

    transform_cds_to_records(cds: any): any {
        const data: any = []
        const columns = cds.columns()

        if (columns.length === 0) {
            return [];
        }
        for (let i = 0; i < cds.data[columns[0]].length; i++) {
            const item: any = {}
            for (const column of columns) {
                const shape = cds._shapes[column]
                if ((shape !== undefined) && (shape.length > 1) && (typeof shape[0] == "number"))
                    item[column] = cds.data[column].slice(i * shape[1], i * shape[1] + shape[1])
                else
                    item[column] = cds.data[column][i]
            }
            data.push(item)
        }
        return data
    }

    // https://stackoverflow.com/questions/5999998/check-if-a-variable-is-of-function-type
    isFunction(functionToCheck: any) {
        if (functionToCheck) {
            const stringName = {}.toString.call(functionToCheck);
            return stringName === '[object Function]' || stringName === '[object AsyncFunction]';
        } else { return false }
    }

    /**
     * Handles changes to `this.model.columnDataSource`
     * by
     * updating the data source of `this.webComponentElement`
     * using the function or property specifed in `this.model.columnDataSourceLoadFunction`
     */
    handleColumnDataSourceChange(): void {
        if (this.model.columnDataSource) {
            let data: any // list
            const columnDataSourceOrient: any = this.model.columnDataSourceOrient;
            if (columnDataSourceOrient === "records") {
                data = this.transform_cds_to_records(this.model.columnDataSource);
            } else {
                // @ts-ignore
                data = this.model.columnDataSource.data;
            }
            const loadFunctionName: string = this.model.columnDataSourceLoadFunction.toString();
            const loadFunction = this.webComponentElement[loadFunctionName]
            if (this.isFunction(loadFunction)) {
                this.webComponentElement[loadFunctionName](data)
            } else {
                this.webComponentElement[loadFunctionName] = data
            }

        }
        // Todo: handle situation where this.model.columnDataSource is null
    }

    private activate_scripts(el: Element) {
        Array.from(el.querySelectorAll("script")).forEach((oldScript: Element) => {
            const newScript = document.createElement("script")
            Array.from(oldScript.attributes)
                .forEach(attr => newScript.setAttribute(attr.name, attr.value))
            newScript.appendChild(document.createTextNode(oldScript.innerHTML))
            if (oldScript.parentNode) {
                oldScript.parentNode.replaceChild(newScript, oldScript)
            }
        })
    }

    // See https://stackoverflow.com/questions/6491463/accessing-nested-javascript-objects-with-string-key
    /**
     * Example:
     *
     * `get_nested_property(element, "textInput.value")` returns `element.textInput.value`
     *
     * @param element
     * @param property_
     */
    get_nested_property(element: any, property_: string): string {
        property_ = property_.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
        property_ = property_.replace(/^\./, '');           // strip a leading dot
        let a = property_.split('.');
        for (let i = 0, n = a.length; i < n; ++i) {
            let k = a[i];
            if (k in element) {
                element = element[k];
            } else {
                return "";
            }
        }
        return element;
    }

    set_nested_property(element: any, property_: string, value: any): void {
        property_ = property_.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
        property_ = property_.replace(/^\./, '');           // strip a leading dot
        let a = property_.split('.');
        for (let i = 0, n = a.length; i < n; ++i) {
            let k = a[i];
            if (k in element) {
                element[k] = value;
            } else {
                return;
            }
        }
    }

    /**
     * Handles events from `eventsToWatch` by
     *
     * - Incrementing the count of the event
     * - Checking if any properties have changed
     *
     * @param ev The Event Fired
     */
    eventHandler(ev: Event): void {
        let event = ev.type;
        this.eventsCount[event] += 1;
        let eventsCountLastChanged: any = {};
        eventsCountLastChanged[event] = this.eventsCount[event]
        this.model.eventsCountLastChange = eventsCountLastChanged;

        this.checkIfPropertiesChanged()
    }

    /** Checks if any properties have changed. In case this is communicated to the server.
     *
     * For example the Wired `DropDown` does not run the `onchange` event handler when the selection changes.
     * Insted the `select` event is fired. Thus we can subscribe to this event and manually check for property changes.
     */
    checkIfPropertiesChanged(): void {
        let propertiesChange: any = {};
        for (let property in this.model.propertiesToWatch) {
            let oldValue: any = this.propertyValues[property];
            let newValue: any = this.get_nested_property(this.webComponentElement, property);
            if (oldValue != newValue) {
                propertiesChange[property] = newValue;
                this.propertyValues[property] = newValue;
            }
        }
        if (Object.keys(propertiesChange).length) {
            this.model.propertiesLastChange = propertiesChange;
        }
    }

    /** Handles the `WebComponentElement` `(on)change` event
     *
     * Communicates any changed properties in `propertiesToWatch` to the server
     * by updating `this.model.propertiesLastChange`.
     * @param ev
     */
    handlePropertiesChange(ev: any): void {
        let properties_change: any = new Object();
        for (let property in this.model.propertiesToWatch) {
            if (property in ev.detail) {
                properties_change[property] = ev.detail[property];
                this.propertyValues[property] = ev.detail[property];
            }
        }
        if (Object.keys(properties_change).length) {
            this.model.propertiesLastChange = properties_change;
        }
    }

    initPropertyValues(): void {
        this.propertyValues = new Object();
        if (!this.webComponentElement) { return; }

        for (let property in this.model.propertiesToWatch) {
            let old_value = this.propertyValues[property];
            let new_value = this.get_nested_property(this.webComponentElement, property);
            if (new_value !== old_value) {
                this.propertyValues[property] = new_value;
            }
        }
    }
    /**
     * Handles changes to `this.model.attributesLastChange`
     * by
     * updating the attributes of `this.webComponentElement` accordingly
     */
    handleAttributesLastChangeChange(): void {
        if (!this.webComponentElement) { return; }

        let attributesLastChange: any = this.model.attributesLastChange;
        for (let attribute in this.model.attributesLastChange) {
            if (attribute in this.model.attributesToWatch) {
                let old_value = this.webComponentElement.getAttribute(attribute);
                let new_value = attributesLastChange[attribute]
                if (old_value !== new_value) {
                    if (new_value === null) {
                        this.webComponentElement.removeAttribute(attribute)
                    } else {
                        this.webComponentElement.setAttribute(attribute, new_value)
                    }

                }
            }
        }
    }
    /**
    * Handles changes to `this.model.propertiesLastChange`
    * by
    * updating the properties of `this.webComponentElement` accordingly
    */
    handlePropertiesLastChangeChange(): void {
        if (!this.webComponentElement) { return; }

        let propertiesLastChange: any = this.model.propertiesLastChange;
        for (let property in this.model.propertiesLastChange) {
            if (property in this.model.propertiesToWatch) {
                let value = propertiesLastChange[property]
                this.set_nested_property(this.webComponentElement, property, value);
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
        attributesLastChange: p.Property<p.Any>, // A dictionary
        propertiesToWatch: p.Property<p.Any>, // A dictionary
        propertiesLastChange: p.Property<p.Any>, // A dictionary
        eventsToWatch: p.Property<p.Any> // A dictionary
        eventsCountLastChange: p.Property<p.Any> // A Dictionary
        columnDataSource: p.Property<p.Any> // A ColumnDataSource
        columnDataSourceOrient: p.Property<p.String>
        columnDataSourceLoadFunction: p.Property<p.String>
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
            attributesLastChange: [p.Any], // A dictionary
            propertiesToWatch: [p.Any], // A dictionary
            propertiesLastChange: [p.Any], // A dictionary
            eventsToWatch: [p.Any], // A dictionary
            eventsCountLastChange: [p.Any], // A list
            columnDataSource: [p.Any], // A ColumnDataSource
            columnDataSourceOrient: [p.Any], // A string
            columnDataSourceLoadFunction: [p.Any], // A string
        })
    }
}
