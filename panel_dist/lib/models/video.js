import { px } from "@bokehjs/core/dom";
import { HTMLBox, HTMLBoxView } from "./layout";
import video_css from "../styles/models/video.css";
export class VideoView extends HTMLBoxView {
    static __name__ = "VideoView";
    video_el;
    _time;
    _blocked = false;
    _setting = false;
    initialize() {
        super.initialize();
        this._time = Date.now();
    }
    connect_signals() {
        super.connect_signals();
        const { loop, paused, muted, autoplay, time, value, volume } = this.model.properties;
        this.on_change(loop, () => this.set_loop());
        this.on_change(paused, () => this.set_paused());
        this.on_change(muted, () => this.set_muted());
        this.on_change(autoplay, () => this.set_autoplay());
        this.on_change(time, () => this.set_time());
        this.on_change(value, () => this.set_value());
        this.on_change(volume, () => this.set_volume());
    }
    stylesheets() {
        return [...super.stylesheets(), video_css];
    }
    render() {
        super.render();
        this.video_el = document.createElement("video");
        const container_el = document.createElement("div");
        container_el.className = "pn-video-container";
        container_el.style.height = "100%";
        container_el.style.width = "100%";
        const { sizing_mode } = this.model;
        if (sizing_mode == null || sizing_mode === "fixed") {
            const { width, height } = this.model;
            if (width != null) {
                this.video_el.width = width;
            }
            if (height != null) {
                this.video_el.height = height;
            }
        }
        const { max_width, max_height } = this.model;
        if (max_width != null) {
            this.video_el.style.maxWidth = px(max_width);
        }
        if (max_height != null) {
            this.video_el.style.maxHeight = px(max_height);
        }
        this.video_el.controls = true;
        this.video_el.src = this.model.value;
        this.video_el.currentTime = this.model.time;
        this.video_el.loop = this.model.loop;
        this.video_el.muted = this.model.muted;
        this.video_el.autoplay = this.model.autoplay;
        if (this.model.volume != null) {
            this.video_el.volume = this.model.volume / 100;
        }
        else {
            this.model.volume = this.video_el.volume * 100;
        }
        this.video_el.onpause = () => this.model.paused = true;
        this.video_el.onplay = () => this.model.paused = false;
        this.video_el.ontimeupdate = () => this.update_time();
        this.video_el.onvolumechange = () => this.update_volume();
        container_el.append(this.video_el);
        this.shadow_el.append(container_el);
        if (!this.model.paused) {
            void this.video_el.play();
        }
    }
    update_time() {
        if (this._setting) {
            this._setting = false;
            return;
        }
        if ((Date.now() - this._time) < this.model.throttle) {
            return;
        }
        this._blocked = true;
        this.model.time = this.video_el.currentTime;
        this._time = Date.now();
    }
    update_volume() {
        if (this._setting) {
            this._setting = false;
            return;
        }
        this._blocked = true;
        this.model.volume = this.video_el.volume * 100;
    }
    set_loop() {
        this.video_el.loop = this.model.loop;
    }
    set_muted() {
        this.video_el.muted = this.model.muted;
    }
    set_autoplay() {
        this.video_el.autoplay = this.model.autoplay;
    }
    set_paused() {
        const { paused } = this.model;
        if (!this.video_el.paused && paused) {
            this.video_el.pause();
        }
        if (this.video_el.paused && !paused) {
            void this.video_el.play();
        }
    }
    set_volume() {
        if (this._blocked) {
            this._blocked = false;
            return;
        }
        this._setting = true;
        const { volume } = this.model;
        if (volume != null) {
            this.video_el.volume = volume / 100;
        }
    }
    set_time() {
        if (this._blocked) {
            this._blocked = false;
            return;
        }
        this._setting = true;
        this.video_el.currentTime = this.model.time;
    }
    set_value() {
        this.video_el.src = this.model.value;
    }
}
export class Video extends HTMLBox {
    static __name__ = "Video";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = VideoView;
        this.define(({ Bool, Int, Float, Str, Nullable }) => ({
            loop: [Bool, false],
            paused: [Bool, true],
            muted: [Bool, false],
            autoplay: [Bool, false],
            time: [Float, 0],
            throttle: [Int, 250],
            value: [Str, ""],
            volume: [Nullable(Int), null],
        }));
    }
}
//# sourceMappingURL=video.js.map