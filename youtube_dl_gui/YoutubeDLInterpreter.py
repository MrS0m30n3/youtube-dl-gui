#! /usr/bin/env python

'''
Parse OptionHandler object into list
and call youtube_dl.main(list) using
subprocess (we use this method to let
youtube_dl.main() handle all the hard
work)
'''

from .Utils import (
    video_is_dash,
    os_type,
    fix_path,
    add_PATH
)

LANGUAGES = {"English":"en",
            "Greek":"gr",
            "Portuguese":"pt",
            "French":"fr",
            "Italian":"it",
            "Russian":"ru",
            "Spanish":"es",
            "German":"de"}

VIDEOFORMATS = {"default":"0",
                "mp4 [1280x720]":"22",
                "mp4 [640x360]":"18",
                "webm [640x360]":"43",
                "flv [400x240]":"5",
                "3gp [320x240]":"36",
                "mp4 1080p(DASH)":"137",
                "mp4 720p(DASH)":"136",
                "mp4 480p(DASH)":"135",
                "mp4 360p(DASH)":"134"}

DASH_AUDIO_FORMATS = {"none":"none",
                      "DASH m4a audio 128k":"140",
                      "DASH webm audio 48k":"171"}

AUDIO_Q = {"high":"0",
           "mid":"5",
           "low":"9"}

class YoutubeDLInterpreter():

    def __init__(self, optManager, youtubeDLFile):
        self.youtubeDLFile = youtubeDLFile
        self.optManager = optManager
        self.opts = []
        self.set_os()
        self.set_progress_opts()
        self.set_output_opts()
        self.set_auth_opts()
        self.set_connection_opts()
        self.set_video_opts()
        self.set_playlist_opts()
        self.set_filesystem_opts()
        self.set_subtitles_opts()
        self.set_audio_opts()
        self.set_other_opts()

    def get_options(self):
        return self.opts

    def set_os(self):
        if os_type == 'nt':
            self.opts = [self.youtubeDLFile]
            add_PATH(self.optManager.options['youtubedl_path'])
        else:
            path = fix_path(self.optManager.options['youtubedl_path'])
            self.opts = ['python', path + self.youtubeDLFile]

    def set_progress_opts(self):
        ''' Do NOT change this option '''
        self.opts.append('--newline')

    def set_playlist_opts(self):
        if self.optManager.options['playlist_start'] != 1:
            self.opts.append('--playlist-start')
            self.opts.append(str(self.optManager.options['playlist_start']))
        if self.optManager.options['playlist_end'] != 0:
            self.opts.append('--playlist-end')
            self.opts.append(str(self.optManager.options['playlist_end']))
        if self.optManager.options['max_downloads'] != 0:
            self.opts.append('--max-downloads')
            self.opts.append(str(self.optManager.options['max_downloads']))
        if self.optManager.options['min_filesize'] != '0':
            self.opts.append('--min-filesize')
            self.opts.append(self.optManager.options['min_filesize'])
        if self.optManager.options['max_filesize'] != '0':
            self.opts.append('--max-filesize')
            self.opts.append(self.optManager.options['max_filesize'])

    def set_auth_opts(self):
        if self.optManager.options['username'] != '':
            self.opts.append('-u')
            self.opts.append(self.optManager.options['username'])
        if self.optManager.options['password'] != '':
            self.opts.append('-p')
            self.opts.append(self.optManager.options['password'])
        if self.optManager.options['video_password'] != '':
            self.opts.append('--video-password')
            self.opts.append(self.optManager.options['video_password'])

    def set_connection_opts(self):
        if self.optManager.options['retries'] != 10:
            self.opts.append('-R')
            self.opts.append(str(self.optManager.options['retries']))
        if self.optManager.options['proxy'] != '':
            self.opts.append('--proxy')
            self.opts.append(self.optManager.options['proxy'])
        if self.optManager.options['user_agent'] != '':
            self.opts.append('--user-agent')
            self.opts.append(self.optManager.options['user_agent'])
        if self.optManager.options['referer'] != '':
            self.opts.append('--referer')
            self.opts.append(self.optManager.options['referer'])

    def set_video_opts(self):
        if self.optManager.options['video_format'] != 'default':
            self.opts.append('-f')
            if video_is_dash(self.optManager.options['video_format']):
                vf = VIDEOFORMATS[self.optManager.options['video_format']]
                af = DASH_AUDIO_FORMATS[self.optManager.options['dash_audio_format']]
                if af != 'none':
                    self.opts.append(vf+'+'+af)
                else:
                    self.opts.append(vf)
            else:
                self.opts.append(VIDEOFORMATS[self.optManager.options['video_format']])

    def set_filesystem_opts(self):
        if self.optManager.options['ignore_errors']:
            self.opts.append('-i')
        if self.optManager.options['write_description']:
            self.opts.append('--write-description')
        if self.optManager.options['write_info']:
            self.opts.append('--write-info-json')
        if self.optManager.options['write_thumbnail']:
            self.opts.append('--write-thumbnail')

    def set_subtitles_opts(self):
        if self.optManager.options['write_all_subs']:
            self.opts.append('--all-subs')
        if self.optManager.options['write_auto_subs']:
            self.opts.append('--write-auto-sub')
        if self.optManager.options['write_subs']:
            self.opts.append('--write-sub')
            if self.optManager.options['subs_lang'] != 'English':
                self.opts.append('--sub-lang')
                self.opts.append(LANGUAGES[self.optManager.options['subs_lang']])
        if self.optManager.options['embed_subs']:
            self.opts.append('--embed-subs')

    def set_output_opts(self):
        path = fix_path(self.optManager.options['save_path'])
        self.opts.append('-o')
        if self.optManager.options['output_format'] == 'id':
            self.opts.append(path + '%(id)s.%(ext)s')
        elif self.optManager.options['output_format'] == 'title':
            self.opts.append(path + '%(title)s.%(ext)s')
        elif self.optManager.options['output_format'] == 'custom':
            self.opts.append(path + self.optManager.options['output_template'])

    def set_audio_opts(self):
        if self.optManager.options['to_audio']:
            self.opts.append('-x')
            self.opts.append('--audio-format')
            self.opts.append(self.optManager.options['audio_format'])
            if self.optManager.options['audio_quality'] != 'mid':
                self.opts.append('--audio-quality')
                self.opts.append(AUDIO_Q[self.optManager.options['audio_quality']])
            if self.optManager.options['keep_video']:
                self.opts.append('-k')

    def set_other_opts(self):
        if self.optManager.options['cmd_args'] != '':
            for option in self.optManager.options['cmd_args'].split():
                self.opts.append(option)
