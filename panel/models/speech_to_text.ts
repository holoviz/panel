import * as p from "@bokehjs/core/properties"
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// Hack inspired by https://stackoverflow.com/questions/38087013/angular2-web-speech-api-voice-recognition
export interface IWindow extends Window {
    webkitSpeechRecognition: any;
}
const {webkitSpeechRecognition} : IWindow = <IWindow><unknown>window;

export class SpeechToTextView extends HTMLBoxView {
    model: SpeechToText
    recognition: any

    initialize(): void {
        console.log("initialize")
        console.log(this.model)
        super.initialize()

        this.recognition = new webkitSpeechRecognition();
        console.log(this.recognition);
    }

    connect_signals(): void {
        console.log("connect")
        console.log(this.model)
        super.connect_signals()

        this.connect(this.model.properties.starts.change, () => {this.recognition.starts=this.model.starts;console.log("starts");})
        this.connect(this.model.properties.stops.change, () => {this.recognition.stops=this.model.stops;console.log("stops");})
        this.connect(this.model.properties.aborts.change, () => {this.recognition.aborts=this.model.aborts;console.log("aborts");})
        // this.connect(this.model.properties.grammars.change, () => {this.recognition.grammars=this.model.grammars;console.log("grammars");})
        this.connect(this.model.properties.lang.change, () => {this.recognition.lang=this.model.lang;console.log("lang");})
        this.connect(this.model.properties.continous.change, () => {this.recognition.continous=this.model.continous;console.log("continous");})
        this.connect(this.model.properties.interim_results.change, () => {this.recognition.interim_results=this.model.interim_results;console.log("interim_results");})
        this.connect(this.model.properties.max_alternatives.change, () => {this.recognition.max_alternatives=this.model.max_alternatives;console.log("max_alternatives");})
        this.connect(this.model.properties.service_uri.change, () => {this.recognition.service_uri=this.model.service_uri;console.log("service_uri");})
    }

    render(): void {
        console.log("render")
        console.log(this.model)
        super.render()
        this.el.innerHTML="Hello Speech Recognition"
    }
}

export namespace SpeechToText {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    starts: p.Property<number>
    stops: p.Property<number>
    aborts: p.Property<any>

    grammars: p.Property<any[]>
    lang: p.Property<string>
    continous: p.Property<boolean>
    interim_results: p.Property<boolean>
    max_alternatives: p.Property<number>
    service_uri: p.Property<string>
  }
}

export interface SpeechToText extends SpeechToText.Attrs {}

export class SpeechToText extends HTMLBox {
  properties: SpeechToText.Props

  constructor(attrs?: Partial<SpeechToText.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.speech_to_text"

  static init_SpeechToText(): void {
    this.prototype.default_view = SpeechToTextView

    this.define<SpeechToText.Props>({
        starts: [ p.Number, 0     ],
        stops: [ p.Number, 0     ],
        aborts: [ p.Number, 0     ],

        grammars: [p.Array, []],
        lang: [p.String, ],
        continous: [ p.Boolean,   false ],
        interim_results: [ p.Boolean,   false ],
        max_alternatives: [ p.Number,   1 ],
        service_uri: [p.String, ]
    })
  }
}