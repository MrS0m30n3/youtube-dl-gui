#!/usr/bin/env python2

"""Youtubedlg module to update youtube-dl binary. """

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


class UpdateThread(Thread):

    """Python Thread that downloads youtube-dl binary.

    Attributes:
        LATEST_YOUTUBE_DL (string): URL with the latest youtube-dl binary.
        PUBLISHER_TOPIC (string): Subscription topic for the wx Publisher.
        DOWNLOAD_TIMEOUT (int): Download timeout in seconds.
    
    Args:
        download_path (string): Absolute path where UpdateThread will download
            the latest youtube-dl.

        quiet (boolean): If True UpdateThread won't send the finish signal
            back to the caller. Finish signal can be used to make sure that
            UpdateThread has been completed in an asynchronous way.
    
    """

    LATEST_YOUTUBE_DL = 'https://yt-dl.org/latest/'
    PUBLISHER_TOPIC = 'update'
    DOWNLOAD_TIMEOUT = 20

    def __init__(self, download_path, quiet=False):
        super(UpdateThread, self).__init__()
        self.download_path = download_path
        self.quiet = quiet
        self.start()

    def run(self):
        self._talk_to_gui("Downloading latest youtube-dl. Please wait...")

        source_file = self.LATEST_YOUTUBE_DL + YOUTUBEDL_BIN
        destination_file = os.path.join(self.download_path, YOUTUBEDL_BIN)

        check_path(self.download_path)

        try:
            stream = urlopen(source_file, timeout=self.DOWNLOAD_TIMEOUT)

            with open(destination_file, 'wb') as dest_file:
                dest_file.write(stream.read())

            msg = 'Youtube-dl downloaded correctly'
        except (HTTPError, URLError, IOError) as e:
            msg = 'Youtube-dl download failed ' + str(e)

        self._talk_to_gui(msg)

        if not self.quiet:
            self._talk_to_gui('finish')

    def _talk_to_gui(self, data):
        """Send data back to the GUI using wx CallAfter and wx Publisher.
        
        Args:
            data (string): Can be either a message that informs for the 
                update process or a 'finish' signal which shows that the 
                update process has been completed.
        
        """
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)
