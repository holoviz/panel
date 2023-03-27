import * as p from "@bokehjs/core/properties"
import { HTMLBox, HTMLBoxView } from "./layout"

const iconStarted = `<svg xmlns="http://www.w3.org/2000/svg" height="22px" style="vertical-align: middle;" fill="currentColor" class="bi bi-mic" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/>
  <path fill-rule="evenodd" d="M10 8V3a2 2 0 1 0-4 0v5a2 2 0 1 0 4 0zM8 0a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V3a3 3 0 0 0-3-3z"/>
</svg>`
const iconNotStarted = `<svg xmlns="http://www.w3.org/2000/svg" height="22px" style="vertical-align: middle;" fill="currentColor" class="bi bi-mic-mute" viewBox="0 0 16 16">
<path fill-rule="evenodd" d="M12.734 9.613A4.995 4.995 0 0 0 13 8V7a.5.5 0 0 0-1 0v1c0 .274-.027.54-.08.799l.814.814zm-2.522 1.72A4 4 0 0 1 4 8V7a.5.5 0 0 0-1 0v1a5 5 0 0 0 4.5 4.975V15h-3a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-3v-2.025a4.973 4.973 0 0 0 2.43-.923l-.718-.719zM11 7.88V3a3 3 0 0 0-5.842-.963l.845.845A2 2 0 0 1 10 3v3.879l1 1zM8.738 9.86l.748.748A3 3 0 0 1 5 8V6.121l1 1V8a2 2 0 0 0 2.738 1.86zm4.908 3.494l-12-12 .708-.708 12 12-.708.707z"/>
</svg>`

const titleStarted = "Click to STOP the speech recognition.";
const titleNotStarted = "Click to START the speech recognition.";

// Hack inspired by https://stackoverflow.com/questions/38087013/angular2-web-speech-api-voice-recognition
interface IWindow extends Window {
  webkitSpeechRecognition: any;
  webkitSpeechGrammarList: any;
}
const {webkitSpeechRecognition} : IWindow = <IWindow><unknown>window;
const {webkitSpeechGrammarList} : IWindow = <IWindow><unknown>window;

function htmlToElement(html: string) {
  var template = document.createElement('template');
  html = html.trim(); // Never return a text node of whitespace as the result
  template.innerHTML = html;
  return <HTMLElement>template.content.firstChild;
}

function deserializeGrammars(grammars: any[]){
  if (grammars) {
    var speechRecognitionList = new webkitSpeechGrammarList();
    for (let grammar of grammars){
      if (grammar.src)
        speechRecognitionList.addFromString(grammar.src, grammar.weight)
      else if (grammar.uri)
        speechRecognitionList.addFromURI(grammar.uri, grammar.weight)
    }
    return speechRecognitionList
  } else
    return null
}

function round(value: number) {
  return Math.round((value + Number.EPSILON) * 100) / 100
}

function serializeResults(results_: any) {
  const results = [];
  for (let result of results_) {
    let alternatives: { confidence: number; transcript: string; }[] = [];
    let item = { is_final: result.isFinal, alternatives: alternatives };
    for (let i = 0; i < result.length; i++) {
      let alternative = {
	confidence: round(result[i].confidence),
	transcript: result[i].transcript
      };
      alternatives.push(alternative)
    }
    item.alternatives = alternatives
    results.push(item)
  }
  return results
}

export class SpeechToTextView extends HTMLBoxView {
  model: SpeechToText
  recognition: any
  buttonEl: HTMLElement

  initialize(): void {
    super.initialize()

    this.recognition = new webkitSpeechRecognition();
    this.recognition.lang = this.model.lang;
    this.recognition.continuous = this.model.continuous;
    this.recognition.interimResults = this.model.interim_results;
    this.recognition.maxAlternatives = this.model.max_alternatives;
    this.recognition.serviceURI = this.model.service_uri;
    this.setGrammars()

    this.recognition.onresult = (event: any) => {
      this.model.results = serializeResults(event.results)
    }
    this.recognition.onerror = (event: any) => {
      console.log("SpeechToText Error")
      console.log(event);
    }
    this.recognition.onnomatch = (event: any) => {
      console.log("SpeechToText No Match")
      console.log(event)
    }

    this.recognition.onaudiostart = () => this.model.audio_started = true
    this.recognition.onaudioend = () => this.model.audio_started = false
    this.recognition.onsoundstart = () => this.model.sound_started = true
    this.recognition.onsoundend = () => this.model.sound_started = false
    this.recognition.onspeechstart = () => this.model.speech_started=true
    this.recognition.onspeechend = () => this.model.speech_started=false
    this.recognition.onstart = () => {
      this.buttonEl.onclick = () => {this.recognition.stop()}
      this.buttonEl.innerHTML = this.iconStarted();
      this.buttonEl.setAttribute("title", titleStarted);
      this.model.started = true;
    }
    this.recognition.onend = () => {
      this.buttonEl.onclick = () => { this.recognition.start() }
      this.buttonEl.innerHTML = this.iconNotStarted();
      this.buttonEl.setAttribute("title", titleNotStarted);
      this.model.started = false;
    }

    this.buttonEl = htmlToElement(`<button class="bk bk-btn bk-btn-${this.model.button_type}" type="button" title="${titleNotStarted}"></button>`)
    this.buttonEl.innerHTML = this.iconNotStarted()
    this.buttonEl.onclick = () => this.recognition.start()
  }

