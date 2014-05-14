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
        (
            'lib/python2.7/site-packages/youtube_dl_gui/icons',
            [
                'youtube_dl_gui/icons/youtube-dl-gui.ico',
                'youtube_dl_gui/icons/youtube-dl-gui_16x16.png',
                'youtube_dl_gui/icons/youtube-dl-gui_24x24.png',
                'youtube_dl_gui/icons/youtube-dl-gui_32x32.png',
                'youtube_dl_gui/icons/youtube-dl-gui_48x48.png',
                'youtube_dl_gui/icons/youtube-dl-gui_64x64.png',
                'youtube_dl_gui/icons/youtube-dl-gui_96x96.png',
                'youtube_dl_gui/icons/youtube-dl-gui_128x128.png',
                'youtube_dl_gui/icons/youtube-dl-gui_256x256.png'
            ]
        )
    ]
)
