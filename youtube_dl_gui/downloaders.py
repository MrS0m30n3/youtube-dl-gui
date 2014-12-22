#!/usr/bin/env python2

"""Python module to download videos. 

This module contains the actual downloaders responsible 
for downloading the video files. It's more like a driver module 
that connects the youtubedlg with different 3rd party (or not) downloaders.

Note:
    downloaders.py is part of the youtubedlg package but it can be used
    as a stand alone driver module for downloading videos.

"""

import os
import sys
import locale
import subprocess


class YoutubeDLDownloader(object):

    """Python class for downloading videos using youtube-dl & subprocess.
    
    Attributes:
        OK, ERROR, STOPPED, ALREADY, FILESIZE_ABORT (int): 'Random' integers 
        that describe the return code from the download() method.
        
    Args:
        youtubedl_path (string): Absolute path to youtube-dl binary.
        
        data_hook (function): Optional callback function to retrieve download 
            process data. 
            
        log_manager (logmanager.LogManager): Object responsible for writing
            errors to the log.
        
    Note:
        For available data keys check self._data under __init__()
        
    Example:
        How to use YoutubeDLDownloader from a python script.
        
            from downloaders import YoutubeDLDownloader
            
            def data_hook(data):
                print data
            
            downloader = YoutubeDLDownloader('/usr/bin/youtube-dl', data_hook)
            
            downloader.download(<URL STRING>, ['-f', 'flv'])
        
    """
    
    OK = 0
    ERROR = 1
    STOPPED = 2
    ALREADY = 3
    FILESIZE_ABORT = 4

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
        """Download url using given options.

        Args:
            url (string): URL string to download.
            options (list): Python list that contains youtube-dl options.
            
        Returns:
            An integer that shows the status of the download process.
            Right now we support 5 different return codes.
            
            OK (0): The download process completed successfully.
            ERROR (1): An error occured during the download process.
            STOPPED (2): The download process was stopped from the user.
            ALREADY (3): The given url is already downloaded.
            FILESIZE_ABORT (4): The corresponding url video file was larger or
                smaller from the given options filesize limit.
        
        """
        self._reset()

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
        """Stop the download process and set return code to STOPPED. """
        if self._proc_is_alive():
            self._proc.kill()
            self._return_code = self.STOPPED

    def _last_data_hook(self):
        """Set the last data information based on the return code. """
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
        elif self._return_code == self.ALREADY:
            self._data['status'] = 'Already Downloaded'
        else:
            self._data['status'] = 'Filesize Abort'
            
        self._hook_data()
            
    def _reset(self):
        """Reset the data. """
        self._return_code = 0
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
            
    def _sync_data(self, data):
        """ Synchronise self._data with data. It also filters some keys.
        
        Args:
            data (dictionary): Python dictionary that contains different
                keys. The keys are not standar the dictionary can also be
                empty when there are no data to extract. See extract_data().
        
        """
        for key in data:
            if key == 'filename':
                # Keep only the filename on data['filename']
                data['filename'] = os.path.basename(data['filename'])

            if key == 'status':
                if data['status'] == 'Already Downloaded':
                    # Set self._return_code to already downloaded
                    # and trash that key (GUI won't read it if it's None)
                    self._return_code = self.ALREADY
                    data['status'] = None
                    
                if data['status'] == 'Filesize Abort':
                    # Set self._return_code to filesize abort
                    # and trash that key (GUI won't read it if it's None)
                    self._return_code = self.FILESIZE_ABORT
                    data['status'] = None

            self._data[key] = data[key]

    def _log(self, data):
        """Log data using log_manager.
        
        Args:
            data (string): String to write in the log file.
        
        """
        if self.log_manager is not None:
            self.log_manager.log(data)

    def _hook_data(self):
        """Pass self._data back to data_hook. """
        if self.data_hook is not None:
            self.data_hook(self._data)

    def _proc_is_alive(self):
        """Return True if self._proc is alive. Else False. """
        if self._proc is None:
            return False

        return self._proc.poll() is None

    def _read(self):
        """Read subprocess stdout, stderr.
        
        Returns:
            Python tuple that contains the STDOUT string and 
            the STDERR string.
        
        """
        stdout = stderr = ''

        stdout = self._read_stream(self._proc.stdout)

        if not stdout:
            stderr = self._read_stream(self._proc.stderr)

        return stdout, stderr

    def _read_stream(self, stream):
        """Read subprocess stream.
        
        Args:
            stream (subprocess.PIPE): Subprocess pipe. Can be either STDOUT
                or STDERR.
        
        Returns:
            String that contains the stream (STDOUT or STDERR) string.
        
        """
        if self._proc is None:
            return ''

        return stream.readline().rstrip()

    def _get_cmd(self, url, options):
        """Build the subprocess command.
        
        Args:
            url (string): URL string to download.
            options (list): Python list that contains youtube-dl options.
        
        Returns:
            Python list that contains the command to execute.
        
        """
        if os.name == 'nt':
            cmd = [self.youtubedl_path] + options + [url]
        else:
            cmd = ['python', self.youtubedl_path] + options + [url]

        return cmd

    def _create_process(self, cmd):
        """Create new subprocess.
        
        Args:
            cmd (list): Python list that contains the command to execute.
        
        """
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
    """Extract data from youtube-dl stdout.
    
    Args:
        stdout (string): String that contains the youtube-dl stdout.
        
    Returns:
        Python dictionary. For available keys check self._data under
        YoutubeDLDownloader.__init__().
    
    """
    data_dictionary = dict()
        
    if not stdout:
        return data_dictionary
        
    stdout = [string for string in stdout.split(' ') if string != '']

    stdout[0] = stdout[0].lstrip('\r')
    
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
            
        # Get filesize abort status
        if stdout[-1] == 'Aborting.':
            data_dictionary['status'] = 'Filesize Abort'

    elif stdout[0] == '[ffmpeg]':
        data_dictionary['status'] = 'Post Processing'

    else:
        data_dictionary['status'] = 'Pre Processing'

    return data_dictionary
