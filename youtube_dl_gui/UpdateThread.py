#!/usr/bin/env python2

''' Youtube-dlG module to download youtube-dl. '''

from threading import Thread
from urllib2 import urlopen, URLError, HTTPError

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .utils import (
    get_youtubedl_filename,
    check_path,
    fix_path
)


class UpdateThread(Thread):

    '''
    Download latest youtube-dl.

    Params
        download_path: Absolute path where UpdateThread
                       should download the latest youtube-dl.

        quiet: If True UpdateThread won't send any messages back to caller.
    '''

    LATEST_YOUTUBE_DL = 'https://yt-dl.org/latest/'
    PUBLISHER_TOPIC = 'update'
    DOWNLOAD_TIMEOUT = 20

    def __init__(self, download_path, quiet):
        super(UpdateThread, self).__init__()
        self.download_path = fix_path(download_path)
        self.quiet = quiet
        self.start()

    def run(self):
        self._callafter("Downloading latest youtube-dl. Please wait...")

        youtubedl = get_youtubedl_filename()

        source_file = self.LATEST_YOUTUBE_DL + youtubedl
        destination_file = self.download_path + youtubedl

        check_path(self.download_path)

        try:
            stream = urlopen(source_file, timeout=self.DOWNLOAD_TIMEOUT)

            with open(destination_file, 'wb') as dest_file:
                dest_file.write(stream.read())

            msg = 'Youtube-dl downloaded correctly'
        except (HTTPError, URLError, IOError) as e:
            msg = 'Youtube-dl download failed ' + str(e)

        self._callafter(msg)
        if not self.quiet:
            self._callafter('finish')

    def _callafter(self, data):
        ''' CallAfter wrapper. '''
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)
