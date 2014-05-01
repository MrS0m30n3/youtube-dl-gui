#! /usr/bin/env python

import json

from .Utils import (
    get_HOME,
    file_exist,
    os_type,
    fix_path,
    check_path
)

SETTINGS_FILENAME = 'settings.json'
LINUX_FILES_PATH = get_HOME() + '/.youtube-dl-gui'
WINDOWS_FILES_PATH = get_HOME() + '\\youtube-dl-gui'

class OptionsHandler():

    settings_abs_path = ''
    sensitive_keys = ('sudo_password', 'password', 'video_password')

    def __init__(self):
        self.set_settings_path()
        self.load_settings()

    def load_settings(self):
        self.load_default()
        check_path(self.get_config_path())
        if file_exist(self.settings_abs_path):
            self.load_from_file()

    def load_default(self):
        self.options = {
                'save_path': get_HOME(),
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
                'open_dl_dir': False,
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
                'youtubedl_path': self.get_config_path(),
                'cmd_args': '',
                'enable_log': True,
                'log_time': True
        }
        
    def get_config_path(self):
        if os_type == 'nt':
            return WINDOWS_FILES_PATH
        return LINUX_FILES_PATH

    def set_settings_path(self):
        self.settings_abs_path = fix_path(self.get_config_path()) + SETTINGS_FILENAME

    def settings_are_valid(self, settings_dictionary):
        ''' Check settings.json dictionary '''
        for key in self.options:
            if key not in settings_dictionary:
                return False
        if len(settings_dictionary) != len(self.options):
            return False
        return True
        
    def remove_sensitive_data(self):
        for key in self.sensitive_keys:
            self.options[key] = ''
        
    def load_from_file(self):
        with open(self.settings_abs_path, 'rb') as f:
            try:
                options = json.load(f)
                if self.settings_are_valid(options):
                    self.options = options
                else:
                    self.load_default()
            except:
                self.load_default()

    def save_to_file(self):
        check_path(self.get_config_path())
        with open(self.settings_abs_path, 'wb') as f:
            self.remove_sensitive_data()
            json.dump(self.options, f, indent=4, separators=(',', ': '))
 