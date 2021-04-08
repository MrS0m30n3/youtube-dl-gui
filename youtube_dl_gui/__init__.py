# -*- coding: utf-8 -*-

"""Youtubedlg __init__ file.

Responsible on how the package looks from the outside.

Example:
    In order to load the GUI from a python script.

        import youtube_dl_gui

        youtube_dl_gui.main()

"""

from gettext import translation
import sys
import os


try:
    import wx
except ImportError as error:
    print(error)
    sys.exit(1)

from .formats import *
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

from .logmanager import LogManager
from .optionsmanager import OptionsManager
from .utils import (
    get_config_path,
    get_locale_file,
    os_path_exists,
    YOUTUBEDL_BIN
)

__packagename__ = "youtube_dl_gui"

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
    lang = translation(__packagename__,
                       locale_dir,
                       [opt_manager.options['locale_name']])
except IOError:
    opt_manager.options['locale_name'] = 'en_US'
    lang = translation(__packagename__,
                       locale_dir,
                       [opt_manager.options['locale_name']])


# Redefine _ to gettext in builtins
_ = lang.gettext
OUTPUT_FORMATS, DEFAULT_FORMATS, AUDIO_FORMATS, VIDEO_FORMATS, FORMATS = reload_strings(_)

# wx.Locale
locale = {
    'ar_SA': wx.LANGUAGE_ARABIC,
    'cs_CZ': wx.LANGUAGE_CZECH,
    'en_US': wx.LANGUAGE_ENGLISH_US,
    'fr_FR': wx.LANGUAGE_FRENCH,
    'es_CU': wx.LANGUAGE_SPANISH,
    'it_IT': wx.LANGUAGE_ITALIAN,
    'ja_JP': wx.LANGUAGE_JAPANESE,
    'ko_KR': wx.LANGUAGE_KOREAN,
    'pt_BR': wx.LANGUAGE_PORTUGUESE_BRAZILIAN,
    'ru_RU': wx.LANGUAGE_RUSSIAN,
    'es_ES': wx.LANGUAGE_SPANISH
}

from .mainframe import MainFrame


def main():
    """The real main. Creates and calls the main app windows. """
    youtubedl_path = os.path.join(opt_manager.options["youtubedl_path"], YOUTUBEDL_BIN)

    app = wx.App()
    # Set wx.Locale
    app.locale = wx.Locale(
        locale.get(opt_manager.options['locale_name'], wx.LANGUAGE_ENGLISH_US)
    )
    frame = MainFrame(opt_manager, log_manager)
    frame.Show()

    if opt_manager.options["disable_update"] and not os_path_exists(youtubedl_path):
        wx.MessageBox(_("Failed to locate youtube-dl and updates are disabled"), _("Error"), wx.OK | wx.ICON_ERROR)
        frame.close()

    app.MainLoop()
