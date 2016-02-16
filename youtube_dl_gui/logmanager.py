#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg module responsible for handling the log stuff. """

from __future__ import unicode_literals

import os.path
from time import strftime

from .utils import (
    os_path_exists,
    get_encoding,
    check_path
)


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
    MAX_LOGSIZE = 524288  # Bytes

    def __init__(self, config_path, add_time=False):
        self.config_path = config_path
        self.add_time = add_time
        self.log_file = os.path.join(config_path, self.LOG_FILENAME)
        self._encoding = get_encoding()
        self._init_log()
        self._auto_clear_log()

    def log_size(self):
        """Return log file size in Bytes. """
        if not os_path_exists(self.log_file):
            return 0

        return os.path.getsize(self.log_file)

    def clear(self):
        """Clear log file. """
        self._write('', 'w')

    def log(self, data):
        """Log data to the log file.

        Args:
            data (string): String to write to the log file.

        """
        if isinstance(data, basestring):
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

            log.write(msg.encode(self._encoding, 'ignore'))

    def _init_log(self):
        """Initialize the log file if not exist. """
        if not os_path_exists(self.log_file):
            self._write('', 'w')

    def _auto_clear_log(self):
        """Auto clear the log file. """
        if self.log_size() > self.MAX_LOGSIZE:
            self.clear()
