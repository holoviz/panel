import param

import panel as pn


class NewProject(pn.viewable.Viewer):
    create = param.Event()
    gallery = param.Parameter()

    def __init__(self, **params):
        super().__init__(**params)
        with param.edit_constant(self):
            self.name = "New"

    def __panel__(self):
        return pn.pane.Markdown("New", name="New")


# @pn.depends("new", watch=True)
# def _new(self):
#     self._state.project.code = self.gallery.code
#     self._state.requirements = self.gallery.requirements
#     with param.edit_constant(self._state.project):
#         self._state.project.name = "new"
#     self.convert = True

# new_button = pn.widgets.Button.from_param(
#     new_project.param.create, sizing_mode="stretch_width", button_type="primary", name="Create"
# )
# new_tab = pn.Column(
#     new_project.gallery, new_button, sizing_mode="stretch_width", name="New"
# )

# GALLERY_ENTRIES = {
#     "Default": {"code": config.CODE, "requirements": ""},
#     "Hello World": {"code": config.HELLO_WORLD_CODE, "requirements": ""},
# }


# class AppGallery(pn.viewable.Viewer):
#     selection = param.Selector(objects=list(GALLERY_ENTRIES))

#     def __init__(self, **params):
#         super().__init__(**params)
#         self._panel = pn.widgets.RadioBoxGroup.from_param(
#             self.param.selection,
#             sizing_mode="stretch_width",
#             orientation="vertical",
#             margin=(20, 5, 10, 5),
#         )

#     def __panel__(self):
#         return self._panel

#     @property
#     def code(self):
#         return GALLERY_ENTRIES[self.selection]["code"]

#     @property
#     def requirements(self):
#         return GALLERY_ENTRIES[self.selection]["requirements"]
