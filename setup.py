#!/usr/bin/env python2

import sys
from os import name

PY2EXE = len(sys.argv) >= 2 and sys.argv[1] == 'py2exe'

try:
    import py2exe
except ImportError as e:
    if PY2EXE:
        print e
        sys.exit(1)

from distutils.core import setup

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

ICONS_SIZE = ('16x16', '32x32', '64x64', '128x128', '256x256')
ICONS_NAME = 'youtube_dl_gui/icons/youtube-dl-gui_%s.png'

ICONS_LIST = [ICONS_NAME % size for size in ICONS_SIZE]

py2exe_includes = [
    'wx.lib.pubsub.*',
    'wx.lib.pubsub.core.*',
    'wx.lib.pubsub.core.arg1.*'
]

py2exe_options = {
    'includes': py2exe_includes
}

py2exe_windows = {
    'script': 'youtube_dl_gui\\__main__.py',
    'icon_resources': [(0, 'youtube_dl_gui\\icons\\youtube-dl-gui.ico')]
}

py2exe_dependencies = [
    'C:\\Windows\\System32\\ffmpeg.exe',
    'C:\\Windows\\System32\\ffprobe.exe',
    'C:\\python27\\DLLs\MSVCP90.dll'
]

# Set icons path
if PY2EXE:
    icons_path = 'icons'
else:
    # On windows you have to copy the icons manually if you dont use py2exe
    icons_path = '/usr/local/share/icons/hicolor/'

# Set params
if PY2EXE:
    data_files = [
        ('', py2exe_dependencies),
        (icons_path, ICONS_LIST)
    ]

    params = {
        'data_files': data_files,
        'windows': [py2exe_windows],
        'options': {'py2exe': py2exe_options}
    }
else:
    data_files = []
    if name != 'nt':
        for index, size in enumerate(ICONS_SIZE):
            data_file = (icons_path + size + '/apps', [ICONS_LIST[index]])
            data_files.append(data_file)

    params = {
        'data_files': data_files
    }

setup(
    name=__appname__,
    author=__author__,
    url=__projecturl__,
    version=__version__,
    license=__license__,
    author_email=__contact__,
    description=__description__,
    long_description=__descriptionfull__,

    packages=['youtube_dl_gui'],

    **params
)
