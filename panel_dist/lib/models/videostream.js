import { HTMLBox, HTMLBoxView } from "./layout";
export class VideoStreamView extends HTMLBoxView {
    static __name__ = "VideoStreamView";
    videoEl;
    canvasEl;
    constraints = {
        audio: false,
        video: true,
    };
    timer;
    initialize() {
        super.initialize();
        if (this.model.timeout !== null) {
            this.set_timeout();
        }
    }
    connect_signals() {
        super.connect_signals();
        const { timeout, snapshot, paused } = this.model.properties;
        this.on_change(timeout, () => this.set_timeout());
        this.on_change(snapshot, () => this.snapshot());
        this.on_change(paused, () => this.pause());
    }
    pause() {
        if (this.model.paused) {
            if (this.timer != null) {
                clearInterval(this.timer);
                this.timer = null;
            }
            this.videoEl.pause();
        }
        else {
            this.videoEl.play();
        }
        this.set_timeout();
    }
    set_timeout() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        if (this.model.timeout != null && this.model.timeout > 0) {
            this.timer = setInterval(() => this.snapshot(), this.model.timeout);
        }
    }
    snapshot() {
        this.canvasEl.width = this.videoEl.videoWidth;
        this.canvasEl.height = this.videoEl.videoHeight;
        const context = this.canvasEl.getContext("2d");
        if (context) {
            context.drawImage(this.videoEl, 0, 0, this.canvasEl.width, this.canvasEl.height);
        }
        this.model.value = this.canvasEl.toDataURL(`image/${this.model.format}`, 0.95);
    }
    remove() {
        super.remove();
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
    render() {
        super.render();
        if (this.videoEl) {
            return;
        }
        this.videoEl = document.createElement("video");
        if (!this.model.sizing_mode || this.model.sizing_mode === "fixed") {
            if (this.model.height) {
                this.videoEl.height = this.model.height;
            }
            if (this.model.width) {
                this.videoEl.width = this.model.width;
            }
        }
        this.videoEl.style.objectFit = "fill";
        this.videoEl.style.minWidth = "100%";
        this.videoEl.style.minHeight = "100%";
        this.canvasEl = document.createElement("canvas");
        this.shadow_el.appendChild(this.videoEl);
        if (navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia(this.constraints)
                .then(stream => {
                this.videoEl.srcObject = stream;
                if (!this.model.paused) {
                    this.videoEl.play();
                }
            })
                .catch(console.error);
        }
    }
}
export class VideoStream extends HTMLBox {
    static __name__ = "VideoStream";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = VideoStreamView;
        this.define(({ Any, Bool, Int, Nullable, Str }) => ({
            format: [Str, "png"],
            paused: [Bool, false],
            snapshot: [Bool, false],
            timeout: [Nullable(Int), null],
            value: [Any],
        }));
        this.override({
            height: 240,
            width: 320,
        });
    }
}
//# sourceMappingURL=videostream.js.map