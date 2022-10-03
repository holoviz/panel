import param

import panel as pn


class SourceEditor(pn.viewable.Viewer):
    project = param.Parameter(constant=True)  # Todo: Should be ClassSelector

    def __init__(self, project):
        super().__init__(project=project)
        self._panel = self._get_panel()

    def __panel__(self):
        return self._panel

    def _get_panel(self):
        code_tab = pn.widgets.Ace.from_param(
            self.project.source.param.code,
            language="python",
            theme="monokai",
            sizing_mode="stretch_both",
            name="app.py",
        )
        readme_tab = pn.widgets.Ace.from_param(
            self.project.source.param.readme,
            language="markdown",
            theme="monokai",
            sizing_mode="stretch_both",
            name="readme.md",
        )

        @pn.depends(dataurl=self.project.source.param.thumbnail)
        def thumbnail_tab(dataurl):
            return pn.pane.HTML(
                f"""<img src={dataurl} style="height:100%;width:100%"></img>""",
                max_width=700,
                name="thumbnail.png",
                sizing_mode="scale_width",
            )

        requirements_tab = pn.widgets.Ace.from_param(
            self.project.source.param.requirements,
            language="txt",
            theme="monokai",
            sizing_mode="stretch_both",
            name="requirements.txt",
        )
        return pn.Tabs(
            code_tab,
            readme_tab,
            ("thumbnail.png", thumbnail_tab),
            requirements_tab,
            sizing_mode="stretch_both",
        )
