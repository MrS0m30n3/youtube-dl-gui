#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtube-dlg setup file.

Note:
    If you get 'TypeError: decoding Unicode is not supported' when you run
    py2exe then apply the following patch:

    http://sourceforge.net/p/py2exe/patches/28/

"""

import os
import sys
import shutil

PY2EXE = len(sys.argv) >= 2 and sys.argv[1] == 'py2exe'

if PY2EXE:
    try:
        import py2exe
    except ImportError as error:
        print error
        sys.exit(1)

from distutils.core import setup
from distutils.sysconfig import get_python_lib

from youtube_dl_gui import (
    __author__,
    __appname__,
    __contact__,
    __version__,
    __license__,
    __projecturl__,
    __description__,
    __descriptionfull__
)


ICONS_SIZES = ('16x16', '32x32', '48x48', '64x64', '128x128', '256x256')
ICONS_TEMPLATE = 'youtube_dl_gui/icons/youtube-dl-gui_{size}.png'

ICONS_LIST = [ICONS_TEMPLATE.format(size=size) for size in ICONS_SIZES]


# Set icons path
PY2EXE_ICONS = 'icons'
WINDOWS_ICONS = os.path.join(get_python_lib(), 'youtube_dl_gui', 'icons')
LINUX_ICONS = '/usr/share/icons/hicolor/'

LINUX_FALLBACK_ICONS = '/usr/share/pixmaps/'


# Set localization files path
LOCALE_PATH = os.path.join('youtube_dl_gui', 'locale')

PY2EXE_LOCALE_DIR = 'locale'
WIN_LOCALE_DIR = os.path.join(get_python_lib(), 'youtube_dl_gui', 'locale')
LINUX_LOCALE_DIR = '/usr/share/{app_name}/locale/'.format(app_name=__appname__.lower())


def create_scripts():
    dest_dir = os.path.join('build', '_scripts')

    dest_file = os.path.join(dest_dir, 'youtube-dl-gui')
    src_file = os.path.join('youtube_dl_gui', '__main__.py')

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    shutil.copyfile(src_file, dest_file)


def set_locale_files(data_files):
    for directory in os.listdir(LOCALE_PATH):
        locale_lang = os.path.join(directory, 'LC_MESSAGES')

        src = os.path.join(LOCALE_PATH, locale_lang, 'youtube_dl_gui.mo')

        if PY2EXE:
            dst = os.path.join(PY2EXE_LOCALE_DIR, locale_lang)
        elif os.name == 'nt':
            dst = os.path.join(WIN_LOCALE_DIR, locale_lang)
        else:
            dst = os.path.join(LINUX_LOCALE_DIR, locale_lang)

        data_files.append((dst, [src]))


def py2exe_setup():
    create_scripts()

    py2exe_dependencies = [
        'C:\\Windows\\System32\\ffmpeg.exe',
        'C:\\Windows\\System32\\ffprobe.exe',
        'C:\\python27\\DLLs\\MSVCP90.dll'
    ]

    py2exe_data_files = [
        ('', py2exe_dependencies),
        (PY2EXE_ICONS, ICONS_LIST)
    ]

    set_locale_files(py2exe_data_files)

    py2exe_options = {
        'includes': ['wx.lib.pubsub.*',
                     'wx.lib.pubsub.core.*',
                     'wx.lib.pubsub.core.arg1.*']
    }

    py2exe_windows = {
        'script': 'build\\_scripts\\youtube-dl-gui',
        'icon_resources': [(0, 'youtube_dl_gui\\icons\\youtube-dl-gui.ico')]
    }

    params = {
        'data_files': py2exe_data_files,
        'windows': [py2exe_windows],
        'options': {'py2exe': py2exe_options}
    }

    return params

def normal_setup():
    data_files = list()

    if os.name == 'nt':
        icons_dir = (WINDOWS_ICONS, ICONS_LIST)
        data_files.append(icons_dir)

        set_locale_files(data_files)

        params = {'data_files': data_files}
    else:
        # Create all the hicolor icons
        for index, size in enumerate(ICONS_SIZES):
            icons_dest = os.path.join(LINUX_ICONS, size, 'apps')
            icons_dir = (icons_dest, [ICONS_LIST[index]])

            data_files.append(icons_dir)

        # Add the 48x48 icon as fallback
        fallback_icon = (LINUX_FALLBACK_ICONS, [ICONS_LIST[2]])
        data_files.append(fallback_icon)

        set_locale_files(data_files)

        create_scripts()
        params = {'data_files': data_files, 'scripts': ['build/_scripts/youtube-dl-gui']}

    return params


if PY2EXE:
    params = py2exe_setup()
else:
    params = normal_setup()


setup(
    author              = __author__,
    name                = __appname__,
    version             = __version__,
    license             = __license__,
    author_email        = __contact__,
    url                 = __projecturl__,
    description         = __description__,
    long_description    = __descriptionfull__,
    packages            = ['youtube_dl_gui'],

    **params
)
