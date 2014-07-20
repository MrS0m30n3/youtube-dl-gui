#!/usr/bin/env python2

''' Youtube-dlg __init__ file. '''

import sys

try:
    import wx
except ImportError as e:
    print e
    sys.exit(1)

from .MainFrame import MainFrame
from .version import __version__

from .data import (
    __author__,
    __appname__,
    __contact__,
    __license__,
    __projecturl__,
    __licensefull__,
    __description__,
    __descriptionfull__,
)


def main():
    ''' Call youtube-dlg main window. '''
    app = wx.App()
    frame = MainFrame()
    frame.Centre()
    frame.Show()
    app.MainLoop()
