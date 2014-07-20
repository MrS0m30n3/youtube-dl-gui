#!/usr/bin/env python2

''' Simple log system for youtube-dlG. '''

import os.path
from time import strftime

import wx

from .utils import (
    check_path,
    fix_path
)


class LogManager(object):

    '''
    Simple log manager for youtube-dlG.

    Params
        config_path: Absolute path where LogManager should store the log file.
        add_time: If True LogManager will also log the time.

    Accessible Methods
        size()
            Params: None

            Return: Log file size in Bytes

        clear()
            Params: None

            Return: None

        log()
            Params: Data to log

            Return: None

    Accessible Variables
        log_file: Absolute path to log file.
    '''

    LOG_FILENAME = 'log'
    MAX_FILESIZE = 524288  # 524288B = 512kB

    def __init__(self, config_path, add_time=False):
        self.config_path = config_path
        self.add_time = add_time
        self.log_file = fix_path(config_path) + self.LOG_FILENAME
        self._init_log()
        self._auto_clear_log()

    def size(self):
        ''' Return log file size in Bytes. '''
        if not os.path.exists(self.log_file):
            return 0

        return os.path.getsize(self.log_file)

    def clear(self):
        ''' Clear log file. '''
        self._write('', 'w')

    def log(self, data):
        ''' Log data to log file. '''
        self._write(data + '\n', 'a')

    def _write(self, data, mode):
        ''' Write data to log file using mode. '''
        check_path(self.config_path)

        with open(self.log_file, mode) as log_file:
            if self.add_time:
                time = '[%s] ' % strftime('%c')
                log_file.write(time)

            log_file.write(data)

    def _init_log(self):
        ''' Init log file if not exist. '''
        if not os.path.exists(self.log_file):
            self._write('', 'w')

    def _auto_clear_log(self):
        ''' Auto clear log file. '''
        if self.size() > self.MAX_FILESIZE:
            self.clear()


class LogGUI(wx.Frame):

    '''
    Simple GUI for LogManager

    Accessible Methods
        load()
            Params: File to load

            Return: None
    '''

    TITLE = 'Log Viewer'

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, self.TITLE, size=(650, 200))

        panel = wx.Panel(self)

        self._text_area = wx.TextCtrl(
            panel,
            -1,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )

        sizer = wx.BoxSizer()
        sizer.Add(self._text_area, 1, wx.EXPAND)
        panel.SetSizerAndFit(sizer)

    def load(self, filename):
        ''' Load file on text area if file exists. '''
        if os.path.exists(filename):
            self._text_area.LoadFile(filename)
