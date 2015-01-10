#!/usr/bin/env python2

"""Youtubedlg module responsible for handling the log stuff. """

import os.path
from time import strftime

import wx

from .utils import check_path


class LogManager(object):

    """Simple log manager for youtube-dl.

    This class is mainly used to log the youtube-dl STDERR.

    Attributes:
        LOG_FILENAME (string): Filename of the log file.
        TIME_TEMPLATE (string): Custom template to log the time.
        MAX_LOGSIZE (int): Maximum size(Bytes) of the log file.

    Args:
        config_path (string): Absolute path where LogManager should
            store the log file.

        add_time (boolean): If True LogManager will also log the time.

    """

    LOG_FILENAME = "log"
    TIME_TEMPLATE = "[{time}] {error_msg}"
    MAX_LOGSIZE = 524288

    def __init__(self, config_path, add_time=False):
        self.config_path = config_path
        self.add_time = add_time
        self.log_file = os.path.join(config_path, self.LOG_FILENAME)
        self._init_log()
        self._auto_clear_log()

    def log_size(self):
        """Return log file size in Bytes. """
        if not os.path.exists(self.log_file):
            return 0

        return os.path.getsize(self.log_file)

    def clear(self):
        """Clear log file. """
        self._write('', 'w')

    def log(self, data):
        """Log data to the log file. """
        self._write(data + '\n', 'a')

    def _write(self, data, mode):
        """Write data to the log file.

        That's the main method for writing to the log file.

        Args:
            data (string): String to write on the log file.
            mode (string): Can be any IO mode supported by python.

        """
        check_path(self.config_path)

        with open(self.log_file, mode) as log:
            if mode == 'a' and self.add_time:
                msg = self.TIME_TEMPLATE.format(time=strftime('%c'), error_msg=data)
            else:
                msg = data

            log.write(msg)

    def _init_log(self):
        """Initialize the log file if not exist. """
        if not os.path.exists(self.log_file):
            self._write('', 'w')

    def _auto_clear_log(self):
        """Auto clear the log file. """
        if self.log_size() > self.MAX_LOGSIZE:
            self.clear()


class LogGUI(wx.Frame):

    """Simple window for reading the STDERR.

    Attributes:
        TITLE (string): Frame title.
        FRAME_SIZE (tuple): Tuple that holds the frame size (width, height).

    Args:
        parent (wx.Window): Frame parent.

    """

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
        """Load file content on the text area. """
        if os.path.exists(filename):
            self._text_area.LoadFile(filename)
