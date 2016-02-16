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
import locale
import subprocess

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


def remove_shortcuts(path):
    """Return given path after removing the shortcuts. """
    return path.replace('~', os_path_expanduser('~'))


def absolute_path(filename):
    """Return absolute path to the given file. """
    return os_path_dirname(os_path_realpath(os_path_abspath(filename)))


def open_dir(path):
    """Open path using default file navigator.
    Return True if path exists else False. """
    path = remove_shortcuts(path)

    if not os_path_exists(path):
        return False

    if os.name == 'nt':
        os_startfile(path)
    else:
        subprocess.call(('xdg-open', path))

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

    if sys.platform == 'darwin':
      SEARCH_DIRS.append('/usr/local/Cellar/youtube-dl-gui/{version}/share/locale'.format(version=__version__))

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

        __main__ dir, library dir, /usr/share/pixmaps, $XDG_DATA_DIRS

    """
    SIZES = ('256x256', '128x128', '64x64', '48x48', '32x32', '16x16')
    ICON_NAME = 'youtube-dl-gui_%s.png'

    ICONS_LIST = [ICON_NAME % size for size in SIZES]

    search_dirs = [
        os.path.join(absolute_path(sys.argv[0]), 'icons'),
        os.path.join(os_path_dirname(__file__), 'icons'),
    ]

    # Append $XDG_DATA_DIRS on search_dirs
    path = os_getenv('XDG_DATA_DIRS')

    if path is not None:
        for xdg_path in path.split(':'):
            xdg_path = os.path.join(xdg_path, 'icons', 'hicolor')

            for size in SIZES:
                search_dirs.append(os.path.join(xdg_path, size, 'apps'))

    # Also append /usr/share/pixmaps on search_dirs
    search_dirs.append('/usr/share/pixmaps')

    for directory in search_dirs:
        for icon in ICONS_LIST:
            icon_file = os.path.join(directory, icon)

            if os_path_exists(icon_file):
                return icon_file

    return None


class TwoWayOrderedDict(dict):

    """Custom data structure which implements a two way ordrered dictionary.

    TwoWayOrderedDict it's a custom dictionary in which you can get the
    key:value relationship but you can also get the value:key relationship.
    It also remembers the order in which the items were inserted and supports
    almost all the features of the build-in dict.

    Note:
        Ways to create a new dictionary.

        *) d = TwoWayOrderedDict(a=1, b=2) (Unordered)
        *) d = TwoWayOrderedDict({'a': 1, 'b': 2}) (Unordered)

        *) d = TwoWayOrderedDict([('a', 1), ('b', 2)]) (Ordered)
        *) d = TwoWayOrderedDict(zip(['a', 'b', 'c'], [1, 2, 3])) (Ordered)

    Examples:
        >>> d = TwoWayOrderedDict(a=1, b=2)
        >>> d['a']
        1
        >>> d[1]
        'a'
        >>> print d
        TwoWayOrderedDict([('a', 1), ('b', 2)])

    """

    _PREV = 0
    _KEY = 1
    _NEXT = 2

    def __init__(self, *args, **kwargs):
        self._items = item = []
        self._items += [item, None, item]  # Double linked list [prev, key, next]
        self._items_map = {}  # Map link list items into keys to speed up lookup
        self._load(args, kwargs)

    def __setitem__(self, key, value):
        if key in self:
            # If self[key] == key for example {'b': 'b'} and we
            # do d['b'] = 2 then we dont want to remove the 'b'
            # from our linked list because we will lose the order
            if self[key] in self._items_map and key != self[key]:
                self._remove_mapped_key(self[key])

            dict.__delitem__(self, self[key])

        if value in self:
            # If value == key we dont have to remove the
            # value from the items_map because the value is
            # the key and we want to keep the key in our
            # linked list in order to keep the order.
            if value in self._items_map and key != value:
                self._remove_mapped_key(value)

            if self[value] in self._items_map:
                self._remove_mapped_key(self[value])

            # Check if self[value] is in the dict
            # for cases like {'a': 'a'} where we
            # have only one copy instead of {'a': 1, 1: 'a'}
            if self[value] in self:
                dict.__delitem__(self, self[value])

        if key not in self._items_map:
            last = self._items[self._PREV]  # self._items prev always points to the last item
            last[self._NEXT] = self._items[self._PREV] = self._items_map[key] = [last, key, self._items]

        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        if self[key] in self._items_map:
            self._remove_mapped_key(self[key])

        if key in self._items_map:
            self._remove_mapped_key(key)

        dict.__delitem__(self, self[key])

        # Check if key is in the dict
        # for cases like {'a': 'a'} where we
        # have only one copy instead of {'a': 1, 1: 'a'}
        if key in self:
            dict.__delitem__(self, key)

    def __len__(self):
        return len(self._items_map)

    def __iter__(self):
        curr = self._items[self._NEXT]
        while curr is not self._items:
            yield curr[self._KEY]
            curr = curr[self._NEXT]

    def __reversed__(self):
        curr = self._items[self._PREV]
        while curr is not self._items:
            yield curr[self._KEY]
            curr = curr[self._PREV]

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.items() == other.items()
        return False

    def __ne__(self, other):
        return not self == other

    def _remove_mapped_key(self, key):
        """Remove the given key both from the linked list
        and the map dictionary. """
        prev, __, next = self._items_map.pop(key)
        prev[self._NEXT] = next
        next[self._PREV] = prev

    def _load(self, args, kwargs):
        """Load items into our dictionary. """
        for item in args:
            if type(item) == dict:
                item = item.iteritems()

            for key, value in item:
                self[key] = value

        for key, value in kwargs.items():
            self[key] = value

    def items(self):
        return [(key, self[key]) for key in self]

    def values(self):
        return [self[key] for key in self]

    def keys(self):
        return list(self)

    def pop(self, key, default=_RANDOM_OBJECT):
        try:
            value = self[key]

            del self[key]
        except KeyError as error:
            if default == _RANDOM_OBJECT:
                raise error

            value = default

        return value

    def popitem(self, last=True):
        """Remove and return a (key, value) pair from the dictionary.
        If the dictionary is empty calling popitem() raises a KeyError.

        Args:
            last (bool): When False popitem() will remove the first item
                from the list.

        Note:
            popitem() is useful to destructively iterate over a dictionary.

        Raises:
            KeyError

        """
        if not self:
            raise KeyError('popitem(): dictionary is empty')

        if last:
            __, key, __ = self._items[self._PREV]
        else:
            __, key, __ = self._items[self._NEXT]

        value = self.pop(key)

        return key, value

    def update(self, *args, **kwargs):
        self._load(args, kwargs)

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def copy(self):
        return self.__class__(self.items())

    def clear(self):
        self._items = item = []
        self._items += [item, None, item]
        self._items_map = {}
        dict.clear(self)
