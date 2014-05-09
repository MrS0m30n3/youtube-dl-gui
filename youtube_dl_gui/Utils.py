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
    exists as file_exist,
    getsize as get_filesize
)

def remove_empty_items(array):
    return [x for x in array if x != '']

def remove_spaces(string):
    return string.replace(' ', '')

def string_to_array(string, char=' '):
    return string.split(char)

def preferredencoding():
    try:
        pref = locale.getpreferredencoding()
        u'TEST'.encode(pref)
    except:
        pref = 'UTF-8'
    return pref

def get_encoding():
    if sys.version_info >= (3, 0):
        return None
    if sys.platform == 'win32':
        # Refer to http://stackoverflow.com/a/9951851/35070
        return preferredencoding()
    return None

def encode_list(data_list, encoding):
    return [x.encode(encoding, 'ignore') for x in data_list]

def video_is_dash(video):
    return "DASH" in video

def have_dash_audio(audio):
    return audio != "none"

def get_path_seperator():
    return '\\' if os_type == 'nt' else '/'

def fix_path(path):
    if path != '' and path[-1:] != get_path_seperator():
        path += get_path_seperator()
    path_list = path.split(get_path_seperator())
    for i in range(len(path_list)):
        if path_list[i] == '~':
            path_list[i] = get_HOME()
    return get_path_seperator().join(path_list)

def get_HOME():
    return os.path.expanduser("~")

def add_PATH(path):
    os.environ["PATH"] += os.pathsep + path
    
def abs_path(filename):
    path = os.path.abspath(filename).split(get_path_seperator())
    path.pop()
    return get_path_seperator().join(path)
    
def get_filename(path):
    return path.split(get_path_seperator())[-1]

def open_dir(path):
    if os_type == 'nt':
        os.startfile(path)
    else:
        subprocess.call(('xdg-open', path))

def check_path(path):
    if not file_exist(path):
        makedir(path)
        
def get_user_config_path():
    if os_type == 'nt':
        path = os.getenv('APPDATA')
    else:
        path = fix_path(get_HOME()) + '.config'
    return path
        
def shutdown_sys(password=''):
    if os_type == 'nt':
        subprocess.call(['shutdown', '/s', '/t', '1'])
    else:
        if password == '':
            subprocess.call(['/sbin/shutdown', '-h', 'now'])
        else:
            p = subprocess.Popen(['sudo', '-S', '/sbin/shutdown', '-h', 'now'],
                                 stdin=subprocess.PIPE)
            p.communicate(password+'\n')
            
