#! /usr/bin/env python

from time import sleep
from threading import Thread

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .YDLOptionsParser import OptionsParser
from .DownloadObject import DownloadObject

from .Utils import (
    get_youtubedl_filename,
    remove_file,
    file_exist,
    fix_path
)


class DownloadManager(Thread):

    PUBLISHER_TOPIC = 'download_manager'
    MAX_DOWNLOAD_THREADS = 3

    def __init__(self, download_list, opt_manager, log_manager=None):
        super(DownloadManager, self).__init__()
        self.download_list = download_list
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self.stopped = False
        self._threads_lst = []
        self._running = True
        self._kill = False
        self.start()

    def run(self):
        while self._running:
            # If download list is not empty
            if self.download_list:
                url, index = self._extract_data()

                self._check_download_queue()

                if self._running:
                    self._download(url, index)
            else:
                if not self.downloading():
                    self._running = False
                else:
                    sleep(0.1)

        self._terminate_all()
        if not self._kill:
            self._callafter('finish')

    def downloading(self):
        ''' Return True if at least one download thread is alive '''
        for thread in self._threads_lst:
            if thread.is_alive():
                return True
        return False

    def add_download_item(self, item):
        ''' Add download item on download list '''
        self.download_list.append(item)

    def close(self, kill=False):
        self._callafter('close')
        self._running = False
        self._kill = kill
        self.stopped = True

    def _download(self, url, index):
        ''' Download given url '''
        dl_thread = DownloadThread(url, index, self.opt_manager, self.log_manager)
        self._threads_lst.append(dl_thread)

    def _extract_data(self):
        ''' Extract url, index from download list '''
        data = self.download_list.pop(0)
        url = data['url']
        index = data['index']
        return url, index

    def _terminate_all(self):
        ''' Close down all download threads '''
        for thread in self._threads_lst:
            if thread.is_alive():
                thread.close()
                thread.join()

    def _check_download_queue(self):
        while len(self._threads_lst) >= self.MAX_DOWNLOAD_THREADS:
            sleep(1)
            for thread in self._threads_lst:
                if not self._running:
                    return
                if not thread.is_alive():
                    self._threads_lst.remove(thread)

    def _callafter(self, data):
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)


class DownloadThread(Thread):

    '''
    Params
        url: URL to download.
        index: ListCtrl index for the current DownloadThread.
        opt_manager: OptionsHandler.OptionsHandler object.
        log_manager: Any logger which implements log().

    Accessible Methods
        close()
            Params: None
    '''

    PUBLISHER_TOPIC = 'download_thread'

    def __init__(self, url, index, opt_manager, log_manager=None):
        super(DownloadThread, self).__init__()
        self.log_manager = log_manager
        self.opt_manager = opt_manager
        self.index = index
        self.url = url
        self._dl_object = None
        self.start()

    def run(self):
        youtubedl_path = self._get_youtubedl_path()
        options = OptionsParser(self.opt_manager).parse()

        self._dl_object = DownloadObject(youtubedl_path, self._data_hook, self.log_manager)

        return_code = self._dl_object.download(self.url, options)

        if self.opt_manager.options['clear_dash_files']:
            self._clear_dash()

        if return_code == self._dl_object.OK:
            self._callafter(self._get_status_pack('Finished'))

        elif return_code == self._dl_object.ERROR:
            self._callafter(self._get_status_pack('Error'))

        elif return_code == self._dl_object.ALREADY:
            self._callafter(self._get_status_pack('Already-Downloaded'))

    def close(self):
        if self._dl_object is not None:
            self._callafter(self._get_status_pack('Stopping'))
            self._dl_object.stop()

    def _clear_dash(self):
        ''' Clear DASH files after ffmpeg mux '''
        for fl in self._dl_object.files_list:
            if file_exist(fl):
                remove_file(fl)

    def _data_hook(self, data):
        ''' Add download index and send data back to caller '''
        data['index'] = self.index
        data['status'] = self._get_status(data)
        self._callafter(data)

    def _callafter(self, data):
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)

    def _get_status_pack(self, message):
        ''' Return simple status pack '''
        data = {'index': self.index, 'status': message}
        return data

    def _get_status(self, data):
        ''' Return download process status '''
        if data['playlist_index'] is not None:
            playlist_info = '%s/%s' % (data['playlist_index'], data['playlist_size'])
        else:
            playlist_info = ''

        if data['status'] == 'pre_process':
            msg = 'Pre-Processing %s' % playlist_info
        elif data['status'] == 'download':
            msg = 'Downloading %s' % playlist_info
        elif data['status'] == 'post_process':
            msg = 'Post-Processing %s' % playlist_info
        else:
            msg = ''

        return msg

    def _get_youtubedl_path(self):
        ''' Retrieve youtube-dl path '''
        path = self.opt_manager.options['youtubedl_path']
        path = fix_path(path) + get_youtubedl_filename()
        return path
