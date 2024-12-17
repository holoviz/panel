import type {CSSProperties} from "./util"
import {vtkns, applyStyle} from "./util"

//------------------------//
//Custom Extended Classes
//------------------------//

const DEFAULT_VALUES = {
  containerStyle: null,
  controlPanelStyle: null,
  listenWindowResize: true,
  resizeCallback: null,
  controllerVisibility: true,
  synchronizerContextName: "default",
}

const STYLE_CONTROL_PANEL: CSSProperties = {
  position: "absolute",
  left: "25px",
  top: "25px",
  backgroundColor: "white",
  borderRadius: "5px",
  listStyle: "none",
  padding: "5px 10px",
  margin: "0",
  display: "block",
  border: "solid 1px black",
  maxWidth: "calc(100vw - 70px)",
  maxHeight: "calc(100vh - 60px)",
  overflow: "auto",
}

function panelFullScreenRenderWindowSynchronized(publicAPI: any, model: any) {
  // Panel (modification) synchronizable renderWindow
  model.renderWindow = vtkns.SynchronizableRenderWindow.newInstance({
    synchronizerContext: model.synchronizerContext,
  })

  // OpenGlRenderWindow
  model.openGLRenderWindow = vtkns.OpenGLRenderWindow.newInstance()
  model.openGLRenderWindow.setContainer(model.container)
  model.renderWindow.addView(model.openGLRenderWindow)

  // Interactor
  model.interactor = vtkns.RenderWindowInteractor.newInstance()
  model.interactor.setInteractorStyle(vtkns.InteractorStyleTrackballCamera.newInstance())
  model.interactor.setView(model.openGLRenderWindow)
  model.interactor.initialize()
  model.interactor.bindEvents(model.container)

  publicAPI.getRenderer = () => model.renderWindow.getRenderers()[0]

  publicAPI.removeController = () => {
    const el = model.controlContainer
    if (el) {
      el.parentNode.removeChild(el)
    }
  }

  publicAPI.setControllerVisibility = (visible: boolean) => {
    model.controllerVisibility = visible
    if (model.controlContainer) {
      if (visible) {
        model.controlContainer.style.display = "block"
      } else {
        model.controlContainer.style.display = "none"
      }
    }
  }

  publicAPI.toggleControllerVisibility = () => {
    publicAPI.setControllerVisibility(!model.controllerVisibility)
  }

  publicAPI.addController = (html: string) => {
    model.controlContainer = document.createElement("div")
    applyStyle(
      model.controlContainer,
      model.controlPanelStyle || STYLE_CONTROL_PANEL,
    )
    model.rootContainer.appendChild(model.controlContainer)
    model.controlContainer.innerHTML = html

    publicAPI.setControllerVisibility(model.controllerVisibility)

    model.rootContainer.addEventListener("keypress", (e: KeyboardEvent) => {
      if (String.fromCharCode(e.charCode) === "c") {
        publicAPI.toggleControllerVisibility()
      }
    })
  }

  // Properly release GL context
  publicAPI.delete = (window as any).vtk.macro.chain(
    publicAPI.setContainer,
    model.openGLRenderWindow.delete,
    publicAPI.delete,
  )

  // Handle window resize
  publicAPI.resize = () => {
    const dims = model.container.getBoundingClientRect()
    const devicePixelRatio = window.devicePixelRatio || 1
    model.openGLRenderWindow.setSize(
      Math.floor(dims.width * devicePixelRatio),
      Math.floor(dims.height * devicePixelRatio),
    )
    if (model.resizeCallback) {
      model.resizeCallback(dims)
    }
    model.renderWindow.render()
  }

  publicAPI.setResizeCallback = (cb: CallableFunction) => {
    model.resizeCallback = cb
    publicAPI.resize()
  }

  if (model.listenWindowResize) {
    window.addEventListener("resize", publicAPI.resize)
  }
  publicAPI.resize()
}

export function initialize_fullscreen_render(): void {
  const FullScreenRenderWindowSynchronized: any = {
    newInstance: (window as any).vtk.macro.newInstance(
      (publicAPI: any, model: any, initialValues: any = {}) => {
        Object.assign(model, DEFAULT_VALUES, initialValues);

        // Object methods
        (window as any).vtk.macro.obj(publicAPI, model);
        (window as any).vtk.macro.get(publicAPI, model, [
          "renderWindow",
          "openGLRenderWindow",
          "interactor",
          "rootContainer",
          "container",
          "controlContainer",
          "synchronizerContext",
        ])

        // Object specific methods
        panelFullScreenRenderWindowSynchronized(publicAPI, model)
      },
    ),
  }
  vtkns.FullScreenRenderWindowSynchronized = FullScreenRenderWindowSynchronized
}
