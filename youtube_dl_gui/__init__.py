#! /usr/bin/env python

from sys import exit

try:
  import wx
except ImportError, e:
  print '[ERROR]', e
  print 'Please install latest wx.Python'
  exit(1)

from .YoutubeDLGUI import MainFrame
from .version import __version__
from .data import (
    __author__,
    __contact__,
    __projecturl__,
    __appname__,
    __license__,
    __description__,
    __descriptionfull__,
    __licensefull__
)

def main():
  app = wx.App()
  frame = MainFrame()
  frame.Centre()
  frame.Show()
  app.MainLoop()
  
