#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg module to update youtube-dl binary.

Attributes:
    UPDATE_PUB_TOPIC (string): wxPublisher subscription topic of the
        UpdateThread thread.

"""

from __future__ import unicode_literals

import os.path
from threading import Thread
from urllib2 import urlopen, URLError, HTTPError

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .utils import (
    YOUTUBEDL_BIN,
    check_path
)

UPDATE_PUB_TOPIC = 'update'


class UpdateThread(Thread):

    """Python Thread that downloads youtube-dl binary.

    Attributes:
        LATEST_YOUTUBE_DL (string): URL with the latest youtube-dl binary.
        DOWNLOAD_TIMEOUT (int): Download timeout in seconds.

    Args:
        download_path (string): Absolute path where UpdateThread will download
            the latest youtube-dl.

        quiet (boolean): If True UpdateThread won't send the finish signal
            back to the caller. Finish signal can be used to make sure that
            the UpdateThread has been completed in an asynchronous way.

    """

    LATEST_YOUTUBE_DL = 'https://yt-dl.org/latest/'
    DOWNLOAD_TIMEOUT = 20

    def __init__(self, download_path, quiet=False):
        super(UpdateThread, self).__init__()
        self.download_path = download_path
        self.quiet = quiet
        self.start()

    def run(self):
        self._talk_to_gui('download')

        source_file = self.LATEST_YOUTUBE_DL + YOUTUBEDL_BIN
        destination_file = os.path.join(self.download_path, YOUTUBEDL_BIN)

        check_path(self.download_path)

        try:
            stream = urlopen(source_file, timeout=self.DOWNLOAD_TIMEOUT)

            with open(destination_file, 'wb') as dest_file:
                dest_file.write(stream.read())

            self._talk_to_gui('correct')
        except (HTTPError, URLError, IOError) as error:
            self._talk_to_gui('error', unicode(error))

        if not self.quiet:
            self._talk_to_gui('finish')

    def _talk_to_gui(self, signal, data=None):
        """Communicate with the GUI using wxCallAfter and wxPublisher.

        Args:
            signal (string): Unique signal string that informs the GUI for the
                update process.

            data (string): Can be any string data to pass along with the
                given signal. Default is None.

        Note:
            UpdateThread supports 4 signals.
                1) download: The update process started
                2) correct: The update process completed successfully
                3) error: An error occured while downloading youtube-dl binary
                4) finish: The update thread is ready to join

        """
        CallAfter(Publisher.sendMessage, UPDATE_PUB_TOPIC, (signal, data))
