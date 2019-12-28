# -*- coding: utf-8 -*-
"""
Defines a FileSelector widget which allows selecting files and
directories on the server.
"""
from __future__ import absolute_import, division, unicode_literals

import os
import glob

from collections import OrderedDict

import param

from ..layout import Column, Divider, Row
from ..viewable import Layoutable
from .base import CompositeWidget
from .button import Button
from .input import TextInput
from .select import CrossSelector


class FileSelector(CompositeWidget):

    directory = param.String(default=os.getcwd(), doc="""
        The directory to explore.""")

    only_files = param.Boolean(default=False, doc="""
        Whether to only allow selecting files.""")

    file_keyword = param.String(default='*', doc="""
        A glob-like query expression to limit the displayed files.""")

    value = param.List(default=[], doc="""
        List of selected files.""")

    def __init__(self, directory=None, **params):
        if directory is not None:
            params['directory'] = os.path.abspath(os.path.expanduser(directory))
        super(FileSelector, self).__init__(**params)

        # Set up layout
        layout = {p: getattr(self, p) for p in Layoutable.param
                  if p not in ('name', 'height') and getattr(self, p) is not None}
        sel_layout = dict(layout)
        if self.height:
            sel_layout['height'] = self.height-100
        self._selector = CrossSelector(**sel_layout)
        self._go = Button(name='↵', disabled=True, width=25, margin=(5, 25, 0, 0))
        self._directory = TextInput(value=self.directory, width_policy='max')
        self._home = Button(name='🏠', width=25, margin=(5, 15, 0, 10), disabled=True)
        self._back = Button(name='◀', width=25, margin=(5, 10), disabled=True)
        self._forward = Button(name='▶', width=25, margin=(5, 10), disabled=True)
        self._up = Button(name='▲', width=25, margin=(5, 10), disabled=True)
        self._nav_bar = Row(
            self._home, self._back, self._forward, self._up, self._directory, self._go,
            margin=(0, 10), width_policy='max'
        )
        self._composite = Column(self._nav_bar, Divider(margin=(0, 20)), self._selector, **layout)

        # Set up state
        self._stack = []
        self._cwd = None
        self._position = -1
        self._update_files(True)

        # Set up callback
        self.link(self._directory, directory='value')
        self._selector.param.watch(self._update_value, 'value')
        self._go.on_click(self._update_files)
        self._home.on_click(self._go_home)
        self._up.on_click(self._go_up)
        self._back.on_click(self._go_back)
        self._forward.on_click(self._go_forward)
        self._directory.param.watch(self._dir_change, 'value')
        self._selector._lists[False].param.watch(self._select, 'value')

    def _update_value(self, event):
        value = [v for v in event.new if not self.only_files or os.path.isfile(v)]
        self._selector.value = value
        self.value = value

    def _dir_change(self, event):
        path = os.path.abspath(os.path.expanduser(self._directory.value))
        if not path.startswith(self.directory):
            self._directory.value = self.directory
            return
        elif path != self._directory.value:
            self._directory.value = path
        self._go.disabled = path == self._cwd

    def _update_files(self, event=None):
        path = os.path.abspath(self._directory.value)
        if not os.path.isdir(path):
            self._selector.options = ['Entered path is not valid']
            self._selector.disabled = True
            return
        elif event is not None and (not self._stack or path != self._stack[-1]):
            self._stack.append(path)
            self._position += 1

        self._cwd = path
        self._go.disabled = True
        self._home.disabled = path == self.directory
        self._up.disabled = path == self.directory
        if self._position == len(self._stack)-1:
            self._forward.disabled = True
        if 0 <= self._position and len(self._stack) > 1:
            self._back.disabled = False

        file_paths = glob.glob(os.path.join(path, '*' + self.file_keyword + '*'))
        files = sorted([p for p in file_paths if os.path.isfile(p)])
        dir_paths = glob.glob(os.path.join(path, '*'))
        dirs = sorted([p for p in dir_paths if os.path.isdir(p)])
        combined = dirs + files
        abbreviated = ['./'+f.split(os.path.sep)[-1] for f in combined]
        options = OrderedDict()
        if path != self.directory:
            options['..'] = os.path.abspath(os.path.join(path, '..')) 
        options.update(zip(abbreviated, combined))
        self._selector.options = options

    def _select(self, event):
        if len(event.new) != 1:
            self._directory.value = self._cwd
            return
        
        sel = os.path.abspath(os.path.join(self._cwd, event.new[0]))
        if os.path.isdir(sel):
            self._directory.value = sel
        else:
            self._directory.value = self._cwd

    def _go_home(self, event):
        self._directory.value = self.directory
        self._update_files(True)

    def _go_back(self, event):
        self._position -= 1
        self._directory.value = self._stack[self._position]
        self._update_files()
        self._forward.disabled = False
        if self._position == 0:
            self._back.disabled = True

    def _go_forward(self, event):
        self._position += 1
        self._directory.value = self._stack[self._position]
        self._update_files()

    def _go_up(self, event=None):
        path = self._cwd.split(os.path.sep)
        self._directory.value = os.path.sep.join(path[:-1])
        self._update_files(True)
