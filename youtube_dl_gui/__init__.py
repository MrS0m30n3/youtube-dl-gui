#!/usr/bin/env python2

''' Youtube-dlg __init__ file. '''

import sys
import os.path

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

from .utils import get_config_path
from .OptionsManager import OptionsManager
from .LogManager import LogManager


def main():
    ''' Call youtube-dlg main window. '''
    config_path = os.path.join(get_config_path(), __appname__.lower())
    
    opt_manager = OptionsManager(config_path)
    log_manager = None
    
    if opt_manager.options['enable_log']:
        log_manager = LogManager(config_path, opt_manager.options['log_time'])
    
    app = wx.App()
    frame = MainFrame(opt_manager, log_manager)
    frame.Centre()
    frame.Show()
    app.MainLoop()
