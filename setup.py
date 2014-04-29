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

setup(name=__appname__,
      version=__version__,
      description=__description__,
      long_description=__descriptionfull__,
      license=__license__,
      author=__author__,
      author_email=__contact__,
      url=__projecturl__,
      packages=['youtube_dl_gui'],
      data_files=[('lib/python2.7/site-packages/youtube_dl_gui/icons', 
                   ['youtube_dl_gui/icons/youtube-dl-gui.png'])])
