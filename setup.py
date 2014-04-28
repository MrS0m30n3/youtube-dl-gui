#! /usr/bin/env python

from distutils.core import setup
from youtube_dl_gui import version

setup(name='Youtube-DLG',
      version=version.__version__,
      description='Youtube-dl GUI',
      long_description='A cross platform front-end GUI of the popular youtube-dl written in wxPython.',
      license='UNLICENSE',
      platforms='cross-platform',
      author='Sotiris Papadopoulos',
      author_email='ytubedlg@gmail.com',
      url='https://github.com/MrS0m30n3/youtube-dl-gui',
      packages=['youtube_dl_gui'],
      data_files=[('icons', ['youtube_dl_gui/icons/youtube-dl-gui.png'])])
