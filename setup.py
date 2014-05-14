#! /usr/bin/env python

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

icons_path = '/usr/local/share/icons/hicolor/'
youtube_dl_icons = 'youtube_dl_gui/icons/youtube-dl-gui_'

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
    data_files=[
        (icons_path + '16x16/apps', [youtube_dl_icons + '16x16.png']),
        (icons_path + '32x32/apps', [youtube_dl_icons + '32x32.png']),
        (icons_path + '64x64/apps', [youtube_dl_icons + '64x64.png']),
        (icons_path + '128x128/apps', [youtube_dl_icons + '128x128.png']),
        (icons_path + '256x256/apps', [youtube_dl_icons + '256x256.png'])
    ]
)
