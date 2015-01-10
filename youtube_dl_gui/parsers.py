#!/usr/bin/env python2

"""Youtubedlg module to parse the options.

Note:
    If you want to add new values on the module attributes
    e.g. (SUBS_LANG, VIDEO_FORMATS, etc..) you also need to add the
    values on the optionsframe module in order for them to be
    visible from the GUI.

"""

import os.path

from .utils import remove_shortcuts

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
    "none": "0",
    "3gp [176x144]": "17",
    "3gp [320x240]": "36",
    "flv [400x240]": "5",
    "flv [640x360]": "34",
    "flv [854x480]": "35",
    "webm [640x360]": "43",
    "webm [854x480]": "44",
    "webm [1280x720]": "45",
    "webm [1920x1080]": "46",
    "mp4 [640x360]": "18",
    "mp4 [1280x720]": "22",
    "mp4 [1920x1080]": "37",
    "mp4 [4096x3072]": "38",
    "mp4 144p (DASH)": "160",
    "mp4 240p (DASH)": "133",
    "mp4 360p (DASH)": "134",
    "mp4 480p (DASH)": "135",
    "mp4 720p (DASH)": "136",
    "mp4 1080p (DASH)": "137",
    "mp4 1440p (DASH)": "264",
    "mp4 2160p (DASH)": "138",
    "webm 240p (DASH)": "242",
    "webm 360p (DASH)": "243",
    "webm 480p (DASH)": "244",
    "webm 720p (DASH)": "247",
    "webm 1080p (DASH)": "248",
    "webm 1440p (DASH)": "271",
    "webm 2160p (DASH)": "272",
    "mp4 360p (3D)": "82",
    "mp4 480p (3D)": "83",
    "mp4 720p (3D)": "84",
    "mp4 1080p (3D)": "85",
    "webm 360p (3D)": "100",
    "webm 480p (3D)": "101",
    "webm 720p (3D)": "102",
    "m4a 48k (DASH AUDIO)": "139",
    "m4a 128k (DASH AUDIO)": "140",
    "m4a 256k (DASH AUDIO)": "141",
    "webm 48k (DASH AUDIO)": "171",
    "webm 256k (DASH AUDIO)": "172"
}

AUDIO_QUALITY = {
    "high": "0",
    "mid": "5",
    "low": "9"
}

FILESIZE_UNITS = {
    'Bytes': '',
    'Kilobytes': 'k',
    'Megabytes': 'm',
    'Gigabytes': 'g',
    'Terabytes': 't',
    'Petabytes': 'p',
    'Exabytes': 'e',
    'Zettabytes': 'z',
    'Yottabytes': 'y'
}

class OptionHolder():
    
    """Simple data structure that holds informations for the given option.
    
    Args:
        name (string): Option name. Must be a valid option name
            from the optionsmanager.OptionsManager class.
            See optionsmanager.OptionsManager load_default() method.
            
        flag (string): The option command line switch.
            See https://github.com/rg3/youtube-dl/#options
            
        default_value (any): The option default value. Must be the same type
            with the corresponding option from the optionsmanager.OptionsManager
            class.
            
        requirements (list): The requirements for the given option. This 
            argument is a list of strings with the name of all the options
            that this specific option needs. For example 'subs_lang' needs the
            'write_subs' option to be enabled.
    
    """
    
    def __init__(self, name, flag, default_value, requirements=[]):
        self.name = name
        self.flag = flag
        self.requirements = requirements
        self.default_value = default_value

    def is_boolean(self):
        """Returns True if the option is a boolean switch else False. """
        return type(self.default_value) is bool
        
    def check_requirements(self, options_dict):
        """Check if the required options are enabled.
        
        Args:
            options_dict (dictionary): Dictionary with all the options.
            
        Returns:
            True if any of the required options is enabled else False.
        
        """
        if not self.requirements:
            return True
            
        return any(map(lambda x: options_dict[x], self.requirements))
        
