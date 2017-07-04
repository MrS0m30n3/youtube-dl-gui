#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Contains test cases for the parsers module."""

from __future__ import unicode_literals

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from youtube_dl_gui.parsers import OptionsParser
except ImportError as error:
    print error
    sys.exit(1)


class TestParse(unittest.TestCase):

    """Test case for OptionsParser parse method."""

    def setUp(self):
        # Create the options_dict based on the OptionHolder
        # items inside the OptionsParser object
        self.options_dict = {item.name:item.default_value for item in OptionsParser()._ydl_options}

        # Add extra options used by the OptionsParser.parse method
        self.options_dict["save_path"] = "/home/user/Workplace/test/youtube"
        self.options_dict["cmd_args"] = ""
        self.options_dict["output_format"] = 1  # Title
        self.options_dict["second_video_format"] = "0"
        self.options_dict["min_filesize_unit"] = ""
        self.options_dict["max_filesize_unit"] = ""

    def check_options_parse(self, expected_options):
        options_parser = OptionsParser()

        self.assertItemsEqual(options_parser.parse(self.options_dict), expected_options)

    def test_parse_to_audio_requirement_bug(self):
        """Test case for the 'to_audio' requirement."""

        self.options_dict["audio_quality"] = "9"
        self.options_dict["audio_format"] = "mp3"
        self.options_dict["embed_thumbnail"] = True

        expected_cmd_list = ["--newline",
                             "-x",
                             "--audio-format",
                             "mp3",
                             "--embed-thumbnail",
                             "--audio-quality",
                             "9",
                             "-o",
                             "/home/user/Workplace/test/youtube/%(title)s.%(ext)s"]

        self.check_options_parse(expected_cmd_list)

        # Setting 'to_audio' to True should return the same results
        # since the '-x' flag is already set on audio extraction
        self.options_dict["to_audio"] = True

        self.check_options_parse(expected_cmd_list)

    def test_parse_cmd_args_with_quotes(self):
        """Test the youtube-dl cmd line args parsing when quotes are presented.

        See: https://github.com/MrS0m30n3/youtube-dl-gui/issues/54

        """

        self.options_dict["video_format"] = "mp4"

        # Test with three quoted 'cmd_args'
        self.options_dict["cmd_args"] = "--recode-video mkv --postprocessor-args \"-codec copy -report\""

        expected_cmd_list = ["--newline",
                             "-f",
                             "mp4",
                             "-o",
                             "/home/user/Workplace/test/youtube/%(title)s.%(ext)s",
                             "--recode-video",
                             "mkv",
                             "--postprocessor-args",
                             "-codec copy -report"]

        self.check_options_parse(expected_cmd_list)


        # Test with two quoted 'cmd_args'
        self.options_dict["cmd_args"] = "--postprocessor-args \"-y -report\""

        expected_cmd_list = ["--newline",
                             "-f",
                             "mp4",
                             "-o",
                             "/home/user/Workplace/test/youtube/%(title)s.%(ext)s",
                             "--postprocessor-args",
                             "-y -report"]

        self.check_options_parse(expected_cmd_list)


        # Test with one quoted 'cmd_arg' followed by other cmd line args
        self.options_dict["cmd_args"] = "--postprocessor-args \"-y\" -v"

        expected_cmd_list = ["--newline",
                             "-f",
                             "mp4",
                             "-o",
                             "/home/user/Workplace/test/youtube/%(title)s.%(ext)s",
                             "--postprocessor-args",
                             "-y",
                             "-v"]

        self.check_options_parse(expected_cmd_list)


        # Test the example presented in issue #54
        self.options_dict["cmd_args"] = "-f \"(mp4)[width<1300]\""
        self.options_dict["video_format"] = "0"  # Set video format to 'default'

        expected_cmd_list = ["--newline",
                             "-o",
                             "/home/user/Workplace/test/youtube/%(title)s.%(ext)s",
                             "-f",
                             "(mp4)[width<1300]"]

        self.check_options_parse(expected_cmd_list)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
