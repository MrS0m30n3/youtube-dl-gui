#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg module that contains util functions.

Attributes:
    _RANDOM_OBJECT (object): Object that it's used as a default parameter.

    YOUTUBEDL_BIN (string): Youtube-dl binary filename.

"""

from __future__ import unicode_literals

import os
import sys
import json
import math
import locale
import subprocess

try:
    from twodict import TwoWayOrderedDict
except ImportError as error:
    print error
    sys.exit(1)

from .info import __appname__
from .version import __version__


_RANDOM_OBJECT = object()


YOUTUBEDL_BIN = 'youtube-dl'
if os.name == 'nt':
    YOUTUBEDL_BIN += '.exe'


FILESIZE_METRICS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]

KILO_SIZE = 1024.0


def get_encoding():
    """Return system encoding. """
    try:
        encoding = locale.getpreferredencoding()
        'TEST'.encode(encoding)
    except:
        encoding = 'UTF-8'

    return encoding


def convert_on_bounds(func):
    """Decorator to convert string inputs & outputs.

    Covert string inputs & outputs between 'str' and 'unicode' at the
    application bounds using the preferred system encoding. It will convert
    all the string params (args, kwargs) to 'str' type and all the
    returned strings values back to 'unicode'.

    """
    def convert_item(item, to_unicode=False):
        """The actual function which handles the conversion.

        Args:
            item (-): Can be any python item.

            to_unicode (boolean): When True it will convert all the 'str' types
                to 'unicode'. When False it will convert all the 'unicode'
                types back to 'str'.

        """
        if to_unicode and isinstance(item, str):
            # Convert str to unicode
            return item.decode(get_encoding(), 'ignore')

        if not to_unicode and isinstance(item, unicode):
            # Convert unicode to str
            return item.encode(get_encoding(), 'ignore')

        if hasattr(item, '__iter__'):
            # Handle iterables
            temp_list = []

            for sub_item in item:
                if isinstance(item, dict):
                    temp_list.append((sub_item, convert_item(item[sub_item])))
                else:
                    temp_list.append(convert_item(sub_item))

            return type(item)(temp_list)

        return item

    def wrapper(*args, **kwargs):
        returned_value = func(*convert_item(args), **convert_item(kwargs))

        return convert_item(returned_value, True)

    return wrapper


# See: https://github.com/MrS0m30n3/youtube-dl-gui/issues/57
# Patch os functions to convert between 'str' and 'unicode' on app bounds
os_sep = unicode(os.sep)
os_getenv = convert_on_bounds(os.getenv)
os_makedirs = convert_on_bounds(os.makedirs)
os_path_isdir = convert_on_bounds(os.path.isdir)
os_path_exists = convert_on_bounds(os.path.exists)
os_path_dirname = convert_on_bounds(os.path.dirname)
os_path_abspath = convert_on_bounds(os.path.abspath)
os_path_realpath = convert_on_bounds(os.path.realpath)
os_path_expanduser = convert_on_bounds(os.path.expanduser)

# Patch Windows specific functions
if os.name == 'nt':
    os_startfile = convert_on_bounds(os.startfile)

def remove_file(filename):
    if os_path_exists(filename):
        os.remove(filename)
        return True

    return False

def remove_shortcuts(path):
    """Return given path after removing the shortcuts. """
    return path.replace('~', os_path_expanduser('~'))


def absolute_path(filename):
    """Return absolute path to the given file. """
    return os_path_dirname(os_path_realpath(os_path_abspath(filename)))


def open_file(file_path):
    """Open file in file_path using the default OS application.

    Returns:
        True on success else False.

    """
    file_path = remove_shortcuts(file_path)

    if not os_path_exists(file_path):
        return False

    if os.name == "nt":
        os_startfile(file_path)
    else:
        subprocess.call(("xdg-open", file_path))

    return True


def encode_tuple(tuple_to_encode):
    """Turn size tuple into string. """
    return '%s/%s' % (tuple_to_encode[0], tuple_to_encode[1])


def decode_tuple(encoded_tuple):
    """Turn tuple string back to tuple. """
    s = encoded_tuple.split('/')
    return int(s[0]), int(s[1])


def check_path(path):
    """Create path if not exist. """
    if not os_path_exists(path):
        os_makedirs(path)


def get_config_path():
    """Return user config path.

    Note:
        Windows = %AppData% + app_name
        Linux   = ~/.config + app_name

    """
    if os.name == 'nt':
        path = os_getenv('APPDATA')
    else:
        path = os.path.join(os_path_expanduser('~'), '.config')

    return os.path.join(path, __appname__.lower())


def shutdown_sys(password=None):
    """Shuts down the system.
    Returns True if no errors occur else False.

    Args:
        password (string): SUDO password for linux.

    Note:
        On Linux you need to provide sudo password if you don't
        have elevated privileges.

    """
    _stderr = subprocess.PIPE
    _stdin = None
    info = None
    encoding = get_encoding()

    if os.name == 'nt':
        cmd = ['shutdown', '/s', '/t', '1']

        # Hide subprocess window
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        if password:
            _stdin = subprocess.PIPE
            password = ('%s\n' % password).encode(encoding)
            cmd = ['sudo', '-S', '/sbin/shutdown', '-h', 'now']
        else:
            cmd = ['/sbin/shutdown', '-h', 'now']

    cmd = [item.encode(encoding, 'ignore') for item in cmd]

    shutdown_proc = subprocess.Popen(cmd,
                                     stderr=_stderr,
                                     stdin=_stdin,
                                     startupinfo=info)

    output = shutdown_proc.communicate(password)[1]

    return not output or output == "Password:"


def to_string(data):
    """Convert data to string.
    Works for both Python2 & Python3. """
    return '%s' % data


def get_time(seconds):
    """Convert given seconds to days, hours, minutes and seconds.

    Args:
        seconds (float): Time in seconds.

    Returns:
        Dictionary that contains the corresponding days, hours, minutes
        and seconds of the given seconds.

    """
    dtime = dict(seconds=0, minutes=0, hours=0, days=0)

    dtime['days'] = int(seconds / 86400)
    dtime['hours'] = int(seconds % 86400 / 3600)
    dtime['minutes'] = int(seconds % 86400 % 3600 / 60)
    dtime['seconds'] = int(seconds % 86400 % 3600 % 60)

    return dtime


def get_locale_file():
    """Search for youtube-dlg locale file.

    Returns:
        The path to youtube-dlg locale file if exists else None.

    Note:
        Paths that get_locale_file() func searches.

        __main__ dir, library dir

    """
    DIR_NAME = "locale"

    SEARCH_DIRS = [
        os.path.join(absolute_path(sys.argv[0]), DIR_NAME),
        os.path.join(os_path_dirname(__file__), DIR_NAME),
    ]

    for directory in SEARCH_DIRS:
        if os_path_isdir(directory):
            return directory

    return None


def get_icon_file():
    """Search for youtube-dlg app icon.

    Returns:
        The path to youtube-dlg icon file if exists, else returns None.

    """
    ICON_NAME = "youtube-dl-gui.png"

    pixmaps_dir = get_pixmaps_dir()

    if pixmaps_dir is not None:
        icon_file = os.path.join(pixmaps_dir, ICON_NAME)

        if os_path_exists(icon_file):
            return icon_file

    return None


def get_pixmaps_dir():
    """Return absolute path to the pixmaps icons folder.

    Note:
        Paths we search: __main__ dir, library dir

    """
    search_dirs = [
        os.path.join(absolute_path(sys.argv[0]), "data"),
        os.path.join(os_path_dirname(__file__), "data")
    ]

    for directory in search_dirs:
        pixmaps_dir = os.path.join(directory, "pixmaps")

        if os_path_exists(pixmaps_dir):
            return pixmaps_dir

    return None


def to_bytes(string):
    """Convert given youtube-dl size string to bytes."""
    value = 0.0

    for index, metric in enumerate(reversed(FILESIZE_METRICS)):
        if metric in string:
            value = float(string.split(metric)[0])
            break

    exponent = index * (-1) + (len(FILESIZE_METRICS) - 1)

    return round(value * (KILO_SIZE ** exponent), 2)


def format_bytes(bytes):
    """Format bytes to youtube-dl size output strings."""
    if bytes == 0.0:
        exponent = 0
    else:
        exponent = int(math.log(bytes, KILO_SIZE))

    suffix = FILESIZE_METRICS[exponent]
    output_value = bytes / (KILO_SIZE ** exponent)

    return "%.2f%s" % (output_value, suffix)


def build_command(options_list, url):
    """Build the youtube-dl command line string."""

    def escape(option):
        """Wrap option with double quotes if it contains special symbols."""
        special_symbols = [" ", "(", ")"]

        for symbol in special_symbols:
            if symbol in option:
                return "\"{}\"".format(option)

        return option

    # If option has special symbols wrap it with double quotes
    # Probably not the best solution since if the option already contains
    # double quotes it will be a mess, see issue #173
    options = [escape(option) for option in options_list]

    # Always wrap the url with double quotes
    url = "\"{}\"".format(url)

    return " ".join([YOUTUBEDL_BIN] + options + [url])
