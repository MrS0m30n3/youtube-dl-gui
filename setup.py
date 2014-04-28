#! /usr/bin/env python

from distutils.core import setup
from youtube_dl_gui import version

name = 'Youtube-DLG'
desc = 'Youtube-dl GUI'
ldesc = 'A cross platform front-end GUI of the popular youtube-dl written in wxPython'
license = 'UNLICENSE'
platform = 'Cross-Platform'
author = 'Sotiris Papadopoulos'
author_email = 'ytubedlg@gmail.com'
project_url = 'http://mrs0m30n3.github.io/youtube-dl-gui/'
packages = ['youtube_dl_gui']
data_files = [('lib/python2.7/site-packages/youtube_dl_gui/icons', 
		['youtube_dl_gui/icons/youtube-dl-gui.png'])]

setup(name=name,
      version=version.__version__,
      description=desc,
      long_description=ldesc,
      license=license,
      platforms=platform,
      author=author,
      author_email=author_email,
      url=project_url,
      packages=packages,
      data_files=data_files)
