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
                    temp_list.append((sub_item, covert_item(item[sub_item])))
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

        __main__ dir, library dir, /usr/share/youtube-dlg/locale

    """
    DIR_NAME = 'locale'

    SEARCH_DIRS = [
        os.path.join(absolute_path(sys.argv[0]), DIR_NAME),
        os.path.join(os_path_dirname(__file__), DIR_NAME),
        os.path.join('/usr', 'share', __appname__.lower(), DIR_NAME)
    ]

    for directory in SEARCH_DIRS:
        if os_path_isdir(directory):
            return directory

    return None


def get_icon_file():
    """Search for youtube-dlg app icon.

    Returns:
        The path to youtube-dlg icon file if exists, else returns None.

    Note:
        Paths that get_icon_file() function searches.

        __main__ dir, library dir, $XDG_DATA_DIRS

    """
    ICON_NAME = "youtube-dl-gui.png"
    SIZES = ("256", "128", "64", "48", "32", "16")

    DIR_TEMPLATE = os.path.join("icons", "hicolor", "{size}x{size}", "apps", ICON_NAME)

    ICONS = [DIR_TEMPLATE.format(size=size) for size in SIZES]

    search_dirs = [
        os.path.join(absolute_path(sys.argv[0]), "data"),
        os.path.join(os_path_dirname(__file__), "data"),
    ]

    # Append $XDG_DATA_DIRS on search_dirs
    path = os_getenv("XDG_DATA_DIRS")

    if path is not None:
        for xdg_path in path.split(':'):
            search_dirs.append(xdg_path)

    # Also append /usr/share/pixmaps on search_dirs
    #search_dirs.append("/usr/share/pixmaps")

    for directory in search_dirs:
        for icon in ICONS:
            icon_file = os.path.join(directory, icon)

            if os_path_exists(icon_file):
                return icon_file

    return None


def get_pixmaps_dir():
    """Return absolute path to the pixmaps icons folder."""
    # TODO probably will need support for other directories py2exe etc
    return os.path.join(absolute_path(__file__), "data", "pixmaps")


def json_load(filename):
    if os_path_exists(filename):
        with open(filename) as input_json_file:
            return json.load(input_json_file)

    return []


def json_store(filename, item):
    with open(filename, 'w') as output_json_file:
        json.dump(item, output_json_file)

def read_formats():
    """Returns a twodict containing all the formats from 'data/formats'."""
    # TODO Support for other directories? Test with py2exe
    formats_file = os.path.join(absolute_path(__file__), "data", "formats")

    if os_path_exists(formats_file):
        formats_dict = TwoWayOrderedDict()

        with open(formats_file) as input_file:
            for line in input_file:
                format_id, format_label = line.split('-')

                formats_dict[format_id.strip()] = format_label.strip()

        return formats_dict

    return None
