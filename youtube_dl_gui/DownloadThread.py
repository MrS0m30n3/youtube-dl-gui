#! /usr/bin/env python

from time import sleep
from threading import Thread

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .YoutubeDLInterpreter import YoutubeDLInterpreter
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

    def __init__(self, downloadlist, opt_manager, logmanager=None):
        super(DownloadManager, self).__init__()
        self.downloadlist = downloadlist
        self.opt_manager = opt_manager
        self.logmanager = logmanager
        self.running = True
        self.kill = False
        self.procList = []
        self.procNo = 0
        self.start()

    def run(self):
        while self.running:
            if self.downloadlist:
                # Extract url, index from data
                url, index = self.extract_data()
                # Wait for your turn if there are not more positions in 'queue'
                while self.procNo >= self.MAX_DOWNLOAD_THREADS:
                    proc = self.check_queue()
                    if proc != None:
                        self.procList.remove(proc)
                        self.procNo -= 1
                    sleep(1)
                # If we still running create new ProcessWrapper thread
                if self.running:
                    self.procList.append(
                      DownloadThread(
                        url,
                        index,
                        self.opt_manager,
                        self.logmanager
                      )
                    )
                    self.procNo += 1
            else:
                # Return True if at least one process is alive else return False
                if not self.downloading():
                    self.running = False
                else:
                    sleep(0.1)
        # If we reach here close down all child threads
        self.terminate_all()
        if not self.kill:
            self._callafter('finish')

    def downloading(self):
        for proc in self.procList:
            if proc.isAlive():
                return True
        return False

    def _add_download_item(self, downloadItem):
        self.downloadlist.append(downloadItem)

    def extract_data(self):
        data = self.downloadlist.pop(0)
        url = data['url']
        index = data['index']
        return url, index

    def terminate_all(self):
        for proc in self.procList:
            if proc.isAlive():
                proc.close()
                proc.join()

    def check_queue(self):
        for proc in self.procList:
            if not self.running: break
            if not proc.isAlive():
                return proc
        return None
       
    def _callafter(self, data):
        CallAfter(Publisher.sendMessage, self.PUBLISHER_TOPIC, data)
       
    def close(self, kill=False):
        self.kill = kill
        self.procNo = 0
        self.running = False
        self._callafter('close')

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
        options = YoutubeDLInterpreter(self.opt_manager).get_options()
        
        self._dl_object = DownloadObject(youtubedl_path, self._data_hook, self.log_manager)
        
        success = self._dl_object.download(self.url, options)
        
        if self.opt_manager.options['clear_dash_files']:
            self._clear_dash()
            
        if success:
            self._callafter(self._get_status_pack('Finished'))
        else:
            self._callafter(self._get_status_pack('Error'))
    
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
        
        return msg
        
    def _get_youtubedl_path(self):
        ''' Retrieve youtube-dl path '''
        path = self.opt_manager.options['youtubedl_path']
        path = fix_path(path) + get_youtubedl_filename()
        return path
