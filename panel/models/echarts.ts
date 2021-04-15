import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "./layout"

const mouse_events = [
  'click', 'dblclick', 'mousedown', 'mousemove', 'mouseup', 'mouseover', 'mouseout',
  'globalout', 'contextmenu'
];

const events = [
  'highlight', 'downplay', 'selectchanged', 'legendselectchangedEvent', 'legendselected',
  'legendunselected', 'legendselectall', 'legendinverseselect', 'legendscroll', 'datazoom',
  'datarangeselected', 'timelineplaychanged', 'restore', 'dataviewchanged', 'magictypechanged',
  'geoselectchanged', 'geoselected', 'geounselected', 'axisareaselected', 'brush', 'brushEnd',
  'rushselected', 'globalcursortaken', 'rendered', 'finished'
];

const all_events = mouse_events.concat(events);

export class EChartsView extends HTMLBoxView {
  model: ECharts
  _chart: any
  container: Element


  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => this._plot())
    const {width, height, renderer, theme} = this.model.properties
    this.on_change([width, height], () => this._resize())
    this.on_change([theme, renderer], () => this.render())
  }

  render(): void {
    if (this._chart != null)
      (window as any).echarts.dispose(this._chart);
    super.render()
    this.container = div({style: "height: 100%; width: 100%;"})
    const config = {width: this.model.width, height: this.model.height, renderer: this.model.renderer}
    this._chart = (window as any).echarts.init(
      this.container,
      this.model.theme,
      config
    )
    this._plot()
    this.shadow_el.append(this.container)
  }

  override remove(): void {
    super.remove()
    if (this._chart != null)
      (window as any).echarts.dispose(this._chart);
  }

  after_layout(): void {
    super.after_layout()
    this._chart.resize()
  }

  _plot(): void {
    if ((window as any).echarts == null)
      return
    this._chart.setOption(this.model.data);
  }

  _resize(): void {
    this._chart.resize({width: this.model.width, height: this.model.height});
  }

  _subscribe(): void {
    if ((window as any).echarts == null)
      return
    for (let key in this.model.event_config) {
      if (all_events.includes(key)) {
        let value = this.model.event_config[key];
        console.log(value, typeof value);
        if (value == null) {
          console.log("Subscribed to Echarts event:", key, "without query - logging events at console.")
          this._chart.on(key, value, function (params: any) {
            console.log(params);
          });
        } else {
          if (typeof value === 'object') {
            if ('query' in value && 'base_url' in value && 'identifier' in value) {
              console.log("Subscribed with open new browser tab to Echarts event:",
                key, "with query:", value['query'])
              this._chart.on(key, value['query'], function (params: any) {
                if ("data" in params) {
                  if (value['identifier'] in params.data) {
                    console.log("Opening new brower tab:", value['base_url'] + params.data[value['identifier']]);
                    window.open(value['base_url'] + params.data[value['identifier']], '_blank')?.focus();
                  }
                }
              });
            } else if ('query' in value && 'handler' in value) {
              console.log("Subscribed with handler to Echarts event:",
                key, "with query:", value['query'])
              this._chart.on(key, value['query'], eval(value['handler']))
            }
          } else {
            console.log("Subscribed to Echarts event:", key, "with query:", value)
            this._chart.on(key, value,  (params: any) => {
              sendEvent({"test": "test"}, this.model);
              console.log("Send events from patams:", params);
            });
          }
        }
      } else {
        console.warn("Couldn't subscribe to unknown Echarts event:", key, "- ignoring it.");
      }
    }
  }
}

export namespace ECharts {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    event_config: p.Property<any>
    event: p.Property<any>
    renderer: p.Property<string>
    theme: p.Property<string>
  }
}

export interface ECharts extends ECharts.Attrs {}

export class ECharts extends HTMLBox {
  properties: ECharts.Props

  constructor(attrs?: Partial<ECharts.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.echarts"

  static {
    this.prototype.default_view = EChartsView

    this.define<ECharts.Props>(({ Any, String }) => ({
      data:         [Any, {}],
      event_config: [Any, {}],
      event:        [Any, {}],
      theme:        [String, "default"],
      renderer:     [String, "canvas"]
    }))
  }
}

function sendEvent(event: any, model: ECharts): void {
  const eventData: any = filterEventData(event)
  // To make sure event gets sent we add a uuid
  // https://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid
  eventData.uuid = uuidv4()

  model.event = eventData
}

function filterEventData(event: any) {
  return event
}

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
