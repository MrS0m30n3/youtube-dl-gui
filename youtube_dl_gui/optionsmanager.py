#!/usr/bin/env python2

"""Youtubedlg module to handle settings. """

import json
import os.path

from .utils import check_path


class OptionsManager(object):

    """Handles youtubedlg options.
    
    This class is responsible for storing and retrieving the options.

    Attributes:
        SETTINGS_FILENAME (string): Filename of the settings file.
        SENSITIVE_KEYS (tuple): Contains the keys that we don't want
            to store on the settings file. (SECURITY ISSUES).
            
    Args:
        config_path (string): Absolute path where OptionsManager
            should store the settings file.

    Note:
        See load_default() method for available options.
            
    Example:
        Access the options using the 'options' variable.
        
        opt_manager = OptionsManager('.')
        opt_manager.options['save_path'] = '~/Downloads'
            
    """

    SETTINGS_FILENAME = 'settings.json'
    SENSITIVE_KEYS = ('sudo_password', 'password', 'video_password')

    def __init__(self, config_path):
        self.config_path = config_path
        self.settings_file = os.path.join(config_path, self.SETTINGS_FILENAME)
        self.options = dict()
        self.load_default()
        self.load_from_file()

    def load_default(self):
        """Load the default options.
        
        Note:
            This method is automatically called by the constructor.
        
        Options Description:
            
            save_path (string): Path where youtube-dl should store the 
                downloaded file. Default is $HOME.
                
            video_format (string): Video format to download. For available
                video formats see 'parsers' module (VIDEO_FORMATS attribute).
                When this options is set to 'default' youtube-dl will choose
                the best video format available for the given URL.
            
            second_video_format (string): Video format to mix with the first
                one. (-f 18+17). For available video formats see 'video_format'
                option. (This option must NOT be 'default').
                
            to_audio (boolean): If True the youtube-dl will post process the 
                video file.
                
            keep_video (boolen): If True youtube-dl will keep the video file
                after post processing it.
                
            audio_format (string): Audio format of the post processed file.
                Available values are "mp3", "wav", "aac", "m4a", "vorbis".
            
            audio_quality (string): Audio quality of the post processed file.
                Available values are "low", "mid", "high".
                
            restrict_filenames (boolean): If True youtube-dl will restrict
                the downloaded file filename to ASCII characters only.
                
            output_format (string): This option sets the downloaded file
                output template. Available values are 'id', 'title', 'custom'
                
                'id' -> '%(id)s.%(ext)s'
                'title' -> '%(title)s.%(ext)s'
                'custom' -> Loads the template from the 'output_template'
                    option.
                    
            output_template (string): Can be any output template supported
                by youtube-dl.
                
            playlist_start (int): Playlist index to start downloading.
            
            playlist_end (int): Playlist index to stop downloading.
            
            max_downloads (int): Maximum number of video files to download
                from the given playlist.
                
            min_filesize (float): Minimum file size of the video file.
                If the video file is smaller than the given size then
                youtube-dl will abort the download process.
                
            max_filesize (float): Maximum file size of the video file.
                If the video file is larger than the given size then
                youtube-dl will abort the download process.
                
            min_filesize_unit (string): Minimum file size unit.
                Available values 'Bytes', 'Kilobytes', 'Megabytes', 
                'Gigabytes', 'Terabytes', 'Petabytes', 'Exabytes', 
                'Zettabytes', 'Yottabytes'.
                
            max_filesize_unit (string): Maximum file size unit.
                See 'min_filesize_unit' option for available values.
                
            write_subs (boolean): If True youtube-dl will try downloading
                the subtitles file for the given URL.
                
            write_all_subs (boolean): If True youtube-dl will try downloading
                all the available subtitles files for the given URL.
                
            write_auto_subs (boolean): If True youtube-dl will try downloading
                the automatic subtitles file for the given URL.
                
            embed_subs (boolean): If True youtube-dl will merge the subtitles
                file with the video. (ONLY mp4 files).
                
            subs_lang (string): Language of the subtitles file to download.
                Needs 'write_subs' option. For available subtitles see 
                'parsers' module. (SUBS_LANG attribute).
                
            ignore_errors (boolean): If True youtube-dl will ignore the errors
                and continue the download process.
                
            open_dl_dir (boolean): If True youtube-dlg will open the
                destination folder after download process has been completed.
                
            write_description (boolean): If True youtube-dl will write video
                description to a .description file.
                
            write_info (boolean): If True youtube-dl will write video 
                metadata to a .info.json file.
                
            write_thumbnail (boolean): If True youtube-dl will write
                thumbnail image to disk.
                
            retries (int): Number of youtube-dl retries.
            
            user_agent (string): Specify a custom user agent for youtube-dl.
            
            referer (string): Specify a custom referer to use if the video 
                access is restricted to one domain.
                
            proxy (string): Use the specified HTTP/HTTPS proxy.
            
            shutdown (boolean): If True youtube-dlg will turn the computer
                off after the download process has been completed.
                
            sudo_password (string): SUDO password for the shutdown process if
                the user does not have root access.
                
            username (string): Username to login with.
            
            password (string): Password to login with.
            
            video_password (string): Video password for the given URL.
            
            youtubedl_path (string): Absolute path to the youtube-dl binary.
                Default is the self.config_path. You can change this option
                to point on /usr/local/bin etc.. if you want to use the 
                youtube-dl binary on your system. This is also the directory
                where youtube-dlg will auto download the youtube-dl if not
                exists so you should make sure you have write access if you
                want to update the youtube-dl binary from within youtube-dlg.
                
            cmd_args (string): String that contains extra youtube-dl options
                seperated by spaces.
                
            enable_log (boolean): If True youtube-dlg will enable 
                the LogManager. See main() function under __init__().
                
            log_time (boolean): See logmanager.LogManager add_time attribute.
                
        """
        self.options = {
            'save_path': os.path.expanduser('~'),
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
            'min_filesize': 0,
            'max_filesize': 0,
            'min_filesize_unit': 'Bytes',
            'max_filesize_unit': 'Bytes',
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
        """Load options from settings file. """
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
        """Save options to settings file. """
        check_path(self.config_path)

        with open(self.settings_file, 'wb') as settings_file:
            options = self._get_options()
            json.dump(options,
                      settings_file,
                      indent=4,
                      separators=(',', ': '))

    def _settings_are_valid(self, settings_dictionary):
        """Check settings.json dictionary.
        
        Args:
            settings_dictionary (dictionary): Options dictionary loaded
                from the settings file. See load_from_file() method.
        
        Returns:
            True if settings.json dictionary is valid, else False.
        
        """
        for key in self.options:
            if key not in settings_dictionary:
                return False

        return True

    def _get_options(self):
        """Return options dictionary without SENSITIVE_KEYS. """
        temp_options = self.options.copy()
        
        for key in self.SENSITIVE_KEYS:
            temp_options[key] = ''
            
        return temp_options
        