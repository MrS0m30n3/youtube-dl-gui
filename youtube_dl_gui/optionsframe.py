#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg module responsible for the options window. """

from __future__ import unicode_literals

import os
import gettext

import wx

from .version import __version__

from .info import (
    __descriptionfull__,
    __licensefull__,
    __projecturl__,
    __appname__,
    __author__
)

from .utils import (
    TwoWayOrderedDict as twodict,
    os_path_exists,
    get_icon_file
)
#TODO Set up load-save methods
#TODO Adjust layout
#TODO Set frame's min size
#TODO Add labels to gettext


class OptionsFrame(wx.Frame):

    """Youtubedlg options frame class.

    Args:
        parent (mainframe.MainFrame): Parent class.

    """

    FRAME_TITLE = _("Options")

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=self.FRAME_TITLE, size=parent.opt_manager.options["opts_win_size"])
        self.opt_manager = parent.opt_manager
        self.log_manager = parent.log_manager
        self.app_icon = None

        # Set the app icon
        app_icon_path = get_icon_file()
        if app_icon_path is not None:
            self.app_icon = wx.Icon(app_icon_path, wx.BITMAP_TYPE_PNG)
            self.SetIcon(self.app_icon)

        self._was_shown = False

        # Create options frame basic components
        self.panel = wx.Panel(self)

        self.notebook = wx.Notebook(self.panel)
        self.separator_line = wx.StaticLine(self.panel)
        self.reset_button = wx.Button(self.panel, label="Reset")
        self.close_button = wx.Button(self.panel, label="Close")

        # Create tabs
        tab_args = (self, self.notebook)

        self.tabs = (
            (GeneralTab(*tab_args), "General"),
            (FormatsTab(*tab_args), "Formats"),
            (DownloadsTab(*tab_args), "Downloads"),
            (AdvancedTab(*tab_args), "Advanced"),
            (ExtraTab(*tab_args), "Extra")
        )

        # Add tabs on notebook
        for tab, label in self.tabs:
            self.notebook.AddPage(tab, label)

        # Bind events
        self.Bind(wx.EVT_BUTTON, self._on_reset, self.reset_button)
        self.Bind(wx.EVT_BUTTON, self._on_close, self.close_button)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        self._set_layout()
        self.load_all_options()

    def _set_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)
        main_sizer.Add(self.separator_line, 0, wx.EXPAND)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.reset_button)
        buttons_sizer.Add(self.close_button)

        main_sizer.Add(buttons_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        self.panel.SetSizer(main_sizer)

    def _on_close(self, event):
        """Event handler for wx.EVT_CLOSE event."""
        self.save_all_options()
        self.Hide()

    def _on_reset(self, event):
        """Event handler for the reset button wx.EVT_BUTTON event."""
        self.reset()

    def reset(self):
        """Reset the default options."""
        self.opt_manager.load_default()
        self.load_all_options()

    def load_all_options(self):
        """Load all the options on each tab."""
        for tab, _ in self.tabs:
            tab.load_options()

    def save_all_options(self):
        """Save all the options from all the tabs back to the OptionsManager."""
        for tab, _ in self.tabs:
            tab.save_options()

    def Show(self, *args, **kwargs):
        # CenterOnParent can't go to main frame's __init__ as main frame may change
        # own position and options frame won't be centered on main frame anymore.
        if not self._was_shown:
            self._was_shown = True
            self.CenterOnParent()
        return wx.Frame.Show(self, *args, **kwargs)


class TabPanel(wx.Panel):

    """Main tab class from which each tab inherits.

    Args:
        parent (OptionsFrame): The parent of all tabs.

        notebook (wx.Notebook): The container for each tab.

    Notes:
        In order to use a different size you must overwrite the below *_SIZE
        attributes on the corresponding child object.

    """

    CHECKBOX_SIZE = (-1, -1)
    if os.name == "nt":
        # Make checkboxes look the same on Windows
        CHECKBOX_SIZE = (-1, 25)

    BUTTONS_SIZE = (-1, -1)
    TEXTCTRL_SIZE = (-1, -1)
    SPINCTRL_SIZE = (70, -1)

    def __init__(self, parent, notebook):
        wx.Panel.__init__(self, notebook)
        self.opt_manager = parent.opt_manager
        self.log_manager = parent.log_manager
        self.app_icon = parent.app_icon

        self.reset_handler = parent.reset

    # Shortcut methods below

    def crt_button(self, label, event_handler=None):
        button = wx.Button(self, label=label, size=self.BUTTONS_SIZE)

        if event_handler is not None:
            button.Bind(wx.EVT_BUTTON, event_handler)

        return button

    def crt_checkbox(self, label, event_handler=None):
        checkbox = wx.CheckBox(self, label=label, size=self.CHECKBOX_SIZE)

        if event_handler is not None:
            checkbox.Bind(wx.EVT_CHECKBOX, event_handler)

        return checkbox

    def crt_textctrl(self, style=None):
        if style is None:
            textctrl = wx.TextCtrl(self, size=self.TEXTCTRL_SIZE)
        else:
            textctrl = wx.TextCtrl(self, size=self.TEXTCTRL_SIZE, style=style)

        return textctrl

    def crt_combobox(self, choices, size=(-1, -1), event_handler=None):
        combobox = wx.ComboBox(self, choices=choices, size=size, style=wx.CB_READONLY)

        if event_handler is not None:
            combobox.Bind(wx.EVT_COMBOBOX, event_handler)

        return combobox

    def crt_spinctrl(self, spin_range=(0, 9999)):
        spinctrl = wx.SpinCtrl(self, size=self.SPINCTRL_SIZE)
        spinctrl.SetRange(*spin_range)

        return spinctrl

    def crt_statictext(self, label):
        return wx.StaticText(self, wx.ID_ANY, label)


class GeneralTab(TabPanel):

    LOCALE_NAMES = twodict([
        ('ar_AR', 'Arabic'),
        ('cs_CZ', 'Czech'),
        ('en_US', 'English'),
        ('fr_FR', 'French'),
        ('de_DE', 'German'),
        ('it_IT', 'Italian'),
        ('he_IS', 'Hebrew'),
        ('hu_HU', 'Hungarian'),
        ('pt_BR', 'Portuguese'),
        ('ru_RU', 'Russian'),
        ('es_ES', 'Spanish'),
        ('es_MX', 'Mexican Spanish'),
        ('tr_TR', 'Turkish')
    ])

    # TODO Add support on parsers.py
    OUTPUT_FORMATS = [
        "Title",
        "Title + Quality",
        "Title + ID",
        "Title + ID + Quality",
        "Custom"
    ]

    def __init__(self, *args, **kwargs):
        super(GeneralTab, self).__init__(*args, **kwargs)

        self.language_label = self.crt_statictext("Language")
        self.language_combobox = self.crt_combobox(self.LOCALE_NAMES.values())

        self.filename_format_label = self.crt_statictext("Filename format")
        self.filename_format_combobox = self.crt_combobox(self.OUTPUT_FORMATS)
        self.filename_custom_format = self.crt_textctrl()

        self.filename_opts_label = self.crt_statictext("Filename options")
        self.filename_ascii_checkbox = self.crt_checkbox("Restrict filenames to ASCII")

        self.more_opts_label = self.crt_statictext("More options")
        self.confirm_exit_checkbox = self.crt_checkbox("Confirm on exit")

        self.shutdown_checkbox = self.crt_checkbox("Shutdown")
        self.sudo_textctrl = self.crt_textctrl(wx.TE_PASSWORD)

        self._set_layout()

    def _set_layout(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        vertical_sizer.Add(self.language_label)
        vertical_sizer.Add(self.language_combobox, flag=wx.EXPAND | wx.ALL, border=5)

        vertical_sizer.Add(self.filename_format_label)
        vertical_sizer.Add(self.filename_format_combobox, flag=wx.EXPAND | wx.ALL, border=5)
        vertical_sizer.Add(self.filename_custom_format, flag=wx.EXPAND | wx.ALL, border=5)

        vertical_sizer.Add(self.filename_opts_label)
        vertical_sizer.Add(self.filename_ascii_checkbox, flag=wx.ALL, border=5)

        vertical_sizer.Add(self.more_opts_label)
        vertical_sizer.Add(self.confirm_exit_checkbox, flag=wx.ALL, border=5)

        shutdown_sizer = wx.BoxSizer(wx.HORIZONTAL)
        shutdown_sizer.Add(self.shutdown_checkbox)
        shutdown_sizer.AddSpacer((-1, -1), 1)
        shutdown_sizer.Add(self.sudo_textctrl, 1)

        vertical_sizer.Add(shutdown_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        main_sizer.Add(vertical_sizer, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(main_sizer)

    def load_options(self):
        pass

    def save_options(self):
        pass


class FormatsTab(TabPanel):

    AUDIO_QUALITY = twodict([("0", _("high")), ("5", _("mid")), ("9", _("low"))])

    #TODO Move those to separate file
    AUDIO_FORMATS = ["mp3", "wav", "aac", "m4a", "vorbis", "opus"]

    def __init__(self, *args, **kwargs):
        super(FormatsTab, self).__init__(*args, **kwargs)

        self.video_formats_label = wx.StaticText(self, label="Video formats")
        self.video_formats_checklistbox = wx.CheckListBox(self)

        self.audio_formats_label = wx.StaticText(self, label="Audio formats")
        self.audio_formats_checklistbox = wx.CheckListBox(self)

        self.post_proc_opts_label = wx.StaticText(self, label="Post-Process options")
        self.keep_video_checkbox = wx.CheckBox(self, label="Keep original video")

        self.audio_quality_label = wx.StaticText(self, label="Audio quality")
        self.audio_quality_combobox = wx.ComboBox(self, size=(100, -1), style=wx.CB_READONLY)

        self._set_layout()

    def _set_layout(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        vertical_sizer.Add(self.video_formats_label)
        vertical_sizer.Add(self.video_formats_checklistbox, 1, wx.EXPAND | wx.ALL, border=5)

        vertical_sizer.Add(self.audio_formats_label)
        vertical_sizer.Add(self.audio_formats_checklistbox, 1, wx.EXPAND | wx.ALL, border=5)

        vertical_sizer.Add(self.post_proc_opts_label)
        vertical_sizer.Add(self.keep_video_checkbox, flag=wx.ALL, border=5)

        audio_quality_sizer = wx.BoxSizer(wx.HORIZONTAL)
        audio_quality_sizer.Add(self.audio_quality_label, flag=wx.ALIGN_CENTER_VERTICAL)
        audio_quality_sizer.AddSpacer((20, -1))
        audio_quality_sizer.Add(self.audio_quality_combobox)

        vertical_sizer.Add(audio_quality_sizer, flag=wx.LEFT | wx.RIGHT, border=10)

        main_sizer.Add(vertical_sizer, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(main_sizer)

    def load_options(self):
        pass

    def save_options(self):
        pass


class DownloadsTab(TabPanel):

    SUBS_LANG = twodict([
        ("en", _("English")),
        ("gr", _("Greek")),
        ("pt", _("Portuguese")),
        ("fr", _("French")),
        ("it", _("Italian")),
        ("ru", _("Russian")),
        ("es", _("Spanish")),
        ("tr", _("Turkish")),
        ("de", _("German"))
    ])

    FILESIZES = twodict([
        ("", "Bytes"),
        ("k", "Kilobytes"),
        ("m", "Megabytes"),
        ("g", "Gigabytes"),
        ("t", "Terabytes"),
        ("p", "Petabytes"),
        ("e", "Exabytes"),
        ("z", "Zettabytes"),
        ("y", "Yottabytes")
    ])

    def __init__(self, *args, **kwargs):
        super(DownloadsTab, self).__init__(*args, **kwargs)

        self.subtitles_label = wx.StaticText(self, label="Subtitles")
        self.subtitles_combobox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.subtitles_lang_listbox = wx.ListBox(self)

        self.subtitles_opts_label = wx.StaticText(self, label="Subtitles options")
        self.embed_subs_checkbox = wx.CheckBox(self, label="Embed subtitles into video file (mp4 ONLY)")

        self.playlist_box = wx.StaticBox(self, label="Playlist")

        self.playlist_start_label = wx.StaticText(self, label="Start")
        self.playlist_start_spinctrl = wx.SpinCtrl(self, size=(80, -1))
        self.playlist_stop_label = wx.StaticText(self, label="Stop")
        self.playlist_stop_spinctrl = wx.SpinCtrl(self, size=(80, -1))
        self.playlist_max_label = wx.StaticText(self, label="Max")
        self.playlist_max_spinctrl = wx.SpinCtrl(self, size=(80, -1))

        self.filesize_box = wx.StaticBox(self, label="Filesize")

        self.filesize_min_label = wx.StaticText(self, label="Min")
        self.filesize_min_spinctrl = wx.SpinCtrl(self)
        self.filesize_min_sizeunit_combobox = wx.ComboBox(self)
        self.filesize_max_label = wx.StaticText(self, label="Max")
        self.filesize_max_spinctrl = wx.SpinCtrl(self)
        self.filesize_max_sizeunit_combobox = wx.ComboBox(self)

        self._set_layout()

    def _set_layout(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        vertical_sizer.Add(self.subtitles_label)
        vertical_sizer.Add(self.subtitles_combobox, flag=wx.EXPAND | wx.ALL, border=5)
        vertical_sizer.Add(self.subtitles_lang_listbox, 1, wx.EXPAND | wx.ALL, border=5)

        vertical_sizer.Add(self.subtitles_opts_label)
        vertical_sizer.Add(self.embed_subs_checkbox, flag=wx.ALL, border=5)

        plist_and_fsize_sizer = wx.BoxSizer(wx.HORIZONTAL)
        plist_and_fsize_sizer.Add(self._build_playlist_sizer(), 1, wx.EXPAND)
        plist_and_fsize_sizer.AddSpacer((10, -1))
        plist_and_fsize_sizer.Add(self._build_filesize_sizer(), 1, wx.EXPAND)

        vertical_sizer.Add(plist_and_fsize_sizer, 1, wx.EXPAND | wx.TOP, border=5)

        main_sizer.Add(vertical_sizer, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(main_sizer)

    def _build_playlist_sizer(self):
        left_right_border = 80

        playlist_box_sizer = wx.StaticBoxSizer(self.playlist_box, wx.VERTICAL)
        playlist_box_sizer.AddSpacer((-1, 10))

        start_plist_sizer = wx.BoxSizer(wx.HORIZONTAL)
        start_plist_sizer.AddSpacer((left_right_border, -1))
        start_plist_sizer.Add(self.playlist_start_label, flag=wx.ALIGN_CENTER_VERTICAL)
        start_plist_sizer.AddSpacer((-1, -1), 1)
        start_plist_sizer.Add(self.playlist_start_spinctrl)
        start_plist_sizer.AddSpacer((left_right_border, -1))

        stop_plist_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stop_plist_sizer.AddSpacer((left_right_border, -1))
        stop_plist_sizer.Add(self.playlist_stop_label, flag=wx.ALIGN_CENTER_VERTICAL)
        stop_plist_sizer.AddSpacer((-1, -1), 1)
        stop_plist_sizer.Add(self.playlist_stop_spinctrl)
        stop_plist_sizer.AddSpacer((left_right_border, -1))

        max_plist_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_plist_sizer.AddSpacer((left_right_border, -1))
        max_plist_sizer.Add(self.playlist_max_label, flag=wx.ALIGN_CENTER_VERTICAL)
        max_plist_sizer.AddSpacer((-1, -1), 1)
        max_plist_sizer.Add(self.playlist_max_spinctrl)
        max_plist_sizer.AddSpacer((left_right_border, -1))

        playlist_box_sizer.Add(start_plist_sizer, flag=wx.EXPAND | wx.TOP, border=5)
        playlist_box_sizer.Add(stop_plist_sizer, flag=wx.EXPAND | wx.TOP, border=5)
        playlist_box_sizer.Add(max_plist_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        return playlist_box_sizer

    def _build_filesize_sizer(self):
        left_right_border = 40

        filesize_box_sizer = wx.StaticBoxSizer(self.filesize_box, wx.VERTICAL)
        filesize_box_sizer.AddSpacer((-1, 10))

        max_filesize_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_filesize_sizer.AddSpacer((left_right_border, -1))
        max_filesize_sizer.Add(self.filesize_max_spinctrl)
        max_filesize_sizer.AddSpacer((-1, -1), 1)
        max_filesize_sizer.Add(self.filesize_max_sizeunit_combobox)
        max_filesize_sizer.AddSpacer((left_right_border, -1))

        min_filesize_sizer = wx.BoxSizer(wx.HORIZONTAL)
        min_filesize_sizer.AddSpacer((left_right_border, -1))
        min_filesize_sizer.Add(self.filesize_min_spinctrl)
        min_filesize_sizer.AddSpacer((-1, -1), 1)
        min_filesize_sizer.Add(self.filesize_min_sizeunit_combobox)
        min_filesize_sizer.AddSpacer((left_right_border, -1))

        filesize_box_sizer.Add(self.filesize_max_label, flag=wx.ALIGN_CENTER_HORIZONTAL)
        filesize_box_sizer.Add(max_filesize_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        filesize_box_sizer.Add(self.filesize_min_label, flag=wx.ALIGN_CENTER_HORIZONTAL)
        filesize_box_sizer.Add(min_filesize_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        return filesize_box_sizer

    def load_options(self):
        pass

    def save_options(self):
        pass


class AdvancedTab(TabPanel):

    def __init__(self, *args, **kwargs):
        super(AdvancedTab, self).__init__(*args, **kwargs)

        self.retries_label = wx.StaticText(self, label="Retries")
        self.retries_spinctrl = wx.SpinCtrl(self, size=(70, -1))

        self.auth_label = wx.StaticText(self, label="Authentication")

        self.username_label = wx.StaticText(self, label="Username")
        self.username_textctrl = wx.TextCtrl(self, size=(250, -1))
        self.password_label = wx.StaticText(self, label="Password")
        self.password_textctrl = wx.TextCtrl(self, size=(250, -1), style=wx.TE_PASSWORD)
        self.video_pass_label = wx.StaticText(self, label="Video password")
        self.video_pass_textctrl = wx.TextCtrl(self, size=(250, -1), style=wx.TE_PASSWORD)

        self.network_label = wx.StaticText(self, label="Network")

        self.proxy_label = wx.StaticText(self, label="Proxy")
        self.proxy_textctrl = wx.TextCtrl(self, size=(250, -1))
        self.useragent_label = wx.StaticText(self, label="User agent")
        self.useragent_textctrl = wx.TextCtrl(self, size=(250, -1))
        self.referer_label = wx.StaticText(self, label="Referer")
        self.referer_textctrl = wx.TextCtrl(self, size=(250, -1))

        self.logging_label = wx.StaticText(self, label="Logging")

        self.enable_log_checkbox = wx.CheckBox(self, label="Enable log")
        self.view_log_button = wx.Button(self, label="View")
        self.clear_log_button = wx.Button(self, label="Clear")

        self._set_layout()

    def _set_layout(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        retries_sizer = wx.BoxSizer(wx.HORIZONTAL)
        retries_sizer.AddSpacer((10, -1))
        retries_sizer.Add(self.retries_label, flag=wx.ALIGN_CENTER_VERTICAL)
        retries_sizer.AddSpacer((20, -1))
        retries_sizer.Add(self.retries_spinctrl)
        retries_sizer.AddSpacer((10, -1))

        vertical_sizer.Add(retries_sizer, flag=wx.ALIGN_RIGHT | wx.TOP, border=5)

        vertical_sizer.Add(self.auth_label, flag=wx.TOP, border=5)

        username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        username_sizer.AddSpacer((10, -1))
        username_sizer.Add(self.username_label, flag=wx.ALIGN_CENTER_VERTICAL)
        username_sizer.AddSpacer((-1, -1), 1)
        username_sizer.Add(self.username_textctrl)
        username_sizer.AddSpacer((10, -1))

        vertical_sizer.Add(username_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_sizer.AddSpacer((10, -1))
        password_sizer.Add(self.password_label, flag=wx.ALIGN_CENTER_VERTICAL)
        password_sizer.AddSpacer((-1, -1), 1)
        password_sizer.Add(self.password_textctrl)
        password_sizer.AddSpacer((10, -1))

        vertical_sizer.Add(password_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        video_pass_sizer = wx.BoxSizer(wx.HORIZONTAL)
        video_pass_sizer.AddSpacer((10, -1))
        video_pass_sizer.Add(self.video_pass_label, flag=wx.ALIGN_CENTER_VERTICAL)
        video_pass_sizer.AddSpacer((-1, -1), 1)
        video_pass_sizer.Add(self.video_pass_textctrl)
        video_pass_sizer.AddSpacer((10, -1))

        vertical_sizer.Add(video_pass_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        vertical_sizer.Add(self.network_label, flag=wx.TOP, border=15)

        proxy_sizer = wx.BoxSizer(wx.HORIZONTAL)
        proxy_sizer.AddSpacer((10, -1))
        proxy_sizer.Add(self.proxy_label, flag=wx.ALIGN_CENTER_VERTICAL)
        proxy_sizer.AddSpacer((-1, -1), 1)
        proxy_sizer.Add(self.proxy_textctrl)
        proxy_sizer.AddSpacer((10, -1))

        vertical_sizer.Add(proxy_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        useragent_sizer = wx.BoxSizer(wx.HORIZONTAL)
        useragent_sizer.AddSpacer((10, -1))
        useragent_sizer.Add(self.useragent_label, flag=wx.ALIGN_CENTER_VERTICAL)
        useragent_sizer.AddSpacer((-1, -1), 1)
        useragent_sizer.Add(self.useragent_textctrl)
        useragent_sizer.AddSpacer((10, -1))

        vertical_sizer.Add(useragent_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        referer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        referer_sizer.AddSpacer((10, -1))
        referer_sizer.Add(self.referer_label, flag=wx.ALIGN_CENTER_VERTICAL)
        referer_sizer.AddSpacer((-1, -1), 1)
        referer_sizer.Add(self.referer_textctrl)
        referer_sizer.AddSpacer((10, -1))

        vertical_sizer.Add(referer_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        vertical_sizer.Add(self.logging_label, flag=wx.TOP, border=15)

        logging_sizer = wx.BoxSizer(wx.HORIZONTAL)
        logging_sizer.AddSpacer((10, -1))
        logging_sizer.Add(self.enable_log_checkbox)
        logging_sizer.AddSpacer((-1, -1), 1)
        logging_sizer.Add(self.view_log_button)
        logging_sizer.Add(self.clear_log_button)
        logging_sizer.AddSpacer((10, -1))

        vertical_sizer.Add(logging_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        main_sizer.Add(vertical_sizer, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(main_sizer)

    def load_options(self):
        pass

    def save_options(self):
        pass


class ExtraTab(TabPanel):

    def __init__(self, *args, **kwargs):
        super(ExtraTab, self).__init__(*args, **kwargs)

        self.cmdline_args_label = wx.StaticText(self, label="Command line arguments (e.g. --help)")
        self.cmdline_args_textctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_LINEWRAP)

        self.extra_opts_label = wx.StaticText(self, label="Extra options")
        self.ignore_errors_checkbox = wx.CheckBox(self, label="Ignore errors")

        self._set_layout()

    def _set_layout(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        vertical_sizer.Add(self.cmdline_args_label)
        vertical_sizer.Add(self.cmdline_args_textctrl, 1, wx.EXPAND | wx.ALL, border=5)

        vertical_sizer.Add(self.extra_opts_label)

        extra_opts_sizer = wx.WrapSizer()
        extra_opts_sizer.Add(self.ignore_errors_checkbox)

        vertical_sizer.Add(extra_opts_sizer, flag=wx.ALL, border=5)

        main_sizer.Add(vertical_sizer, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(main_sizer)

    def load_options(self):
        pass

    def save_options(self):
        pass


class LogGUI(wx.Frame):

    """Simple window for reading the STDERR.

    Attributes:
        TITLE (string): Frame title.
        FRAME_SIZE (tuple): Tuple that holds the frame size (width, height).

    Args:
        parent (wx.Window): Frame parent.

    """

    # REFACTOR move it on widgets module

    TITLE = _("Log Viewer")
    FRAME_SIZE = (650, 200)

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, title=self.TITLE, size=self.FRAME_SIZE)

        panel = wx.Panel(self)

        self._text_area = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )

        sizer = wx.BoxSizer()
        sizer.Add(self._text_area, 1, wx.EXPAND)
        panel.SetSizerAndFit(sizer)

    def load(self, filename):
        """Load file content on the text area. """
        if os_path_exists(filename):
            self._text_area.LoadFile(filename)
