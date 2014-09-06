#!/usr/bin/env python2

''' Contains code for youtube-dlG options frame. '''

from os import name

import wx

from .LogManager import LogGUI
from .version import __version__
from .utils import (
    get_icon_path,
    fix_path
)

from .data import (
    __descriptionfull__,
    __licensefull__,
    __projecturl__,
    __appname__,
    __author__
)

AUDIO_QUALITY = ['high', 'mid', 'low']

AUDIO_FORMATS = [
    "mp3",
    "wav",
    "aac",
    "m4a",
    "vorbis"
]

FORMATS = [
    "3gp [176x144]",
    "3gp [320x240]",
    "flv [400x240]",
    "flv [640x360]",
    "flv [854x480]",
    "webm [640x360]",
    "webm [854x480]",
    "webm [1280x720]",
    "webm [1920x1080]",
    "mp4 [640x360]",
    "mp4 [1280x720]",
    "mp4 [1920x1080]",
    "mp4 [4096x3072]",
    "mp4 144p (DASH)",
    "mp4 240p (DASH)",
    "mp4 360p (DASH)",
    "mp4 480p (DASH)",
    "mp4 720p (DASH)",
    "mp4 1080p (DASH)",
    "mp4 1440p (DASH)",
    "mp4 2160p (DASH)",
    "webm 240p (DASH)",
    "webm 360p (DASH)",
    "webm 480p (DASH)",
    "webm 720p (DASH)",
    "webm 1080p (DASH)",
    "webm 1440p (DASH)",
    "webm 2160p (DASH)",
    "mp4 360p (3D)",
    "mp4 480p (3D)",
    "mp4 720p (3D)",
    "mp4 1080p (3D)",
    "webm 360p (3D)",
    "webm 480p (3D)",
    "webm 720p (3D)",
    "m4a 48k (DASH AUDIO)",
    "m4a 128k (DASH AUDIO)",
    "m4a 256k (DASH AUDIO)",
    "webm 48k (DASH AUDIO)",
    "webm 256k (DASH AUDIO)"
]

VIDEO_FORMATS = ["default"] + FORMATS

SECOND_VIDEO_FORMATS = ["none"] + FORMATS

SUBS_LANG = [
    "English",
    "Greek",
    "Portuguese",
    "French",
    "Italian",
    "Russian",
    "Spanish",
    "German"
]

# Set wx.CheckBox height for Windows & Linux
# so it looks the same on both platforms
WX_CHECKBOX_SIZE = (-1, -1)
if name == 'nt':
    WX_CHECKBOX_SIZE = (-1, 25)


class OptionsFrame(wx.Frame):

    '''
    Youtube-dlG options frame.

    Params
        opt_manager: OptionsManager.OptionsManager object.
        parent: Frame parent.
        logger: LogManager.LogManager object.

    Accessible Methods
        reset()
            Params: None

            Return: None

        load_all_options()
            Params: None

            Return: None

        save_all_options()
            Params: None

            Return: None
    '''

    def __init__(self, opt_manager, parent=None, logger=None):
        wx.Frame.__init__(self, parent, -1, "Options", size=(640, 270))

        self.opt_manager = opt_manager

        # Add icon
        icon = get_icon_path()
        if icon is not None:
            self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_PNG))
        
        # Create GUI
        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)

        # Create Tabs
        self.tabs = (
            (GeneralPanel(notebook, self.opt_manager, self.reset), "General"),
            (VideoPanel(notebook), "Video"),
            (AudioPanel(notebook), "Audio"),
            (PlaylistPanel(notebook), "Playlist"),
            (OutputPanel(notebook), "Output"),
            (SubtitlesPanel(notebook), "Subtitles"),
            (FilesystemPanel(notebook), "Filesystem"),
            (ShutdownPanel(notebook), "Shutdown"),
            (AuthenticationPanel(notebook), "Authentication"),
            (ConnectionPanel(notebook), "Connection"),
            (LogPanel(notebook, logger), "Log"),
            (OtherPanel(notebook), "Commands")
        )

        # Add tabs on notebook
        for tab, label in self.tabs:
            notebook.AddPage(tab, label)

        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.load_all_options()

    def OnClose(self, event):
        ''' Event handler for wx.EVT_CLOSE. '''
        self.save_all_options()
        self.Destroy()

    def reset(self):
        ''' Reset default options. '''
        self.opt_manager.load_default()
        self.load_all_options()

    def load_all_options(self):
        ''' Load tabs options. '''
        for tab, _ in self.tabs:
            tab.load_options(self.opt_manager)

    def save_all_options(self):
        ''' Save tabs options '''
        for tab, _ in self.tabs:
            tab.save_options(self.opt_manager)


