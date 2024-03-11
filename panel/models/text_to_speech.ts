import type * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "./layout"

function toVoicesList(voices: SpeechSynthesisVoice[]) {
  const voicesList = []
  for (const voice of voices) {
    const item = {
      default: voice.default,
      lang: voice.lang,
      local_service: voice.localService,
      name: voice.name,
      voice_uri: voice.voiceURI,
    }
    voicesList.push(item)
  }
  return voicesList
}

export class TextToSpeechView extends HTMLBoxView {
  declare model: TextToSpeech

  voices: SpeechSynthesisVoice[]
  _callback: any

  override initialize(): void {
    super.initialize()

    this.model.paused = speechSynthesis.paused
    this.model.pending = speechSynthesis.pending
    this.model.speaking = speechSynthesis.speaking

    // Hack: Keeps speeking for longer texts
    // https://stackoverflow.com/questions/21947730/chrome-speech-synthesis-with-longer-texts
    this._callback = window.setInterval(function() {
      if (!speechSynthesis.paused && speechSynthesis.speaking) {
        window.speechSynthesis.resume()
      }
    }, 10000)

    const populateVoiceList = () => {
      if (typeof speechSynthesis === "undefined") {
        return
      }

      // According to https://talkrapp.com/speechSynthesis.html not all voices are available
      // The article includes code for ios to handle this. Might be useful.
      this.voices = speechSynthesis.getVoices()
      if (!this.voices) {
        return
      }

      this.model.voices = toVoicesList(this.voices)
    }
    populateVoiceList()
    if (typeof speechSynthesis !== "undefined" && speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = populateVoiceList
    }
  }

  override remove(): void {
    if (this._callback != null) {
      clearInterval(this._callback)
    }
    speechSynthesis.cancel()
    super.remove()
  }

  override connect_signals(): void {
    super.connect_signals()

    const {speak, pause, resume, cancel} = this.model.properties
    this.on_change(speak, () => {
      this.speak()
    })
    this.on_change(pause, () => {
      this.model.pause = false
      speechSynthesis.pause()
    })
    this.on_change(resume, () => {
      this.model.resume = false
      speechSynthesis.resume()
    })
    this.on_change(cancel, () => {
      this.model.cancel = false
      speechSynthesis.cancel()
    })
  }

  speak(): void {
    const utterance = new SpeechSynthesisUtterance(this.model.speak.text)
    utterance.pitch = this.model.speak.pitch
    utterance.volume = this.model.speak.volume
    utterance.rate = this.model.speak.rate
    if (this.model.voices) {
      for (const voice of this.voices) {
        if (voice.name === this.model.speak.voice) {
          utterance.voice = voice
        }
      }
    }

    utterance.onpause = () => this.model.paused = true

    utterance.onstart = () => {
      this.model.speaking = true
      this.model.paused = false
      this.model.pending = speechSynthesis.pending
    }

    utterance.onresume = () => this.model.paused = false

    utterance.onend = () => {
      this.model.speaking = false
      this.model.paused = false
      this.model.pending = speechSynthesis.pending
    }

    speechSynthesis.speak(utterance)
    this.model.paused = speechSynthesis.paused
    this.model.pending = speechSynthesis.pending
  }

  override render(): void {
    super.render()
    // Hack: This will make sure voices are assigned when
    // Bokeh/ Panel is served first time with --show option.
    if (!this.model.voices) {
      this.model.voices = toVoicesList(this.voices)
    }
    if (this.model.speak != null && this.model.speak.text) {
      this.speak()
    }
  }
}

export namespace TextToSpeech {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    paused: p.Property<boolean>
    pending: p.Property<boolean>
    speaking: p.Property<boolean>
    voices: p.Property<any[]>
    cancel: p.Property<boolean>
    pause: p.Property<boolean>
    resume: p.Property<boolean>
    speak: p.Property<any>
  }
}

export interface TextToSpeech extends TextToSpeech.Attrs {}

export class TextToSpeech extends HTMLBox {
  declare properties: TextToSpeech.Props

  constructor(attrs?: Partial<TextToSpeech.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.text_to_speech"

  static {
    this.prototype.default_view = TextToSpeechView

    this.define<TextToSpeech.Props>(({Any, List, Bool}) => ({
      paused:   [ Bool,    false ],
      pending:  [ Bool,    false ],
      speaking: [ Bool,    false ],
      voices:   [ List(Any),    [] ],
      cancel:   [ Bool,    false ],
      pause:    [ Bool,    false ],
      resume:   [ Bool,    false ],
      speak:    [ Any,        {}    ],
    }))
  }
}
