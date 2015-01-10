#!/usr/bin/env python2

"""Youtubedlg __init__ file.

Responsible on how the package looks from the outside.

Example:
    In order to load the GUI from a python script.

        import youtube_dl_gui

        youtube_dl_gui.main()

"""

import sys
import os.path

try:
    import wx
except ImportError as error:
    print error
    sys.exit(1)

# For package use
from .version import __version__
from .info import (
    __author__,
    __appname__,
    __contact__,
    __license__,
    __projecturl__,
    __licensefull__,
    __description__,
    __descriptionfull__,
)

from .mainframe import MainFrame
from .logmanager import LogManager
from .optionsmanager import OptionsManager

from .utils import get_config_path


def main():
    """The real main.

    Sets configuration path, enables the managers like OptionsManager,
    LogManager, etc.. and creates the main app window.

    """
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
