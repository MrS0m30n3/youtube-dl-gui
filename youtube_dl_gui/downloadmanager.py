#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg module for managing the download process.

This module is responsible for managing the download process
and update the GUI interface.

Attributes:
    MANAGER_PUB_TOPIC (string): wxPublisher subscription topic of the
        DownloadManager thread.

    WORKER_PUB_TOPIC (string): wxPublisher subscription topic of the
        Worker thread.

Note:
    It's not the actual module that downloads the urls
    thats the job of the 'downloaders' module.

"""

from __future__ import unicode_literals

import time
import os.path

from threading import (
    Thread,
    Lock
)

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .parsers import OptionsParser
from .updatemanager import UpdateThread
from .downloaders import YoutubeDLDownloader

from .utils import YOUTUBEDL_BIN


MANAGER_PUB_TOPIC = 'dlmanager'
WORKER_PUB_TOPIC = 'dlworker'


class DownloadManager(Thread):

    """Manages the download process.

    Attributes:
        WAIT_TIME (float): Time in seconds to sleep.

    Args:
        urls_list (list): Python list that contains multiple dictionaries
            with the url to download and the corresponding row(index) in
            which the worker should send the download process information.

        opt_manager (optionsmanager.OptionsManager): Object responsible for
            managing the youtubedlg options.

        log_manager (logmanager.LogManager): Object responsible for writing
            errors to the log.

    """

    WAIT_TIME = 0.1

    def __init__(self, urls_list, opt_manager, log_manager=None):
        super(DownloadManager, self).__init__()
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self.urls_list = urls_list

        self._time_it_took = 0
        self._successful = 0
        self._running = True

        # Init the custom workers thread pool
        log_lock = None if log_manager is None else Lock()
        wparams = (opt_manager, self._youtubedl_path(), log_manager, log_lock)
        self._workers = [Worker(*wparams) for i in xrange(opt_manager.options['workers_number'])]

        self.start()

    @property
    def successful(self):
        """Returns number of successful downloads. """
        return self._successful

    @property
    def time_it_took(self):
        """Returns time(seconds) it took for the download process
        to complete. """
        return self._time_it_took

    def run(self):
        self._check_youtubedl()
        self._time_it_took = time.time()

        while self._running:
            for worker in self._workers:
                if worker.available() and self.urls_list:
                    worker.download(self.urls_list.pop(0))

            time.sleep(self.WAIT_TIME)

            if not self.urls_list and self._jobs_done():
                break

        # Close all the workers
        for worker in self._workers:
            worker.close()

        # Join and collect
        for worker in self._workers:
            worker.join()
            self._successful += worker.successful

        self._time_it_took = time.time() - self._time_it_took

        if not self._running:
            self._talk_to_gui('closed')
        else:
            self._talk_to_gui('finished')

    def active(self):
        """Returns number of active items.

        Note:
            active_items = (workers that work) + (items waiting in the url_list).

        """
        counter = 0
        for worker in self._workers:
            if not worker.available():
                counter += 1

        counter += len(self.urls_list)

        return counter

    def stop_downloads(self):
        """Stop the download process. Also send 'closing'
        signal back to the GUI.

        Note:
            It does NOT kill the workers thats the job of the
            clean up task in the run() method.

        """
        self._talk_to_gui('closing')
        self._running = False

    def add_url(self, url):
        """Add given url to the urls_list.

        Args:
            url (dictionary): Python dictionary that contains two keys.
                The url and the index of the corresponding row in which
                the worker should send back the information about the
                download process.

        """
        self.urls_list.append(url)

    def _talk_to_gui(self, data):
        """Send data back to the GUI using wxCallAfter and wxPublisher.

        Args:
            data (string): Unique signal string that informs the GUI for the
                download process.

        Note:
            DownloadManager supports 3 signals.
                1) closing: The download process is closing.
                2) closed: The download process has closed.
                3) finished: The download process was completed normally.

        """
        CallAfter(Publisher.sendMessage, MANAGER_PUB_TOPIC, data)

    def _check_youtubedl(self):
        """Check if youtube-dl binary exists. If not try to download it. """
        if not os.path.exists(self._youtubedl_path()):
            UpdateThread(self.opt_manager.options['youtubedl_path'], True).join()

    def _jobs_done(self):
        """Returns True if the workers have finished their jobs else False. """
        for worker in self._workers:
            if not worker.available():
                return False

        return True

    def _youtubedl_path(self):
        """Returns the path to youtube-dl binary. """
        path = self.opt_manager.options['youtubedl_path']
        path = os.path.join(path, YOUTUBEDL_BIN)
        return path


class Worker(Thread):

    """Simple worker which downloads the given url using a downloader
    from the 'downloaders' module.

    Attributes:
        WAIT_TIME (float): Time in seconds to sleep.

    Args:
        opt_manager (optionsmanager.OptionsManager): Check DownloadManager
            description.

        youtubedl (string): Absolute path to youtube-dl binary.

        log_manager (logmanager.LogManager): Check DownloadManager
            description.

        log_lock (threading.Lock): Synchronization lock for the log_manager.
            If the log_manager is set (not None) then the caller has to make
            sure that the log_lock is also set.

    """

    WAIT_TIME = 0.1

    def __init__(self, opt_manager, youtubedl, log_manager=None, log_lock=None):
        super(Worker, self).__init__()
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self.log_lock = log_lock

        self._downloader = YoutubeDLDownloader(youtubedl, self._data_hook, self._log_data)
        self._options_parser = OptionsParser()
        self._running = True
        self._url = None
        self._index = -1
        self._successful = 0

        self.start()

    def run(self):
        while self._running:
            if self._url is not None:
                options = self._options_parser.parse(self.opt_manager.options)
                ret_code = self._downloader.download(self._url, options)

                if (ret_code == YoutubeDLDownloader.OK or
                        ret_code == YoutubeDLDownloader.ALREADY):
                    self._successful += 1

                # Reset url value
                self._url = None

            time.sleep(self.WAIT_TIME)

        # Call the destructor function of YoutubeDLDownloader object
        self._downloader.close()

    def download(self, item):
        """Download given item.

        Args:
            item (dictionary): Python dictionary that contains two keys.
                The url and the index of the corresponding row in which
                the worker should send back the information about the
                download process.

        """
        self._url = item['url']
        self._index = item['index']

    def stop_download(self):
        """Stop the download process of the worker. """
        self._downloader.stop()

    def close(self):
        """Kill the worker after stopping the download process. """
        self._running = False
        self._downloader.stop()

    def available(self):
        """Return True if the worker has no job else False. """
        return self._url is None

    @property
    def successful(self):
        """Return the number of successful downloads for current worker. """
        return self._successful

    def _log_data(self, data):
        """Callback method for self._downloader.

        This method is used to write the given data in a synchronized way
        to the log file using the self.log_manager and the self.log_lock.

        Args:
            data (string): String to write to the log file.

        """
        if self.log_manager is not None:
            self.log_lock.acquire()
            self.log_manager.log(data)
            self.log_lock.release()

    def _data_hook(self, data):
        """Callback method to be used with the YoutubeDLDownloader object.

        This method takes the data from the downloader, merges the
        playlist_info with the current status(if any) and sends the
        data back to the GUI using the self._talk_to_gui method.

        Args:
            data (dictionary): Python dictionary which contains information
                about the download process. (See YoutubeDLDownloader class).

        """
        if data['status'] is not None and data['playlist_index'] is not None:
            playlist_info = ' '
            playlist_info += data['playlist_index']
            playlist_info += '/'
            playlist_info += data['playlist_size']

            data['status'] += playlist_info

        self._talk_to_gui(data)

    def _talk_to_gui(self, data):
        """Send data back to the GUI after inserting the index. """
        data['index'] = self._index
        CallAfter(Publisher.sendMessage, WORKER_PUB_TOPIC, data)


if __name__ == '__main__':
    """Direct call of the module for testing.

    Raises:
        ValueError: Attempted relative import in non-package

    Note:
        Before you run the tests change relative imports else an exceptions
        will be raised. You need to change relative imports on all the modules
        you are gonna use.

    """
    print "No tests available"
