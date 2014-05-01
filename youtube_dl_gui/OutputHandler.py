#! /usr/bin/env python

from .Utils import (
    remove_empty_items,
    string_to_array,
    get_filename
)

class DownloadHandler():

    def __init__(self, ListCtrl):
        self.ListCtrl = ListCtrl
        self.finished = False
        self.closed = False
        self.error = False
        self.init_handlers()

    def init_handlers(self):
        ''' Initialise handlers '''
        self.handlers = [None for i in range(self.ListCtrl.ListIndex)]

    def _has_closed(self):
        return self.closed

    def _has_finished(self):
        return self.finished

    def _has_error(self):
        return self.error

    def _add_empty_handler(self):
        self.handlers.append(None)

    def handle(self, msg):
        ''' Handles msg base to Signals.txt '''
        pack = msg.data
        if pack.index == -1:
            self.global_handler(pack)
        else:
            self.index_handler(pack)

    def global_handler(self, pack):
        ''' Manage global index = -1 '''
        if pack.header == 'close':
            self.closed = True
        elif pack.header == 'finish':
            self.finished = True

    def index_handler(self, pack):
        ''' Manage handlers base on index '''
        if self.handlers[pack.index] == None:
            self.handlers[pack.index] = IndexDownloadHandler(self.ListCtrl, pack.index)
        self.handlers[pack.index].handle(pack)
        if self.handlers[pack.index].has_error():
            self.error = True

class IndexDownloadHandler():

    def __init__(self, ListCtrl, index):
        self.ListCtrl = ListCtrl
        self.index = index
        self.err = False
        self.info = ''

    def has_error(self):
        return self.err

    def handle(self, pack):
        ''' Handle its pack for current index '''
        if pack.header == 'finish':
            self.finish()
        elif pack.header == 'close':
            self.close()
        elif pack.header == 'error':
            self.error()
        elif pack.header == 'playlist':
            self.playlist(pack.data)
        elif pack.header == 'youtube':
            self.pre_proc()
        elif pack.header == 'download':
            self.download(pack.data)
        elif pack.header == 'ffmpeg':
            self.post_proc()
        elif pack.header == 'remove':
            self.remove()
        elif pack.header == 'filename':
            self.filename(pack.data)

    def finish(self):
        self.ListCtrl._write_data(self.index, 4, '')
        self.ListCtrl._write_data(self.index, 5, 'Finished')

    def close(self):
        self.ListCtrl._write_data(self.index, 3, '')
        self.ListCtrl._write_data(self.index, 4, '')
        self.ListCtrl._write_data(self.index, 5, 'Stopped')

    def error(self):
        self.err = True
        self.ListCtrl._write_data(self.index, 3, '')
        self.ListCtrl._write_data(self.index, 4, '')
        self.ListCtrl._write_data(self.index, 5, 'Error')

    def pre_proc(self):
        self.ListCtrl._write_data(self.index, 5, 'Pre-Processing %s' % self.info)

    def post_proc(self):
        self.ListCtrl._write_data(self.index, 4, '')
        self.ListCtrl._write_data(self.index, 5, 'Post-Processing %s' % self.info)

    def download(self, data):
        self.ListCtrl._write_data(self.index, 1, data[0])
        self.ListCtrl._write_data(self.index, 2, data[1])
        self.ListCtrl._write_data(self.index, 3, data[2])
        self.ListCtrl._write_data(self.index, 4, data[3])
        self.ListCtrl._write_data(self.index, 5, 'Downloading %s' % self.info)

    def playlist(self, data):
        self.ListCtrl._write_data(self.index, 1, '')
        self.ListCtrl._write_data(self.index, 2, '')
        self.ListCtrl._write_data(self.index, 3, '')
        self.ListCtrl._write_data(self.index, 4, '')
        self.info = '%s/%s' % (data[0], data[1])

    def remove(self):
        self.ListCtrl._write_data(self.index, 5, 'Removing DASH Files')

    def filename(self, fl):
        self.ListCtrl._write_data(self.index, 0, get_filename(fl))

class DataPack():

    def __init__(self, header, index=-1, data=None):
        self.header = header
        self.index = index
        self.data = data

class OutputFormatter():

    def __init__(self, stdout):
        dataPack = None

        self.stdout = remove_empty_items(string_to_array(stdout))
        # extract header from stdout
        header = self.extract_header()
        # extract special headers filename, playlist
        header = self.set_filename_header(header)
        header = self.set_playlist_header(header)
        # extract data base on header
        data = self.extract_data(header)
        # extract special ignore header base on header, data
        header = self.set_ignore_header(header, data)
        # create data pack
        self.dataPack = DataPack(header, data=data)

    def extract_header(self):
        header = self.stdout.pop(0).replace('[', '').replace(']', '')
        return header

    def extract_data(self, header):
        ''' Extract data base on header '''
        if header == 'download':
            if '%' in self.stdout[0]:
                if self.stdout[0] != '100%':
                    ''' size, percent, eta, speed '''
                    return [self.stdout[2], self.stdout[0], self.stdout[6], self.stdout[4]]
        if header == 'playlist':
            return [self.stdout[2], self.stdout[4]]
        if header == 'filename':
            return ' '.join(self.stdout[1:])
        return None

    def set_filename_header(self, header):
        if header != 'ffmpeg':
            if self.stdout[0] == 'Destination:':
                return 'filename'
        return header

    def set_playlist_header(self, header):
        if header == 'download':
            if self.stdout[0] == 'Downloading' and self.stdout[1] == 'video':
                return 'playlist'
        return header

    def set_ignore_header(self, header, data):
        if header == 'download' and data == None:
            return 'ignore'
        return header

    def get_data(self):
        return self.dataPack
