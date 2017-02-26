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

    def test_parse_to_audio_requirement_bug(self):
        """Test case for the 'to_audio' requirement."""

        options_dict = {  # Extracted from youtube-dlG settings.json
            'keep_video': False,
            'opts_win_size': (640, 490),
            'open_dl_dir': False,
            'second_video_format': '0',
            'native_hls': False,
            'write_subs': False,
            'workers_number': 3,
            'max_downloads': 0,
            'max_filesize': 0,
            'youtube_dl_debug': False,
            'shutdown': False,
            'selected_format': 'mp3',
            'write_all_subs': False,
            'enable_log': True,
            'embed_thumbnail': True,
            'audio_quality': '9',
            'subs_lang': 'en',
            'audio_format': 'mp3',
            'restrict_filenames': False,
            'min_filesize_unit': '',
            'selected_audio_formats': ['mp3', 'm4a', 'vorbis'],
            'selected_video_formats': ['webm', 'mp4'],
            'save_path': '/home/user/Workplace/test/youtube',
            'output_template': '%(uploader)s/%(title)s.%(ext)s',
            'show_completion_popup': True,
            'locale_name': 'en_US',
            'to_audio': False,
            'confirm_deletion': True,
            'min_filesize': 0,
            'save_path_dirs': ['/home/user/Downloads', '/home/user/Desktop', '/home/user/Videos', '/home/user/Music', '/home/user/Workplace/test/youtube'],
            'sudo_password': '',
            'video_password': '',
            'output_format': 1,
            'embed_subs': False,
            'write_auto_subs': False,
            'video_format': '0',
            'confirm_exit': False,
            'referer': '',
            'proxy': '',
            'add_metadata': False,
            'ignore_errors': False,
            'log_time': True,
            'password': '',
            'playlist_end': 0,
            'write_description': False,
            'retries': 10,
            'cmd_args': '',
            'write_thumbnail': False,
            'playlist_start': 1,
            'nomtime': False,
            'write_info': False,
            'username': '',
            'main_win_size': (930, 560),
            'user_agent': '',
            'max_filesize_unit': '',
            'ignore_config': False,
            'youtubedl_path': '/home/user/.config/youtube-dlg'
        }

        expected_cmd_list = ["--newline",
                             "-x",
                             "--audio-format",
                             "mp3",
                             "--embed-thumbnail",
                             "--audio-quality",
                             "9",
                             "-o",
                             "/home/user/Workplace/test/youtube/%(title)s.%(ext)s"]

        options_parser = OptionsParser()

        self.assertItemsEqual(options_parser.parse(options_dict), expected_cmd_list)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
