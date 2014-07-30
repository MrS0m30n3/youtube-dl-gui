#!/usr/bin/env python2

''' Youtube-dlG module to download videos & handle each download. '''

import time
from threading import Thread

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .OptionsParser import OptionsParser
from .DownloadObject import DownloadObject

from .utils import (
    get_youtubedl_filename,
    fix_path
)


class DownloadManager(Thread):

    '''
    Manage youtube-dlG download list.

    Params
        threads_list: Python list that contains DownloadThread objects.

        update_thread: UpdateThread.py thread.
        
    Accessible Methods
        close()
            Params: None

            Return: None

        add_thread()
            Params: DownloadThread object

            Return: None

        alive_threads()
            Params: None

            Return: Number of alive threads.

        not_finished()
            Params: None

            Return: Number of threads not finished yet.

    Properties
        successful_downloads: Number of successful downloads.
        time: Time (seconds) it took for all downloads to complete.
    '''

    PUBLISHER_TOPIC = 'dlmanager'
    MAX_DOWNLOAD_THREADS = 3

    def __init__(self, threads_list, update_thread=None):
        super(DownloadManager, self).__init__()
        self.threads_list = threads_list
        self.update_thread = update_thread
        self._successful_downloads = 0
        self._running = True
        self._time = 0
        self.start()

    def run(self):
        if self.update_thread is not None:
            self.update_thread.join()
        
        self._time = time.time()

        # Main loop
        while self._running and not self._threads_finished():
            for thread in self.threads_list:
                if not self._running:
                    break

                self._start_thread(thread)
                
            time.sleep(0.1)

        # Make sure no child thread is alive
        for thread in self.threads_list:
            if thread.is_alive():
                thread.join()

            # Collect thread status
            if thread.status == 0:
                self._successful_downloads += 1

        self._time = time.time() - self._time

        if not self._running:
            self._callafter('closed')
        else:
            self._callafter('finished')

    @property
    def time(self):
        ''' Return time it took for every download to finish. '''
        return self._time

    @property
    def successful_downloads(self):
        ''' Return number of successful downloads. '''
        return self._successful_downloads

    def close(self):
        ''' Close DownloadManager. '''
        self._callafter('closing')
        self._running = False
        for thread in self.threads_list:
            thread.close()

    def add_thread(self, thread):
        ''' Add new DownloadThread on self.threads_list. '''
        self.threads_list.append(thread)

    def alive_threads(self):
        ''' Return number of alive threads in self.threads_list. '''
        counter = 0

        for thread in self.threads_list:
            if thread.is_alive():
                counter += 1

        return counter

    def not_finished(self):
        ''' Return number of threads not finished. '''
        counter = 0

        for thread in self.threads_list:
            if thread.ident is None or thread.is_alive():
                counter += 1

        return counter

    def _start_thread(self, thread):
        ''' Start given thread if not download queue full. '''
        while self.alive_threads() >= self.MAX_DOWNLOAD_THREADS:
            time.sleep(1)

            if not self._running:
                break

        # If thread has not started
        if thread.ident is None and self._running:
            thread.start()

    def _threads_finished(self):
        ''' Return True if all threads in self.threads_list have finished. '''
        for thread in self.threads_list:
            # If thread has not started or thread is alive
            if thread.ident is None or thread.is_alive():
                return False

        return True

    def _callafter(self, data):
        ''' CallAfter wrapper. '''
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)


class DownloadThread(Thread):

    '''
    DownloadObject Thread wrapper for youtube-dlg.

    Params
        url: Video url to download.
        index: ListCtrl corresponding row for current thread.
        opt_manager: OptionsManager.OptionsManager object.
        log_manager: Any logger which implements log().

    Accessible Methods
        close()
            Params: None

            Return: None

    Properties
        status: Thread status.
    '''

    PUBLISHER_TOPIC = 'dlthread'

    def __init__(self, url, index, opt_manager, log_manager=None):
        super(DownloadThread, self).__init__()
        self.url = url
        self.index = index
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self._downloader = None
        self._status = 0

    def run(self):
        self._downloader = DownloadObject(
            self._get_youtubedl_path(),
            self._data_hook,
            self.log_manager
        )

        options = OptionsParser(self.opt_manager).parse()

        return_code = self._downloader.download(self.url, options)

        if return_code == DownloadObject.OK:
            self._callafter({'status': 'Finished'})
        elif return_code == DownloadObject.ERROR:
            self._callafter({'status': 'Error', 'speed': '', 'eta': ''})
            self._status = 1
        elif return_code == DownloadObject.STOPPED:
            self._callafter({'status': 'Stopped', 'speed': '', 'eta': ''})
            self._status = 1
        elif return_code == DownloadObject.ALREADY:
            self._callafter({'status': 'Already-Downloaded'})

    @property
    def status(self):
        ''' Return thread status. Use this property after
        thread has joined. (self._status != 0) indicates there was
        an error.
        '''
        return self._status

    def close(self):
        ''' Close download thread. '''
        if self._downloader is not None:
            self._downloader.stop()

    def _data_hook(self, data):
        ''' Merge playlist_info with data['status'] and
        pass data to self._callafter.
        '''
        playlist_info = ''

        if data['playlist_index'] is not None:
            playlist_info = data['playlist_index']
            playlist_info += '/'
            playlist_info += data['playlist_size']

        if data['status'] is not None:
            data['status'] = data['status'] + ' ' + playlist_info

        self._callafter(data)

    def _callafter(self, data):
        ''' Add self.index on data and send data back to caller. '''
        data['index'] = self.index
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)

    def _get_youtubedl_path(self):
        ''' Retrieve youtube-dl path. '''
        path = self.opt_manager.options['youtubedl_path']
        path = fix_path(path) + get_youtubedl_filename()
        return path
