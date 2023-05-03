import * as p from "@bokehjs/core/properties"
import {clone} from "@bokehjs/core/util/object"

import {debounce} from  "debounce"

import {AbstractVTKView, AbstractVTKPlot} from "./vtklayout"

import {initialize_fullscreen_render} from "./panel_fullscreen_renwin_sync"

import {vtkns} from "./util"

const CONTEXT_NAME = "panel"

export class VTKSynchronizedPlotView extends AbstractVTKView {
  model: VTKSynchronizedPlot
  protected _synchronizer_context: any
  protected _arrays: any
  public registerArray: CallableFunction

  initialize(): void {
    super.initialize()
    this._renderable = false

    // Context initialisation
    this._synchronizer_context = vtkns.SynchronizableRenderWindow.getSynchronizerContext(
      `${CONTEXT_NAME}-{this.model.id}`
    )
  }

  connect_signals(): void {
    super.connect_signals()
    const update = debounce(() => {
      this._vtk_renwin.delete()
      this._vtk_renwin = null
      this.invalidate_render()
    }, 20)
    this.connect(this.model.properties.arrays.change, update)
    this.connect(this.model.properties.scene.change, update)
    this.connect(this.model.properties.one_time_reset.change, () => {
      this._vtk_renwin.getRenderWindow().clearOneTimeUpdaters()
    })
  }

  init_vtk_renwin(): void {
    this._vtk_renwin = vtkns.FullScreenRenderWindowSynchronized.newInstance({
      rootContainer: this.el,
      container: this._vtk_container,
      synchronizerContext: this._synchronizer_context,
    })
  }

  override remove(): void {
    if (this._vtk_renwin) {
      this._vtk_renwin.delete()
    }
    super.remove()
  }

  plot(): void {
    this._vtk_renwin.getRenderWindow().clearOneTimeUpdaters()
    const state = clone(this.model.scene)
    this._sync_plot(state, () => this._on_scene_ready()).then(() => {
      this._set_camera_state()
      this._get_camera_state()
    })
  }

  _on_scene_ready(): void {
    this._renderable = true
    this._camera_callbacks.push(
      this._vtk_renwin
        .getRenderer()
        .getActiveCamera()
        .onModified(() => this._vtk_render())
    )
    if (!this._orientationWidget) this._create_orientation_widget()
    if (!this._axes) this._set_axes()
    this._vtk_renwin.resize()
    this._vtk_render()
  }

  _sync_plot(state: any, onSceneReady: CallableFunction): any {
    // Need to ensure all promises are resolved before calling this function
    this._renderable = false
    this._unsubscribe_camera_cb()
    this._synchronizer_context.setFetchArrayFunction((hash: string) => {
      return Promise.resolve(this.model.arrays[hash])
    })
    const renderer = this._synchronizer_context.getInstance(
      this.model.scene.dependencies[0].id
    )
    if (renderer && !this._vtk_renwin.getRenderer())
      this._vtk_renwin.getRenderWindow().addRenderer(renderer)
    return this._vtk_renwin
      .getRenderWindow()
      .synchronize(state).then(onSceneReady)
  }
}

export namespace VTKSynchronizedPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = AbstractVTKPlot.Props & {
    arrays: p.Property<any>
    arrays_processed: p.Property<string[]>
    one_time_reset: p.Property<boolean>
    rebuild: p.Property<boolean>
    scene: p.Property<any>
  }
}

export interface VTKSynchronizedPlot extends VTKSynchronizedPlot.Attrs {}

export class VTKSynchronizedPlot extends AbstractVTKPlot {
  properties: VTKSynchronizedPlot.Props
  outline: any
  outline_actor: any

  static __module__ = "panel.models.vtk"

  constructor(attrs?: Partial<VTKSynchronizedPlot.Attrs>) {
    super(attrs)
    initialize_fullscreen_render()
    this.outline = vtkns.OutlineFilter.newInstance() //use to display bounding box of a selected actor
    const mapper = vtkns.Mapper.newInstance()
    mapper.setInputConnection(this.outline.getOutputPort())
    this.outline_actor = vtkns.Actor.newInstance()
    this.outline_actor.setMapper(mapper)
  }

  getActors(ptr_ref?: string): [any] {
    let actors = this.renderer_el.getRenderer().getActors()
    if (ptr_ref) {
      const context = this.renderer_el.getSynchronizerContext(CONTEXT_NAME)
      actors = actors.filter((actor: any) => {
        const id_actor = context.getInstanceId(actor)
        return id_actor ? id_actor.slice(-16) == ptr_ref.slice(1, 17) : false
      })
    }
    return actors
  }

  static {
    this.prototype.default_view = VTKSynchronizedPlotView

    this.define<VTKSynchronizedPlot.Props>(({Any, Array, Boolean, Bytes, Dict, String}) => ({
      arrays:               [ Dict(Bytes),        {} ],
      arrays_processed:     [ Array(String),      [] ],
      enable_keybindings:   [ Boolean,         false ],
      one_time_reset:       [ Boolean,         false ],
      rebuild:              [ Boolean,         false ],
      scene:                [ Any,                {} ],
    }))

    this.override<VTKSynchronizedPlot.Props>({
      height: 300,
      width: 300,
    })
  }
}
