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

from .utils import (
    YOUTUBEDL_BIN,
    os_path_exists
)


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

            self._talk_to_gui('report_active')

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
            url (dict): Python dictionary that contains two keys.
                The url and the index of the corresponding row in which
                the worker should send back the information about the
                download process.

        """
        self.urls_list.append(url)

    def send_to_worker(self, data):
        """Send data to the Workers.

        Args:
            data (dict): Python dictionary that holds the 'index'
            which is used to identify the Worker thread and the data which
            can be any of the Worker's class valid data. For a list of valid
            data keys see __init__() under the Worker class.

        """
        if 'index' in data:
            for worker in self._workers:
                if worker.has_index(data['index']):
                    worker.update_data(data)

    def _talk_to_gui(self, data):
        """Send data back to the GUI using wxCallAfter and wxPublisher.

        Args:
            data (string): Unique signal string that informs the GUI for the
                download process.

        Note:
            DownloadManager supports 4 signals.
                1) closing: The download process is closing.
                2) closed: The download process has closed.
                3) finished: The download process was completed normally.
                4) report_active: Signal the gui to read the number of active
                    downloads using the active() method.

        """
        CallAfter(Publisher.sendMessage, MANAGER_PUB_TOPIC, data)

    def _check_youtubedl(self):
        """Check if youtube-dl binary exists. If not try to download it. """
        if not os_path_exists(self._youtubedl_path()):
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
    from the downloaders.py module.

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

    Note:
        For available data keys see self._data under the __init__() method.

    """

    WAIT_TIME = 0.1

    def __init__(self, opt_manager, youtubedl, log_manager=None, log_lock=None):
        super(Worker, self).__init__()
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self.log_lock = log_lock

        self._downloader = YoutubeDLDownloader(youtubedl, self._data_hook, self._log_data)
        self._options_parser = OptionsParser()
        self._successful = 0
        self._running = True

        self._wait_for_reply = False

        self._data = {
            'playlist_index': None,
            'playlist_size': None,
            'new_filename': None,
            'extension': None,
            'filesize': None,
            'filename': None,
            'percent': None,
            'status': None,
            'index': None,
            'speed': None,
            'path': None,
            'eta': None,
            'url': None
        }

        self.start()

    def run(self):
        while self._running:
            if self._data['url'] is not None:
                options = self._options_parser.parse(self.opt_manager.options)
                ret_code = self._downloader.download(self._data['url'], options)

                if (ret_code == YoutubeDLDownloader.OK or
                        ret_code == YoutubeDLDownloader.ALREADY):
                    self._successful += 1

                # Ask GUI for name updates
                self._talk_to_gui('receive', {'source': 'filename', 'dest': 'new_filename'})

                # Wait until you get a reply
                while self._wait_for_reply:
                    time.sleep(self.WAIT_TIME)

                self._reset()

            time.sleep(self.WAIT_TIME)

        # Call the destructor function of YoutubeDLDownloader object
        self._downloader.close()

    def download(self, item):
        """Download given item.

        Args:
            item (dict): Python dictionary that contains two keys.
                The url and the index of the corresponding row in which
                the worker should send back the information about the
                download process.

        """
        self._data['url'] = item['url']
        self._data['index'] = item['index']

    def stop_download(self):
        """Stop the download process of the worker. """
        self._downloader.stop()

    def close(self):
        """Kill the worker after stopping the download process. """
        self._running = False
        self._downloader.stop()

    def available(self):
        """Return True if the worker has no job else False. """
        return self._data['url'] is None

    def has_index(self, index):
        """Return True if index is equal to self._data['index'] else False. """
        return self._data['index'] == index

    def update_data(self, data):
        """Update self._data from the given data. """
        if self._wait_for_reply:
            # Update data only if a receive request has been issued
            for key in data:
                self._data[key] = data[key]

            self._wait_for_reply = False

    @property
    def successful(self):
        """Return the number of successful downloads for current worker. """
        return self._successful

    def _reset(self):
        """Reset self._data back to the original state. """
        for key in self._data:
            self._data[key] = None

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
        """Callback method for self._downloader.

        This method updates self._data and sends the updates back to the
        GUI using the self._talk_to_gui() method.

        Args:
            data (dict): Python dictionary which contains information
                about the download process. For more info see the
                extract_data() function under the downloaders.py module.

        """
        # Temp dictionary which holds the updates
        temp_dict = {}

        # Update each key
        for key in data:
            if self._data[key] != data[key]:
                self._data[key] = data[key]
                temp_dict[key] = data[key]

        # Build the playlist status if there is an update
        if self._data['playlist_index'] is not None:
            if 'status' in temp_dict or 'playlist_index' in temp_dict:
                temp_dict['status'] = '{status} {index}/{size}'.format(
                        status=self._data['status'],
                        index=self._data['playlist_index'],
                        size=self._data['playlist_size']
                    )

        if len(temp_dict):
            self._talk_to_gui('send', temp_dict)

    def _talk_to_gui(self, signal, data):
        """Communicate with the GUI using wxCallAfter and wxPublisher.

        Send/Ask data to/from the GUI. Note that if the signal is 'receive'
        then the Worker will wait until it receives a reply from the GUI.

        Args:
            signal (string): Unique string that informs the GUI about the
                communication procedure.

            data (dict): Python dictionary which holds the data to be sent
                back to the GUI. If the signal is 'send' then the dictionary
                contains the updates for the GUI (e.g. percentage, eta). If
                the signal is 'receive' then the dictionary contains exactly
                three keys. The 'index' (row) from which we want to retrieve
                the data, the 'source' which identifies a column in the
                wxListCtrl widget and the 'dest' which tells the wxListCtrl
                under which key to store the retrieved data.

        Note:
            Worker class supports 2 signals.
                1) send: The Worker sends data back to the GUI
                         (e.g. Send status updates).
                2) receive: The Worker asks data from the GUI
                            (e.g. Receive the name of a file).

        Structure:
            ('send', {'index': <item_row>, data_to_send*})

            ('receive', {'index': <item_row>, 'source': 'source_key', 'dest': 'destination_key'})

        """
        data['index'] = self._data['index']

        if signal == 'receive':
            self._wait_for_reply = True

        CallAfter(Publisher.sendMessage, WORKER_PUB_TOPIC, (signal, data))

