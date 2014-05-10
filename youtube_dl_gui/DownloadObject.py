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
            Return: On download error return False else True.

        stop()
            Params: None

    Acessible Variables
        files_list: Python list that contains all the files DownloadObject
                    instance has downloaded.

    Data_hook Keys
        See self._init_data().
    '''

    STDERR_IGNORE = ''  # Default filter for our self._log() method

    def __init__(self, youtubedl_path, data_hook=None, logger=None):
        self.youtubedl_path = youtubedl_path
        self.data_hook = data_hook
        self.logger = logger
        self.files_list = []
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
        ''' Download url using given options list. '''
        error = False

        cmd = self._get_cmd(url, options)
        cmd = self._encode_cmd(cmd)
        info = self._get_process_info()

        self._proc = self._create_process(cmd, info)

        while self._proc_is_alive():
            stdout, stderr = self._read()

            data = extract_data(stdout)
            synced = self._sync_data(data)

            if stderr != '':
                error = True

            if self.logger is not None:
                self._log(stderr)

            if self.data_hook is not None and synced:
                self._hook_data()

        return (not error)

    def stop(self):
        ''' Stop download process. '''
        if self._proc is not None:
            self._proc.kill()

    def _sync_data(self, data):
        ''' Sync data between extract_data() dictionary and self._data.
        Return True if synced else return False.
        '''
        synced = False
        for key in data:
            if key == 'filename':
                # Save full file path on files_list
                self._add_on_files_list(data['filename'])
                # Keep only the filename not the path on data['filename']
                data['filename'] = get_filename(data['filename'])

            self._data[key] = data[key]
            synced = True

        return synced

    def _add_on_files_list(self, filename):
        ''' Add filename on files_list. '''
        self.files_list.append(filename)

    def _log(self, data):
        if data != self.STDERR_IGNORE:
            self.logger.log(data)

    def _hook_data(self):
        ''' Pass self._data back to data_hook. '''
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
        ''' Read subprocess stdout. '''
        if self._proc is None:
            return ''

        stdout = self._proc.stdout.readline()
        return stdout.rstrip()

    def _read_stderr(self):
        ''' Read subprocess stderr. '''
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

    header = stdout.pop(0).replace('[', '').replace(']', '')

    if header == 'download':
        data_dictionary['status'] = 'download'

        if stdout[0] == 'Destination:':
            data_dictionary['filename'] = ' '.join(stdout[1:])

        elif '%' in stdout[0]:
            if stdout[0] == '100%':
                data_dictionary['speed'] = ''
            else:
                data_dictionary['percent'] = stdout[0]
                data_dictionary['filesize'] = stdout[2]
                data_dictionary['speed'] = stdout[4]
                data_dictionary['eta'] = stdout[6]

        elif stdout[0] == 'Downloading' and stdout[1] == 'video':
            data_dictionary['playlist_index'] = stdout[2]
            data_dictionary['playlist_size'] = stdout[4]

    if header == 'ffmpeg':
        data_dictionary['status'] = 'post_process'

    if header == 'youtube':
        data_dictionary['status'] = 'pre_process'

    return data_dictionary
