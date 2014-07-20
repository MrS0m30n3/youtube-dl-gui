#!/usr/bin/env python2

''' Contains youtube-dlG util functions. '''

import os
import sys
import subprocess


def is_dash(word):
    ''' Return True if "DASH" in word. '''
    return "DASH" in word


def path_seperator():
    ''' Return path seperator for current OS. '''
    return '\\' if os.name == 'nt' else '/'


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
    ''' Return user $HOME path. '''
    return os.path.expanduser("~")


def abs_path(filename):
    ''' Return absolute path. '''
    path = os.path.realpath(os.path.abspath(filename))
    return os.path.dirname(path)


def open_dir(path):
    ''' Open path using default file navigator. '''
    if os.name == 'nt':
        os.startfile(path)
    else:
        subprocess.call(('xdg-open', path))


def check_path(path):
    ''' Create path if not exist. '''
    if not os.path.exists(path):
        os.makedirs(path)


def get_youtubedl_filename():
    ''' Return youtube-dl executable name. '''
    youtubedl_fl = 'youtube-dl'
    if os.name == 'nt':
        youtubedl_fl += '.exe'

    return youtubedl_fl


def get_config_path():
    ''' Return user config path. Windows=AppData, Linux=~/.config. '''
    if os.name == 'nt':
        path = os.getenv('APPDATA')
    else:
        path = fix_path(get_home()) + '.config'

    return path


def shutdown_sys(password=''):
    ''' Shutdown system. !!!On Linux you need to provide
    password for sudo if you dont have admin prev.
    '''
    if os.name == 'nt':
        subprocess.call(['shutdown', '/s', '/t', '1'])
    else:
        if password == '':
            subprocess.call(['/sbin/shutdown', '-h', 'now'])
        else:
            shutdown_proc = subprocess.Popen(
                ['sudo', '-S', '/sbin/shutdown', '-h', 'now'],
                stdin=subprocess.PIPE
            )
            shutdown_proc.communicate(password + '\n')


def get_time(seconds):
    ''' Return day, hours, minutes, seconds from given seconds. '''
    dtime = {'seconds': 0, 'minutes': 0, 'hours': 0, 'days': 0}

    if seconds < 60:
        dtime['seconds'] = seconds
    elif seconds < 3600:
        dtime['minutes'] = seconds / 60
        dtime['seconds'] = seconds % 60
    elif seconds < 86400:
        dtime['hours'] = seconds / 3600
        dtime['minutes'] = seconds % 3600 / 60
        dtime['seconds'] = seconds % 3600 % 60
    else:
        dtime['days'] = seconds / 86400
        dtime['hours'] = seconds % 86400 / 3600
        dtime['minutes'] = seconds % 86400 % 3600 / 60
        dtime['seconds'] = seconds % 86400 % 3600 % 60

    return dtime


def get_icon_path():
    ''' Return path to the icon file if exist else return None.
    Search __main__ dir, $XDG_DATA_DIRS, /usr/share/pixmaps in that order. '''

    SIZES = ('256x256', '128x128', '64x64', '32x32', '16x16')
    ICON_NAME = 'youtube-dl-gui_%s.png'

    ICONS_LIST = [ICON_NAME % size for size in SIZES]

    # __main__ dir
    path = os.path.join(abs_path(sys.argv[0]), 'icons')

    for icon in ICONS_LIST:
        icon_path = os.path.join(path, icon)

        if os.path.exists(icon_path):
            return icon_path

    # $XDG_DATA_DIRS/icons
    path = os.getenv('XDG_DATA_DIRS')

    if path is not None:
        for temp_path in path.split(':'):
            temp_path = os.path.join(temp_path, 'icons', 'hicolor')

            for size in SIZES:
                icon_path = os.path.join(temp_path, size, 'apps')
                icon_path = fix_path(icon_path) + ICON_NAME % size

                if os.path.exists(icon_path):
                    return icon_path

    # /usr/share/pixmaps
    path = '/usr/share/pixmaps/'
    for icon in ICONS_LIST:
        icon_path = path + icon

        if os.path.exists(icon_path):
            return icon_path

    return None
