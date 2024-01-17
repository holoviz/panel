import { Column, ColumnView } from "./column";
import * as p from "@bokehjs/core/properties";
import {build_views} from "@bokehjs/core/build_views"
import {UIElementView} from "@bokehjs/models/ui/ui_element"

export class LogView extends ColumnView {
  model: Log;
  _intersection_observer: IntersectionObserver
  _last_visible: UIElementView | null
  _sync: boolean

  override initialize(): void {
    super.initialize()
    this._sync = true
    this._intersection_observer = new IntersectionObserver((entries) => {
      const visible = [...this.model.visible_objects]
      const nodes = this.node_map
      for (const entry of entries) {
	const id = nodes.get(entry.target).id
	if (entry.isIntersecting) {
	  if (!visible.includes(id)) {
	    visible.push(id)
	  }
	} else if (visible.includes(id))  {
	  visible.splice(visible.indexOf(id), 1)
	}
      }
      if (this._sync) {
	this.model.visible_objects = visible
      }
      if (visible.length) {
	const refs = this.child_models.map((model) => model.id)
	const indices = visible.map((ref) => refs.indexOf(ref))
	this._last_visible = this.child_views[Math.min(...indices)]
      } else {
	this._last_visible = null
      }
    }, {
      root: this.el,
      threshold: .01
    })
  }

  get node_map(): any {
    const nodes = new Map()
    for (const view of this.child_views) {
      nodes.set(view.el, view.model)
    }
    return nodes
  }

  async update_children(): Promise<void> {
    this._sync = false
    await super.update_children()
    this._sync = true
    if (this._last_visible != null) {
      this._last_visible.el.scrollIntoView(true)
    }
  }

  async build_child_views(): Promise<UIElementView[]> {
    const {created, removed} = await build_views(this._child_views, this.child_models, {parent: this})

    const visible = this.model.visible_objects
    for (const view of removed) {
      if (visible.includes(view.model.id)) {
	visible.splice(visible.indexOf(view.model.id), 1)
      }
      this._resize_observer.unobserve(view.el)
      this._intersection_observer.unobserve(view.el)
    }
    this.model.visible_objects = [...visible]

    for (const view of created) {
      this._resize_observer.observe(view.el, {box: "border-box"})
      this._intersection_observer.observe(view.el)
    }

    return created
  }
}

export namespace Log {
  export type Attrs = p.AttrsOf<Props>;
  export type Props = Column.Props & {
    visible_objects: p.Property<string[]>;
  };
}

export interface Log extends Log.Attrs { }

export class Log extends Column {
  properties: Log.Props;

  constructor(attrs?: Partial<Log.Attrs>) {
    super(attrs);
  }

  static __module__ = "panel.models.layout";

  static {
    this.prototype.default_view = LogView;

    this.define<Log.Props>(({ Array, String }) => ({
      visible_objects: [Array(String), []]
    }));
  }
}
