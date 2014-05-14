#! /usr/bin/env python

import wx

from time import strftime
from .Utils import (
    get_filesize,
    check_path,
    file_exist,
    fix_path
)


class LogManager(object):

    LOG_FILENAME = 'log'
    MAX_FILESIZE = 524288  # 524288B = 512kB

    def __init__(self, config_path, add_time=False):
        self.config_path = config_path
        self.add_time = add_time
        self.log_file = self._get_log_file()
        self._auto_clear_log()

    def size(self):
        if not file_exist(self.log_file):
            return 0
        return get_filesize(self.log_file)

    def clear(self):
        self._write('', 'w')

    def log(self, data):
        self._write(data + '\n', 'a')

    def _write(self, data, mode):
        check_path(self.config_path)

        with open(self.log_file, mode) as fl:
            if self.add_time:
                t = '[%s] ' % strftime('%c')
                fl.write(t)
            fl.write(data)

    def _auto_clear_log(self):
        if self.size() > self.MAX_FILESIZE:
            self.clear()

    def _get_log_file(self):
        return fix_path(self.config_path) + self.LOG_FILENAME


class LogGUI(wx.Frame):

    TITLE = 'Log Viewer'

    def __init__(self, log_file, parent=None, id=-1):
        wx.Frame.__init__(self, parent, id, self.TITLE, size=(650, 200))

        panel = wx.Panel(self)

        text_area = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        sizer = wx.BoxSizer()
        sizer.Add(text_area, 1, wx.EXPAND)
        panel.SetSizerAndFit(sizer)

        text_area.LoadFile(log_file)
