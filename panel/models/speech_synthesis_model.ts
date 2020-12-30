import * as p from "@bokehjs/core/properties"
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

function toVoicesList(voices: SpeechSynthesisVoice[]) {
  var voicesList = [];
  for (let voice of voices) {
    var item = {
      default: voice.default,
      lang: voice.lang,
      local_service: voice.localService,
      name: voice.name,
      voice_uri: voice.voiceURI,
    };
    voicesList.push(item);
  }
  return voicesList;
}
export class SpeechSynthesisModelView extends HTMLBoxView {
  model: SpeechSynthesisModel
  voices: SpeechSynthesisVoice[]

  initialize(): void {
    super.initialize()

    this.model.paused = speechSynthesis.paused;
    this.model.pending = speechSynthesis.pending;
    this.model.speaking = speechSynthesis.speaking;

    const this_=this;

    // Hack: The only way to get these parameters updated
    window.setInterval(function(){
      // Without checking for diffs I can see from notebook activity indicator that communication is sent from
      // browser to server all the time.
      if (this_.model.paused !== speechSynthesis.paused){
        this_.model.paused = speechSynthesis.paused;
      }
      if (this_.model.pending !== speechSynthesis.pending){
        this_.model.pending = speechSynthesis.pending;
      }
      if (this_.model.speaking !== speechSynthesis.speaking){
        this_.model.speaking !== speechSynthesis.speaking;
      }
    }, 1000);

    // Hack: Keeps speeking for longer texts
    // https://stackoverflow.com/questions/21947730/chrome-speech-synthesis-with-longer-texts
    window.setInterval(function(){
      if (!speechSynthesis.paused && speechSynthesis.speaking){
        window.speechSynthesis.resume();
      }
    }, 10000)

    function populateVoiceList() {
      if(typeof speechSynthesis === 'undefined') {
        return;
      }

      // According to https://talkrapp.com/speechSynthesis.html not all voices are available
      // The article includes code for ios to handle this. Might be useful.
      this_.voices = speechSynthesis.getVoices();
      if (!this_.voices){
        return;
      }

      this_.model.voices = toVoicesList(this_.voices);
    }
    populateVoiceList();
    if (typeof speechSynthesis !== 'undefined' && speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = populateVoiceList;
    }
  }

  connect_signals(): void {
      super.connect_signals()

      this.connect(this.model.properties.speaks.change, () => {
        let utterance = new SpeechSynthesisUtterance(this.model.speaks.text);
        utterance.pitch=this.model.speaks.pitch
        utterance.volume=this.model.speaks.volume
        utterance.rate=this.model.speaks.rate
        if (this.model.voices){
          for (let voice of this.voices){
            if (voice.name===this.model.speaks.voice){
              utterance.voice = voice;
            }

          }
        }
        speechSynthesis.speak(utterance);
        this.model.paused = speechSynthesis.paused;
      })
      this.connect(this.model.properties.pauses.change, () => {
        speechSynthesis.pause();
      })
      this.connect(this.model.properties.resumes.change, () => {
        // Hack: Two times resume seems to work better in Win10 Chrome
        speechSynthesis.resume();
      })
      this.connect(this.model.properties.cancels.change, () => {
        speechSynthesis.cancel();
      })
  }

  render(): void {
    super.render()

    // Hack: This will make sure voices are assigned when
    // Bokeh/ Panel is served first time with --show option.
    if (!this.model.voices){
      this.model.voices = toVoicesList(this.voices);
    }
  }


}

export namespace SpeechSynthesisModel {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    paused: p.Property<boolean>
    pending: p.Property<boolean>
    speaking: p.Property<boolean>
    voices: p.Property<any[]>

    cancels: p.Property<number>
    pauses: p.Property<number>
    resumes: p.Property<number>
    speaks: p.Property<any>
  }
}

export interface SpeechSynthesisModel extends SpeechSynthesisModel.Attrs {}

export class SpeechSynthesisModel extends HTMLBox {
  properties: SpeechSynthesisModel.Props

  constructor(attrs?: Partial<SpeechSynthesisModel.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.speech_synthesis_model"

  static init_SpeechSynthesisModel(): void {
    this.prototype.default_view = SpeechSynthesisModelView

    this.define<SpeechSynthesisModel.Props>({
      paused: [ p.Boolean,   false ],
      pending: [ p.Boolean,   false ],
      speaking: [ p.Boolean,   false ],
      voices: [p.Array, []],
      cancels: [ p.Number, 0     ],
      pauses: [ p.Number, 0     ],
      resumes: [ p.Number, 0     ],
      speaks: [ p.Any,    {}    ],
    })
  }
}
