#!/usr/bin/env python2

''' Simple log system for youtube-dlG. '''

import os.path
from time import strftime

import wx

from .utils import check_path


class LogManager(object):

    '''
    OUT_OF_DATE
    Simple log manager for youtube-dlG.

    Params
        config_path: Absolute path where LogManager should store the log file.
        add_time: If True LogManager will also log the time.

    Accessible Methods
        log_size()
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

    LOG_FILENAME = "log"
    TIME_TEMPLATE = "[{time}] {error_msg}"
    MAX_LOGSIZE = 524288  # 524288B = 512kB

    def __init__(self, config_path, add_time=False):
        self.config_path = config_path
        self.add_time = add_time
        self.log_file = os.path.join(config_path, self.LOG_FILENAME)
        self._init_log()
        self._auto_clear_log()

    def log_size(self):
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

        with open(self.log_file, mode) as log:
            if mode == 'a' and self.add_time:
                msg = self.TIME_TEMPLATE.format(time=strftime('%c'), error_msg=data)
            else:
                msg = data

            log.write(msg)

    def _init_log(self):
        ''' Init log file if not exist. '''
        if not os.path.exists(self.log_file):
            self._write('', 'w')

    def _auto_clear_log(self):
        ''' Auto clear log file. '''
        if self.log_size() > self.MAX_LOGSIZE:
            self.clear()


class LogGUI(wx.Frame):

    '''
    Simple GUI for LogManager

    Accessible Methods
        load()
            Params: File to load

            Return: None
    '''

    TITLE = "Log Viewer"
    FRAME_SIZE = (650, 200)

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, title=self.TITLE, size=self.FRAME_SIZE)

        panel = wx.Panel(self)

        self._text_area = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )

        sizer = wx.BoxSizer()
        sizer.Add(self._text_area, 1, wx.EXPAND)
        panel.SetSizerAndFit(sizer)

    def load(self, filename):
        ''' Load file on text area if file exists. '''
        if os.path.exists(filename):
            self._text_area.LoadFile(filename)