  iconStarted(): string {
    if (this.model.button_started!=='')
      return this.model.button_started
    else
      return iconStarted
  }

  iconNotStarted(): string {
    if (this.model.button_not_started!=='')
      return this.model.button_not_started
    else
      return iconNotStarted
  }

  setIcon(): void {
    if (this.model.started)
      this.buttonEl.innerHTML = this.iconStarted()
    else
      this.buttonEl.innerHTML = this.iconNotStarted()
  }

  connect_signals(): void {
    super.connect_signals()

    this.connect(this.model.properties.start.change, () => {
      this.model.start = false
      this.recognition.start()
    })
    this.connect(this.model.properties.stop.change, () => {
      this.model.stop = false
      this.recognition.stop()
    })
    this.connect(this.model.properties.abort.change, () => {
      this.model.abort = false
      this.recognition.abort()
    })
    this.connect(this.model.properties.grammars.change, () => this.setGrammars())
    this.connect(this.model.properties.lang.change, () => this.recognition.lang = this.model.lang)
    this.connect(this.model.properties.continuous.change, () => this.recognition.continuous = this.model.continuous)
    this.connect(this.model.properties.interim_results.change, () => this.recognition.interimResults = this.model.interim_results)
    this.connect(this.model.properties.max_alternatives.change, () => this.recognition.maxAlternatives = this.model.max_alternatives)
    this.connect(this.model.properties.service_uri.change, () => this.recognition.serviceURI = this.model.service_uri)
    this.connect(this.model.properties.button_type.change, () => this.buttonEl.className = `bk bk-btn bk-btn-${this.model.button_type}`)
    this.connect(this.model.properties.button_hide.change, () => this.render())
    const {button_not_started, button_started} = this.model.properties
    this.on_change([button_not_started, button_started], () => this.setIcon())
  }

  setGrammars(): void {
    this.recognition.grammars = deserializeGrammars(this.model.grammars);
  }

  render(): void {
    super.render()
    if (!this.model.button_hide)
      this.shadow_el.appendChild(this.buttonEl)
  }
}

export namespace SpeechToText {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    start: p.Property<boolean>
    stop: p.Property<boolean>
    abort: p.Property<boolean>
    grammars: p.Property<any[]>
    lang: p.Property<string>
    continuous: p.Property<boolean>
    interim_results: p.Property<boolean>
    max_alternatives: p.Property<number>
    service_uri: p.Property<string>
    started: p.Property<boolean>
    audio_started: p.Property<boolean>
    sound_started: p.Property<boolean>
    speech_started: p.Property<boolean>
    button_type: p.Property<string>
    button_hide: p.Property<boolean>
    button_not_started: p.Property<string>
    button_started: p.Property<string>
    results: p.Property<any[]>
  }
}

export interface SpeechToText extends SpeechToText.Attrs {}

export class SpeechToText extends HTMLBox {
  properties: SpeechToText.Props

  constructor(attrs?: Partial<SpeechToText.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.speech_to_text"

  static {
    this.prototype.default_view = SpeechToTextView

    this.define<SpeechToText.Props>(({Any, Array, Boolean, Number, String}) => ({
      start: [ Boolean, false ],
      stop: [ Boolean, false ],
      abort: [ Boolean, false ],
      grammars: [ Array(Any), [] ],
      lang: [ String, '' ],
      continuous: [ Boolean,   false ],
      interim_results: [ Boolean,   false ],
      max_alternatives: [ Number,   1 ],
      service_uri: [ String, '' ],
      started: [ Boolean,   false ],
      audio_started: [ Boolean,   false ],
      sound_started: [ Boolean,   false ],
      speech_started: [ Boolean,   false ],
      button_type: [ String, 'light' ],
      button_hide: [ Boolean,   false ],
      button_not_started: [ String,   '' ],
      button_started: [ String,   '' ],
      results: [ Array(Any), [] ],
    }))
  }
}
