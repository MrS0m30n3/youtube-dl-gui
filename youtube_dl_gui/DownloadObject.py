#! /usr/bin/env python

import subprocess

from .Utils import (
    get_encoding,
    get_filename,
    encode_list,
    os_type
)


class DownloadObject(object):

    '''
    Download videos using youtube-dl & subprocess.

    Params
        youtubedl_path: Absolute path of youtube-dl.
        data_hook: Can be any function with one parameter, the data.
        logger: Can be any logger which implements log().

    Accessible Methods
        download()
            Params: URL to download
                    Options list e.g. ['--help']
            
            Return: DownlaodObject.OK
                    DownloadObject.ERROR
                    DownloadObject.STOPPED
                    DownloadObject.ALREADY
        stop()
            Params: None

    Acessible Variables
        files_list: Python list that contains all the files DownloadObject
                    instance has downloaded.

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

    def __init__(self, youtubedl_path, data_hook=None, logger=None):
        self.youtubedl_path = youtubedl_path
        self.data_hook = data_hook
        self.logger = logger
        self.files_list = []
        self._return_code = 0
        self._proc = None
        self._init_data()

    def _init_data(self):
        ''' Keep the __init__() clean. '''
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
        self._return_code = self.OK

        cmd = self._get_cmd(url, options)
        cmd = self._encode_cmd(cmd)
        info = self._get_process_info()

        self._proc = self._create_process(cmd, info)

        while self._proc_is_alive():
            stdout, stderr = self._read()

            data = extract_data(stdout)
            updated = self._update_data(data)

            if stderr != '':
                self._return_code = self.ERROR
                self._log(stderr)

            if updated:
                self._hook_data()

        return self._return_code

    def stop(self):
        if self._proc is not None:
            self._proc.kill()
            self._return_code = self.STOPPED

    def _update_data(self, data):
        ''' Update self._data from data.
        Return True if updated else return False.
        '''
        updated = False
        
        for key in data:
            if key == 'filename':
                # Save full file path on files_list
                self._add_on_files_list(data['filename'])
                # Keep only the filename not the path on data['filename']
                data['filename'] = get_filename(data['filename'])

            if key == 'status':
                # Set self._return_code to already downloaded
                if data[key] == 'already_downloaded':
                    self._return_code = self.ALREADY
                    # Trash that key
                    data[key] = None

            self._data[key] = data[key]
            updated = True

        return updated

    def _add_on_files_list(self, filename):
        self.files_list.append(filename)

    def _log(self, data):
        if self.logger is not None:
            self.logger.log(data)

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
        stdout = self._read_stdout()
        if stdout == '':
            stderr = self._read_stderr()
        else:
            stderr = ''
        return stdout, stderr

    def _read_stdout(self):
        if self._proc is None:
            return ''

        stdout = self._proc.stdout.readline()
        return stdout.rstrip()

    def _read_stderr(self):
        if self._proc is None:
            return ''

        stderr = self._proc.stderr.readline()
        return stderr.rstrip()

    def _create_process(self, cmd, info):
        return subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                startupinfo=info)

    def _get_cmd(self, url, options):
        ''' Return command for subprocess. '''
        if os_type == 'nt':
            cmd = [self.youtubedl_path] + options + [url]
        else:
            cmd = ['python', self.youtubedl_path] + options + [url]
        return cmd

    def _encode_cmd(self, cmd):
        ''' Encode command for subprocess.
        Refer to http://stackoverflow.com/a/9951851/35070
        '''
        encoding = get_encoding()
        if encoding is not None:
            cmd = encode_list(cmd, encoding)
        return cmd

    def _get_process_info(self):
        ''' Hide subprocess window on Windows. '''
        if os_type == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            return info
        else:
            return None


def extract_data(stdout):
    ''' Extract data from youtube-dl stdout. '''
    data_dictionary = {}

    stdout = [s for s in stdout.split(' ') if s != '']

    if len(stdout) == 0:
        return data_dictionary

    header = stdout.pop(0)

    if header[0] == '[' and header[-1] == ']':
        header = header.replace('[', '').replace(']', '')
        
        if header == 'download':
            data_dictionary['status'] = 'download'

            # Get filename
            if stdout[0] == 'Destination:':
                data_dictionary['filename'] = ' '.join(stdout[1:])

            # Get progress info
            if '%' in stdout[0]:
                if stdout[0] == '100%':
                    data_dictionary['speed'] = ''
                    data_dictionary['eta'] = ''
                else:
                    data_dictionary['percent'] = stdout[0]
                    data_dictionary['filesize'] = stdout[2]
                    data_dictionary['speed'] = stdout[4]
                    data_dictionary['eta'] = stdout[6]

            # Get playlist info
            if stdout[0] == 'Downloading' and stdout[1] == 'video':
                data_dictionary['playlist_index'] = stdout[2]
                data_dictionary['playlist_size'] = stdout[4]

            # Get file already downloaded status
            if stdout[-1] == 'downloaded':
                data_dictionary['status'] = 'already_downloaded'

        elif header == 'ffmpeg':
            data_dictionary['status'] = 'post_process'
            
        else:
            data_dictionary['status'] = 'pre_process'

    return data_dictionary

