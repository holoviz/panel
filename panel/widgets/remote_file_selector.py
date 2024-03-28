import asyncio
import threading

from abc import abstractmethod
from pathlib import PurePosixPath
from typing import (
    ClassVar, Dict, List, Optional, Type,
)

import param

from panel.layout import (
    Column, Divider, ListPanel, Row,
)

from ..pane.markup import Markdown
from ..viewable import Layoutable
from .base import CompositeWidget
from .button import Button
from .input import TextInput
from .select import CrossSelector


class RemoteFileProvider(param.Parameterized):
    """
    `RemoteFileProvider` is an abstract class used by `RemoteFileSelector` to
    list content of a remote filesystem.

    Reference: https://panel.holoviz.org/reference/widgets/RemoteFileSelector.html

    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def ls(self, path):
        """
        Concrete classes must implement this method to list the content of a remote filesystem.

        Arguments
        ---------
        path: str
            The path to search

        Returns
        -------
        A tuple of two lists: the first one contains the directories, the second one contains the files.
        Each element of the lists is a string representing the *name* (not the full path) of the directory or file.


        """
        raise NotImplementedError()

# for S3RemoteFileProvider
import s3fs


class S3RemoteFileProvider(RemoteFileProvider):
    """
    `S3RemoteFileProvider` is a concrete class used by `RemoteFileSelector` to
    list content of a S3 Bucket.
    It relies on [s3fs](https://s3fs.readthedocs.io/) and needs an instance of a configured `s3fs.S3FileSystem` object.

    Arguments
    ---------
    fs : s3fs.S3FileSystem
        An instance of a configured `s3fs.S3FileSystem` object.
    buckets : List[str]
        List of the S3 buckets to browse.
        The buckets will appear as the root directories in the file selector.
        If only one bucket is provided, the root directory will be the bucket itself.
    file_pattern : str
        A glob-like pattern to filter the files. Default is `'*'`.

    Returns
    -------
    An instance of `S3RemoteFileProvider`.


    :Example:
    ```python
    import s3fs

    fs = s3fs.S3FileSystem(
        key= ... ,
        secret= ... ,
        client_kwargs = {"endpoint_url": ... }, # optional - for non-AWS S3 buckets
    )

    remote_file_provider = S3RemoteFileProvider(fs=fs,  bucket="my_bucket")

    remote_file_selector = RemoteFileSelector(provider=remote_file_provider)
    ```

    Reference: https://panel.holoviz.org/reference/widgets/RemoteFileSelector.html

    """

    file_pattern = param.String(default='*', doc="""
        A glob-like pattern to filter the files.""")

    def __init__(self, fs:s3fs.core.S3FileSystem, buckets:List[str], file_pattern:str='*'):
        super().__init__()
        self.fs = fs
        self.buckets = buckets
        self.file_pattern = file_pattern

    async def ls(self, path:PurePosixPath):

        if str(path) == '/' and len(self.buckets) > 1:
                return self.buckets, []

        else:

            if len(self.buckets) == 1:
                current_root = self.buckets[0] + str(path)
                # ensure trailing slash
                current_root = (current_root + "/").replace("//", "/")
            else:
                # remove leading slash
                current_root = str(path)[1:]
                # ensure trailing slash
                current_root = (current_root + "/").replace("//", "/")

            raw_ls = self.fs.ls(current_root, detail=True)
            dirs = [ d['name'].replace(current_root, "") for d in raw_ls if d['type'] == 'directory' ]

            raw_glob = self.fs.glob(current_root + self.file_pattern, detail=True)
            files = [ d['name'].replace(current_root, "") for d in raw_glob.values() if d['type'] == 'file' ]

            return dirs, files


class RemoteFileSelector(CompositeWidget):
    """
    The `RemoteFileSelector` widget allows browsing a remote filesystem,
    by using a `RemoteFileProvider`, and select files from it.

    Reference: https://panel.holoviz.org/reference/widgets/RemoteFileSelector.html

    :Example:

    >>> remote_file_provider = S3RemoteFileProvider(...)
    >>> remote_file_selector = RemoteFileSelector(provider=remote_file_provider)

    """

    directory = param.String(default="/", doc="""
        The directory to explore.""")

    size = param.Integer(default=10, doc="""
        The number of options shown at once (note this is the only
        way to control the height of this widget)""")

    value = param.List(default=[], doc="""
        List of selected files.""")

    _composite_type: ClassVar[Type[ListPanel]] = Column

    _provider : RemoteFileProvider = None

    _dir_prefix : str = '📁 '

    # Used to navigate in the history of paths visited
    _cache_cwd : List[str] = []
    _history_position : int = -1

    # associates a path (str) to a list of files (list of str)
    _cache_filelist : Dict[str, List[str]] = {}

    def __init__(self, provider: RemoteFileProvider, **params):

        self._provider = provider

        if params.get('width') and params.get('height') and 'sizing_mode' not in params:
            params['sizing_mode'] = None

        super().__init__(**params)

        # Set up layout
        layout = {p: getattr(self, p) for p in Layoutable.param
                  if p not in ('name', 'height', 'margin') and getattr(self, p) is not None}
        sel_layout = dict(layout, sizing_mode='stretch_width', height=300, margin=0)
        self._selector = CrossSelector(
            size=self.size, **sel_layout,
        )

        self._back = Button(name='◀', width=40, height=40, margin=(5, 10, 0, 0),
                            align='center')
        self._forward = Button(name='▶', width=40, height=40, margin=(5, 10, 0, 0),
                                align='center')
        self._up = Button(name='⬆', width=40, height=40, margin=(5, 10, 0, 0),
                          align='center')
        self._directory = TextInput(value=self.directory, margin=(5, 10, 0, 0), width_policy='max',
                                    disabled=True)
        self._down = Button(name='⬇', disabled=True, width=40, height=40, margin=(5, 5, 0, 0), align='center')
        self._reload = Button(name='↻', width=40, height=40, margin=(5, 0, 0, 10), align='center')
        self._nav_bar = Row(
            self._back, self._forward, self._up, self._directory, self._down, self._reload,
            **dict(layout, width=None, margin=0, width_policy='max')
        )

        self._composite[:] = [self._nav_bar, Divider(margin=0), self._selector]
        style = 'h4 { margin-block-start: 0; margin-block-end: 0;}'
        self._selector._selected.insert(0, Markdown('#### Selected files', margin=0, stylesheets=[style]))
        self._selector._unselected.insert(0, Markdown('#### File Browser', margin=0, stylesheets=[style]))
        self.link(self._selector, size='size')


        # Set up state
        self._stack = []
        self._cwd = PurePosixPath("/")
        self._cache_cwd.append(self._cwd)
        self._position = -1

        #asyncio.ensure_future(self._update_files(True))

        self.update_back_forward_buttons_state()

        # Set up callback
        #self.link(self._directory, directory='value')
        self._selector.param.watch(self._update_value, 'value')
        self._down.on_click(self.did_click_down)
        self._reload.on_click(self.did_click_reload)
        self._up.on_click(self.did_click_up)
        self._back.on_click(self.did_click_back)
        self._forward.on_click(self.did_click_forward)
        # self._directory.param.watch(self._dir_change, 'value')
        self._selector._lists[False].param.watch(self._select, 'value')
        self._selector._lists[True].param.watch(self._select, 'value')

        self.update_files_with_loading()



    def _update_value(self, event: param.parameterized.Event):
        # the following code makes sure that the paths shown on the right list
        # is made of absolute paths, and not relative paths.


        if len(event.new) == len(event.old):
            # second update, do nothing
            return

        if len(event.new) > len(event.old):
            # When adding files/dirs ...
            added = [ v for v in event.new if v not in event.old ]
            remaining_options = [ v for v in self._selector.options if v not in added]

            prefixed_added = []
            for f in added:
                if f.startswith(self._dir_prefix):
                    new_f = self._cwd /  f.replace(self._dir_prefix, '')
                    prefixed_added.append( self._dir_prefix + str(new_f) )
                else:
                    prefixed_added.append( str(self._cwd /  f) )
            to_add = [v for v in prefixed_added if v not in added]

            self._selector.options = remaining_options + prefixed_added
            self._selector.value = event.old + to_add
            # triggers a second call to this function
            self.value = self._selector.value


        else:
            # When removing files/dirs
            removed = [ v for v in event.old if v not in event.new ]
            remaining_options = [ v for v in self._selector.options if v not in removed]

            unprefixed_removed = []
            for f in removed:

                has_dir_prefix = f.startswith(self._dir_prefix)
                if has_dir_prefix:
                    f = f.replace(self._dir_prefix, '')

                f = PurePosixPath(f)
                if f.parent == self._cwd:
                    if has_dir_prefix:
                        unprefixed_removed.append( self._dir_prefix + f.stem )
                    else:
                        unprefixed_removed.append( f.stem )

            self._selector.options = remaining_options + unprefixed_removed
            # triggers a second call to this function
            self.value = self._selector.value

    def run_async_in_thread(self, async_func):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_func)
        loop.close()


    def did_click_reload(self, event=None):
        self.update_files_with_loading()

    def update_files_with_loading(self):

        self._selector._lists[False].loading = True

        thread = threading.Thread(target=self.run_async_in_thread, args=(self._update_files(),))
        thread.start()
        thread.join()

        self._selector._lists[False].loading = False


    async def _update_files(
        self, event: Optional[param.parameterized.Event] = None, refresh: bool = False
    ):
        dirs, files = await self._provider.ls(self._cwd)

        paths = [p for p in sorted(dirs)+sorted(files) ]
        abbreviated = [(self._dir_prefix if f in dirs else '')+f for f in paths]
        options = abbreviated

        self._cache_filelist[self._cwd] = options + self.value
        self._selector.options = options + self.value
        self._selector.value = self.value


    # Called when clicking on a directory or file in the left list
    def _select(self, event: param.parameterized.Event):
        if len(event.new) != 1:
            return

        selected_item = event.new[0].replace(self._dir_prefix, '')
        is_dir = event.new[0].startswith(self._dir_prefix)

        self._directory.value = str(self._cwd / selected_item)

        self._down.disabled = not is_dir


    def did_click_down(self, event: param.parameterized.Event):

        self._cwd = PurePosixPath(self._directory.value)
        self.update_files_with_loading()

        self.flush_history()

    def did_click_up(self, event: Optional[param.parameterized.Event] = None):

        self._cwd = self._cwd.parent
        self._directory.value = str(self._cwd)
        self.update_files_with_loading()

        self.flush_history()

    def flush_history(self):
        if self._history_position != -1:
            del self._cache_cwd[self._history_position+1:]
            self._history_position = -1
        self._cache_cwd.append(self._cwd)
        self.update_back_forward_buttons_state()

    def did_click_back(self, event: param.parameterized.Event):

        self._history_position -= 1
        self.update_back_forward_buttons_state()

        self._cwd = self._cache_cwd[self._history_position]
        self._directory.value = str(self._cwd)
        self._selector.options = self._cache_filelist[self._cwd]


    def did_click_forward(self, event: param.parameterized.Event):
        self._history_position += 1
        self.update_back_forward_buttons_state()

        self._cwd = self._cache_cwd[self._history_position]
        self._directory.value = str(self._cwd)
        self._selector.options = self._cache_filelist[self._cwd]


    def update_back_forward_buttons_state(self):
        self._back.disabled = self._history_position == -len(self._cache_cwd)
        self._forward.disabled = self._history_position == - 1
