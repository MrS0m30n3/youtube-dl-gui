#!/usr/bin/env python2

from .Utils import (
    video_is_dash,
    fix_path
)

SUBS_LANG = {
    "English": "en",
    "Greek": "gr",
    "Portuguese": "pt",
    "French": "fr",
    "Italian": "it",
    "Russian": "ru",
    "Spanish": "es",
    "German": "de"
}

VIDEO_FORMATS = {
    "default": "0",
    "mp4 [1280x720]": "22",
    "mp4 [640x360]": "18",
    "webm [640x360]": "43",
    "flv [400x240]": "5",
    "3gp [320x240]": "36",
    "mp4 1080p(DASH)": "137",
    "mp4 720p(DASH)": "136",
    "mp4 480p(DASH)": "135",
    "mp4 360p(DASH)": "134"
}

DASH_AUDIO_FORMATS = {
    "none": "none",
    "DASH m4a audio 128k": "140",
    "DASH webm audio 48k": "171"
}

AUDIO_QUALITY = {
    "high": "0",
    "mid": "5",
    "low": "9"
}


class OptionsParser():

    ''' Parse OptionsHandler object into youtube-dl options list '''

    def __init__(self, opt_manager):
        self._options = opt_manager.options
        self.opts = []

    def parse(self):
        self._set_progress_opts()
        self._set_output_opts()
        self._set_auth_opts()
        self._set_connection_opts()
        self._set_video_opts()
        self._set_playlist_opts()
        self._set_filesystem_opts()
        self._set_subtitles_opts()
        self._set_audio_opts()
        self._set_other_opts()
        return self.opts

    def _set_progress_opts(self):
        ''' Do NOT change this option '''
        self.opts.append('--newline')

    def _set_playlist_opts(self):
        if self._options['playlist_start'] != 1:
            self.opts.append('--playlist-start')
            self.opts.append(str(self._options['playlist_start']))
        if self._options['playlist_end'] != 0:
            self.opts.append('--playlist-end')
            self.opts.append(str(self._options['playlist_end']))
        if self._options['max_downloads'] != 0:
            self.opts.append('--max-downloads')
            self.opts.append(str(self._options['max_downloads']))
        if self._options['min_filesize'] != '0':
            self.opts.append('--min-filesize')
            self.opts.append(self._options['min_filesize'])
        if self._options['max_filesize'] != '0':
            self.opts.append('--max-filesize')
            self.opts.append(self._options['max_filesize'])

    def _set_auth_opts(self):
        if self._options['username'] != '':
            self.opts.append('-u')
            self.opts.append(self._options['username'])
        if self._options['password'] != '':
            self.opts.append('-p')
            self.opts.append(self._options['password'])
        if self._options['video_password'] != '':
            self.opts.append('--video-password')
            self.opts.append(self._options['video_password'])

    def _set_connection_opts(self):
        if self._options['retries'] != 10:
            self.opts.append('-R')
            self.opts.append(str(self._options['retries']))
        if self._options['proxy'] != '':
            self.opts.append('--proxy')
            self.opts.append(self._options['proxy'])
        if self._options['user_agent'] != '':
            self.opts.append('--user-agent')
            self.opts.append(self._options['user_agent'])
        if self._options['referer'] != '':
            self.opts.append('--referer')
            self.opts.append(self._options['referer'])

    def _set_video_opts(self):
        if self._options['video_format'] != 'default':
            self.opts.append('-f')

            if video_is_dash(self._options['video_format']):
                vf = VIDEO_FORMATS[self._options['video_format']]
                af = DASH_AUDIO_FORMATS[self._options['dash_audio_format']]
                if af != 'none':
                    self.opts.append(vf + '+' + af)
                else:
                    self.opts.append(vf)
            else:
                self.opts.append(VIDEO_FORMATS[self._options['video_format']])

    def _set_filesystem_opts(self):
        if self._options['ignore_errors']:
            self.opts.append('-i')
        if self._options['write_description']:
            self.opts.append('--write-description')
        if self._options['write_info']:
            self.opts.append('--write-info-json')
        if self._options['write_thumbnail']:
            self.opts.append('--write-thumbnail')

    def _set_subtitles_opts(self):
        if self._options['write_all_subs']:
            self.opts.append('--all-subs')
        if self._options['write_auto_subs']:
            self.opts.append('--write-auto-sub')
        if self._options['write_subs']:
            self.opts.append('--write-sub')
            if self._options['subs_lang'] != 'English':
                self.opts.append('--sub-lang')
                self.opts.append(SUBS_LANG[self._options['subs_lang']])
        if self._options['embed_subs']:
            self.opts.append('--embed-subs')

    def _set_output_opts(self):
        path = fix_path(self._options['save_path'])
        self.opts.append('-o')
        if self._options['output_format'] == 'id':
            self.opts.append(path + '%(id)s.%(ext)s')
        elif self._options['output_format'] == 'title':
            self.opts.append(path + '%(title)s.%(ext)s')
        elif self._options['output_format'] == 'custom':
            self.opts.append(path + self._options['output_template'])
        if self._options['restrict_filenames']:
            self.opts.append('--restrict-filenames')

    def _set_audio_opts(self):
        if self._options['to_audio']:
            self.opts.append('-x')
            self.opts.append('--audio-format')
            self.opts.append(self._options['audio_format'])
            if self._options['audio_quality'] != 'mid':
                self.opts.append('--audio-quality')
                self.opts.append(AUDIO_QUALITY[self._options['audio_quality']])
            if self._options['keep_video']:
                self.opts.append('-k')

    def _set_other_opts(self):
        if self._options['cmd_args'] != '':
            for option in self._options['cmd_args'].split():
                self.opts.append(option)
