import * as p from "core/properties"
import {clone} from "core/util/object";
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box";
import {div} from "core/dom";

export class VTKPlotView extends HTMLBoxView {
  model: VTKPlot
  protected _vtk: any
  protected _container: HTMLDivElement
  protected _rendererEl: any
  protected _renderer: any
  protected _camera: any
  protected _interactor: any
  protected _setting: boolean = false

  initialize(): void {
    super.initialize()
    this._vtk = (window as any).vtk
    this._container = div({
      style: {
        width: "100%",
        height: "100%"
      }
    });
  }

  after_layout(): void {
    super.after_layout()
    if (!this._rendererEl) {
      this._rendererEl = this._vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
        rootContainer: this.el,
        container: this._container
      });
      this._renderer = this._rendererEl.getRenderer()
      this._interactor = this._rendererEl.getInteractor()
      this._camera = this._renderer.getActiveCamera()
      this._plot()
      this._camera.onModified(() => this._get_camera_state())
      this._key_binding()
    }
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => this._plot())
    this.connect(this.model.properties.camera.change, () => this._set_camera_state())
    this.connect(this.model.properties.enable_keybindings.change, () => this._key_binding())
  }

  _key_binding(): void {
    if (this.model.enable_keybindings) {
      document.querySelector('body')!.addEventListener('keypress',this._interactor.handleKeyPress)
      document.querySelector('body')!.addEventListener('keydown',this._interactor.handleKeyDown)
      document.querySelector('body')!.addEventListener('keyup',this._interactor.handleKeyUp)
    } else {
      document.querySelector('body')!.removeEventListener('keypress',this._interactor.handleKeyPress)
      document.querySelector('body')!.removeEventListener('keydown',this._interactor.handleKeyDown)
      document.querySelector('body')!.removeEventListener('keyup',this._interactor.handleKeyUp)
    }
  }

  render() {
    super.render()
    if (!(this._container === this.el.childNodes[0]))
      this.el.appendChild(this._container)
  }

  _get_camera_state(): void {
    if (!this._setting) {
      this._setting = true;
      const state = clone(this._camera.get());
      delete state.classHierarchy;
      delete state.vtkObject;
      delete state.vtkCamera;
      delete state.viewPlaneNormal;
      this.model.camera = state;
      this._setting = false;
    }
  }

  _set_camera_state(): void {
    if (!this._setting) {
      this._setting = true;
      try {
        this._camera.set(this.model.camera);
      } finally {
        this._setting = false;
      }
      this._rendererEl.getRenderWindow().render();
    }
  }

  _plot(): void{
    if (!this.model.append) {
      this._delete_all_actors()
    }
    if (!this.model.data) {
      this._rendererEl.getRenderWindow().render()
      return
    }
    const dataAccessHelper = this._vtk.IO.Core.DataAccessHelper.get('zip', {
      zipContent: atob(this.model.data),
      callback: (_zip: any) => {
        const sceneImporter = this._vtk.IO.Core.vtkHttpSceneLoader.newInstance({
          renderer: this._rendererEl.getRenderer(),
          dataAccessHelper,
        })
        const fn = this._vtk.macro.debounce(() => setTimeout(
          this._rendererEl.getRenderWindow().render,
           100), 100)
        sceneImporter.setUrl('index.json')
        sceneImporter.onReady(fn)
      }
    })
  }

  _delete_all_actors(): void{
    this._renderer.getActors().map((actor: unknown) => this._renderer.removeActor(actor))
  }
}


export namespace VTKPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<string>
    append: p.Property<boolean>
    camera: p.Property<any>
    enable_keybindings: p.Property<boolean>
  }
}

export interface VTKPlot extends VTKPlot.Attrs {}

export class VTKPlot extends HTMLBox {
  properties: VTKPlot.Props

  constructor(attrs?: Partial<VTKPlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "VTKPlot"
    this.prototype.default_view = VTKPlotView

    this.define<VTKPlot.Props>({
      data:               [ p.String         ],
      append:             [ p.Boolean, false ],
      camera:             [ p.Any            ],
      enable_keybindings: [ p.Boolean, false ]
    })

    this.override({
      height: 300,
      width: 300
    });
  }
}
VTKPlot.initClass()
