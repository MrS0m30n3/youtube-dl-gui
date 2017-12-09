#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contains test cases for the utils.py module."""

from __future__ import unicode_literals

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    import mock

    from youtube_dl_gui import utils
except ImportError as error:
    print error
    sys.exit(1)


class TestToBytes(unittest.TestCase):

    """Test case for the to_bytes method."""

    def test_to_bytes_bytes(self):
        self.assertEqual(utils.to_bytes("596.00B"), 596.00)
        self.assertEqual(utils.to_bytes("133.55B"), 133.55)

    def test_to_bytes_kilobytes(self):
        self.assertEqual(utils.to_bytes("1.00KiB"), 1024.00)
        self.assertEqual(utils.to_bytes("5.55KiB"), 5683.20)

    def test_to_bytes_megabytes(self):
        self.assertEqual(utils.to_bytes("13.64MiB"), 14302576.64)
        self.assertEqual(utils.to_bytes("1.00MiB"), 1048576.00)

    def test_to_bytes_gigabytes(self):
        self.assertEqual(utils.to_bytes("1.00GiB"), 1073741824.00)
        self.assertEqual(utils.to_bytes("1.55GiB"), 1664299827.20)

    def test_to_bytes_terabytes(self):
        self.assertEqual(utils.to_bytes("1.00TiB"), 1099511627776.00)


class TestFormatBytes(unittest.TestCase):

    """Test case for the format_bytes method."""

    def test_format_bytes_bytes(self):
        self.assertEqual(utils.format_bytes(518.00), "518.00B")

    def test_format_bytes_kilobytes(self):
        self.assertEqual(utils.format_bytes(1024.00), "1.00KiB")

    def test_format_bytes_megabytes(self):
        self.assertEqual(utils.format_bytes(1048576.00), "1.00MiB")

    def test_format_bytes_gigabytes(self):
        self.assertEqual(utils.format_bytes(1073741824.00), "1.00GiB")

    def test_format_bytes_terabytes(self):
        self.assertEqual(utils.format_bytes(1099511627776.00), "1.00TiB")


class TestBuildCommand(unittest.TestCase):

    """Test case for the build_command method."""

    def setUp(self):
        self.url = "https://www.youtube.com/watch?v=aaaaaaaaaaa&list=AAAAAAAAAAA"

        self.options = ["-o", None, "-f", "mp4", "--ignore-config"]

        self.result = "{{ydl_bin}} -o \"{{tmpl}}\" -f mp4 --ignore-config \"{url}\"".format(url=self.url)

    def run_tests(self, ydl_bin, tmpl):
        """Run the main test.

        Args:
            ydl_bin (str): Name of the youtube-dl binary
            tmpl (str): Youtube-dl output template

        """
        utils.YOUTUBEDL_BIN = ydl_bin
        self.options[1] = tmpl  # Plug the template in our options

        result = self.result.format(ydl_bin=ydl_bin, tmpl=tmpl)

        self.assertEqual(utils.build_command(self.options, self.url), result)

    def test_build_command_with_spaces_linux(self):
        tmpl = "/home/user/downloads/%(upload_date)s/%(id)s_%(playlist_id)s - %(format)s.%(ext)s"

        self.run_tests("youtube-dl", tmpl)

    def test_build_command_without_spaces_linux(self):
        tmpl = "/home/user/downloads/%(id)s.%(ext)s"

        self.run_tests("youtube-dl", tmpl)

    def test_build_command_with_spaces_windows(self):
        tmpl = "C:\\downloads\\%(upload_date)s\\%(id)s_%(playlist_id)s - %(format)s.%(ext)s"

        self.run_tests("youtube-dl.exe", tmpl)

    def test_build_command_without_spaces_windows(self):
        tmpl = "C:\\downloads\\%(id)s.%(ext)s"

        self.run_tests("youtube-dl.exe", tmpl)


class TestConvertItem(unittest.TestCase):

    """Test case for the convert_item function."""

    def setUp(self):
        self.input_list_u = ["v1", "v2", "v3"]
        self.input_list_s = [str("v1"), str("v2"), str("v3")]

        self.input_tuple_u = ("v1", "v2", "v3")
        self.input_tuple_s = (str("v1"), str("v2"), str("v3"))

        self.input_dict_u = {"k1": "v1", "k2": "v2"}
        self.input_dict_s = {str("k1"): str("v1"), str("k2"): str("v2")}

    def check_iter(self, iterable, iter_type, is_unicode):
        check_type = unicode if is_unicode else str

        iterable = utils.convert_item(iterable, is_unicode)

        self.assertIsInstance(iterable, iter_type)

        for item in iterable:
            if iter_type == dict:
                self.assertIsInstance(iterable[item], check_type)

            self.assertIsInstance(item, check_type)

    def test_convert_item_unicode_str(self):
        self.assertIsInstance(utils.convert_item("test"), str)

    def test_convert_item_unicode_unicode(self):
        self.assertIsInstance(utils.convert_item("test", True), unicode)

    def test_convert_item_str_unicode(self):
        self.assertIsInstance(utils.convert_item(str("test"), True), unicode)

    def test_convert_item_str_str(self):
        self.assertIsInstance(utils.convert_item(str("test")), str)

    def test_convert_item_list_empty(self):
        self.assertEqual(len(utils.convert_item([])), 0)

    def test_convert_item_dict_empty(self):
        self.assertEqual(len(utils.convert_item({})), 0)

    def test_convert_item_list_unicode_str(self):
        self.check_iter(self.input_list_u, list, False)

    def test_convert_item_list_str_unicode(self):
        self.check_iter(self.input_list_s, list, True)

    def test_convert_item_tuple_unicode_str(self):
        self.check_iter(self.input_tuple_u, tuple, False)

    def test_convert_item_tuple_str_unicode(self):
        self.check_iter(self.input_tuple_s, tuple, True)

    def test_convert_item_dict_unicode_str(self):
        self.check_iter(self.input_dict_u, dict, False)

    def test_convert_item_dict_str_unicode(self):
        self.check_iter(self.input_dict_s, dict, True)


class TestGetDefaultLang(unittest.TestCase):

    """Test case for the get_default_lang function."""

    @mock.patch("youtube_dl_gui.utils.locale_getdefaultlocale")
    def run_tests(self, ret_value, result, mock_getdefaultlocale):
        """Run the main test.

        Args:
            ret_value (tuple): Return tuple of the locale.getdefaultlocale module
            result (unicode): Result we want to see
            mock_getdefaultlocale (MagicMock): Mock object
        """
        mock_getdefaultlocale.return_value = ret_value
        lang = utils.get_default_lang()

        mock_getdefaultlocale.assert_called_once()
        self.assertEqual(lang, result)

    def test_get_default_lang(self):
        self.run_tests(("it_IT", "UTF-8"), "it_IT")

    def test_get_default_lang_none(self):
        self.run_tests((None, None), "en_US")

    def test_get_default_lang_empty(self):
        self.run_tests(("", ""), "en_US")


def main():
    unittest.main()


if __name__ == "__main__":
    main()
