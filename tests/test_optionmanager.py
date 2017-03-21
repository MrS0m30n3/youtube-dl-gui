#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Testing for the package optionmanager."""

import os
import unittest

from youtube_dl_gui.optionsmanager import get_config_path


class TestConfigPath(unittest.TestCase):

    """Minor test for get_config_path."""

    def test_get_path_posix_unicode(self):
        """Check path for posix system with unicode character."""
        os.environ['HOME'] = '/home/ùsername'
        self.assertEqual(
            get_config_path('posix'),
            u"/home/ùsername/.config/youtube-dlg"
        )

    def test_get_path_posix(self):
        """Check path for posix system."""
        os.environ['HOME'] = '/home/username'
        self.assertEqual(
            get_config_path('posix'),
            "/home/username/.config/youtube-dlg"
        )

    def test_get_path_win_unicode(self):
        """Check path for Windows system with unicode character."""
        os.environ['APPDATA'] = 'C:\\Dócuments and Settings\\' \
                                'User Name\\Application Data'
        self.assertEqual(
            get_config_path('nt'),
            u'C:\\Dócuments and Settings\\User Name\\'
            u'Application Data\\youtube-dlg'
        )

    def test_get_path_win(self):
        """Check path for Windows system."""
        os.environ['APPDATA'] = 'C:\\Documents and Settings\\' \
            'User Name\\Application Data'
        self.assertEqual(
            get_config_path('nt'),
            'C:\\Documents and Settings\\User Name\\'
            'Application Data\\youtube-dlg'
        )

    def test_get_path_not_support(self):
        """Check for unsupported system"""
        os.name = 'java'
        self.assertRaises(Exception, get_config_path())

    def test_get_settings_json_unix(self):
        """Get the absolute path to the file settings.json in Unix."""
        os.environ['HOME'] = '/home/username'
        self.assertEqual(
            get_config_path('posix', settings_file=True),
            "/home/username/.config/youtube-dlg/settings.json"
        )

    def test_get_settings_json_win(self):
        """Get the absolute path to the file settings.json in Windows."""
        os.environ['APPDATA'] = 'C:\\Documents and Settings\\' \
            'User Name\\Application Data'
        self.assertEqual(
            get_config_path('nt', settings_file=True),
            'C:\\Documents and Settings\\User Name\\'
            'Application Data\\youtube-dlg\\settings.json'
        )

if __name__ == "__main__":
    unittest.main()
