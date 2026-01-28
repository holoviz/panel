import { View } from "@bokehjs/core/view";
import { copy } from "@bokehjs/core/util/array";
import { Model } from "@bokehjs/model";
import { Receiver } from "@bokehjs/protocol/receiver";
function get_json(file, callback) {
    const xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open("GET", file, true);
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4 && xobj.status == 200) {
            callback(xobj.responseText);
        }
    };
    xobj.send(null);
}
export class StateView extends View {
    static __name__ = "StateView";
}
export class State extends Model {
    static __name__ = "State";
    _receiver;
    _cache;
    constructor(attrs) {
        super(attrs);
        this._receiver = new Receiver();
        this._cache = {};
    }
    apply_state(state) {
        this._receiver.consume(state.header);
        this._receiver.consume(state.metadata);
        this._receiver.consume(state.content);
        if (this._receiver.message && this.document) {
            this.document.apply_json_patch(this._receiver.message.content);
        }
    }
    _receive_json(result, path) {
        const state = JSON.parse(result);
        this._cache[path] = state;
        let current = this.state;
        for (const i of this.values) {
            if (current instanceof Map) {
                current = current.get(i);
            }
            else {
                current = current[i];
            }
        }
        if (current === path) {
            this.apply_state(state);
        }
        else if (this._cache[current]) {
            this.apply_state(this._cache[current]);
        }
    }
    set_state(widget, value) {
        const values = copy(this.values);
        const index = this.widgets[widget.id];
        values[index] = value;
        let state = this.state;
        for (const i of values) {
            if (state instanceof Map) {
                state = state.get(i);
            }
            else {
                state = state[i];
            }
        }
        this.values = values;
        if (this.json) {
            if (this._cache[state]) {
                this.apply_state(this._cache[state]);
            }
            else {
                get_json(state, (result) => this._receive_json(result, state));
            }
        }
        else {
            this.apply_state(state);
        }
    }
    static __module__ = "panel.models.state";
    static {
        this.prototype.default_view = StateView;
        this.define(({ Any, Bool }) => ({
            json: [Bool, false],
            state: [Any, {}],
            widgets: [Any, {}],
            values: [Any, []],
        }));
    }
}
//# sourceMappingURL=state.js.map