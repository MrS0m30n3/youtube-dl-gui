#!/usr/bin/env python2

''' Contains youtube-dlG util functions. '''

import os
import sys
import subprocess


YOUTUBEDL_BIN = 'youtube-dl'
if os.name == 'nt':
    YOUTUBEDL_BIN += '.exe'


def remove_shortcuts(path):
    ''' Return the path after removing the shortcuts. '''
    path = path.replace('~', os.path.expanduser('~'))
    return path


def absolute_path(filename):
    ''' Return absolute path. '''
    path = os.path.realpath(os.path.abspath(filename))
    return os.path.dirname(path)


def open_dir(path):
    ''' Open path using default file navigator. '''
    path = remove_shortcuts(path)
    
    if os.name == 'nt':
        os.startfile(path)
    else:
        subprocess.call(('xdg-open', path))


def check_path(path):
    ''' Create path if not exist. '''
    if not os.path.exists(path):
        os.makedirs(path)


def get_config_path():
    ''' Return user config path. Windows=AppData, Linux=~/.config. '''
    if os.name == 'nt':
        path = os.getenv('APPDATA')
    else:
        path = os.path.join(os.path.expanduser('~'), '.config')

    return path


def shutdown_sys(password=''):
    ''' Shutdown system. !!!On Linux you need to provide
    password for sudo if you dont have admin prev.
    '''
    if os.name == 'nt':
        subprocess.call(['shutdown', '/s', '/t', '1'])
    else:
        if not password:
            subprocess.call(['/sbin/shutdown', '-h', 'now'])
        else:
            subprocess.Popen(['sudo', '-S', '/sbin/shutdown', '-h', 'now'],
                             stdin=subprocess.PIPE).communicate(password + '\n')


def get_time(seconds):
    ''' Return day, hours, minutes, seconds from given seconds. '''
    dtime = dict(seconds=0, minutes=0, hours=0, days=0)

    dtime['days'] = seconds / 86400
    dtime['hours'] = seconds % 86400 / 3600
    dtime['minutes'] = seconds % 86400 % 3600 / 60
    dtime['seconds'] = seconds % 86400 % 3600 % 60

    return dtime


def get_icon_file():
    ''' Return path to the icon file if exist else return None.
    Search __main__ dir, $XDG_DATA_DIRS, /usr/share/pixmaps in that order. '''
    SIZES = ('256x256', '128x128', '64x64', '48x48', '32x32', '16x16')
    ICON_NAME = 'youtube-dl-gui_%s.png'

    ICONS_LIST = [ICON_NAME % size for size in SIZES]

    # __main__ dir
    path = os.path.join(absolute_path(sys.argv[0]), 'icons')

    for icon in ICONS_LIST:
        icon_file = os.path.join(path, icon)

        if os.path.exists(icon_file):
            return icon_file

    if os.name != 'nt':
        # $XDG_DATA_DIRS/icons
        path = os.getenv('XDG_DATA_DIRS')

        if path is not None:
            for xdg_path in path.split(':'):
                xdg_path = os.path.join(xdg_path, 'icons', 'hicolor')

                for size in SIZES:
                    icon_name = ICON_NAME % size
                    icon_file = os.path.join(xdg_path, size, 'apps', icon_name)

                    if os.path.exists(icon_file):
                        return icon_file

        # /usr/share/pixmaps
        path = '/usr/share/pixmaps'
        
        for icon in ICONS_LIST:
            icon_file = os.path.join(path, icon)

            if os.path.exists(icon_file):
                return icon_file

    return None
