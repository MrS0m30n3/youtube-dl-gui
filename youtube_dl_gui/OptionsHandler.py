#! /usr/bin/env python

import json

from .Utils import (
    check_path,
    file_exist,
    get_home,
    fix_path
)


class OptionsHandler(object):

    SETTINGS_FILENAME = 'settings.json'
    SENSITIVE_KEYS = ('sudo_password', 'password', 'video_password')

    def __init__(self, config_path):
        self.config_path = config_path
        self.settings_file = self._get_settings_file()
        self.load_default()
        self.load_from_file()

    def load_default(self):
        self.options = {
            'save_path': get_home(),
            'video_format': 'default',
            'dash_audio_format': 'none',
            'clear_dash_files': False,
            'to_audio': False,
            'keep_video': False,
            'audio_format': 'mp3',
            'audio_quality': 'mid',
            'restrict_filenames': False,
            'output_format': 'title',
            'output_template': '%(uploader)s/%(title)s.%(ext)s',
            'playlist_start': 1,
            'playlist_end': 0,
            'max_downloads': 0,
            'min_filesize': '0',
            'max_filesize': '0',
            'write_subs': False,
            'write_all_subs': False,
            'write_auto_subs': False,
            'embed_subs': False,
            'subs_lang': 'English',
            'ignore_errors': True,
            'open_dl_dir': True,
            'write_description': False,
            'write_info': False,
            'write_thumbnail': False,
            'retries': 10,
            'user_agent': '',
            'referer': '',
            'proxy': '',
            'shutdown': False,
            'sudo_password': '',
            'username': '',
            'password': '',
            'video_password': '',
            'youtubedl_path': self.config_path,
            'cmd_args': '',
            'enable_log': True,
            'log_time': False
        }

    def load_from_file(self):
        if not file_exist(self.settings_file):
            self.load_default()
            return

        with open(self.settings_file, 'rb') as f:
            try:
                options = json.load(f)

                # Raise WrongSettings Exception if NOT
                self._settings_are_valid(options)
                self.options = options
            except:
                self.load_default()

    def save_to_file(self):
        check_path(self.config_path)

        with open(self.settings_file, 'wb') as f:
            self._remove_sensitive_data()
            json.dump(self.options, f, indent=4, separators=(',', ': '))

    def _settings_are_valid(self, settings_dictionary):
        ''' Check settings.json dictionary and raise WrongSettings Exception '''
        if len(settings_dictionary) != len(self.options):
            raise WrongSettings()

        for key in self.options:
            if key not in settings_dictionary:
                raise WrongSettings()

    def _remove_sensitive_data(self):
        ''' Remove sensitive data from self.options (passwords, etc) '''
        for key in self.SENSITIVE_KEYS:
            self.options[key] = ''

    def _get_settings_file(self):
        ''' Return abs path to settings file '''
        return fix_path(self.config_path) + self.SETTINGS_FILENAME


class WrongSettings(Exception):
    ''' Wrong settings exception.

    This exception will be raised if settings dictionary is not valid.
    '''
    pass
