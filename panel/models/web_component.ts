import { div, label } from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import { bk_input_group } from "@bokehjs/styles/widgets/inputs"

function htmlDecode(input: string): string | null {
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
}

export class WebComponentView extends HTMLBoxView {
  model: WebComponent
  webComponentElement: any // Element
  eventsCount: any // Dict
  propertyValues: any // Dict

  protected label_el: HTMLLabelElement
  protected group_el: HTMLElement

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.name.change, () => this.handleNameChange())
    this.connect(this.model.properties.innerHTML.change, () => this.render())
    this.connect(this.model.properties.attributesLastChange.change, () => this.handleAttributesLastChangeChange())
    this.connect(this.model.properties.propertiesLastChange.change, () => this.handlePropertiesLastChangeChange())
    this.connect(this.model.properties.columnDataSource.change, () => this.handleColumnDataSourceChange())
  }

  private handleNameChange() {
    if (this.label_el)
      this.label_el.textContent = this.model.name
  }

  render(): void {
    super.render()
    if (this.el.innerHTML !== this.model.innerHTML)
      this.createOrUpdateWebComponentElement()
  }

  after_layout(): void {
    if ("after_layout" in this.webComponentElement)
      this.webComponentElement.after_layout()
  }

  private createOrUpdateWebComponentElement() {
    if (this.webComponentElement)
      this.webComponentElement.onchange = null

    // @Philippfr: How do we make sure the component is automatically sized according to the
    // parameters of the WebComponent like width, height, sizing_mode etc?
    // Should we set height and width to 100% or similar?
    // For now I've set min_height as a part of .py __init__ for some of the Wired components?
    const title = this.model.name
    if (this.model.componentType === "inputgroup" && title) {
      this.group_el = div({ class: bk_input_group }, this.label_el)
      this.group_el.innerHTML = (htmlDecode(this.model.innerHTML) as string)
      this.webComponentElement = this.group_el.firstElementChild
      this.label_el = label({ style: { display: title.length == 0 ? "none" : "" } }, title)
      this.group_el.insertBefore(this.label_el, this.webComponentElement)
      this.el.appendChild(this.group_el)
    } else {
      this.el.innerHTML = (htmlDecode(this.model.innerHTML) as string)
      this.webComponentElement = this.el.firstElementChild
    }

    this.activate_scripts(this.webComponentElement.parentNode)

    // Initialize properties
    this.initPropertyValues()
    this.handlePropertiesLastChangeChange()
    this.handleColumnDataSourceChange()

    // Subscribe to events
    this.webComponentElement.onchange = (ev: any) => this.handlePropertiesChange(ev)
    this.addEventListeners()
    this.addAttributesMutationObserver()
  }

  addAttributesMutationObserver(): void {
    if (!this.model.attributesToWatch)
      return

    let options = {
      childList: false,
      attributes: true,
      characterData: false,
      subtree: false,
      attributeFilter: Object.keys(this.model.attributesToWatch),
      attributeOldValue: false,
      characterDataOldValue: false
    };

    const handleAttributesChange = (_: Array<MutationRecord>): void => {
      let attributesLastChange: any = new Object();

      for (let attribute in this.model.attributesToWatch) {
        const value = this.webComponentElement.getAttribute(attribute)
        attributesLastChange[attribute] = value;
      }

      if (this.model.attributesLastChange !== attributesLastChange)
        this.model.attributesLastChange = attributesLastChange
    }

    let observer = new MutationObserver(handleAttributesChange)
    observer.observe(this.webComponentElement, options)
  }

  private addEventListeners() {
    this.eventsCount = {}
    for (let event in this.model.eventsToWatch) {
      this.eventsCount[event] = 0
      this.webComponentElement.addEventListener(event, (ev: Event) => this.eventHandler(ev), false)
    }
  }

  transform_cds_to_records(cds: ColumnDataSource): any {
    const data: any = []
    const columns = cds.columns()

    if (columns.length === 0) {
      return [];
    }
    for (let i = 0; i < cds.data[columns[0]].length; i++) {
      const item: any = {}
      for (const column of columns) {
        const shape = (cds._shapes[column] as any)
        if ((shape !== undefined) && (shape.length > 1) && (typeof shape[0] == "number"))
          item[column] = cds.get_array(column).slice(i * shape[1], i * shape[1] + shape[1])
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
    } else {
      return false
    }
  }

  /**
   * Handles changes to `this.model.columnDataSource`
   * by
   * updating the data source of `this.webComponentElement`
   * using the function or property specifed in `this.model.columnDataSourceLoadFunction`
   */
  handleColumnDataSourceChange(): void {
    // @Philippfr: Right now we just reload all the data
    // For example Perspective has an `update` function to append data
    // Is this something we could/ should support?
    if (this.model.columnDataSource) {
      let data: any // list
      const columnDataSourceOrient: any = this.model.columnDataSourceOrient
      if (columnDataSourceOrient === "records")
        data = this.transform_cds_to_records(this.model.columnDataSource)
      else
        data = this.model.columnDataSource.data; // @ts-ignore
      const loadFunctionName: string = this.model.columnDataSourceLoadFunction.toString();
      const loadFunction = this.webComponentElement[loadFunctionName]
      if (this.isFunction(loadFunction))
        this.webComponentElement[loadFunctionName](data)
      else
        this.webComponentElement[loadFunctionName] = data
    }
    // Todo: handle situation where this.model.columnDataSource is null
  }

  private activate_scripts(el: Element) {
    Array.from(el.querySelectorAll("script")).forEach((oldScript: Element) => {
      const newScript = document.createElement("script")
      Array.from(oldScript.attributes)
        .forEach(attr => newScript.setAttribute(attr.name, attr.value))
      newScript.appendChild(document.createTextNode(oldScript.innerHTML))
      if (oldScript.parentNode)
        oldScript.parentNode.replaceChild(newScript, oldScript)
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
    property_ = property_.replace(/^\./, '');       // strip a leading dot
    let a = property_.split('.');
    for (let i = 0, n = a.length; i < n; ++i) {
      let k = a[i];
      if (k in element)
        element = element[k]
      else
        return ""
    }
    return element;
  }

  set_nested_property(element: any, property_: string, value: any): void {
    // @Phillipfr: I need your help to understand and solve this
    // hack: Setting the value of the WIRED-SLIDER before its ready
    // will destroy the setter.
    // I don't yet understand this.
    console.log("set_nested_property")
    console.log(element)
    console.log(property_)
    console.log(value)
    if (["WIRED-SLIDER"].indexOf(element.tagName)>=0){
      const setter = element.__lookupSetter__(property_);
      if (!setter){return}
    }

    const pList = property_.split('.');
    if (pList.length === 1)
      element[property_] = value
    else {
      const len = pList.length
      for (let i = 0; i < len-1; i++) {
        const elem = pList[i]
        if( !element[elem] ) element[elem] = {}
        element = element[elem]
      }
      element[pList[len-1]] = value;
    }
  }

  // set_nested_property(element: any, property_: string, value: any): void {
  //   console.log(element);
  //   console.log(property_);
  //   console.log(value);
  //   property_ = property_.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
  //   property_ = property_.replace(/^\./, '');       // strip a leading dot
  //   let a = property_.split('.');
  //   console.log(a)
  //   if (a.length == 1) {
  //     // Hack:
  //     // for some reason the wired-checkbox checked property is not in the element on construction
  //     // So the `k in element` test below fails.
  //     // I've added this line to handle that.
  //     console.log("length 1", element, a[0])
  //     element[a[0]] = value
  //   } else {
  //     for (let i = 0, n = a.length; i < n; ++i) {
  //       let k = a[i];
  //       if (k in element) {
  //         console.log("nested")
  //         console.log(k);
  //         console.log(element[k]);
  //         element[k] = value;
  //       } else {
  //         return;
  //       }
  //     }
  //   }
  // }

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
    const propertiesChange: any = {};
    for (const property in this.model.propertiesToWatch) {
      const oldValue: any = this.propertyValues[property];
      const newValue: any = this.get_nested_property(this.webComponentElement, property);
      if (oldValue != newValue) {
        propertiesChange[property] = newValue;
        this.propertyValues[property] = newValue;
      }
    }
    if (Object.keys(propertiesChange).length)
      this.model.propertiesLastChange = propertiesChange
  }

  /** Handles the `WebComponentElement` `(on)change` event
   *
   * Communicates any changed properties in `propertiesToWatch` to the server
   * by updating `this.model.propertiesLastChange`.
   * @param ev
   */
  handlePropertiesChange(ev: any): void {
    const properties_change: any = new Object();
    for (const property in this.model.propertiesToWatch) {
      if (property in ev.detail) {
        properties_change[property] = ev.detail[property];
        this.propertyValues[property] = ev.detail[property];
      }
    }
    if (Object.keys(properties_change).length)
      this.model.propertiesLastChange = properties_change
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
    if (!this.webComponentElement)
      return

    let attributesLastChange: any = this.model.attributesLastChange;
    for (let attribute in this.model.attributesLastChange) {
      if (attribute in this.model.attributesToWatch) {
        let old_value = this.webComponentElement.getAttribute(attribute);
        let new_value = attributesLastChange[attribute]
        if (old_value !== new_value) {
          if (new_value === null)
            this.webComponentElement.removeAttribute(attribute)
          else
            this.webComponentElement.setAttribute(attribute, new_value)
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
    console.log("handlePropertiesLastChangeChange propertiesLastChange=", propertiesLastChange);
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
  // @Philipfr: How do I make property types more specific
  export type Props = HTMLBox.Props & {
    componentType: p.Property<string>,
    innerHTML: p.Property<string>,
    attributesToWatch: p.Property<any> // A dictionary
    attributesLastChange: p.Property<any>, // A dictionary
    propertiesToWatch: p.Property<any>, // A dictionary
    propertiesLastChange: p.Property<any>, // A dictionary
    eventsToWatch: p.Property<any> // A dictionary
    eventsCountLastChange: p.Property<any> // A Dictionary
    columnDataSource: p.Property<ColumnDataSource> // A ColumnDataSource
    columnDataSourceOrient: p.Property<string>
    columnDataSourceLoadFunction: p.Property<string>
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
      // @Philipfr: How do I make property types more specific
      componentType: [p.String, 'htmlbox'],
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
