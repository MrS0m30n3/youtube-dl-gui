#!/usr/bin/env python2

''' Python module to download videos using youtube-dl & subprocess. '''

import os
import sys
import locale
import subprocess


class YoutubeDLDownloader(object):

    '''
    OUT_OF_DATE
    Download videos using youtube-dl & subprocess.

    Params
        youtubedl_path: Absolute path of youtube-dl.
        data_hook: Can be any function with one parameter, the data.
        log_manager: Can be any log_manager which implements log().

    Accessible Methods
        download()
            Params: URL to download
                    Options list e.g. ['--help']

            Return: DownlaodObject.OK
                    YoutubeDLDownloader.ERROR
                    YoutubeDLDownloader.STOPPED
                    YoutubeDLDownloader.ALREADY
        stop()
            Params: None

            Return: None

    Data_hook Keys
        'playlist_index',
        'playlist_size',
        'filesize',
        'filename',
        'percent',
        'status',
        'speed',
        'eta'
    '''

    # download() return codes
    OK = 0
    ERROR = 1
    STOPPED = 2
    ALREADY = 3

    def __init__(self, youtubedl_path, data_hook=None, log_manager=None):
        self.youtubedl_path = youtubedl_path
        self.log_manager = log_manager
        self.data_hook = data_hook

        self._return_code = 0
        self._proc = None
        self._data = {
            'playlist_index': None,
            'playlist_size': None,
            'filesize': None,
            'filename': None,
            'percent': None,
            'status': None,
            'speed': None,
            'eta': None
        }

    def download(self, url, options):
        ''' Download given url using youtube-dl &
        return self._return_code.
        '''
        self._return_code = self.OK

        cmd = self._get_cmd(url, options)
        self._create_process(cmd)

        while self._proc_is_alive():
            stdout, stderr = self._read()

            if stderr:
                self._return_code = self.ERROR
                self._log(stderr)
            
            if stdout:
                self._sync_data(extract_data(stdout))
                self._hook_data()

        self._last_data_hook()
            
        return self._return_code

    def stop(self):
        ''' Stop downloading. '''
        if self._proc_is_alive():
            self._proc.kill()
            self._return_code = self.STOPPED

    def _last_data_hook(self):
        if self._return_code == self.OK:
            self._data['status'] = 'Finished'
        elif self._return_code == self.ERROR:
            self._data['status'] = 'Error'
            self._data['speed'] = ''
            self._data['eta'] = ''
        elif self._return_code == self.STOPPED:
            self._data['status'] = 'Stopped'
            self._data['speed'] = ''
            self._data['eta'] = ''
        else:
            self._data['status'] = 'Already Downloaded'
            
        self._hook_data()
            
    def _sync_data(self, data):
        ''' Synchronise self._data with data. '''
        for key in data:
            if key == 'filename':
                # Keep only the filename on data['filename']
                data['filename'] = os.path.basename(data['filename'])

            if key == 'status' and data['status'] == 'Already Downloaded':
                # Set self._return_code to already downloaded
                # and trash that key (GUI won't read it if it's None)
                self._return_code = self.ALREADY
                data['status'] = None

            self._data[key] = data[key]

    def _log(self, data):
        ''' Log data using self.log_manager. '''
        if self.log_manager is not None:
            self.log_manager.log(data)

    def _hook_data(self):
        ''' Pass self._data back to data_hook. '''
        if self.data_hook is not None:
            self.data_hook(self._data)

    def _proc_is_alive(self):
        ''' Return True if self._proc is alive. '''
        if self._proc is None:
            return False

        return self._proc.poll() is None

    def _read(self):
        ''' Read subprocess stdout, stderr. '''
        stdout = stderr = ''

        stdout = self._read_stream(self._proc.stdout)

        if not stdout:
            stderr = self._read_stream(self._proc.stderr)

        return stdout, stderr

    def _read_stream(self, stream):
        ''' Read subprocess stream. '''
        if self._proc is None:
            return ''

        return stream.readline().rstrip()

    def _get_cmd(self, url, options):
        ''' Return command for subprocess. '''
        if os.name == 'nt':
            cmd = [self.youtubedl_path] + options + [url]
        else:
            cmd = ['python', self.youtubedl_path] + options + [url]

        return cmd

    def _create_process(self, cmd):
        ''' Create new subprocess. '''
        encoding = info = None

        # Hide subprocess window on Windows
        if os.name == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # Encode command for subprocess
        # Refer to http://stackoverflow.com/a/9951851/35070
        if sys.version_info < (3, 0) and sys.platform == 'win32':
            try:
                encoding = locale.getpreferredencoding()
                u'TEST'.encode(encoding)
            except:
                encoding = 'UTF-8'

        if encoding is not None:
            cmd = [item.encode(encoding, 'ignore') for item in cmd]

        self._proc = subprocess.Popen(cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      startupinfo=info)


def extract_data(stdout):
    ''' Extract data from youtube-dl stdout. '''
    data_dictionary = dict()
        
    if not stdout:
        return data_dictionary
        
    stdout = [string for string in stdout.split(' ') if string != '']

    if stdout[0] == '[download]':
        data_dictionary['status'] = 'Downloading'

        # Get filename
        if stdout[1] == 'Destination:':
            data_dictionary['filename'] = ' '.join(stdout[1:])

        # Get progress info
        if '%' in stdout[1]:
            if stdout[1] == '100%':
                data_dictionary['speed'] = ''
                data_dictionary['eta'] = ''
            else:
                data_dictionary['percent'] = stdout[1]
                data_dictionary['filesize'] = stdout[3]
                data_dictionary['speed'] = stdout[5]
                data_dictionary['eta'] = stdout[7]

        # Get playlist info
        if stdout[1] == 'Downloading' and stdout[2] == 'video':
            data_dictionary['playlist_index'] = stdout[3]
            data_dictionary['playlist_size'] = stdout[5]

        # Get file already downloaded status
        if stdout[-1] == 'downloaded':
            data_dictionary['status'] = 'Already Downloaded'

    elif stdout[0] == '[ffmpeg]':
        data_dictionary['status'] = 'Post Processing'

    else:
        data_dictionary['status'] = 'Pre Processing'

    return data_dictionary
