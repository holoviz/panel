import { Enum } from "@bokehjs/core/kinds";
import { div, empty, span } from "@bokehjs/core/dom";
import { Widget, WidgetView } from "@bokehjs/models/widgets/widget";
import { to_string } from "@bokehjs/core/util/pretty";
const SVG_STRINGS = {
    slower: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-minus" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M5 12l14 0" /></svg>',
    first: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-track-prev-filled" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M20.341 4.247l-8 7a1 1 0 0 0 0 1.506l8 7c.647 .565 1.659 .106 1.659 -.753v-14c0 -.86 -1.012 -1.318 -1.659 -.753z" stroke-width="0" fill="currentColor" /><path d="M9.341 4.247l-8 7a1 1 0 0 0 0 1.506l8 7c.647 .565 1.659 .106 1.659 -.753v-14c0 -.86 -1.012 -1.318 -1.659 -.753z" stroke-width="0" fill="currentColor" /></svg>',
    previous: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-skip-back-filled" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M19.496 4.136l-12 7a1 1 0 0 0 0 1.728l12 7a1 1 0 0 0 1.504 -.864v-14a1 1 0 0 0 -1.504 -.864z" stroke-width="0" fill="currentColor" /><path d="M4 4a1 1 0 0 1 .993 .883l.007 .117v14a1 1 0 0 1 -1.993 .117l-.007 -.117v-14a1 1 0 0 1 1 -1z" stroke-width="0" fill="currentColor" /></svg>',
    reverse: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-play-filled" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" style="transform: scaleX(-1);"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M6 4v16a1 1 0 0 0 1.524 .852l13 -8a1 1 0 0 0 0 -1.704l-13 -8a1 1 0 0 0 -1.524 .852z" stroke-width="0" fill="currentColor" /></svg>',
    pause: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-pause-filled" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 4h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h2a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2z" stroke-width="0" fill="currentColor" /><path d="M17 4h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h2a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2z" stroke-width="0" fill="currentColor" /></svg>',
    play: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-play-filled" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M6 4v16a1 1 0 0 0 1.524 .852l13 -8a1 1 0 0 0 0 -1.704l-13 -8a1 1 0 0 0 -1.524 .852z" stroke-width="0" fill="currentColor" /></svg>',
    next: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-skip-forward-filled" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M3 5v14a1 1 0 0 0 1.504 .864l12 -7a1 1 0 0 0 0 -1.728l-12 -7a1 1 0 0 0 -1.504 .864z" stroke-width="0" fill="currentColor" /><path d="M20 4a1 1 0 0 1 .993 .883l.007 .117v14a1 1 0 0 1 -1.993 .117l-.007 -.117v-14a1 1 0 0 1 1 -1z" stroke-width="0" fill="currentColor" /></svg>',
    last: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-track-next-filled" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M2 5v14c0 .86 1.012 1.318 1.659 .753l8 -7a1 1 0 0 0 0 -1.506l-8 -7c-.647 -.565 -1.659 -.106 -1.659 .753z" stroke-width="0" fill="currentColor" /><path d="M13 5v14c0 .86 1.012 1.318 1.659 .753l8 -7a1 1 0 0 0 0 -1.506l-8 -7c-.647 -.565 -1.659 -.106 -1.659 .753z" stroke-width="0" fill="currentColor" /></svg>',
    faster: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-plus" width="12" height="12" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 5l0 14" /><path d="M5 12l14 0" /></svg>',
};
function press(btn_list) {
    btn_list.forEach((btn) => btn.style.borderStyle = "inset");
}
function unpress(btn_list) {
    btn_list.forEach((btn) => btn.style.borderStyle = "outset");
}
export class PlayerView extends WidgetView {
    static __name__ = "PlayerView";
    buttonEl;
    titleEl;
    groupEl;
    sliderEl;
    loop_state;
    timer;
    _toggle_reverse;
    _toogle_pause;
    _toggle_play;
    _changing = false;
    slower;
    first;
    previous;
    reverse;
    pause;
    play;
    next;
    last;
    faster;
    connect_signals() {
        super.connect_signals();
        const { title, value_align, direction, value, loop_policy, disabled, show_loop_controls, show_value, scale_buttons, visible_buttons, visible_loop_options } = this.model.properties;
        this.on_change(title, () => this.update_title_and_value());
        this.on_change(value_align, () => this.set_value_align());
        this.on_change(direction, () => this.set_direction());
        this.on_change(value, () => this.render());
        this.on_change(loop_policy, () => this.set_loop_state(this.model.loop_policy));
        this.on_change(disabled, () => this.toggle_disable());
        this.on_change(show_loop_controls, () => {
            if (this.model.show_loop_controls && this.loop_state.parentNode != this.groupEl) {
                this.groupEl.appendChild(this.loop_state);
            }
            else if (!this.model.show_loop_controls && this.loop_state.parentNode == this.groupEl) {
                this.groupEl.removeChild(this.loop_state);
            }
        });
        this.on_change(show_value, () => this.update_title_and_value());
        this.on_change(scale_buttons, () => this.update_css());
        this.on_change(visible_buttons, () => this.update_css());
        this.on_change(visible_loop_options, () => this.update_css());
    }
    toggle_disable() {
        this.sliderEl.disabled = this.model.disabled;
        for (const el of this.buttonEl.children) {
            const anyEl = el;
            anyEl.disabled = this.model.disabled;
        }
        for (const el of this.loop_state.children) {
            if (el.tagName == "input") {
                const anyEl = el;
                anyEl.disabled = this.model.disabled;
            }
        }
    }
    get_height() {
        return 250;
    }
    update_css() {
        const button_style_small = `text-align: center; flex-grow: 1; margin: 2px; transform: scale(${this.model.scale_buttons}); max-width: 50px;`;
        const button_style = `text-align: center; flex-grow: 2; margin: 2px; transform: scale(${this.model.scale_buttons}); max-width: 50px;`;
        const buttons = {
            slower: this.slower,
            first: this.first,
            previous: this.previous,
            reverse: this.reverse,
            pause: this.pause,
            play: this.play,
            next: this.next,
            last: this.last,
            faster: this.faster,
        };
        for (const [name, button] of Object.entries(buttons)) {
            if (button) {
                if (this.model.visible_buttons.includes(name)) {
                    button.style.display = ""; // Reset to default display
                    if (name === "slower" || name === "faster") {
                        button.style.cssText += button_style_small;
                    }
                    else {
                        button.style.cssText += button_style;
                    }
                }
                else {
                    button.style.display = "none"; // Hide the button completely
                }
            }
        }
        for (const el of this.loop_state.children) {
            if (el.tagName.toLowerCase() == "input") {
                const anyEl = el;
                if (this.model.visible_loop_options.includes(anyEl.value)) {
                    anyEl.style.display = "";
                }
                else {
                    anyEl.style.display = "none";
                }
            }
            else if (el.tagName.toLowerCase() == "label") {
                const anyEl = el;
                if (this.model.visible_loop_options.includes(anyEl.innerHTML.toLowerCase())) {
                    anyEl.style.display = "";
                }
                else {
                    anyEl.style.display = "none";
                }
            }
        }
    }
    render() {
        if (this.sliderEl == null) {
            super.render();
        }
        else {
            this.sliderEl.min = String(this.model.start);
            this.sliderEl.max = String(this.model.end);
            this.sliderEl.value = String(this.model.value);
            return;
        }
        // Layout to group the elements
        this.groupEl = div();
        this.groupEl.style.display = "flex";
        this.groupEl.style.flexDirection = "column";
        // Display Value
        this.titleEl = div();
        this.titleEl.classList.add("pn-player-title");
        this.titleEl.style.padding = "0 5px 0 5px";
        this.update_title_and_value();
        this.set_value_align();
        // Slider
        this.sliderEl = document.createElement("input");
        this.sliderEl.style.width = "100%";
        this.sliderEl.setAttribute("type", "range");
        this.sliderEl.value = String(this.model.value);
        this.sliderEl.min = String(this.model.start);
        this.sliderEl.max = String(this.model.end);
        this.sliderEl.addEventListener("input", (ev) => {
            this.set_frame(parseInt(ev.target.value), false);
        });
        this.sliderEl.addEventListener("change", (ev) => {
            this.set_frame(parseInt(ev.target.value));
        });
        // Buttons
        const button_div = div();
        this.buttonEl = button_div;
        button_div.style.cssText = "margin: 0 auto; display: flex; padding: 5px; align-items: stretch; justify-content: center; width: 100%;";
        this.slower = document.createElement("button");
        this.slower.classList.add("slower");
        this.slower.innerHTML = SVG_STRINGS.slower;
        this.slower.onclick = () => this.slower_speed();
        button_div.appendChild(this.slower);
        this.first = document.createElement("button");
        this.first.classList.add("first");
        this.first.innerHTML = SVG_STRINGS.first;
        this.first.onclick = () => this.first_frame();
        button_div.appendChild(this.first);
        this.previous = document.createElement("button");
        this.previous.classList.add("previous");
        this.previous.innerHTML = SVG_STRINGS.previous;
        this.previous.onclick = () => this.previous_frame();
        button_div.appendChild(this.previous);
        this.reverse = document.createElement("button");
        this.reverse.classList.add("reverse");
        this.reverse.innerHTML = SVG_STRINGS.reverse;
        this.reverse.onclick = () => this.reverse_animation();
        button_div.appendChild(this.reverse);
        this.pause = document.createElement("button");
        this.pause.classList.add("pause");
        this.pause.innerHTML = SVG_STRINGS.pause;
        this.pause.onclick = () => this.pause_animation();
        button_div.appendChild(this.pause);
        this.play = document.createElement("button");
        this.play.classList.add("play");
        this.play.innerHTML = SVG_STRINGS.play;
        this.play.onclick = () => this.play_animation();
        button_div.appendChild(this.play);
        this.next = document.createElement("button");
        this.next.classList.add("next");
        this.next.innerHTML = SVG_STRINGS.next;
        this.next.onclick = () => this.next_frame();
        button_div.appendChild(this.next);
        this.last = document.createElement("button");
        this.last.classList.add("last");
        this.last.innerHTML = SVG_STRINGS.last;
        this.last.onclick = () => this.last_frame();
        button_div.appendChild(this.last);
        this.faster = document.createElement("button");
        this.faster.classList.add("faster");
        this.faster.innerHTML = SVG_STRINGS.faster;
        this.faster.onclick = () => this.faster_speed();
        button_div.appendChild(this.faster);
        // toggle
        this._toggle_reverse = () => {
            unpress([this.pause, this.play]);
            press([this.reverse]);
        };
        this._toogle_pause = () => {
            unpress([this.reverse, this.play]);
            press([this.pause]);
        };
        this._toggle_play = () => {
            unpress([this.reverse, this.pause]);
            press([this.play]);
        };
        // Loop control
        this.loop_state = document.createElement("form");
        this.loop_state.style.cssText = "margin: 0 auto; display: table";
        const once = document.createElement("input");
        once.classList.add("once");
        once.type = "radio";
        once.value = "once";
        once.name = "state";
        const once_label = document.createElement("label");
        once_label.innerHTML = "Once";
        once_label.classList.add("once-label");
        once_label.style.cssText = "padding: 0 10px 0 5px; user-select:none;";
        const loop = document.createElement("input");
        loop.classList.add("loop");
        loop.setAttribute("type", "radio");
        loop.setAttribute("value", "loop");
        loop.setAttribute("name", "state");
        const loop_label = document.createElement("label");
        loop_label.classList.add("loop-label");
        loop_label.innerHTML = "Loop";
        loop_label.style.cssText = "padding: 0 10px 0 5px; user-select:none;";
        const reflect = document.createElement("input");
        reflect.classList.add("reflect");
        reflect.setAttribute("type", "radio");
        reflect.setAttribute("value", "reflect");
        reflect.setAttribute("name", "state");
        const reflect_label = document.createElement("label");
        loop_label.classList.add("reflect-label");
        reflect_label.innerHTML = "Reflect";
        reflect_label.style.cssText = "padding: 0 10px 0 5px; user-select:none;";
        if (this.model.loop_policy == "once") {
            once.checked = true;
        }
        else if (this.model.loop_policy == "loop") {
            loop.checked = true;
        }
        else {
            reflect.checked = true;
        }
        // Compose everything
        this.loop_state.appendChild(once);
        this.loop_state.appendChild(once_label);
        this.loop_state.appendChild(loop);
        this.loop_state.appendChild(loop_label);
        this.loop_state.appendChild(reflect);
        this.loop_state.appendChild(reflect_label);
        this.groupEl.appendChild(this.titleEl);
        this.groupEl.appendChild(this.sliderEl);
        this.groupEl.appendChild(button_div);
        if (this.model.show_loop_controls) {
            this.groupEl.appendChild(this.loop_state);
        }
        this.toggle_disable();
        this.update_css();
        this.shadow_el.appendChild(this.groupEl);
    }
    set_frame(frame, throttled = true) {
        this.model.value = frame;
        this.update_title_and_value();
        if (throttled) {
            this.model.value_throttled = frame;
        }
        if (this.sliderEl.value != String(frame)) {
            this.sliderEl.value = String(frame);
        }
    }
    get_loop_state() {
        const button_group = this.loop_state.state;
        for (let i = 0; i < button_group.length; i++) {
            const button = button_group[i];
            if (button.checked) {
                return button.value;
            }
        }
        return "once";
    }
    update_title_and_value() {
        empty(this.titleEl);
        const hide_header = this.model.title == null || (this.model.title.length == 0 && !this.model.show_value);
        this.titleEl.style.display = hide_header ? "none" : "";
        if (!hide_header) {
            this.titleEl.style.visibility = "visible";
            const { title } = this.model;
            if (title != null && title.length > 0) {
                if (this.contains_tex_string(title)) {
                    this.titleEl.innerHTML = `${this.process_tex(title)}`;
                    if (this.model.show_value) {
                        this.titleEl.innerHTML += ": ";
                    }
                }
                else {
                    this.titleEl.textContent = `${title}`;
                    if (this.model.show_value) {
                        this.titleEl.textContent += ": ";
                    }
                }
            }
            if (this.model.show_value) {
                this.append_value_to_title_el();
            }
        }
        else {
            this.titleEl.style.visibility = "hidden";
        }
    }
    append_value_to_title_el() {
        this.titleEl.appendChild(span({ class: "pn-player-value" }, to_string(this.model.value)));
    }
    set_value_align() {
        switch (this.model.value_align) {
            case "start":
                this.titleEl.style.textAlign = "left";
                break;
            case "center":
                this.titleEl.style.textAlign = "center";
                break;
            case "end":
                this.titleEl.style.textAlign = "right";
                break;
        }
    }
    set_loop_state(state) {
        const button_group = this.loop_state.state;
        for (let i = 0; i < button_group.length; i++) {
            const button = button_group[i];
            if (button.value == state) {
                button.checked = true;
            }
        }
    }
    next_frame() {
        this.set_frame(Math.min(this.model.end, this.model.value + this.model.step));
    }
    previous_frame() {
        this.set_frame(Math.max(this.model.start, this.model.value - this.model.step));
    }
    first_frame() {
        this.set_frame(this.model.start);
    }
    last_frame() {
        this.set_frame(this.model.end);
    }
    updateSpeedButton(button, interval, originalSVG) {
        const fps = 1000 / interval;
        button.innerHTML = `${fps.toFixed(1)}<br>fps`;
        setTimeout(() => {
            button.innerHTML = originalSVG;
        }, this.model.preview_duration); // Show for 1.5 seconds
    }
    slower_speed() {
        this.model.interval = Math.round(this.model.interval / 0.7);
        this.updateSpeedButton(this.slower, this.model.interval, SVG_STRINGS.slower);
        if (this.model.direction > 0) {
            this.play_animation();
        }
        else if (this.model.direction < 0) {
            this.reverse_animation();
        }
    }
    faster_speed() {
        this.model.interval = Math.round(this.model.interval * 0.7);
        this.updateSpeedButton(this.faster, this.model.interval, SVG_STRINGS.faster);
        if (this.model.direction > 0) {
            this.play_animation();
        }
        else if (this.model.direction < 0) {
            this.reverse_animation();
        }
    }
    anim_step_forward() {
        if (this.model.value < this.model.end) {
            this.next_frame();
        }
        else {
            const loop_state = this.get_loop_state();
            if (loop_state == "loop") {
                this.first_frame();
            }
            else if (loop_state == "reflect") {
                this.last_frame();
                this.reverse_animation();
            }
            else {
                this.pause_animation();
                this.last_frame();
            }
        }
    }
    anim_step_reverse() {
        if (this.model.value > this.model.start) {
            this.previous_frame();
        }
        else {
            const loop_state = this.get_loop_state();
            if (loop_state == "loop") {
                this.last_frame();
            }
            else if (loop_state == "reflect") {
                this.first_frame();
                this.play_animation();
            }
            else {
                this.pause_animation();
                this.first_frame();
            }
        }
    }
    set_direction() {
        if (this._changing) {
            return;
        }
        else if (this.model.direction === 0) {
            this.pause_animation();
        }
        else if (this.model.direction === 1) {
            this.play_animation();
        }
        else if (this.model.direction === -1) {
            this.reverse_animation();
        }
    }
    pause_animation() {
        this._toogle_pause();
        this._changing = true;
        this.model.direction = 0;
        this._changing = false;
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
    play_animation() {
        this.pause_animation();
        this._toggle_play();
        this._changing = true;
        this.model.direction = 1;
        this._changing = false;
        if (!this.timer) {
            this.timer = setInterval(() => this.anim_step_forward(), this.model.interval);
        }
    }
    reverse_animation() {
        this.pause_animation();
        this._toggle_reverse();
        this._changing = true;
        this.model.direction = -1;
        this._changing = false;
        if (!this.timer) {
            this.timer = setInterval(() => this.anim_step_reverse(), this.model.interval);
        }
    }
}
export const LoopPolicy = Enum("once", "loop", "reflect");
export class Player extends Widget {
    static __name__ = "Player";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = PlayerView;
        this.define(({ Bool, Int, Float, List, Str }) => ({
            direction: [Int, 0],
            interval: [Int, 500],
            start: [Int, 0],
            end: [Int, 10],
            step: [Int, 1],
            loop_policy: [LoopPolicy, "once"],
            title: [Str, ""],
            value: [Int, 0],
            value_align: [Str, "start"],
            value_throttled: [Int, 0],
            preview_duration: [Int, 1500],
            show_loop_controls: [Bool, true],
            show_value: [Bool, true],
            button_scale: [Float, 1],
            scale_buttons: [Float, 1],
            visible_buttons: [List(Str), ["slower", "first", "previous", "reverse", "pause", "play", "next", "last", "faster"]],
            visible_loop_options: [List(Str), ["once", "loop", "reflect"]],
        }));
        this.override({ width: 400 });
    }
}
//# sourceMappingURL=player.js.map