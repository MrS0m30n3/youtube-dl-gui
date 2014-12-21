#!/usr/bin/env python2

''' Youtube-dlG module to download videos & handle each download. '''

import time
import os.path
from threading import Thread

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .parsers import OptionsParser
from .updthread import UpdateThread
from .downloaders import YoutubeDLDownloader

from .utils import YOUTUBEDL_BIN


class DownloadManager(Thread):
    
    """ DownloadManager """
    
    PUBLISHER_TOPIC = 'dlmanager'
    WORKERS_NUMBER = 3
    WAIT_TIME = 0.1
    
    def __init__(self, urls_list, opt_manager, log_manager=None):
        super(DownloadManager, self).__init__()
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self.urls_list = urls_list
        
        self._time_it_took = 0
        self._successful = 0
        self._running = True
        
        self._workers = self._init_workers()
        self.start()
    
    @property
    def successful(self):
        return self._successful
        
    @property
    def time_it_took(self):
        return self._time_it_took
        
    def increase_succ(self):
        self._successful += 1
    
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
                
        # Clean up
        for worker in self._workers:
            worker.close()
            worker.join()
            
        self._time_it_took = time.time() - self._time_it_took
        
        if not self._running:
            self._talk_to_gui('closed')
        else:
            self._talk_to_gui('finished')
                
    def active(self):
        counter = 0
        for worker in self._workers:
            if not worker.available():
                counter += 1
                
        counter += len(self.urls_list)
        
        return counter
    
    def stop_downloads(self):
        self._talk_to_gui('closing')
        self._running = False
        for worker in self._workers:
            worker.stop_download()
    
    def add_url(self, url):
        self.urls_list.append(url)
    
    def _talk_to_gui(self, data):
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)
    
    def _check_youtubedl(self):
        if not os.path.exists(self._youtubedl_path()):
            UpdateThread(self.opt_manager.options['youtubedl_path'], True).join()
    
    def _jobs_done(self):
        for worker in self._workers:
            if not worker.available():
                return False
                
        return True
    
    def _youtubedl_path(self):
        path = self.opt_manager.options['youtubedl_path']
        path = os.path.join(path, YOUTUBEDL_BIN)
        return path
    
    def _init_workers(self):
        youtubedl = self._youtubedl_path()
        return [Worker(self.opt_manager, youtubedl, self.increase_succ, self.log_manager) for i in xrange(self.WORKERS_NUMBER)]

        
class Worker(Thread):
    
    PUBLISHER_TOPIC = 'dlworker'
    WAIT_TIME = 0.1
    
    def __init__(self, opt_manager, youtubedl, increase_succ, log_manager=None):
        super(Worker, self).__init__()
        self.increase_succ = increase_succ
        self.opt_manager = opt_manager
        
        self._downloader = YoutubeDLDownloader(youtubedl, self._data_hook, log_manager)
        self._options_parser = OptionsParser()
        self._running = True
        self._url = None
        self._index = -1
        
        self.start()
        
    def run(self):
        while self._running:
            if self._url is not None:
                options = self._options_parser.parse(self.opt_manager.options)                
                ret_code = self._downloader.download(self._url, options)
            
                if (ret_code == YoutubeDLDownloader.OK or
                        ret_code == YoutubeDLDownloader.ALREADY):
                    self.increase_succ()
                
                # Reset
                self._url = None
            
            time.sleep(self.WAIT_TIME)
    
    def download(self, item):
        self._url = item['url']
        self._index = item['index']
    
    def stop_download(self):
        self._downloader.stop()
    
    def close(self):
        self._running = False
        self._downloader.stop()
    
    def available(self):
        return self._url is None
    
    def _data_hook(self, data):
        if data['status'] is not None and data['playlist_index'] is not None:
            playlist_info = ' '
            playlist_info += data['playlist_index']
            playlist_info += '/'
            playlist_info += data['playlist_size']
                
            data['status'] += playlist_info

        self._talk_to_gui(data)
    
    def _talk_to_gui(self, data):
        data['index'] = self._index
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)

        
if __name__ == '__main__':
    ''' Direct call of module for testing. Before
    you run the tests change relative imports or you will
    get [ValueError: Attempted relative import in non-package].
    You need to change relative imports on all the modules
    you are gonna use.'''
    print "No tests available"
        
