#! /usr/bin/env python

import os
import sys
import locale
import subprocess

from os import (
    remove as remove_file,
    makedirs as makedir,
    name as os_type,
)

from os.path import (
    getsize as get_filesize,
    exists as file_exist
)


def get_encoding():
    if sys.version_info >= (3, 0):
        return None

    if sys.platform == 'win32':
        try:
            enc = locale.getpreferredencoding()
            u'TEST'.encode(enc)
        except:
            enc = 'UTF-8'
        return enc
    return None


def encode_list(lst, encoding):
    return [item.encode(encoding, 'ignore') for item in lst]


def video_is_dash(video):
    return "DASH" in video


def audio_is_dash(audio):
    return audio != "none"


def path_seperator():
    ''' Return path seperator for current OS '''
    return '\\' if os_type == 'nt' else '/'


def fix_path(path):
    ''' Add path seperator at the end of the path
    if not exist and replace ~ with user $HOME '''
    if path == '':
        return path

    if path[-1:] != path_seperator():
        path += path_seperator()

    path_list = path.split(path_seperator())
    for index, item in enumerate(path_list):
        if item == '~':
            path_list[index] = get_home()

    path = path_seperator().join(path_list)
    return path


def get_home():
    return os.path.expanduser("~")


def abs_path(filename):
    path = os.path.realpath(os.path.abspath(filename))
    path = path.split(path_seperator())
    path.pop()
    return path_seperator().join(path)


def get_filename(path):
    return path.split(path_seperator())[-1]


def open_dir(path):
    if os_type == 'nt':
        os.startfile(path)
    else:
        subprocess.call(('xdg-open', path))


def check_path(path):
    if not file_exist(path):
        makedir(path)


def get_youtubedl_filename():
    youtubedl_fl = 'youtube-dl'
    if os_type == 'nt':
        youtubedl_fl += '.exe'
    return youtubedl_fl


def get_user_config_path():
    if os_type == 'nt':
        path = os.getenv('APPDATA')
    else:
        path = fix_path(get_home()) + '.config'
    return path


def shutdown_sys(password=''):
    if os_type == 'nt':
        subprocess.call(['shutdown', '/s', '/t', '1'])
    else:
        if password == '':
            subprocess.call(['/sbin/shutdown', '-h', 'now'])
        else:
            p = subprocess.Popen(
                ['sudo', '-S', '/sbin/shutdown', '-h', 'now'],
                stdin=subprocess.PIPE
            )
            p.communicate(password + '\n')
