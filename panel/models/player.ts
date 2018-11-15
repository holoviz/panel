import * as p from "core/properties"
import {div} from "core/dom"
import {Widget, WidgetView} from "models/widgets/widget"

export class PlayerView extends WidgetView {
  model: Player

  protected sliderEl: HTMLElement
  protected loop_state: HTMLElement
  protected timer: any

  initialize(options: any): void {
    super.initialize(options)
    this.render()
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.change, () => this.render())
    this.connect(this.model.properties.value.change, () => this.render())
    this.connect(this.model.properties.loop_policy.change, () => this.set_loop_state(this.model.loop_policy))
  }

  get_height(): number {
    return 250
  }

  render(): void {
    if (this.sliderEl == null) {
      super.render()
    } else {
      this.sliderEl.style = `width:{this.model.width}px`
      this.sliderEl.min = this.model.start;
      this.sliderEl.max = this.model.end;
      this.sliderEl.value = this.model.value;
      return
    }

    // Slider
    this.sliderEl = document.createElement('input')
    this.sliderEl.setAttribute("type", "range");
    this.sliderEl.style = `width:{this.model.width}px`
    this.sliderEl.value = this.model.value;
    this.sliderEl.min = this.model.start;
    this.sliderEl.max = this.model.end;
    this.sliderEl.onchange = (ev) => this.set_frame(parseInt(ev.target.value))

    // Buttons
    const button_div = div() as any;
    button_div.style = "margin: 0 auto; display: table; padding: 5px"
    const button_style = "text-align: center; min-width: 40px";

    const slower = document.createElement('button')
    slower.style = "text-align: center; min-width: 20px"
    slower.appendChild(document.createTextNode('–'))
    slower.onclick = () => this.slower()
    button_div.appendChild(slower)

    const first = document.createElement('button')
    first.style = button_style
    first.appendChild(document.createTextNode('❚◀◀'))
    first.onclick = () => this.first_frame()
    button_div.appendChild(first)

    const previous = document.createElement('button')
    previous.style = button_style
    previous.appendChild(document.createTextNode('❚◀'))
    previous.onclick = () => this.previous_frame()
    button_div.appendChild(previous)

    const reverse = document.createElement('button')
    reverse.style = button_style
    reverse.appendChild(document.createTextNode('◀'))
    reverse.onclick = () => this.reverse_animation()
    button_div.appendChild(reverse)

    const pause = document.createElement('button')
    pause.style = button_style
    pause.appendChild(document.createTextNode('❚❚'))
    pause.onclick = () => this.pause_animation()
    button_div.appendChild(pause)

    const play = document.createElement('button')
    play.style = button_style
    play.appendChild(document.createTextNode('▶'))
    play.onclick = () => this.play_animation()
    button_div.appendChild(play)

    const next = document.createElement('button')
    next.style = button_style
    next.appendChild(document.createTextNode('▶❚'))
    next.onclick = () => this.next_frame()
    button_div.appendChild(next)

    const last = document.createElement('button')
    last.style = button_style
    last.appendChild(document.createTextNode('▶▶❚'))
    last.onclick = () => this.last_frame()
    button_div.appendChild(last)

    const faster = document.createElement('button')
    faster.style = "text-align: center; min-width: 20px"
    faster.appendChild(document.createTextNode('+'))
    faster.onclick = () => this.faster()
    button_div.appendChild(faster)

    // Loop control
    this.loop_state = document.createElement('form')
    this.loop_state.style = "margin: 0 auto; display: table"

    const once = document.createElement('input')
    once.type = "radio";
    once.value = "once";
    once.name = "state";
    const once_label = document.createElement('label');
    once_label.innerHTML = "Once"
    once_label.style = "padding: 0 10px 0 5px; user-select:none;"

    const loop = document.createElement('input')
    loop.setAttribute("type", "radio");
    loop.setAttribute("value", "loop");
    loop.setAttribute("name", "state");
    const loop_label = document.createElement('label');
    loop_label.innerHTML = "Loop"
    loop_label.style = "padding: 0 10px 0 5px; user-select:none;"

    const reflect = document.createElement('input')
    reflect.setAttribute("type", "radio");
    reflect.setAttribute("value", "reflect");
    reflect.setAttribute("name", "state");
    const reflect_label = document.createElement('label');
    reflect_label.innerHTML = "Reflect"
    reflect_label.style = "padding: 0 10px 0 5px; user-select:none;"

    if (this.model.loop_policy == "once")
      once.checked = true
    else if (this.model.loop_policy == "loop")
      loop.checked = true
    else
      reflect.checked = true

    // Compose everything
    this.loop_state.appendChild(once)
    this.loop_state.appendChild(once_label)
    this.loop_state.appendChild(loop)
    this.loop_state.appendChild(loop_label)
    this.loop_state.appendChild(reflect)
    this.loop_state.appendChild(reflect_label)

    this.el.appendChild(this.sliderEl)
    this.el.appendChild(button_div)
    this.el.appendChild(this.loop_state)
  }

  set_frame(frame: number): void {
    if (this.model.value != frame)
      this.model.value = frame;
    if (this.sliderEl.value != frame)
      this.sliderEl.value = frame;
  }

  get_loop_state(): void {
    var button_group = this.loop_state.state;
    for (var i = 0; i < button_group.length; i++) {
      var button = button_group[i];
      if (button.checked)
        return button.value;
    }
  }

  set_loop_state(state: string): void {
    var button_group = this.loop_state.state;
    for (var i = 0; i < button_group.length; i++) {
      var button = button_group[i];
      if (button.value == state)
        button.checked = true
    }
  }

  next_frame(): void {
    this.set_frame(Math.min(this.model.end, this.model.value + this.model.step));
  }

  previous_frame(): void {
    this.set_frame(Math.max(this.model.start, this.model.value - this.model.step));
  }

  first_frame(): void {
    this.set_frame(this.model.start);
  }

  last_frame(): void {
    this.set_frame(this.model.end);
  }

  slower(): void {
    this.model.interval = Math.round(this.model.interval/0.7);
    if (this.model.direction > 0)
      this.play_animation()
    else if (this.direction < 0)
      this.reverse_animation()
  }

  faster(): void {
    this.model.interval = Math.round(this.model.interval * 0.7);
    if (this.model.direction > 0)
      this.play_animation()
    else if(this.model.direction < 0)
      this.reverse_animation()
  }

  anim_step_forward(): void {
    if(this.model.value < this.model.end){
      this.next_frame();
    } else {
      var loop_state = this.get_loop_state();
      if(loop_state == "loop"){
        this.first_frame();
      }else if(loop_state == "reflect"){
        this.last_frame();
        this.reverse_animation();
      }else{
        this.pause_animation();
        this.last_frame();
      }
    }
  }

  anim_step_reverse(): void {
    if(this.model.value > this.model.start){
      this.previous_frame();
    } else {
      var loop_state = this.get_loop_state();
      if(loop_state == "loop"){
        this.last_frame();
      }else if(loop_state == "reflect"){
        this.first_frame();
        this.play_animation();
      }else{
        this.pause_animation();
        this.first_frame();
      }
    }
  }

  pause_animation(): void {
    this.direction = 0;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  play_animation(): void {
    this.pause_animation();
    this.model.direction = 1;
    if (!this.timer)
      this.timer = setInterval(() => this.anim_step_forward(), this.model.interval);
  }

  reverse_animation(): void {
    this.pause_animation();
    this.model.direction = -1;
    if (!this.timer)
      this.timer = setInterval(() => this.anim_step_reverse(), this.model.interval);
  }
}

export namespace Player {
  export interface Attrs extends Widget.Attrs {}
  export interface Props extends Widget.Props {}
}

export interface Player extends Player.Attrs {}

export abstract class Player extends Widget {

  properties: Player.Props

  constructor(attrs?: Partial<Player.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "Player"
    this.prototype.default_view = PlayerView

    this.define({
      direction:         [ p.Number,      0            ],
      interval:          [ p.Number,      500          ],
      start:             [ p.Number,                   ],
      end:               [ p.Number,                   ],
      step:              [ p.Number,      1            ],
      loop_policy:       [ p.Any,         "once"       ],
      value:             [ p.Any,         0            ],
    })

    this.override({width: 350})
  }
}

Player.initClass()
