#!/usr/bin/env python2

''' Youtube-dlG module to handle settings. '''

import json
import os.path

from .utils import (
    check_path,
    get_home,
    fix_path
)


class OptionsManager(object):

    '''
    Manage youtube-dlG settings.

    Params:
        config_path: Absolute path where OptionsManager
                     should store settings file.

    Accessible Methods
        load_default()
            Params: None

            Return: None

        load_from_file()
            Params: None

            Return: None

        save_to_file()
            Params: None

            Return: None

    Accessible Variables
        settings_file: Absolute path to settings file.
        options: Python dictionary that contains all the options.
    '''

    SETTINGS_FILENAME = 'settings.json'
    SENSITIVE_KEYS = ('sudo_password', 'password', 'video_password')

    def __init__(self, config_path):
        self.config_path = config_path
        self.settings_file = fix_path(config_path) + self.SETTINGS_FILENAME
        self.options = {}
        self.load_default()
        self.load_from_file()

    def load_default(self):
        ''' Load default options. '''
        self.options = {
            'save_path': get_home(),
            'video_format': 'default',
            'second_video_format': 'none',
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
        ''' Load options from settings file. '''
        if not os.path.exists(self.settings_file):
            return

        with open(self.settings_file, 'rb') as settings_file:
            try:
                options = json.load(settings_file)
            except:
                self.load_default()

        if self._settings_are_valid(options):
            self.options = options

    def save_to_file(self):
        ''' Save options to settings file. '''
        check_path(self.config_path)

        with open(self.settings_file, 'wb') as settings_file:
            options = self._get_options()
            json.dump(options,
                      settings_file,
                      indent=4,
                      separators=(',', ': '))

    def _settings_are_valid(self, settings_dictionary):
        ''' Check settings.json dictionary. Return True if
        settings.json dictionary is valid, else return False.
        '''
        for key in self.options:
            if key not in settings_dictionary:
                return False

        return True

    def _get_options(self):
        ''' Return options dictionary without SENSITIVE_KEYS. '''
        temp_options = {}

        for key in self.options:
            if key in self.SENSITIVE_KEYS:
                temp_options[key] = ''
            else:
                temp_options[key] = self.options[key]

        return temp_options
