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
import subprocess

from .info import __appname__


_RANDOM_OBJECT = object()


YOUTUBEDL_BIN = 'youtube-dl'
if os.name == 'nt':
    YOUTUBEDL_BIN += '.exe'


def remove_shortcuts(path):
    """Return given path after removing the shortcuts. """
    path = path.replace('~', os.path.expanduser('~'))
    return path


def absolute_path(filename):
    """Return absolute path to the given file. """
    path = os.path.realpath(os.path.abspath(filename))
    return os.path.dirname(path)


def open_dir(path):
    """Open path using default file navigator. """
    path = remove_shortcuts(path)

    if os.name == 'nt':
        os.startfile(path)
    else:
        subprocess.call(('xdg-open', path))


def check_path(path):
    """Create path if not exist. """
    if not os.path.exists(path):
        os.makedirs(path)


def get_config_path():
    """Return user config path.

    Note:
        Windows = %AppData%
        Linux   = ~/.config

    """
    if os.name == 'nt':
        path = os.getenv('APPDATA')
    else:
        path = os.path.join(os.path.expanduser('~'), '.config')

    return path


def shutdown_sys(password=''):
    """Shuts down the system.

    Args:
        password (string): SUDO password for linux.

    Note:
        On Linux you need to provide sudo password if you don't
        have elevated privileges.

    """
    if os.name == 'nt':
        subprocess.call(['shutdown', '/s', '/t', '1'])
    else:
        if not password:
            subprocess.call(['/sbin/shutdown', '-h', 'now'])
        else:
            subprocess.Popen(['sudo', '-S', '/sbin/shutdown', '-h', 'now'],
                             stdin=subprocess.PIPE).communicate(password + '\n')


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
        os.path.join(os.path.dirname(__file__), DIR_NAME),
        os.path.join('/usr', 'share', __appname__.lower(), DIR_NAME)
    ]

    for directory in SEARCH_DIRS:
        if os.path.isdir(directory):
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
        os.path.join(os.path.dirname(__file__), 'icons'),
    ]

    # Append $XDG_DATA_DIRS on search_dirs
    path = os.getenv('XDG_DATA_DIRS')

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

            if os.path.exists(icon_file):
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
