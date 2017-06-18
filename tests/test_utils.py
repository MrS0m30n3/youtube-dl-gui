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


def main():
    unittest.main()


if __name__ == "__main__":
    main()
