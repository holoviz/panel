import { HTMLBox, HTMLBoxView } from "./layout";
function toVoicesList(voices) {
    const voicesList = [];
    for (const voice of voices) {
        const item = {
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
export class TextToSpeechView extends HTMLBoxView {
    static __name__ = "TextToSpeechView";
    voices;
    _callback;
    initialize() {
        super.initialize();
        this.model.paused = speechSynthesis.paused;
        this.model.pending = speechSynthesis.pending;
        this.model.speaking = speechSynthesis.speaking;
        // Hack: Keeps speeking for longer texts
        // https://stackoverflow.com/questions/21947730/chrome-speech-synthesis-with-longer-texts
        this._callback = window.setInterval(function () {
            if (!speechSynthesis.paused && speechSynthesis.speaking) {
                window.speechSynthesis.resume();
            }
        }, 10000);
        const populateVoiceList = () => {
            if (typeof speechSynthesis === "undefined") {
                return;
            }
            // According to https://talkrapp.com/speechSynthesis.html not all voices are available
            // The article includes code for ios to handle this. Might be useful.
            this.voices = speechSynthesis.getVoices();
            if (!this.voices) {
                return;
            }
            this.model.voices = toVoicesList(this.voices);
        };
        populateVoiceList();
        if (typeof speechSynthesis !== "undefined" && speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = populateVoiceList;
        }
    }
    remove() {
        if (this._callback != null) {
            clearInterval(this._callback);
        }
        speechSynthesis.cancel();
        super.remove();
    }
    connect_signals() {
        super.connect_signals();
        const { speak, pause, resume, cancel } = this.model.properties;
        this.on_change(speak, () => {
            this.speak();
        });
        this.on_change(pause, () => {
            this.model.pause = false;
            speechSynthesis.pause();
        });
        this.on_change(resume, () => {
            this.model.resume = false;
            speechSynthesis.resume();
        });
        this.on_change(cancel, () => {
            this.model.cancel = false;
            speechSynthesis.cancel();
        });
    }
    speak() {
        const utterance = new SpeechSynthesisUtterance(this.model.speak.text);
        utterance.pitch = this.model.speak.pitch;
        utterance.volume = this.model.speak.volume;
        utterance.rate = this.model.speak.rate;
        if (this.model.voices) {
            for (const voice of this.voices) {
                if (voice.name === this.model.speak.voice) {
                    utterance.voice = voice;
                }
            }
        }
        utterance.onpause = () => this.model.paused = true;
        utterance.onstart = () => {
            this.model.speaking = true;
            this.model.paused = false;
            this.model.pending = speechSynthesis.pending;
        };
        utterance.onresume = () => this.model.paused = false;
        utterance.onend = () => {
            this.model.speaking = false;
            this.model.paused = false;
            this.model.pending = speechSynthesis.pending;
        };
        speechSynthesis.speak(utterance);
        this.model.paused = speechSynthesis.paused;
        this.model.pending = speechSynthesis.pending;
    }
    render() {
        super.render();
        // Hack: This will make sure voices are assigned when
        // Bokeh/ Panel is served first time with --show option.
        if (!this.model.voices) {
            this.model.voices = toVoicesList(this.voices);
        }
        if (this.model.speak != null && this.model.speak.text) {
            this.speak();
        }
    }
}
export class TextToSpeech extends HTMLBox {
    static __name__ = "TextToSpeech";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.text_to_speech";
    static {
        this.prototype.default_view = TextToSpeechView;
        this.define(({ Any, List, Bool }) => ({
            paused: [Bool, false],
            pending: [Bool, false],
            speaking: [Bool, false],
            voices: [List(Any), []],
            cancel: [Bool, false],
            pause: [Bool, false],
            resume: [Bool, false],
            speak: [Any, {}],
        }));
    }
}
//# sourceMappingURL=text_to_speech.js.map