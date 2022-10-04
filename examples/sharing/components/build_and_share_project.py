import uuid

import param

import panel as pn


class JSActions(pn.reactive.ReactiveHTML):
    # .event cannot trigger on js side. Thus I use Integer
    _url = param.String()
    _open = param.Boolean()
    _copy = param.Boolean()

    _template = """<div id="jsaction" style="height:0px;width:0px"></div>"""
    _scripts = {
        # Todo: Make this more robust by removing fragile replace
        "_open": "url=window.location.href.replace('theme=default','').replace('/sharing','/') +  data._url;window.open(url, '_blank')",
        "_copy": "url=window.location.href.replace('theme=default','').replace('/sharing','/') +  data._url;navigator.clipboard.writeText(url)",
    }

    def __init__(self):
        super().__init__(height=0, width=0, sizing_mode="fixed", margin=0)

    def open(self, url: str):
        """Opens the url in a new tab"""
        if url:
            self._url = url
            self._open = not self._open
        else:
            raise ValueError("No url to open")

    def copy(self, url: str):
        """Copies the url to the clipboard"""
        if url:
            self._url = url
            self._copy = not self._copy
        else:
            raise ValueError("No url to copy")


class BuildAndShareProject(pn.viewable.Viewer):
    convert = param.Event()
    save = param.Event()

    open_developer_link = param.Event()
    open_shared_link = param.Event()
    copy_shared_link = param.Event()

    _state = param.Parameter()  # Todo: Make this ClassParameter with class_=AppState
    _jsactions = param.ClassSelector(class_=JSActions)

    def __init__(self, state, **params):  # Todo: type annotate this
        if not "_jsactions" in params:
            params["_jsactions"] = JSActions()
        super().__init__(_state=state, **params)

        self._panel = self._get_panel()

    def __panel__(self):
        return self._panel

    @pn.depends("convert", watch=True)
    def _convert(self):
        self._state.build()

        if pn.state.notifications:
            pn.state.notifications.success("Build succeeded")

    @pn.depends("save", watch=True)
    def _save(self):
        key = self._state.shared_key
        self._state.site.production_storage[key] = self._state.project

        if pn.state.notifications:
            pn.state.notifications.success("Release succeeded")

    @pn.depends("open_developer_link", watch=True)
    def _open_developer_link(self):
        self._jsactions.open(url=self._state.development_url)

    @pn.depends("open_shared_link", watch=True)
    def _open_shared_link(self):
        self._jsactions.open(url=self._state.shared_url)

    @pn.depends("copy_shared_link", watch=True)
    def _copy_shared_link(self):
        self._jsactions.copy(url=self._state.shared_url)

    def _download_callback(self):
        key = self._state.development_key
        return self._state.site.development_storage.get_zipped_folder(key=key)

    def _get_panel(self):
        convert_button = pn.widgets.Button.from_param(
            self.param.convert,
            name="▶ BUILD",
            sizing_mode="stretch_width",
            align="end",
            button_type="primary",
        )
        open_developer_link_button = pn.widgets.Button.from_param(
            self.param.open_developer_link,
            name="🔗 OPEN",
            width=125,
            sizing_mode="fixed",
            align="end",
            button_type="light",
        )
        download_converted_files = pn.widgets.FileDownload(
            callback=self._download_callback,
            filename="build.zip",
            width=125,
            button_type="light",
            sizing_mode="fixed",
            label="📁 DOWNLOAD",
        )
        share_button = pn.widgets.Button.from_param(
            self.param.save,
            name="❤️ RELEASE",
            sizing_mode="stretch_width",
            align="end",
            button_type="success",
        )
        open_shared_link_button = pn.widgets.Button.from_param(
            self.param.open_shared_link,
            name="🔗 OPEN",
            width=125,
            sizing_mode="fixed",
            align="end",
            button_type="light",
        )
        copy_shared_link_button = pn.widgets.Button.from_param(
            self.param.copy_shared_link,
            name="✂️ COPY",
            width=125,
            sizing_mode="fixed",
            align="end",
            button_type="light",
        )

        return pn.Row(
            self._jsactions,
            convert_button, open_developer_link_button, download_converted_files,
            share_button, open_shared_link_button, copy_shared_link_button,
            sizing_mode="stretch_width",
            margin=(20, 5, 10, 5),
        )
