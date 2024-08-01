import type {IterViews} from "@bokehjs/core/build_views"
import {build_view} from "@bokehjs/core/build_views"
import {ButtonType} from "@bokehjs/core/enums"
import type * as p from "@bokehjs/core/properties"

import {InputWidget, InputWidgetView} from "@bokehjs/models/widgets/input_widget"
import type {IconView} from "@bokehjs/models/ui/icons/icon"
import {Icon} from "@bokehjs/models/ui/icons/icon"

import buttons_css, * as buttons from "@bokehjs/styles/buttons.css"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {nbsp, text, button, input} from "@bokehjs/core/dom"

function dataURItoBlob(dataURI: string) {
  // convert base64 to raw binary data held in a string

  const byteString = atob(dataURI.split(",")[1])

  // separate out the mime component
  const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0]

  // write the bytes of the string to an ArrayBuffer
  const ab = new ArrayBuffer(byteString.length)
  const ia = new Uint8Array(ab)
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i)
  }

  // write the ArrayBuffer to a blob, and you're done
  const bb = new Blob([ab], {type: mimeString})
  return bb
}

export class FileDownloadView extends InputWidgetView {
  declare model: FileDownload

  protected icon_view?: IconView

  anchor_el: HTMLAnchorElement
  button_el: HTMLButtonElement
  declare input_el: HTMLInputElement  // HACK: So this.input_el.id = "input" can be set in Bokeh 3.4
  _downloadable: boolean = false
  _click_listener: any
  _prev_href: string | null = ""
  _prev_download: string | null = ""

  override *children(): IterViews {
    yield* super.children()
    if (this.icon_view != null) {
      yield this.icon_view
    }
  }

  override *controls() {
    yield (this.anchor_el as any)
    yield (this.button_el as any)
  }

  override connect_signals(): void {
    super.connect_signals()

    const {button_type, filename, _transfers, label} = this.model.properties
    this.on_change(button_type, () => this._update_button_style())
    this.on_change(filename, () => this._update_download())
    this.on_change(_transfers, () => this._handle_click())
    this.on_change(label, () => this._update_label())
  }

  override remove(): void {
    if (this.icon_view != null) {
      this.icon_view.remove()
    }
    super.remove()
  }

  override async lazy_initialize(): Promise<void> {
    await super.lazy_initialize()
    const {icon} = this.model
    if (icon != null) {
      this.icon_view = await build_view(icon, {parent: this})
    }
  }

  _render_input(): HTMLElement {
    // Create an anchor HTML element that is styled as a bokeh button.
    // When its 'href' and 'download' attributes are set, it's a downloadable link:
    // * A click triggers a download
    // * A right click allows to "Save as" the file

    // There are three main cases:
    // 1. embed=True: The widget is a download link
    // 2. auto=False: The widget is first a button and becomes a download link after the first click
    // 3. auto=True: The widget is a button, i.e right click to "Save as..." won't work
    this.anchor_el = document.createElement("a")
    this.button_el = button({
      disabled: this.model.disabled,
    })
    if (this.icon_view != null) {
      const separator = this.model.label != "" ? nbsp() : text("")
      this.anchor_el.appendChild(this.icon_view.el)
      this.anchor_el.appendChild(separator)
      this.icon_view.render()
    }
    this._update_button_style()
    this._update_label()

    // Changing the disabled property calls render() so it needs to be handled here.
    // This callback is inherited from ControlView in bokehjs.
    if (this.model.disabled) {
      this.anchor_el.setAttribute("disabled", "")
      this._downloadable = false
    } else {
      this.anchor_el.removeAttribute("disabled")
      // auto=False + toggle Disabled ==> Needs to reset the link as it was.
      if (this._prev_download) {
        this.anchor_el.download = this._prev_download
      }
      if (this._prev_href) {
        this.anchor_el.href = this._prev_href
      }
      if (this.anchor_el.download && this.anchor_el.download) {
        this._downloadable = true
      }
    }

    // If embedded the button is just a download link.
    // Otherwise clicks will be handled by the code itself, allowing for more interactivity.
    if (this.model.embed) {
      this._make_link_downloadable()
    } else {
      // Add a "click" listener, note that it's not going to
      // handle right clicks (they won't increment 'clicks')
      this._click_listener = this._increment_clicks.bind(this)
      this.anchor_el.addEventListener("click", this._click_listener)
    }
    this.button_el.appendChild(this.anchor_el)
    this.input_el = input() // HACK: So this.input_el.id = "input" can be set in Bokeh 3.4
    return this.button_el
  }

