#!/usr/bin/env python2

import os
import sys

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


def py2exe_setup():
    py2exe_dependencies = [
        'C:\\Windows\\System32\\ffmpeg.exe',
        'C:\\Windows\\System32\\ffprobe.exe',
        'C:\\python27\\DLLs\\MSVCP90.dll'
    ]

    py2exe_data_files = [
        ('', py2exe_dependencies),
        (PY2EXE_ICONS, ICONS_LIST)
    ]
    
    py2exe_options = {
        'includes': ['wx.lib.pubsub.*',
                     'wx.lib.pubsub.core.*',
                     'wx.lib.pubsub.core.arg1.*']
    }

    py2exe_windows = {
        'script': 'youtube_dl_gui\\__main__.py',
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
    else:
        # Create all the hicolor icons
        for index, size in enumerate(ICONS_SIZES):
            icons_dest = os.path.join(LINUX_ICONS, size, 'apps')
            icons_dir = (icons_dest, [ICONS_LIST[index]])
            
            data_files.append(icons_dir)
        
        # Add the 48x48 icon as fallback
        fallback_icon = (LINUX_FALLBACK_ICONS, [ICONS_LIST[2]])
        data_files.append(fallback_icon)

    params = {'data_files': data_files}
    
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