class LogPanel(wx.Panel):

    '''
    Options frame log tab panel.

    Params
        parent: wx.Panel parent.
        logger: LogManager.LogManager.object.
    '''

    def __init__(self, parent, logger):
        wx.Panel.__init__(self, parent)

        self.logger = logger

        # Create components
        self.enable_checkbox = wx.CheckBox(self, label='Enable Log', size=WX_CHECKBOX_SIZE)
        self.time_checkbox = wx.CheckBox(self, label='Write Time', size=WX_CHECKBOX_SIZE)
        self.clear_button = wx.Button(self, label='Clear Log')
        self.view_button = wx.Button(self, label='View Log')

        if self.logger is None:
            self.time_checkbox.Disable()
            self.clear_button.Disable()
            self.view_button.Disable()

        # Set BoxSizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(20)
        main_sizer.Add(self.enable_checkbox, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.time_checkbox, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(15)
        main_sizer.Add(self._create_buttons_sizer(), flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Create extra items
        if logger is not None:
            path_text = wx.StaticText(self, label="Path: " + self.logger.log_file)
            self.log_size = wx.StaticText(self, label="Log Size %s Bytes" % self.logger.size())

            main_sizer.AddSpacer(20)
            main_sizer.Add(path_text, flag=wx.ALIGN_CENTER_HORIZONTAL)
            main_sizer.AddSpacer(10)
            main_sizer.Add(self.log_size, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(main_sizer)

        # Set Events
        self.Bind(wx.EVT_CHECKBOX, self.OnEnable, self.enable_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnTime, self.time_checkbox)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clear_button)
        self.Bind(wx.EVT_BUTTON, self.OnView, self.view_button)

    def _create_buttons_sizer(self):
        ''' Create buttons BoxSizer. '''
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.clear_button)
        sizer.AddSpacer(20)
        sizer.Add(self.view_button)

        return sizer

    def _create_popup(self, text, title, style):
        ''' Create popup. '''
        wx.MessageBox(text, title, style)

    def OnTime(self, event):
        ''' Event handler for self.time_checkbox. '''
        if self.logger is not None:
            self.logger.add_time = self.time_checkbox.GetValue()

    def OnEnable(self, event):
        ''' Event handler for self.enable_checkbox. '''
        self._create_popup(
            'Please restart ' + __appname__,
            'Restart',
            wx.OK | wx.ICON_INFORMATION
        )

    def OnClear(self, event):
        ''' Event handler for self.clear_button. '''
        if self.logger is not None:
            self.logger.clear()
            self.log_size.SetLabel("Log Size %s Bytes" % self.logger.size())

    def OnView(self, event):
        ''' Event handler for self.view_button. '''
        if self.logger is not None:
            logger_gui = LogGUI(self)
            logger_gui.Show()
            logger_gui.load(self.logger.log_file)

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.enable_checkbox.SetValue(opt_manager.options['enable_log'])
        self.time_checkbox.SetValue(opt_manager.options['log_time'])

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['enable_log'] = self.enable_checkbox.GetValue()
        opt_manager.options['log_time'] = self.time_checkbox.GetValue()


class ShutdownPanel(wx.Panel):

    '''
    Options frame shutdown tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.shutdown_checkbox = wx.CheckBox(self, label='Shutdown when finished', size=WX_CHECKBOX_SIZE)
        self.sudo_pass_box = wx.TextCtrl(self, size=(250, 25), style=wx.TE_PASSWORD)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(40)
        main_sizer.Add(self.shutdown_checkbox, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(20)
        main_sizer.Add(wx.StaticText(self, label='SUDO password'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.sudo_pass_box, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnShutdownCheck, self.shutdown_checkbox)

    def OnShutdownCheck(self, event):
        ''' Event handler for self.shutdown_checkbox. '''
        if name != 'nt':
            self.sudo_pass_box.Enable(self.shutdown_checkbox.GetValue())

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.shutdown_checkbox.SetValue(opt_manager.options['shutdown'])
        self.sudo_pass_box.SetValue(opt_manager.options['sudo_password'])
        if name == 'nt' or not opt_manager.options['shutdown']:
            self.sudo_pass_box.Disable()

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['shutdown'] = self.shutdown_checkbox.GetValue()
        opt_manager.options['sudo_password'] = self.sudo_pass_box.GetValue()


class PlaylistPanel(wx.Panel):

    '''
    Options frame playlist tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.start_spinner = wx.SpinCtrl(self, size=(70, 20))
        self.start_spinner.SetRange(1, 999)
        self.stop_spinner = wx.SpinCtrl(self, size=(70, 20))
        self.stop_spinner.SetRange(0, 999)
        self.max_spinner = wx.SpinCtrl(self, size=(70, 20))
        self.max_spinner.SetRange(0, 999)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(20)
        main_sizer.Add(wx.StaticText(self, label='Playlist Start'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.start_spinner, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(15)
        main_sizer.Add(wx.StaticText(self, label='Playlist Stop'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.stop_spinner, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(15)
        main_sizer.Add(wx.StaticText(self, label='Max Downloads'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.max_spinner, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(main_sizer)

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.start_spinner.SetValue(opt_manager.options['playlist_start'])
        self.stop_spinner.SetValue(opt_manager.options['playlist_end'])
        self.max_spinner.SetValue(opt_manager.options['max_downloads'])

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['playlist_start'] = self.start_spinner.GetValue()
        opt_manager.options['playlist_end'] = self.stop_spinner.GetValue()
        opt_manager.options['max_downloads'] = self.max_spinner.GetValue()


class ConnectionPanel(wx.Panel):

    '''
    Options frame connection tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Create components
        self.retries_spinner = wx.SpinCtrl(self, size=(50, -1))
        self.retries_spinner.SetRange(1, 99)
        self.user_agent_box = wx.TextCtrl(self, size=(550, -1))
        self.referer_box = wx.TextCtrl(self, size=(550, -1))
        self.proxy_box = wx.TextCtrl(self, size=(550, -1))

        # Set BoxSizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(10)
        main_sizer.Add(self._create_retries_sizer())
        main_sizer.AddSpacer(10)
        main_sizer.Add(wx.StaticText(self, label='User Agent'), flag=wx.LEFT, border=10)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.user_agent_box, flag=wx.LEFT, border=10)
        main_sizer.AddSpacer(10)
        main_sizer.Add(wx.StaticText(self, label='Referer'), flag=wx.LEFT, border=10)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.referer_box, flag=wx.LEFT, border=10)
        main_sizer.AddSpacer(10)
        main_sizer.Add(wx.StaticText(self, label='Proxy'), flag=wx.LEFT, border=10)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.proxy_box, flag=wx.LEFT, border=10)

        self.SetSizer(main_sizer)

    def _create_retries_sizer(self):
        ''' Create retries BoxSizer. '''
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.AddSpacer(10)
        sizer.Add(wx.StaticText(self, label='Retries'))
        sizer.AddSpacer(5)
        sizer.Add(self.retries_spinner)

        return sizer

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.proxy_box.SetValue(opt_manager.options['proxy'])
        self.referer_box.SetValue(opt_manager.options['referer'])
        self.retries_spinner.SetValue(opt_manager.options['retries'])
        self.user_agent_box.SetValue(opt_manager.options['user_agent'])

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['proxy'] = self.proxy_box.GetValue()
        opt_manager.options['referer'] = self.referer_box.GetValue()
        opt_manager.options['retries'] = self.retries_spinner.GetValue()
        opt_manager.options['user_agent'] = self.user_agent_box.GetValue()


class AuthenticationPanel(wx.Panel):

    '''
    Options frame authentication tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.username_box = wx.TextCtrl(self, size=(250, 25))
        self.password_box = wx.TextCtrl(self, size=(250, 25), style=wx.TE_PASSWORD)
        self.video_pass_box = wx.TextCtrl(self, size=(250, 25), style=wx.TE_PASSWORD)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(15)
        main_sizer.Add(wx.StaticText(self, label='Username'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.username_box, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(15)
        main_sizer.Add(wx.StaticText(self, label='Password'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.password_box, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(15)
        main_sizer.Add(wx.StaticText(self, label='Video Password (vimeo, smotri)'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.video_pass_box, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(main_sizer)

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.username_box.SetValue(opt_manager.options['username'])
        self.password_box.SetValue(opt_manager.options['password'])
        self.video_pass_box.SetValue(opt_manager.options['video_password'])

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['username'] = self.username_box.GetValue()
        opt_manager.options['password'] = self.password_box.GetValue()
        opt_manager.options['video_password'] = self.video_pass_box.GetValue()


class AudioPanel(wx.Panel):

    '''
    Options frame audio tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.to_audio_checkbox = wx.CheckBox(self, label='Convert to Audio', size=WX_CHECKBOX_SIZE)
        self.keep_video_checkbox = wx.CheckBox(self, label='Keep Video', size=WX_CHECKBOX_SIZE)
        self.audio_format_combo = wx.ComboBox(self, choices=AUDIO_FORMATS, size=(160, 30))
        self.audio_quality_combo = wx.ComboBox(self, choices=AUDIO_QUALITY, size=(80, 25))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(15)
        main_sizer.Add(self.to_audio_checkbox, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.keep_video_checkbox, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(10)
        main_sizer.Add(wx.StaticText(self, label='Audio Format'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.audio_format_combo, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(10)
        main_sizer.Add(wx.StaticText(self, label='Audio Quality'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.audio_quality_combo, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnAudioCheck, self.to_audio_checkbox)

    def OnAudioCheck(self, event):
        ''' Event handler for self.to_audio_checkbox. '''
        if self.to_audio_checkbox.GetValue():
            self.audio_format_combo.Enable()
            self.audio_quality_combo.Enable()
        else:
            self.audio_format_combo.Disable()
            self.audio_quality_combo.Disable()

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.to_audio_checkbox.SetValue(opt_manager.options['to_audio'])
        self.keep_video_checkbox.SetValue(opt_manager.options['keep_video'])
        self.audio_format_combo.SetValue(opt_manager.options['audio_format'])
        self.audio_quality_combo.SetValue(opt_manager.options['audio_quality'])
        self.OnAudioCheck(None)

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['to_audio'] = self.to_audio_checkbox.GetValue()
        opt_manager.options['keep_video'] = self.keep_video_checkbox.GetValue()
        opt_manager.options['audio_format'] = self.audio_format_combo.GetValue()
        opt_manager.options['audio_quality'] = self.audio_quality_combo.GetValue()


class VideoPanel(wx.Panel):

    '''
    Options frame video tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.video_format_combo = wx.ComboBox(self, choices=VIDEO_FORMATS, size=(200, 30))
        self.second_video_format_combo = wx.ComboBox(self, choices=SECOND_VIDEO_FORMATS, size=(200, 30))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(30)
        main_sizer.Add(wx.StaticText(self, label='Video Format'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.video_format_combo, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(10)
        main_sizer.Add(wx.StaticText(self, label='Mix Video Format'), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.second_video_format_combo, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_COMBOBOX, self.OnVideoFormatPick, self.video_format_combo)

    def OnVideoFormatPick(self, event):
        ''' Event handler for self.video_format_combo. '''
        if self.video_format_combo.GetValue() != 'default':
            self.second_video_format_combo.Enable()
        else:
            self.second_video_format_combo.Disable()

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.video_format_combo.SetValue(opt_manager.options['video_format'])
        self.second_video_format_combo.SetValue(opt_manager.options['second_video_format'])
        self.OnVideoFormatPick(None)

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['video_format'] = self.video_format_combo.GetValue()
        opt_manager.options['second_video_format'] = self.second_video_format_combo.GetValue()


class OutputPanel(wx.Panel):

    '''
    Options frame output tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.restrict_filenames_checkbox = wx.CheckBox(self, label='Restrict filenames (ASCII)', size=WX_CHECKBOX_SIZE)
        self.id_as_name_checkbox = wx.CheckBox(self, label='ID as Name', size=WX_CHECKBOX_SIZE)
        self.title_checkbox = wx.CheckBox(self, label='Title as Name', size=WX_CHECKBOX_SIZE)
        self.custom_title_checkbox = wx.CheckBox(self, label='Custom Template (youtube-dl)', size=WX_CHECKBOX_SIZE)
        self.title_template_box = wx.TextCtrl(self, size=(300, 20))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(15)
        main_sizer.Add(self.restrict_filenames_checkbox, flag=wx.LEFT, border=5)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.id_as_name_checkbox, flag=wx.LEFT, border=5)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.title_checkbox, flag=wx.LEFT, border=5)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.custom_title_checkbox, flag=wx.LEFT, border=5)
        main_sizer.AddSpacer(10)
        main_sizer.Add(self.title_template_box, flag=wx.LEFT, border=5)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.id_as_name_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.title_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.custom_title_checkbox)

    def _group_load(self, output_format):
        ''' Disable components base on output_format. '''
        if output_format == 'id':
            self.id_as_name_checkbox.SetValue(True)
            self.title_checkbox.SetValue(False)
            self.custom_title_checkbox.SetValue(False)
            self.title_template_box.Disable()
        elif output_format == 'title':
            self.id_as_name_checkbox.SetValue(False)
            self.title_checkbox.SetValue(True)
            self.custom_title_checkbox.SetValue(False)
            self.title_template_box.Disable()
        elif output_format == 'custom':
            self.id_as_name_checkbox.SetValue(False)
            self.title_checkbox.SetValue(False)
            self.custom_title_checkbox.SetValue(True)
            self.title_template_box.Enable()

    def _get_output_format(self):
        ''' Return output_format. '''
        if self.id_as_name_checkbox.GetValue():
            return 'id'
        elif self.title_checkbox.GetValue():
            return 'title'
        elif self.custom_title_checkbox.GetValue():
            return 'custom'

    def OnCheck(self, event):
        ''' Event handler for output checkboxes. '''
        box = event.GetEventObject()

        if box == self.id_as_name_checkbox:
            output_format = 'id'
        elif box == self.title_checkbox:
            output_format = 'title'
        else:
            output_format = 'custom'

        self._group_load(output_format)

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self._group_load(opt_manager.options['output_format'])
        self.title_template_box.SetValue(opt_manager.options['output_template'])
        self.restrict_filenames_checkbox.SetValue(opt_manager.options['restrict_filenames'])

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['output_format'] = self._get_output_format()
        opt_manager.options['output_template'] = self.title_template_box.GetValue()
        opt_manager.options['restrict_filenames'] = self.restrict_filenames_checkbox.GetValue()


class FilesystemPanel(wx.Panel):

    '''
    Options frame filesystem tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.ignore_errors_checkbox = wx.CheckBox(self, label='Ignore Errors', size=WX_CHECKBOX_SIZE)
        self.open_dir_checkbox = wx.CheckBox(self, label='Open download folder', size=WX_CHECKBOX_SIZE)
        self.write_info_checkbox = wx.CheckBox(self, label='Write info to (.json) file', size=WX_CHECKBOX_SIZE)
        self.write_desc_checkbox = wx.CheckBox(self, label='Write description to file', size=WX_CHECKBOX_SIZE)
        self.write_thumbnail_checkbox = wx.CheckBox(self, label='Write thumbnail to disk', size=WX_CHECKBOX_SIZE)

        self.min_filesize_box = wx.TextCtrl(self, size=(70, -1))
        self.max_filesize_box = wx.TextCtrl(self, size=(70, -1))

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(self._set_left_sizer(), flag=wx.EXPAND)
        main_sizer.AddSpacer(150)
        main_sizer.Add(self._set_right_sizer(), 1, flag=wx.EXPAND)

        self.SetSizer(main_sizer)

    def _set_left_sizer(self):
        ''' Set left BoxSizer. '''
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.AddSpacer(15)
        sizer.Add(self.ignore_errors_checkbox, flag=wx.LEFT, border=5)
        sizer.AddSpacer(5)
        sizer.Add(self.open_dir_checkbox, flag=wx.LEFT, border=5)
        sizer.AddSpacer(5)
        sizer.Add(self.write_desc_checkbox, flag=wx.LEFT, border=5)
        sizer.AddSpacer(5)
        sizer.Add(self.write_thumbnail_checkbox, flag=wx.LEFT, border=5)
        sizer.AddSpacer(5)
        sizer.Add(self.write_info_checkbox, flag=wx.LEFT, border=5)

        return sizer

    def _set_right_sizer(self):
        ''' Set right BoxSizer. '''
        static_box = wx.StaticBox(self, label='Filesize (e.g. 50k or 44.6m)')

        sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        sizer.AddSpacer(50)

        # Cross platform hack for the horizontal sizer
        # so it looks the same both on Windows & Linux
        extra_border = 0
        if name != 'nt':
            extra_border = 3

        hor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hor_sizer.Add(wx.StaticText(self, label='Min'))
        hor_sizer.AddSpacer(10 + extra_border)
        hor_sizer.Add(self.min_filesize_box)

        sizer.Add(hor_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        sizer.AddSpacer(10)

        hor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hor_sizer.Add(wx.StaticText(self, label='Max'))
        hor_sizer.AddSpacer(10)
        hor_sizer.Add(self.max_filesize_box)

        sizer.Add(hor_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        return sizer

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.open_dir_checkbox.SetValue(opt_manager.options['open_dl_dir'])
        self.min_filesize_box.SetValue(opt_manager.options['min_filesize'])
        self.max_filesize_box.SetValue(opt_manager.options['max_filesize'])
        self.write_info_checkbox.SetValue(opt_manager.options['write_info'])
        self.ignore_errors_checkbox.SetValue(opt_manager.options['ignore_errors'])
        self.write_desc_checkbox.SetValue(opt_manager.options['write_description'])
        self.write_thumbnail_checkbox.SetValue(opt_manager.options['write_thumbnail'])

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['write_thumbnail'] = self.write_thumbnail_checkbox.GetValue()
        opt_manager.options['write_description'] = self.write_desc_checkbox.GetValue()
        opt_manager.options['ignore_errors'] = self.ignore_errors_checkbox.GetValue()
        opt_manager.options['write_info'] = self.write_info_checkbox.GetValue()
        opt_manager.options['open_dl_dir'] = self.open_dir_checkbox.GetValue()
        opt_manager.options['min_filesize'] = self.min_filesize_box.GetValue()
        opt_manager.options['max_filesize'] = self.max_filesize_box.GetValue()
        # Check min_filesize input
        if opt_manager.options['min_filesize'] == '':
            opt_manager.options['min_filesize'] = '0'
        if opt_manager.options['max_filesize'] == '':
            opt_manager.options['max_filesize'] = '0'


class SubtitlesPanel(wx.Panel):

    '''
    Options frame subtitles tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.write_subs_checkbox = wx.CheckBox(self, label='Download subtitle file by language', size=WX_CHECKBOX_SIZE)
        self.write_all_subs_checkbox = wx.CheckBox(self, label='Download all available subtitles', size=WX_CHECKBOX_SIZE)
        self.write_auto_subs_checkbox = wx.CheckBox(self, label='Download automatic subtitle file (YOUTUBE ONLY)', size=WX_CHECKBOX_SIZE)
        self.embed_subs_checkbox = wx.CheckBox(self, label='Embed subtitles in the video (only for mp4 videos)', size=WX_CHECKBOX_SIZE)
        self.subs_languages_combo = wx.ComboBox(self, choices=SUBS_LANG, size=(140, 30))

        self.embed_subs_checkbox.Disable()
        self.subs_languages_combo.Disable()

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(15)
        main_sizer.Add(self.write_subs_checkbox, flag=wx.LEFT, border=5)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.write_all_subs_checkbox, flag=wx.LEFT, border=5)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.write_auto_subs_checkbox, flag=wx.LEFT, border=5)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.embed_subs_checkbox, flag=wx.LEFT, border=5)
        main_sizer.AddSpacer(10)
        main_sizer.Add(wx.StaticText(self, label='Subtitles Langues'), flag=wx.LEFT, border=10)
        main_sizer.AddSpacer(5)
        main_sizer.Add(self.subs_languages_combo, flag=wx.LEFT, border=15)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnWriteSubsChk, self.write_subs_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnWriteAllSubsChk, self.write_all_subs_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnWriteAutoSubsChk, self.write_auto_subs_checkbox)

    def OnWriteAutoSubsChk(self, event):
        ''' Event handler for self.write_auto_subs_checkbox. '''
        if self.write_auto_subs_checkbox.GetValue():
            self.embed_subs_checkbox.Enable()
            self.write_subs_checkbox.Disable()
            self.write_all_subs_checkbox.Disable()
        else:
            self.embed_subs_checkbox.Disable()
            self.embed_subs_checkbox.SetValue(False)
            self.write_subs_checkbox.Enable()
            self.write_all_subs_checkbox.Enable()

    def OnWriteSubsChk(self, event):
        ''' Event handler for self.write_subs_checkbox. '''
        if self.write_subs_checkbox.GetValue():
            self.embed_subs_checkbox.Enable()
            self.subs_languages_combo.Enable()
            self.write_all_subs_checkbox.Disable()
            self.write_auto_subs_checkbox.Disable()
        else:
            self.embed_subs_checkbox.Disable()
            self.embed_subs_checkbox.SetValue(False)
            self.subs_languages_combo.Disable()
            self.write_all_subs_checkbox.Enable()
            self.write_auto_subs_checkbox.Enable()

    def OnWriteAllSubsChk(self, event):
        ''' Event handler for self.write_all_subs_checkbox. '''
        if self.write_all_subs_checkbox.GetValue():
            self.write_subs_checkbox.Disable()
            self.write_auto_subs_checkbox.Disable()
        else:
            self.write_subs_checkbox.Enable()
            self.write_auto_subs_checkbox.Enable()

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.write_subs_checkbox.SetValue(opt_manager.options['write_subs'])
        self.subs_languages_combo.SetValue(opt_manager.options['subs_lang'])
        self.embed_subs_checkbox.SetValue(opt_manager.options['embed_subs'])
        self.write_all_subs_checkbox.SetValue(opt_manager.options['write_all_subs'])
        self.write_auto_subs_checkbox.SetValue(opt_manager.options['write_auto_subs'])
        self.OnWriteSubsChk(None)
        self.OnWriteAllSubsChk(None)
        self.OnWriteAutoSubsChk(None)

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['write_subs'] = self.write_subs_checkbox.GetValue()
        opt_manager.options['subs_lang'] = self.subs_languages_combo.GetValue()
        opt_manager.options['embed_subs'] = self.embed_subs_checkbox.GetValue()
        opt_manager.options['write_all_subs'] = self.write_all_subs_checkbox.GetValue()
        opt_manager.options['write_auto_subs'] = self.write_auto_subs_checkbox.GetValue()


class GeneralPanel(wx.Panel):

    '''
    Options frame general tab panel.

    Params
        parent: wx.Panel parent.
        opt_manager: OptionsHandler.OptionsHandler object.
        reset_handler: Method to reset all options & frame.
    '''

    def __init__(self, parent, opt_manager, reset_handler):
        wx.Panel.__init__(self, parent)

        self.reset_handler = reset_handler

        self.savepath_box = wx.TextCtrl(self)
        self.about_button = wx.Button(self, label='About', size=(110, 40))
        self.open_button = wx.Button(self, label='Open', size=(110, 40))
        self.reset_button = wx.Button(self, label='Reset Options', size=(110, 40))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(20)
        sp_label = wx.StaticText(self, label='Save Path')
        main_sizer.Add(sp_label, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(10)
        main_sizer.Add(self._create_savepath_sizer(), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        main_sizer.AddSpacer(20)
        main_sizer.Add(self._create_buttons_sizer(), flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(30)
        settings_file = wx.StaticText(self, label='Settings: ' + opt_manager.settings_file)
        main_sizer.Add(settings_file, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.open_button)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, self.about_button)
        self.Bind(wx.EVT_BUTTON, self.OnReset, self.reset_button)

    def _create_savepath_sizer(self):
        ''' Return self.savepath_box BoxSizer. '''
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.savepath_box, 1, flag=wx.LEFT | wx.RIGHT, border=80)

        return sizer

    def _create_buttons_sizer(self):
        ''' Return buttons BoxSizer. '''
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.about_button)
        sizer.Add(self.open_button, flag=wx.LEFT | wx.RIGHT, border=50)
        sizer.Add(self.reset_button)

        return sizer

    def OnReset(self, event):
        ''' Event handler reset button. '''
        self.reset_handler()

    def OnOpen(self, event):
        ''' Event handler open button. '''
        dlg = wx.DirDialog(None, "Choose directory")
        if dlg.ShowModal() == wx.ID_OK:
            self.savepath_box.SetValue(dlg.GetPath())

        dlg.Destroy()

    def OnAbout(self, event):
        ''' Event handler about button. '''
        info = wx.AboutDialogInfo()

        # Load about icon
        app_icon = get_icon_path()
        if app_icon is not None:
            info.SetIcon(wx.Icon(app_icon, wx.BITMAP_TYPE_PNG))
        
        info.SetName(__appname__)
        info.SetVersion(__version__)
        info.SetDescription(__descriptionfull__)
        info.SetWebSite(__projecturl__)
        info.SetLicense(__licensefull__)
        info.AddDeveloper(__author__)

        wx.AboutBox(info)

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.savepath_box.SetValue(opt_manager.options['save_path'])

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['save_path'] = fix_path(self.savepath_box.GetValue())


class OtherPanel(wx.Panel):

    '''
    Options frame command tab panel.

    Params
        parent: wx.Panel parent.
    '''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.cmd_args_box = wx.TextCtrl(self)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(50)
        label = wx.StaticText(self, label='Command line arguments (e.g. --help)')
        main_sizer.Add(label, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(10)
        main_sizer.Add(self._create_cmd_sizer(), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)

        self.SetSizer(main_sizer)

    def _create_cmd_sizer(self):
        ''' Create BoxSizer for self.cmd_args_box. '''
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.cmd_args_box, 1, wx.LEFT | wx.RIGHT, border=80)

        return sizer

    def load_options(self, opt_manager):
        ''' Load panel options from OptionsHandler object. '''
        self.cmd_args_box.SetValue(opt_manager.options['cmd_args'])

    def save_options(self, opt_manager):
        ''' Save panel options to OptionsHandler object. '''
        opt_manager.options['cmd_args'] = self.cmd_args_box.GetValue()
