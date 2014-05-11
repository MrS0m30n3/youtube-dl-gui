#! /usr/bin/env python

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from threading import Thread
from urllib2 import urlopen, URLError, HTTPError

from .Utils import (
    get_youtubedl_filename,
    check_path,
    fix_path
)


class UpdateThread(Thread):

    LATEST_YOUTUBE_DL = 'https://yt-dl.org/latest/'
    PUBLISHER_TOPIC = 'update'
    DOWNLOAD_TIMEOUT = 20

    def __init__(self, download_path):
        super(UpdateThread, self).__init__()
        self.download_path = fix_path(download_path)
        self._youtubedl_file = get_youtubedl_filename()
        self.start()

    def run(self):
        self._callafter("Downloading latest youtube-dl. Please wait...")

        dl_url = self.LATEST_YOUTUBE_DL + self._youtubedl_file
        dst_file = self.download_path + self._youtubedl_file

        check_path(self.download_path)

        try:
            f = urlopen(dl_url, timeout=self.DOWNLOAD_TIMEOUT)

            with open(dst_file, 'wb') as bf:
                bf.write(f.read())

            msg = 'Youtube-dl downloaded correctly'
        except (HTTPError, URLError, IOError) as e:
            msg = 'Youtube-dl download failed ' + str(e)

        self._callafter(msg)
        self._callafter('finish')

    def _callafter(self, data):
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)
