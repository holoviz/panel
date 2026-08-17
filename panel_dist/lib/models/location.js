import { View } from "@bokehjs/core/view";
import { Model } from "@bokehjs/model";
export class LocationView extends View {
    static __name__ = "LocationView";
    _hash_listener;
    _idle_ready = false;
    _pending_url = null;
    _idle_connected = false;
    initialize() {
        super.initialize();
        this.model.pathname = window.location.pathname;
        this.model.search = window.location.search;
        this.model.hash = window.location.hash;
        // Readonly parameters on python side
        this.model.href = window.location.href;
        this.model.hostname = window.location.hostname;
        this.model.protocol = window.location.protocol;
        this.model.port = window.location.port;
        this._hash_listener = () => {
            this.model.hash = window.location.hash;
        };
        window.addEventListener("hashchange", this._hash_listener);
        this._has_finished = true;
        this.notify_finished();
    }
    connect_signals() {
        super.connect_signals();
        const { pathname, search, hash, reload } = this.model.properties;
        this.on_change(pathname, () => this.update("pathname"));
        this.on_change(search, () => this.update("search"));
        this.on_change(hash, () => this.update("hash"));
        this.on_change(reload, () => this.update("reload"));
    }
    remove() {
        super.remove();
        window.removeEventListener("hashchange", this._hash_listener);
    }
    _ensure_idle_gate() {
        if (this._idle_connected) {
            return;
        }
        this._idle_connected = true;
        const doc = this.model.document;
        if (doc.is_idle) {
            this._idle_ready = true;
            return;
        }
        doc.idle.connect(() => {
            this._idle_ready = true;
            if (this._pending_url != null) {
                const url = this._pending_url;
                this._pending_url = null;
                window.history.pushState({}, "", url);
                this.model.href = window.location.href;
            }
        });
    }
    _set_url_gated(url) {
        this._ensure_idle_gate();
        if (this._idle_ready) {
            window.history.pushState({}, "", url);
            this.model.href = window.location.href;
        }
        else {
            this._pending_url = url;
        }
    }
    update(change) {
        const url = `${this.model.pathname}${this.model.search}${this.model.hash}`;
        if (change === "reload") {
            window.history.pushState({}, "", url);
            this.model.href = window.location.href;
            window.location.reload();
            return;
        }
        if (!this.model.reload) {
            this._set_url_gated(url);
            return;
        }
        if (change === "hash") {
            window.location.hash = this.model.hash;
            return;
        }
        window.location.href = url;
    }
}
export class Location extends Model {
    static __name__ = "Location";
    static __module__ = "panel.models.location";
    constructor(attrs) {
        super(attrs);
    }
    static {
        this.prototype.default_view = LocationView;
        this.define(({ Bool, Str }) => ({
            href: [Str, ""],
            hostname: [Str, ""],
            pathname: [Str, ""],
            protocol: [Str, ""],
            port: [Str, ""],
            search: [Str, ""],
            hash: [Str, ""],
            reload: [Bool, false],
        }));
    }
}
//# sourceMappingURL=location.js.map