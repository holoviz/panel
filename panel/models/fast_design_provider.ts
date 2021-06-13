import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

import * as p from "@bokehjs/core/properties"

const win=<any>window;

export class FastDesignProviderView extends HTMLBoxView {
    model: FastDesignProvider
    provider: any;

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.model.properties.provider.change, () => {this.setProvider(), this.getProperties()})
        this.connect(this.model.properties.background_color.change, () => {this.setBackgroundColor();this.getProperties()})
        this.connect(this.model.properties.neutral_color.change, () => {this.setNeutralColor();this.getProperties()})
        this.connect(this.model.properties.accent_base_color.change, () => {this.setAccentColor();this.getProperties()})
        this.connect(this.model.properties.corner_radius.change, () => {this.provider.cornerRadius=this.model.corner_radius;})
    }

    render(): void {
        super.render()
        this.el.style.display = "hide"

        this.setProvider();
        this.setBackgroundColor();
        this.setAccentColor();
        this.setNeutralColor();
        this.getProperties();
    }
    setProvider(): void {
        this.provider = <HTMLElement>document.getElementById(this.model.provider);
    }
    setBackgroundColor(): void {
        if (this.model.background_color){
            win.fastDesignProvider.setBackgroundColor(this.model.background_color, "#" + this.model.provider)
        }
    }
    setAccentColor(): void {
        if (this.model.accent_base_color){
            win.fastDesignProvider.setAccentColor(this.model.accent_base_color, "#" + this.model.provider)
        }
    }
    setNeutralColor(): void {
        if (this.model.neutral_color){
            win.fastDesignProvider.setNeutralColor(this.model.neutral_color, "#" + this.model.provider)
        }
    }

    getProperties(): void {
        const model = this.model;
        const provider = <any>this.provider;
        if (provider===null){return}
        if (provider.backgroundColor && model.background_color!==provider.backgroundColor){
            model.background_color = provider.backgroundColor;
        }
        if (provider.accentBaseColor && model.accent_base_color!==provider.accentBaseColor){
            model.accent_base_color = provider.accentBaseColor
        }

        let palette = provider.accentPalette
        let index = palette.indexOf(this.provider.accentBaseColor.toUpperCase())

        if (provider.accentFillActiveDelta!==undefined){model.accent_fill_active = palette[index+provider.accentFillActiveDelta];}
        if (provider.accentFillHoverDelta!==undefined){model.accent_fill_hover = palette[index+provider.accentFillHoverDelta]}
        if (provider.accentFillRestDelta!==undefined){model.accent_fill_rest = palette[index+provider.accentFillRestDelta]}
        if (provider.accentForegroundActiveDelta!==undefined){model.accent_foreground_active = palette[index+provider.accentForegroundActiveDelta]}
        if (provider.accentForegroundCutDelta!==undefined){model.accent_foreground_cut_rest = palette[index+provider.accentForegroundCutDelta]}
        if (provider.accentForegroundHoverDelta!==undefined){model.accent_foreground_hover = palette[index+provider.accentForegroundHoverDelta]}
        if (provider.accentForegroundRestDelta!==undefined){model.accent_foreground_rest = palette[index+provider.accentForegroundRestDelta]}

        let value: string
        value=window.getComputedStyle(provider).getPropertyValue('--accent-foreground-cut-rest').trim()
        if (value!==""){model.accent_foreground_cut_rest = value}
        value=window.getComputedStyle(provider).getPropertyValue('--neutral-outline-active').trim()
        if (value!==""){model.neutral_outline_active = value}
        value=window.getComputedStyle(provider).getPropertyValue('--neutral-outline-hover').trim()
        if (value!==""){model.neutral_outline_hover = value}
        value=window.getComputedStyle(provider).getPropertyValue('--neutral-outline-rest').trim()
        if (value!==""){model.neutral_outline_rest = value}
        value= window.getComputedStyle(provider).getPropertyValue('--neutral-focus').trim()
        if (value!==""){model.neutral_focus = value}
        value=window.getComputedStyle(provider).getPropertyValue('--neutral-foreground-rest').trim()
        if (value!==""){model.neutral_foreground_rest = value}
        if (this.provider.cornerRadius!==undefined){
            this.model.corner_radius = this.provider.cornerRadius
        } else {
            this.model.corner_radius=3
        }
        this.model.updates +=1;
    }
}

export namespace FastDesignProvider {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        provider: p.Property<string>,

        background_color: p.Property<string>,
        neutral_color: p.Property<string>,
        accent_base_color: p.Property<string>,
        corner_radius: p.Property<number>,

        accent_fill_active: p.Property<string>,
        accent_fill_hover: p.Property<string>,
        accent_fill_rest: p.Property<string>,

        accent_foreground_active: p.Property<string>,
        accent_foreground_cut_rest: p.Property<string>,
        accent_foreground_hover: p.Property<string>,
        accent_foreground_rest: p.Property<string>,

        neutral_outline_active: p.Property<string>,
        neutral_outline_hover: p.Property<string>,
        neutral_outline_rest: p.Property<string>,

        neutral_focus: p.Property<string>,
        neutral_foreground_rest: p.Property<string>,

        updates: p.Property<number>,
    }
}

export interface FastDesignProvider extends FastDesignProvider.Attrs { }

// The Bokeh .ts model corresponding to the Bokeh .py model
export class FastDesignProvider extends HTMLBox {
    properties: FastDesignProvider.Props

    constructor(attrs?: Partial<FastDesignProvider.Attrs>) {
        super(attrs)
    }

    static __module__ = "panel.models.fast_design_provider"

    static init_FastDesignProvider(): void {
        this.prototype.default_view = FastDesignProviderView;

        this.define<FastDesignProvider.Props>({
            provider: [p.String, ],

            background_color: [p.String, ],
            neutral_color: [p.String, ],
            accent_base_color: [p.String, ],
            corner_radius: [p.Int, ],

            accent_fill_active: [p.String, ],
            accent_fill_hover: [p.String, ],
            accent_fill_rest: [p.String, ],

            accent_foreground_active: [p.String, ],
            accent_foreground_cut_rest: [p.String, ],
            accent_foreground_hover: [p.String, ],
            accent_foreground_rest: [p.String, ],

            neutral_outline_active: [p.String, ],
            neutral_outline_hover: [p.String, ],
            neutral_outline_rest: [p.String, ],

            neutral_focus: [p.String, ],
            neutral_foreground_rest: [p.String, ],
            updates: [p.Int, 0],

        })
    }
}