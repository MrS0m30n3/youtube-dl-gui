#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg __init__ file.

Responsible on how the package looks from the outside.

Example:
    In order to load the GUI from a python script.

        import youtube_dl_gui

        youtube_dl_gui.main()

"""

from __future__ import unicode_literals

import sys
import gettext

try:
    import wx
except ImportError as error:
    print error
    sys.exit(1)

__packagename__ = "youtube_dl_gui"

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

gettext.install(__packagename__)
from .formats import reload_strings

from .logmanager import LogManager
from .optionsmanager import OptionsManager

from .utils import (
    get_config_path,
    get_locale_file
)


# Set config path and create options and log managers
config_path = get_config_path()

opt_manager = OptionsManager(config_path)
log_manager = None

if opt_manager.options['enable_log']:
    log_manager = LogManager(config_path, opt_manager.options['log_time'])

# Set gettext before MainFrame import
# because the GUI strings are class level attributes
locale_dir = get_locale_file()

try:
    gettext.translation(__packagename__, locale_dir, [opt_manager.options['locale_name']]).install(unicode=True)
except IOError:
    opt_manager.options['locale_name'] = 'en_US'
    gettext.install(__packagename__)

reload_strings()

from .mainframe import MainFrame


def main():
    """The real main. Creates and calls the main app windows. """
    app = wx.App()
    frame = MainFrame(opt_manager, log_manager)
    frame.Show()
    app.MainLoop()
