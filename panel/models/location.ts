import * as p from "@bokehjs/core/properties"
import { View } from "@bokehjs/core/view"
import { Model } from "@bokehjs/model"

export class LocationView extends View {
    model: Location
}

export namespace Location {
    export type Attrs = p.AttrsOf<Props>

    export type Props = Model.Props & {
        href: p.Property<string>
        hostname: p.Property<string>
        pathname: p.Property<string>
        protocol: p.Property<string>
        port: p.Property<number>
        search: p.Property<string>
        hash_: p.Property<string>
        refresh: p.Property<boolean>
    }
}



export interface Location extends Location.Attrs { }

export class Location extends Model {
    properties: Location.Props

    constructor(attrs?: Partial<Location.Attrs>) {
        super(attrs)
    }

    static __module__ = "panel.models.location"

    static init_Location(): void {
        this.prototype.default_view = LocationView

        this.define<Location.Props>({
            href: [p.String],
            hostname: [p.String],
            pathname: [p.String],
            protocol: [p.String],
            port: [p.Number],
            search: [p.String],
            hash_: [p.String],
            refresh: [p.Boolean],
        })
    }
}