  override render(): void {
    super.render()
    this.group_el.style.display = "flex"
    this.group_el.style.alignItems = "stretch"
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), buttons_css]
  }

  _increment_clicks(): void {
    this.model.clicks = this.model.clicks + 1
  }

  _handle_click(): void {
    // When auto=False the button becomes a link which no longer
    // requires being updated.
    if ((!this.model.auto && this._downloadable) || this.anchor_el.hasAttribute("disabled")) {
      return
    }

    this._make_link_downloadable()

    if (!this.model.embed && this.model.auto) {
      // Temporarily removing the event listener to emulate a click
      // event on the anchor link which will trigger a download.
      this.anchor_el.removeEventListener("click", this._click_listener)
      this.anchor_el.click()

      // In this case #3 the widget is not a link so these attributes are removed.
      this.anchor_el.removeAttribute("href")
      this.anchor_el.removeAttribute("download")

      this.anchor_el.addEventListener("click", this._click_listener)
    }

    // Store the current state for handling changes of the disabled property.
    this._prev_href = this.anchor_el.getAttribute("href")
    this._prev_download = this.anchor_el.getAttribute("download")
  }

  _make_link_downloadable(): void {
    this._update_href()
    this._update_download()
    if (this.anchor_el.download && this.anchor_el.href) {
      this._downloadable = true
    }
  }

  _update_href(): void {
    if (this.model.data) {
      const blob = dataURItoBlob(this.model.data)
      this.anchor_el.href = (URL as any).createObjectURL(blob)
    }
  }

  _update_download(): void {
    if (this.model.filename) {
      this.anchor_el.download = this.model.filename
    }
  }

  _update_label(): void {
    const label = document.createTextNode(this.model.label)
    this.anchor_el.appendChild(label)
  }

  _update_button_style(): void {
    const btn_type = buttons[`btn_${this.model.button_type}` as const]
    if (!this.button_el.hasAttribute("class")) { // When the widget is rendered.
      this.button_el.classList.add(buttons.btn)
      this.button_el.classList.add(btn_type)
    } else {  // When the button type is changed.
      const prev_button_type = this.anchor_el.classList.item(1)
      if (prev_button_type) {
        this.button_el.classList.replace(prev_button_type, btn_type)
      }
    }
  }
}

export namespace FileDownload {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InputWidget.Props & {
    auto: p.Property<boolean>
    button_type: p.Property<ButtonType>
    clicks: p.Property<number>
    data: p.Property<string | null>
    embed: p.Property<boolean>
    icon: p.Property<Icon | null>
    label: p.Property<string>
    filename: p.Property<string | null>
    _transfers: p.Property<number>
  }
}

export interface FileDownload extends FileDownload.Attrs {}

export class FileDownload extends InputWidget {
  declare properties: FileDownload.Props

  constructor(attrs?: Partial<FileDownload.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = FileDownloadView

    this.define<FileDownload.Props>(({Bool, Int, Nullable, Ref, Str}) => ({
      auto:         [ Bool,          false ],
      clicks:       [ Int,                  0 ],
      data:         [ Nullable(Str),  null ],
      embed:        [ Bool,          false ],
      icon:        [ Nullable(Ref(Icon)), null ],
      label:        [ Str,      "Download" ],
      filename:     [ Nullable(Str),  null ],
      button_type:  [ ButtonType,   "default" ], // TODO (bev)
      _transfers:   [ Int,                  0 ],
    }))

    this.override<FileDownload.Props>({
      title: "",
    })
  }
}