class OptionsParser():

    """Parse optionsmanager.OptionsManager options.
    
    This class is responsible for turning some of the youtube-dlg options
    to youtube-dl command line options.
    
    """

    def __init__(self):
        self._ydl_options = [
            OptionHolder('playlist_start', '--playlist-start', 1),
            OptionHolder('playlist_end', '--playlist-end', 0),
            OptionHolder('max_downloads', '--max-downloads', 0),
            OptionHolder('username', '-u', ''),
            OptionHolder('password', '-p', ''),
            OptionHolder('video_password', '--video-password', ''),
            OptionHolder('retries', '-R', 10),
            OptionHolder('proxy', '--proxy', ''),
            OptionHolder('user_agent', '--user-agent', ''),
            OptionHolder('referer', '--referer', ''),
            OptionHolder('ignore_errors', '-i', False),
            OptionHolder('write_description', '--write-description', False),
            OptionHolder('write_info', '--write-info-json', False),
            OptionHolder('write_thumbnail', '--write-thumbnail', False),
            OptionHolder('min_filesize', '--min-filesize', 0),
            OptionHolder('max_filesize', '--max-filesize', 0),
            OptionHolder('write_all_subs', '--all-subs', False),
            OptionHolder('write_auto_subs', '--write-auto-sub', False),
            OptionHolder('write_subs', '--write-sub', False),
            OptionHolder('keep_video', '-k', False),
            OptionHolder('restrict_filenames', '--restrict-filenames', False),
            OptionHolder('save_path', '-o', ''),
            OptionHolder('embed_subs', '--embed-subs', False, ['write_auto_subs', 'write_subs']),
            OptionHolder('to_audio', '-x', False),
            OptionHolder('audio_format', '--audio-format', '', ['to_audio']),
            OptionHolder('video_format', '-f', ''),
            OptionHolder('subs_lang', '--sub-lang', '', ['write_subs']),
            OptionHolder('audio_quality', '--audio-quality', '5', ['to_audio'])
        ]

    def parse(self, options_dictionary):
        """Parse optionsmanager.OptionsManager options.
        
        Parses the given options to youtube-dl command line arguments.
        
        Args:
            options_dictionary (dictionary): Dictionary with all the options.
            
        Returns:
            List of strings with all the youtube-dl command line options.
        
        """
        options_list = ['--newline']
        
        # Create a copy of options_dictionary
        # We don't want to edit the original options dictionary
        # and change some of the options values like 'save_path' etc..
        options_dict = options_dictionary.copy()
        
        self._build_savepath(options_dict)
        self._build_subslang(options_dict)
        self._build_videoformat(options_dict)
        self._build_audioquality(options_dict)
        self._build_filesizes(options_dict)
        
        # Parse basic youtube-dl command line options
        for option in self._ydl_options:
            if option.check_requirements(options_dict):
                value = options_dict[option.name]
                
                if value != option.default_value:
                    options_list.append(option.flag)
                    
                    if not option.is_boolean():
                        options_list.append(str(value))
        
        # Parse cmd_args
        for option in options_dict['cmd_args'].split():
            options_list.append(option)
        
        return options_list

    def _build_savepath(self, options_dict):
        """Build the save path.
        
        We use this method to build the value of the 'save_path' option and
        store it back to the options dictionary.
        
        Args:
            options_dict (dictionary): Copy of the original options dictionary.
        
        """
        save_path = remove_shortcuts(options_dict['save_path'])
        
        if options_dict['output_format'] == 'id':
            save_path = os.path.join(save_path, '%(id)s.%(ext)s')
        elif options_dict['output_format'] == 'title':
            save_path = os.path.join(save_path, '%(title)s.%(ext)s')
        else:
            save_path = os.path.join(save_path, options_dict['output_template'])
        
        options_dict['save_path'] = save_path
        
    def _build_videoformat(self, options_dict):
        """Build the video format.
        
        We use this method to build the value of the 'video_format' option and
        store it back to the options dictionary.
        
        Args:
            options_dict (dictionary): Copy of the original options dictionary.
        
        """
        first_vf = VIDEO_FORMATS[options_dict['video_format']]
        second_vf = VIDEO_FORMATS[options_dict['second_video_format']]
        
        if first_vf != '0' and second_vf != '0':
            options_dict['video_format'] = first_vf + '+' + second_vf
        elif first_vf != '0' and second_vf == '0':
            options_dict['video_format'] = first_vf
        else:
            options_dict['video_format'] = ''

    def _build_subslang(self, options_dict):
        """Build the subtitles language option value.
        
        We use this method to build the value of the 'subs_lang' option and
        store it back to the options dictionary.
        
        Args:
            options_dict (dictionary): Copy of the original options dictionary.
        
        """
        options_dict['subs_lang'] = SUBS_LANG[options_dict['subs_lang']]

    def _build_audioquality(self, options_dict):
        """Build the audio quality option value.
        
        We use this method to build the value of the 'audio_quality' option and
        store it back to the options dictionary.
        
        Args:
            options_dict (dictionary): Copy of the original options dictionary.
        
        """
        options_dict['audio_quality'] = AUDIO_QUALITY[options_dict['audio_quality']]
        
    def _build_filesizes(self, options_dict):
        """Build the filesize options values.
        
        We use this method to build the values of 'min_filesize' and 
        'max_filesize' options and store them back to options dictionary.
        
        Args:
            options_dict (dictionary): Copy of the original options dictionary.
        
        """
        if options_dict['min_filesize']:
            size_unit = FILESIZE_UNITS[options_dict['min_filesize_unit']]
            options_dict['min_filesize'] = str(options_dict['min_filesize']) + size_unit
            
        if options_dict['max_filesize']:
            size_unit = FILESIZE_UNITS[options_dict['max_filesize_unit']]
            options_dict['max_filesize'] = str(options_dict['max_filesize']) + size_unit
        