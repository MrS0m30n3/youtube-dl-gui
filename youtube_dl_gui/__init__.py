#! /usr/bin/env python

from sys import exit

try:
  import wx
except ImportError, e:
  print '[ERROR]', e
  print 'Please install latest wx.Python'
  exit(1)

from .YoutubeDLGUI import MainFrame

def main():
  app = wx.App()
  frame = MainFrame()
  frame.Centre()
  frame.Show()
  app.MainLoop()