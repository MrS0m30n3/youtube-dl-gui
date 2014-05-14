#! /usr/bin/env python

from time import time

import wx
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from .version import __version__
from .UpdateThread import UpdateThread
from .LogManager import LogManager, LogGUI
from .OptionsHandler import OptionsHandler
from .DownloadThread import DownloadManager

from .Utils import (
    get_youtubedl_filename,
    get_user_config_path,
    video_is_dash,
    audio_is_dash,
    shutdown_sys,
    file_exist,
    get_time,
    fix_path,
    abs_path,
    open_dir,
    os_type
)
from .data import (
    __author__,
    __appname__,
    __projecturl__,
    __licensefull__,
    __descriptionfull__
)

AUDIO_FORMATS = ["mp3", "wav", "aac", "m4a"]

VIDEO_FORMATS = [
    "default",
    "mp4 [1280x720]",
    "mp4 [640x360]",
    "webm [640x360]",
    "flv [400x240]",
    "3gp [320x240]",
    "mp4 1080p(DASH)",
    "mp4 720p(DASH)",
    "mp4 480p(DASH)",
    "mp4 360p(DASH)"
]

DASH_AUDIO_FORMATS = [
    "none",
    "DASH m4a audio 128k",
    "DASH webm audio 48k"
]

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

ICON = fix_path(abs_path(__file__)) + 'icons/youtube-dl-gui.png'

CONFIG_PATH = fix_path(get_user_config_path()) + __appname__.lower()


class MainFrame(wx.Frame):

    def __init__(self, parent=None, id=-1):
        wx.Frame.__init__(self, parent, id, __appname__, size=(650, 440))

        # init gui
        self.init_gui()

        # set app icon
        self.SetIcon(wx.Icon(ICON, wx.BITMAP_TYPE_ICO))

        # set publisher for update thread
        Publisher.subscribe(self.update_handler, "update")

        # set publisher for download thread
        Publisher.subscribe(self.download_handler, "download_manager")
        Publisher.subscribe(self.download_handler, "download_thread")

        # init variables
        self.successful_downloads = 0
        self.timer = 0
        self.ori_url_list = []
        self.opt_manager = None
        self.log_manager = None
        self.update_thread = None
        self.download_thread = None

        # init Options
        self.opt_manager = OptionsHandler(CONFIG_PATH)

        # init log manager
        if self.opt_manager.options['enable_log']:
            self.log_manager = LogManager(
                CONFIG_PATH,
                self.opt_manager.options['log_time']
            )

    def init_gui(self):
        self.panel = wx.Panel(self)

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        # Url label
        URLTextBox = wx.BoxSizer(wx.HORIZONTAL)
        URLTextBox.Add(wx.StaticText(self.panel, label='URLs'), flag=wx.TOP, border=10)
        MainBoxSizer.Add(URLTextBox, flag=wx.LEFT, border=20)

        # Urls list
        URLBox = wx.BoxSizer(wx.HORIZONTAL)
        self.url_list = wx.TextCtrl(self.panel, size=(-1, 120), style=wx.TE_MULTILINE | wx.TE_DONTWRAP)
        URLBox.Add(self.url_list, 1)
        MainBoxSizer.Add(URLBox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        # Buttons
        ButtonsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.download_button = wx.Button(self.panel, label='Download', size=(90, 30))
        ButtonsBox.Add(self.download_button)
        self.update_button = wx.Button(self.panel, label='Update', size=(90, 30))
        ButtonsBox.Add(self.update_button, flag=wx.LEFT | wx.RIGHT, border=80)
        self.options_button = wx.Button(self.panel, label='Options', size=(90, 30))
        ButtonsBox.Add(self.options_button)
        MainBoxSizer.Add(ButtonsBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM | wx.TOP, border=10)

        # Status list
        StatusListBox = wx.BoxSizer(wx.HORIZONTAL)
        self.status_list = ListCtrl(self.panel, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        StatusListBox.Add(self.status_list, 1, flag=wx.EXPAND)
        MainBoxSizer.Add(StatusListBox, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        # Status bar
        StatusBarBox = wx.BoxSizer(wx.HORIZONTAL)
        self.status_bar = wx.StaticText(self.panel, label='Author: ' + __author__)
        StatusBarBox.Add(self.status_bar, flag=wx.TOP | wx.BOTTOM, border=5)
        MainBoxSizer.Add(StatusBarBox, flag=wx.LEFT, border=20)

        self.panel.SetSizer(MainBoxSizer)

        # bind events
        self.Bind(wx.EVT_BUTTON, self.OnDownload, self.download_button)
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.update_button)
        self.Bind(wx.EVT_BUTTON, self.OnOptions, self.options_button)
        self.Bind(wx.EVT_TEXT, self.OnTrackListChange, self.url_list)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def youtubedl_exist(self):
        path = fix_path(self.opt_manager.options['youtubedl_path'])
        path += get_youtubedl_filename()

        if file_exist(path):
            return True
        return False

    def update_youtubedl(self):
        self.update_button.Disable()
        self.download_button.Disable()
        self.update_thread = UpdateThread(self.opt_manager.options['youtubedl_path'])

    def status_bar_write(self, msg):
        self.status_bar.SetLabel(msg)

    def reset(self):
        ''' Reset GUI and variables '''
        self.download_button.SetLabel('Download')
        self.successful_downloads = 0
        self.update_button.Enable()
        self.download_thread.join()
        self.download_thread = None
        self.ori_url_list = []
        self.timer = 0

    def fin_tasks(self):
        if self.opt_manager.options['shutdown']:
            self.save_options()
            shutdown_sys(self.opt_manager.options['sudo_password'])
        else:
            self.finished_popup()
            self.open_destination_dir()

    def open_destination_dir(self):
        if self.opt_manager.options['open_dl_dir']:
            open_dir(self.opt_manager.options['save_path'])

    def fin_message(self):
        if self.successful_downloads == 0:
            self.status_bar_write('Done')
            return

        current_time = time()
        dtime = get_time(current_time - self.timer)

        msg = 'Downloaded %s url(s) in ' % self.successful_downloads

        days = int(dtime['days'])
        hours = int(dtime['hours'])
        minutes = int(dtime['minutes'])
        seconds = int(dtime['seconds'])

        if days != 0:
            msg += '%s days, ' % days
        if hours != 0:
            msg += '%s hours, ' % hours
        if minutes != 0:
            msg += '%s minutes, ' % minutes
        msg += '%s seconds ' % seconds

        self.status_bar_write(msg)

    def download_handler(self, msg):
        topic = msg.topic[0]
        data = msg.data

        # Report downloading videos number
        videos_no = self.download_thread.get_items_counter()
        self.status_bar_write('Downloading %s url(s)' % videos_no)

        if topic == 'download_thread':
            self.status_list.write(data)
            if data['status'] == 'Finished' or data['status'] == 'Already-Downloaded':
                self.successful_downloads += 1

        if topic == 'download_manager':
            if data == 'closing':
                self.status_bar_write('Stopping downloads')
            if data == 'closed':
                self.status_bar_write('Downloads stopped')
                self.reset()
            if data == 'finished':
                self.fin_message()
                self.reset()
                self.fin_tasks()

    def update_handler(self, msg):
        if msg.data == 'finish':
            self.update_thread.join()
            self.update_thread = None
            self.update_button.Enable()
            self.download_button.Enable()
        else:
            self.status_bar_write(msg.data)

    def stop_download(self):
        self.download_thread.close()

    def load_on_list(self, url):
        url = url.replace(' ', '')

        if url not in self.ori_url_list and url != '':
            self.ori_url_list.append(url)
            self.status_list.add_item(url)
            return True

        return False

    def start_download(self):
        self.status_list.clear_list()

        for url in self.url_list.GetValue().split('\n'):
            self.load_on_list(url)

        if not self.status_list.is_empty():
            self.download_thread = DownloadManager(
                self.status_list.get_items(),
                self.opt_manager,
                self.log_manager
            )

            self.timer = time()
            self.status_bar_write('Download started')
            self.download_button.SetLabel('Stop')
            self.update_button.Disable()
        else:
            self.no_url_popup()

    def save_options(self):
        self.opt_manager.save_to_file()

    def finished_popup(self):
        wx.MessageBox('Downloads completed.', 'Info', wx.OK | wx.ICON_INFORMATION)

    def no_url_popup(self):
        wx.MessageBox('You need to provide at least one url.', 'Error', wx.OK | wx.ICON_EXCLAMATION)

    def download_ydl_popup(self):
        dial = wx.MessageDialog(self,
                                'Youtube-dl is missing.\nWould you like to download it?',
                                'Error',
                                wx.YES_NO | wx.ICON_ERROR)
        return (dial.ShowModal() == wx.ID_YES)

    def OnTrackListChange(self, event):
        ''' Dynamicaly add urls for download '''
        if self.download_thread is not None:

            for url in self.url_list.GetValue().split('\n'):
                if self.load_on_list(url):
                    item = self.status_list.get_last_item()
                    self.download_thread.add_download_item(item)

    def OnDownload(self, event):
        if self.download_thread is None:
            if self.youtubedl_exist():
                self.start_download()
            elif self.download_ydl_popup():
                self.update_youtubedl()
        else:
            self.stop_download()

    def OnUpdate(self, event):
        if self.download_thread is None and self.update_thread is None:
            self.update_youtubedl()

    def OnOptions(self, event):
        opts_frame = OptionsFrame(self.opt_manager, parent=self, logger=self.log_manager)
        opts_frame.Show()

    def OnClose(self, event):
        if self.download_thread is not None:
            self.download_thread.close(kill=True)
            self.download_thread.join()
        self.save_options()
        self.Destroy()


class ListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):

    ''' Custom ListCtrl class '''

    # Hold column for each data
    DATA_COLUMNS = {
        'filename': 0,
        'filesize': 1,
        'percent': 2,
        'status': 5,
        'speed': 4,
        'eta': 3
    }

    def __init__(self, parent=None, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style)
        ListCtrlAutoWidthMixin.__init__(self)
        self.InsertColumn(0, 'Video', width=150)
        self.InsertColumn(1, 'Size', width=80)
        self.InsertColumn(2, 'Percent', width=65)
        self.InsertColumn(3, 'ETA', width=45)
        self.InsertColumn(4, 'Speed', width=90)
        self.InsertColumn(5, 'Status', width=160)
        self.setResizeColumn(0)
        self.list_index = 0

    def write(self, data):
        ''' Write data on ListCtrl '''
        index = data['index']

        for key in data:
            if key in self.DATA_COLUMNS:
                self._write_data(data[key], index, self.DATA_COLUMNS[key])

    def add_item(self, item):
        ''' Add single item on ListCtrl '''
        self.InsertStringItem(self.list_index, item)
        self.list_index += 1

    def clear_list(self):
        self.DeleteAllItems()
        self.list_index = 0

    def is_empty(self):
        return (self.list_index == 0)

    def get_items(self, start_index=0):
        ''' Return list of items starting from start_index '''
        items = []
        for row in range(start_index, self.list_index):
            item = self._get_item(row)
            items.append(item)
        return items

    def get_last_item(self):
        ''' Return last item of ListCtrl '''
        return self._get_item(self.list_index - 1)

    def _write_data(self, data, row, column):
        ''' Write data on row, column '''
        if isinstance(data, basestring):
            self.SetStringItem(row, column, data)

    def _get_item(self, index):
        ''' Return single item from index '''
        data = {}
        item = self.GetItem(itemId=index, col=0)
        data['url'] = item.GetText()
        data['index'] = index
        return data


class LogPanel(wx.Panel):

    win_border = 0

    def __init__(self, parent, opt_manager, logger):
        wx.Panel.__init__(self, parent)

        self.set_win_border()

        self.opt_manager = opt_manager
        self.logger = logger

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        EnableLogBox = wx.BoxSizer(wx.HORIZONTAL)
        self.enable_log_checkbox = wx.CheckBox(self, label='Enable Log')
        EnableLogBox.Add(self.enable_log_checkbox)
        MainBoxSizer.Add(EnableLogBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20 + self.win_border)

        LogTimeBox = wx.BoxSizer(wx.HORIZONTAL)
        self.log_time_checkbox = wx.CheckBox(self, label='Write Time')
        LogTimeBox.Add(self.log_time_checkbox)
        MainBoxSizer.Add(LogTimeBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5 + self.win_border)

        ButtonsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.clear_log_button = wx.Button(self, label='Clear Log')
        ButtonsBox.Add(self.clear_log_button)
        self.view_log_button = wx.Button(self, label='View Log')
        ButtonsBox.Add(self.view_log_button, flag=wx.LEFT, border=20)
        MainBoxSizer.Add(ButtonsBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        if self.opt_manager.options['enable_log']:
            LogPathBox = wx.BoxSizer(wx.HORIZONTAL)
            LogPathBox.Add(wx.StaticText(self, label='Path: ' + self.get_path()))
            MainBoxSizer.Add(LogPathBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

            LogSizeBox = wx.BoxSizer(wx.HORIZONTAL)
            self.size_text = wx.StaticText(self, label='Log Size: ' + self.get_size())
            LogSizeBox.Add(self.size_text)
            MainBoxSizer.Add(LogSizeBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)

        self.SetSizer(MainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnEnable, self.enable_log_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnTime, self.log_time_checkbox)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clear_log_button)
        self.Bind(wx.EVT_BUTTON, self.OnView, self.view_log_button)

    def set_win_border(self):
        if os_type == 'nt':
            self.win_border = 10

    def get_path(self):
        ''' Return log file abs path '''
        return self.logger.log_file

    def get_size(self):
        ''' Return log file size in Bytes '''
        return str(self.logger.size()) + ' Byte(s)'

    def restart_popup(self):
        wx.MessageBox('Please restart ' + __appname__, 'Restart', wx.OK | wx.ICON_INFORMATION)

    def OnTime(self, event):
        if self.logger is not None:
            self.logger.add_time = self.log_time_checkbox.GetValue()

    def OnEnable(self, event):
        self.restart_popup()

    def OnClear(self, event):
        if self.logger is not None:
            self.logger.clear()
            self.size_text.SetLabel('Log Size: ' + self.get_size())

    def OnView(self, event):
        if self.logger is not None:
            logger_gui = LogGUI(self.get_path(), parent=self)
            logger_gui.Show()

    def load_options(self):
        self.enable_log_checkbox.SetValue(self.opt_manager.options['enable_log'])
        self.log_time_checkbox.SetValue(self.opt_manager.options['log_time'])
        if self.logger is None:
            self.log_time_checkbox.Disable()
            self.clear_log_button.Disable()
            self.view_log_button.Disable()

    def save_options(self):
        self.opt_manager.options['enable_log'] = self.enable_log_checkbox.GetValue()
        self.opt_manager.options['log_time'] = self.log_time_checkbox.GetValue()


class ShutdownPanel(wx.Panel):

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        ShutdownBox = wx.BoxSizer(wx.HORIZONTAL)
        self.shutdown_checkbox = wx.CheckBox(self, label='Shutdown when finished')
        ShutdownBox.Add(self.shutdown_checkbox)
        MainBoxSizer.Add(ShutdownBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=30)

        SUDOTextBox = wx.BoxSizer(wx.HORIZONTAL)
        SUDOTextBox.Add(wx.StaticText(self, label='SUDO password'))
        MainBoxSizer.Add(SUDOTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        SUDOBox = wx.BoxSizer(wx.HORIZONTAL)
        self.sudo_pass_box = wx.TextCtrl(self, size=(-1, 25), style=wx.TE_PASSWORD)
        SUDOBox.Add(self.sudo_pass_box, 1, flag=wx.TOP, border=5)
        MainBoxSizer.Add(SUDOBox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=160)

        self.SetSizer(MainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnShutdownCheck, self.shutdown_checkbox)

    def OnShutdownCheck(self, event):
        if os_type != 'nt':
            if self.shutdown_checkbox.GetValue():
                self.sudo_pass_box.Enable()
            else:
                self.sudo_pass_box.Disable()

    def load_options(self):
        self.shutdown_checkbox.SetValue(self.opt_manager.options['shutdown'])
        self.sudo_pass_box.SetValue(self.opt_manager.options['sudo_password'])
        if os_type == 'nt' or not self.opt_manager.options['shutdown']:
            self.sudo_pass_box.Disable()

    def save_options(self):
        self.opt_manager.options['shutdown'] = self.shutdown_checkbox.GetValue()
        self.opt_manager.options['sudo_password'] = self.sudo_pass_box.GetValue()


class PlaylistPanel(wx.Panel):

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.opt_manager = opt_manager

        MainBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self, label='Playlist Options'), wx.VERTICAL)

        MainBoxSizer.Add((-1, 5))

        StartTextBox = wx.BoxSizer(wx.HORIZONTAL)
        StartTextBox.Add(wx.StaticText(self, label='Playlist Start'))
        MainBoxSizer.Add(StartTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        StartBox = wx.BoxSizer(wx.HORIZONTAL)
        self.start_spinner = wx.SpinCtrl(self, size=(70, 20))
        self.start_spinner.SetRange(1, 999)
        StartBox.Add(self.start_spinner)
        MainBoxSizer.Add(StartBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        StopTextBox = wx.BoxSizer(wx.HORIZONTAL)
        StopTextBox.Add(wx.StaticText(self, label='Playlist Stop'))
        MainBoxSizer.Add(StopTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        StopBox = wx.BoxSizer(wx.HORIZONTAL)
        self.stop_spinner = wx.SpinCtrl(self, size=(70, 20))
        self.stop_spinner.SetRange(0, 999)
        StopBox.Add(self.stop_spinner)
        MainBoxSizer.Add(StopBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        MaxTextBox = wx.BoxSizer(wx.HORIZONTAL)
        MaxTextBox.Add(wx.StaticText(self, label='Max Downloads'))
        MainBoxSizer.Add(MaxTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        MaxBox = wx.BoxSizer(wx.HORIZONTAL)
        self.max_spinner = wx.SpinCtrl(self, size=(70, 20))
        self.max_spinner.SetRange(0, 999)
        MaxBox.Add(self.max_spinner)
        MainBoxSizer.Add(MaxBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        self.SetSizer(MainBoxSizer)

    def load_options(self):
        self.start_spinner.SetValue(self.opt_manager.options['playlist_start'])
        self.stop_spinner.SetValue(self.opt_manager.options['playlist_end'])
        self.max_spinner.SetValue(self.opt_manager.options['max_downloads'])

    def save_options(self):
        self.opt_manager.options['playlist_start'] = self.start_spinner.GetValue()
        self.opt_manager.options['playlist_end'] = self.stop_spinner.GetValue()
        self.opt_manager.options['max_downloads'] = self.max_spinner.GetValue()


class ConnectionPanel(wx.Panel):

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        RetriesBox = wx.BoxSizer(wx.HORIZONTAL)
        RetriesBox.Add(wx.StaticText(self, label='Retries'), flag=wx.RIGHT, border=8)
        self.retries_spinner = wx.SpinCtrl(self, size=(50, -1))
        self.retries_spinner.SetRange(1, 99)
        RetriesBox.Add(self.retries_spinner)
        MainBoxSizer.Add(RetriesBox, flag=wx.LEFT | wx.TOP, border=10)

        UserAgentTextBox = wx.BoxSizer(wx.HORIZONTAL)
        UserAgentTextBox.Add(wx.StaticText(self, label='User Agent'), flag=wx.LEFT, border=15)
        MainBoxSizer.Add(UserAgentTextBox, flag=wx.TOP, border=10)

        MainBoxSizer.Add((-1, 5))

        UserAgentBox = wx.BoxSizer(wx.HORIZONTAL)
        self.user_agent_box = wx.TextCtrl(self)
        UserAgentBox.Add(self.user_agent_box, 1, flag=wx.LEFT, border=10)
        MainBoxSizer.Add(UserAgentBox, flag=wx.EXPAND | wx.RIGHT, border=200)

        RefererTextBox = wx.BoxSizer(wx.HORIZONTAL)
        RefererTextBox.Add(wx.StaticText(self, label='Referer'), flag=wx.LEFT, border=15)
        MainBoxSizer.Add(RefererTextBox, flag=wx.TOP, border=10)

        MainBoxSizer.Add((-1, 5))

        RefererBox = wx.BoxSizer(wx.HORIZONTAL)
        self.referer_box = wx.TextCtrl(self)
        RefererBox.Add(self.referer_box, 1, flag=wx.LEFT, border=10)
        MainBoxSizer.Add(RefererBox, flag=wx.EXPAND | wx.RIGHT, border=200)

        ProxyTextBox = wx.BoxSizer(wx.HORIZONTAL)
        ProxyTextBox.Add(wx.StaticText(self, label='Proxy'), flag=wx.LEFT, border=15)
        MainBoxSizer.Add(ProxyTextBox, flag=wx.TOP, border=10)

        MainBoxSizer.Add((-1, 5))

        ProxyBox = wx.BoxSizer(wx.HORIZONTAL)
        self.proxy_box = wx.TextCtrl(self)
        ProxyBox.Add(self.proxy_box, 1, flag=wx.LEFT, border=10)
        MainBoxSizer.Add(ProxyBox, flag=wx.EXPAND | wx.RIGHT, border=100)

        self.SetSizer(MainBoxSizer)

    def load_options(self):
        self.proxy_box.SetValue(self.opt_manager.options['proxy'])
        self.referer_box.SetValue(self.opt_manager.options['referer'])
        self.retries_spinner.SetValue(self.opt_manager.options['retries'])
        self.user_agent_box.SetValue(self.opt_manager.options['user_agent'])

    def save_options(self):
        self.opt_manager.options['proxy'] = self.proxy_box.GetValue()
        self.opt_manager.options['referer'] = self.referer_box.GetValue()
        self.opt_manager.options['retries'] = self.retries_spinner.GetValue()
        self.opt_manager.options['user_agent'] = self.user_agent_box.GetValue()


class AuthenticationPanel(wx.Panel):

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        UsernameTextBox = wx.BoxSizer(wx.HORIZONTAL)
        UsernameTextBox.Add(wx.StaticText(self, label='Username'))
        MainBoxSizer.Add(UsernameTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        UsernameBox = wx.BoxSizer(wx.HORIZONTAL)
        self.username_box = wx.TextCtrl(self, size=(-1, 25))
        UsernameBox.Add(self.username_box, 1, flag=wx.TOP, border=5)
        MainBoxSizer.Add(UsernameBox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=160)

        PassTextBox = wx.BoxSizer(wx.HORIZONTAL)
        PassTextBox.Add(wx.StaticText(self, label='Password'))
        MainBoxSizer.Add(PassTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        PassBox = wx.BoxSizer(wx.HORIZONTAL)
        self.password_box = wx.TextCtrl(self, size=(-1, 25), style=wx.TE_PASSWORD)
        PassBox.Add(self.password_box, 1, flag=wx.TOP, border=5)
        MainBoxSizer.Add(PassBox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=160)

        VideoPassTextBox = wx.BoxSizer(wx.HORIZONTAL)
        VideoPassTextBox.Add(wx.StaticText(self, label='Video Password (vimeo, smotri)'))
        MainBoxSizer.Add(VideoPassTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        VideoPassBox = wx.BoxSizer(wx.HORIZONTAL)
        self.video_pass_box = wx.TextCtrl(self, size=(-1, 25), style=wx.TE_PASSWORD)
        VideoPassBox.Add(self.video_pass_box, 1, flag=wx.TOP, border=5)
        MainBoxSizer.Add(VideoPassBox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=160)

        self.SetSizer(MainBoxSizer)

    def load_options(self):
        self.username_box.SetValue(self.opt_manager.options['username'])
        self.password_box.SetValue(self.opt_manager.options['password'])
        self.video_pass_box.SetValue(self.opt_manager.options['video_password'])

    def save_options(self):
        self.opt_manager.options['username'] = self.username_box.GetValue()
        self.opt_manager.options['password'] = self.password_box.GetValue()
        self.opt_manager.options['video_password'] = self.video_pass_box.GetValue()


class AudioPanel(wx.Panel):

    win_border = 0
    AUDIO_QUALITY = ['high', 'mid', 'low']

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.set_win_border()

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        ToAudioBox = wx.BoxSizer(wx.HORIZONTAL)
        self.to_audio_checkbox = wx.CheckBox(self, label='Convert to Audio')
        ToAudioBox.Add(self.to_audio_checkbox)
        MainBoxSizer.Add(ToAudioBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15 + self.win_border)

        KeepVideoBox = wx.BoxSizer(wx.HORIZONTAL)
        self.keep_video_checkbox = wx.CheckBox(self, label='Keep Video')
        KeepVideoBox.Add(self.keep_video_checkbox)
        MainBoxSizer.Add(KeepVideoBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5 + self.win_border)

        AudioFormatTextBox = wx.BoxSizer(wx.HORIZONTAL)
        AudioFormatTextBox.Add(wx.StaticText(self, label='Audio Format'))
        MainBoxSizer.Add(AudioFormatTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)

        AudioFormatBox = wx.BoxSizer(wx.HORIZONTAL)
        self.audio_format_combo = wx.ComboBox(self, choices=AUDIO_FORMATS, size=(160, 30))
        AudioFormatBox.Add(self.audio_format_combo)
        MainBoxSizer.Add(AudioFormatBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        AudioQualityTextBox = wx.BoxSizer(wx.HORIZONTAL)
        AudioQualityTextBox.Add(wx.StaticText(self, label='Audio Quality'))
        MainBoxSizer.Add(AudioQualityTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)

        AudioQualityBox = wx.BoxSizer(wx.HORIZONTAL)
        self.audio_quality_combo = wx.ComboBox(self, choices=self.AUDIO_QUALITY, size=(80, 25))
        AudioQualityBox.Add(self.audio_quality_combo)
        MainBoxSizer.Add(AudioQualityBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        self.SetSizer(MainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnAudioCheck, self.to_audio_checkbox)

    def set_win_border(self):
        if os_type == 'nt':
            self.win_border = 5

    def OnAudioCheck(self, event):
        if self.to_audio_checkbox.GetValue():
            self.keep_video_checkbox.Enable()
            self.audio_format_combo.Enable()
            self.audio_quality_combo.Enable()
        else:
            self.keep_video_checkbox.Disable()
            self.audio_format_combo.Disable()
            self.audio_quality_combo.Disable()

    def load_options(self):
        self.to_audio_checkbox.SetValue(self.opt_manager.options['to_audio'])
        self.keep_video_checkbox.SetValue(self.opt_manager.options['keep_video'])
        self.audio_format_combo.SetValue(self.opt_manager.options['audio_format'])
        self.audio_quality_combo.SetValue(self.opt_manager.options['audio_quality'])
        self.OnAudioCheck(None)

    def save_options(self):
        self.opt_manager.options['to_audio'] = self.to_audio_checkbox.GetValue()
        self.opt_manager.options['keep_video'] = self.keep_video_checkbox.GetValue()
        self.opt_manager.options['audio_format'] = self.audio_format_combo.GetValue()
        self.opt_manager.options['audio_quality'] = self.audio_quality_combo.GetValue()


class VideoPanel(wx.Panel):

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        VideoFormatTextBox = wx.BoxSizer(wx.HORIZONTAL)
        VideoFormatTextBox.Add(wx.StaticText(self, label='Video Format'))
        MainBoxSizer.Add(VideoFormatTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        VideoFormatBox = wx.BoxSizer(wx.HORIZONTAL)
        self.video_format_combo = wx.ComboBox(self, choices=VIDEO_FORMATS, size=(160, 30))
        VideoFormatBox.Add(self.video_format_combo)
        MainBoxSizer.Add(VideoFormatBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        DASHAudioTextBox = wx.BoxSizer(wx.HORIZONTAL)
        DASHAudioTextBox.Add(wx.StaticText(self, label='DASH Audio'))
        MainBoxSizer.Add(DASHAudioTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)

        DASHAudioBox = wx.BoxSizer(wx.HORIZONTAL)
        self.dash_audio_combo = wx.ComboBox(self, choices=DASH_AUDIO_FORMATS, size=(160, 30))
        DASHAudioBox.Add(self.dash_audio_combo)
        MainBoxSizer.Add(DASHAudioBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        ClearDASHBox = wx.BoxSizer(wx.HORIZONTAL)
        self.clear_dash_checkbox = wx.CheckBox(self, label='Clear DASH audio/video files')
        ClearDASHBox.Add(self.clear_dash_checkbox)
        MainBoxSizer.Add(ClearDASHBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        self.SetSizer(MainBoxSizer)

        self.Bind(wx.EVT_COMBOBOX, self.OnVideoFormatPick, self.video_format_combo)
        self.Bind(wx.EVT_COMBOBOX, self.OnAudioFormatPick, self.dash_audio_combo)

    def OnAudioFormatPick(self, event):
        if audio_is_dash(self.dash_audio_combo.GetValue()):
            self.clear_dash_checkbox.Enable()
        else:
            self.clear_dash_checkbox.SetValue(False)
            self.clear_dash_checkbox.Disable()

    def OnVideoFormatPick(self, event):
        if video_is_dash(self.video_format_combo.GetValue()):
            self.dash_audio_combo.Enable()
            if audio_is_dash(self.dash_audio_combo.GetValue()):
                self.clear_dash_checkbox.Enable()
        else:
            self.clear_dash_checkbox.SetValue(False)
            self.clear_dash_checkbox.Disable()
            self.dash_audio_combo.Disable()

    def load_options(self):
        self.video_format_combo.SetValue(self.opt_manager.options['video_format'])
        self.dash_audio_combo.SetValue(self.opt_manager.options['dash_audio_format'])
        self.clear_dash_checkbox.SetValue(self.opt_manager.options['clear_dash_files'])
        self.OnVideoFormatPick(None)
        self.OnAudioFormatPick(None)

    def save_options(self):
        self.opt_manager.options['video_format'] = self.video_format_combo.GetValue()
        self.opt_manager.options['dash_audio_format'] = self.dash_audio_combo.GetValue()
        self.opt_manager.options['clear_dash_files'] = self.clear_dash_checkbox.GetValue()


class OutputPanel(wx.Panel):

    win_border = 0

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.set_win_border()

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        RestrictFilenameBox = wx.BoxSizer(wx.HORIZONTAL)
        self.restrict_filenames_checkbox = wx.CheckBox(self, label='Restrict filenames (ASCII)')
        RestrictFilenameBox.Add(self.restrict_filenames_checkbox, flag=wx.LEFT, border=5)
        MainBoxSizer.Add(RestrictFilenameBox, flag=wx.TOP, border=15)

        IDAsNameBox = wx.BoxSizer(wx.HORIZONTAL)
        self.id_as_name_checkbox = wx.CheckBox(self, label='ID as Name')
        IDAsNameBox.Add(self.id_as_name_checkbox, flag=wx.LEFT, border=5)
        MainBoxSizer.Add(IDAsNameBox, flag=wx.TOP, border=5 + self.win_border)

        TitleBox = wx.BoxSizer(wx.HORIZONTAL)
        self.title_checkbox = wx.CheckBox(self, label='Title as Name')
        TitleBox.Add(self.title_checkbox, flag=wx.LEFT, border=5)
        MainBoxSizer.Add(TitleBox, flag=wx.TOP, border=5 + self.win_border)

        CustomTitleBox = wx.BoxSizer(wx.HORIZONTAL)
        self.custom_title_checkbox = wx.CheckBox(self, label='Custom Template (youtube-dl)')
        CustomTitleBox.Add(self.custom_title_checkbox, flag=wx.LEFT, border=5)
        MainBoxSizer.Add(CustomTitleBox, flag=wx.TOP, border=5 + self.win_border)

        MainBoxSizer.Add((-1, 10))

        CustomTemplateBox = wx.BoxSizer(wx.HORIZONTAL)
        self.title_template_box = wx.TextCtrl(self)
        CustomTemplateBox.Add(self.title_template_box, 1, flag=wx.RIGHT, border=300)
        MainBoxSizer.Add(CustomTemplateBox, flag=wx.EXPAND | wx.LEFT, border=5)

        self.SetSizer(MainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnId, self.id_as_name_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnTitle, self.title_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCustom, self.custom_title_checkbox)

    def set_win_border(self):
        if os_type == 'nt':
            self.win_border = 10

    def group_load(self, output_format):
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

    def get_output_format(self):
        if self.id_as_name_checkbox.GetValue():
            return 'id'
        elif self.title_checkbox.GetValue():
            return 'title'
        elif self.custom_title_checkbox.GetValue():
            return 'custom'

    def OnId(self, event):
        self.group_load('id')

    def OnTitle(self, event):
        self.group_load('title')

    def OnCustom(self, event):
        self.group_load('custom')

    def load_options(self):
        self.group_load(self.opt_manager.options['output_format'])
        self.title_template_box.SetValue(self.opt_manager.options['output_template'])
        self.restrict_filenames_checkbox.SetValue(self.opt_manager.options['restrict_filenames'])

    def save_options(self):
        self.opt_manager.options['output_format'] = self.get_output_format()
        self.opt_manager.options['output_template'] = self.title_template_box.GetValue()
        self.opt_manager.options['restrict_filenames'] = self.restrict_filenames_checkbox.GetValue()


class FilesystemPanel(wx.Panel):

    win_border = 0

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.set_win_border()

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        LeftBoxSizer = wx.BoxSizer(wx.VERTICAL)
        RightBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self, label='Filesize (e.g. 50k or 44.6m)'), wx.VERTICAL)

        self.set_left_box(LeftBoxSizer)
        self.set_right_box(RightBoxSizer)

        MainBoxSizer.Add(LeftBoxSizer, 1, flag=wx.EXPAND | wx.ALL, border=10)
        MainBoxSizer.Add(RightBoxSizer, 1, flag=wx.EXPAND | wx.ALL, border=10)

        self.SetSizer(MainBoxSizer)

    def set_win_border(self):
        if os_type == 'nt':
            self.win_border = 10

    def set_left_box(self, box):
        IgnoreErrorsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.ignore_errors_checkbox = wx.CheckBox(self, label='Ignore Errors')
        IgnoreErrorsBox.Add(self.ignore_errors_checkbox, flag=wx.LEFT, border=5)
        box.Add(IgnoreErrorsBox, flag=wx.TOP, border=15)

        OpenDirBox = wx.BoxSizer(wx.HORIZONTAL)
        self.open_dir_checkbox = wx.CheckBox(self, label='Open destination folder when done')
        OpenDirBox.Add(self.open_dir_checkbox, flag=wx.LEFT, border=5)
        box.Add(OpenDirBox, flag=wx.TOP, border=5 + self.win_border)

        WriteDescBox = wx.BoxSizer(wx.HORIZONTAL)
        self.writeDescriptionChk = wx.CheckBox(self, label='Write description to file')
        WriteDescBox.Add(self.writeDescriptionChk, flag=wx.LEFT, border=5)
        box.Add(WriteDescBox, flag=wx.TOP, border=5 + self.win_border)

        WriteInfoBox = wx.BoxSizer(wx.HORIZONTAL)
        self.write_info_checkbox = wx.CheckBox(self, label='Write info to (.json) file')
        WriteInfoBox.Add(self.write_info_checkbox, flag=wx.LEFT, border=5)
        box.Add(WriteInfoBox, flag=wx.TOP, border=5 + self.win_border)

        WriteThumnailBox = wx.BoxSizer(wx.HORIZONTAL)
        self.write_thumbnail_checkbox = wx.CheckBox(self, label='Write thumbnail to disk')
        WriteThumnailBox.Add(self.write_thumbnail_checkbox, flag=wx.LEFT, border=5)
        box.Add(WriteThumnailBox, flag=wx.TOP, border=5 + self.win_border)

    def set_right_box(self, box):
        MinBox = wx.BoxSizer(wx.HORIZONTAL)
        MinBox.Add(wx.StaticText(self, label='Min'), flag=wx.RIGHT, border=12)
        self.min_filesize_box = wx.TextCtrl(self, size=(80, -1))
        MinBox.Add(self.min_filesize_box)
        box.Add(MinBox, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, border=10)

        MaxBox = wx.BoxSizer(wx.HORIZONTAL)
        MaxBox.Add(wx.StaticText(self, label='Max'), flag=wx.RIGHT, border=8)
        self.max_filesize_box = wx.TextCtrl(self, size=(80, -1))
        MaxBox.Add(self.max_filesize_box)
        box.Add(MaxBox, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, border=10)

    def load_options(self):
        self.open_dir_checkbox.SetValue(self.opt_manager.options['open_dl_dir'])
        self.min_filesize_box.SetValue(self.opt_manager.options['min_filesize'])
        self.max_filesize_box.SetValue(self.opt_manager.options['max_filesize'])
        self.write_info_checkbox.SetValue(self.opt_manager.options['write_info'])
        self.ignore_errors_checkbox.SetValue(self.opt_manager.options['ignore_errors'])
        self.writeDescriptionChk.SetValue(self.opt_manager.options['write_description'])
        self.write_thumbnail_checkbox.SetValue(self.opt_manager.options['write_thumbnail'])

    def save_options(self):
        self.opt_manager.options['write_thumbnail'] = self.write_thumbnail_checkbox.GetValue()
        self.opt_manager.options['write_description'] = self.writeDescriptionChk.GetValue()
        self.opt_manager.options['ignore_errors'] = self.ignore_errors_checkbox.GetValue()
        self.opt_manager.options['write_info'] = self.write_info_checkbox.GetValue()
        self.opt_manager.options['open_dl_dir'] = self.open_dir_checkbox.GetValue()
        self.opt_manager.options['min_filesize'] = self.min_filesize_box.GetValue()
        self.opt_manager.options['max_filesize'] = self.max_filesize_box.GetValue()
        self.check_input()

    def check_input(self):
        self.opt_manager.options['min_filesize'].replace('-', '')
        self.opt_manager.options['max_filesize'].replace('-', '')
        if self.opt_manager.options['min_filesize'] == '':
            self.opt_manager.options['min_filesize'] = '0'
        if self.opt_manager.options['max_filesize'] == '':
            self.opt_manager.options['max_filesize'] = '0'


class SubtitlesPanel(wx.Panel):

    win_border = 0

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.set_win_border()

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        DLSubtitlesBox = wx.BoxSizer(wx.HORIZONTAL)
        self.write_subs_checkbox = wx.CheckBox(self, label='Download subtitle file by language')
        DLSubtitlesBox.Add(self.write_subs_checkbox, flag=wx.LEFT, border=10)
        MainBoxSizer.Add(DLSubtitlesBox, flag=wx.TOP, border=15)

        DLAllSubtitlesBox = wx.BoxSizer(wx.HORIZONTAL)
        self.write_all_subs_checkbox = wx.CheckBox(self, label='Download all available subtitles')
        DLAllSubtitlesBox.Add(self.write_all_subs_checkbox, flag=wx.LEFT, border=10)
        MainBoxSizer.Add(DLAllSubtitlesBox, flag=wx.TOP, border=5 + self.win_border)

        DLAutoSubtitlesBox = wx.BoxSizer(wx.HORIZONTAL)
        self.write_auto_subs_checkbox = wx.CheckBox(self, label='Download automatic subtitle file (YOUTUBE ONLY)')
        DLAutoSubtitlesBox.Add(self.write_auto_subs_checkbox, flag=wx.LEFT, border=10)
        MainBoxSizer.Add(DLAutoSubtitlesBox, flag=wx.TOP, border=5 + self.win_border)

        EmbedSubtitlesBox = wx.BoxSizer(wx.HORIZONTAL)
        self.embed_subs_checkbox = wx.CheckBox(self, label='Embed subtitles in the video (only for mp4 videos)')
        self.embed_subs_checkbox.Disable()
        EmbedSubtitlesBox.Add(self.embed_subs_checkbox, flag=wx.LEFT, border=10)
        MainBoxSizer.Add(EmbedSubtitlesBox, flag=wx.TOP, border=5 + self.win_border)

        SubsLanguageTextBox = wx.BoxSizer(wx.HORIZONTAL)
        SubsLanguageTextBox.Add(wx.StaticText(self, label='Subtitles Language'), flag=wx.LEFT, border=15)
        MainBoxSizer.Add(SubsLanguageTextBox, flag=wx.TOP, border=10 + self.win_border)

        SubsLanguageBox = wx.BoxSizer(wx.HORIZONTAL)
        self.subs_languages_combo = wx.ComboBox(self, choices=SUBS_LANG, size=(140, 30))
        self.subs_languages_combo.Disable()
        SubsLanguageBox.Add(self.subs_languages_combo, flag=wx.LEFT, border=10)
        MainBoxSizer.Add(SubsLanguageBox, flag=wx.TOP, border=5)

        self.SetSizer(MainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnWriteSubsChk, self.write_subs_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnWriteAllSubsChk, self.write_all_subs_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnWriteAutoSubsChk, self.write_auto_subs_checkbox)

    def set_win_border(self):
        if os_type == 'nt':
            self.win_border = 5

    def OnWriteAutoSubsChk(self, event):
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
        if self.write_all_subs_checkbox.GetValue():
            self.write_subs_checkbox.Disable()
            self.write_auto_subs_checkbox.Disable()
        else:
            self.write_subs_checkbox.Enable()
            self.write_auto_subs_checkbox.Enable()

    def load_options(self):
        self.write_subs_checkbox.SetValue(self.opt_manager.options['write_subs'])
        self.subs_languages_combo.SetValue(self.opt_manager.options['subs_lang'])
        self.embed_subs_checkbox.SetValue(self.opt_manager.options['embed_subs'])
        self.write_all_subs_checkbox.SetValue(self.opt_manager.options['write_all_subs'])
        self.write_auto_subs_checkbox.SetValue(self.opt_manager.options['write_auto_subs'])
        self.OnWriteSubsChk(None)
        self.OnWriteAllSubsChk(None)
        self.OnWriteAutoSubsChk(None)

    def save_options(self):
        self.opt_manager.options['write_subs'] = self.write_subs_checkbox.GetValue()
        self.opt_manager.options['subs_lang'] = self.subs_languages_combo.GetValue()
        self.opt_manager.options['embed_subs'] = self.embed_subs_checkbox.GetValue()
        self.opt_manager.options['write_all_subs'] = self.write_all_subs_checkbox.GetValue()
        self.opt_manager.options['write_auto_subs'] = self.write_auto_subs_checkbox.GetValue()


class GeneralPanel(wx.Panel):

    def __init__(self, parent, opt_manager, reset_handler):
        wx.Panel.__init__(self, parent)

        self.opt_manager = opt_manager
        self.reset_handler = reset_handler

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        SavePathTextBox = wx.BoxSizer(wx.HORIZONTAL)
        SavePathTextBox.Add(wx.StaticText(self, label='Save Path'))
        MainBoxSizer.Add(SavePathTextBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        SavePathBox = wx.BoxSizer(wx.HORIZONTAL)
        self.savepath_box = wx.TextCtrl(self)
        SavePathBox.Add(self.savepath_box, 1, flag=wx.TOP, border=10)
        MainBoxSizer.Add(SavePathBox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=40)

        ButtonsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.about_button = wx.Button(self, label='About', size=(110, 40))
        ButtonsBox.Add(self.about_button)
        self.open_button = wx.Button(self, label='Open', size=(110, 40))
        ButtonsBox.Add(self.open_button, flag=wx.LEFT | wx.RIGHT, border=50)
        self.reset_button = wx.Button(self, label='Reset Options', size=(110, 40))
        ButtonsBox.Add(self.reset_button)
        MainBoxSizer.Add(ButtonsBox, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        SettingsBox = wx.BoxSizer(wx.HORIZONTAL)
        text = 'Settings: ' + self.opt_manager.settings_file
        SettingsBox.Add(wx.StaticText(self, label=text), flag=wx.TOP, border=30)
        MainBoxSizer.Add(SettingsBox, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(MainBoxSizer)

        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.open_button)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, self.about_button)
        self.Bind(wx.EVT_BUTTON, self.OnReset, self.reset_button)

    def OnReset(self, event):
        self.reset_handler()

    def OnOpen(self, event):
        dlg = wx.DirDialog(None, "Choose directory")
        if dlg.ShowModal() == wx.ID_OK:
            self.savepath_box.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon(ICON, wx.BITMAP_TYPE_ICO))
        info.SetName(__appname__)
        info.SetVersion(__version__)
        info.SetDescription(__descriptionfull__)
        info.SetWebSite(__projecturl__)
        info.SetLicense(__licensefull__)
        info.AddDeveloper(__author__)
        wx.AboutBox(info)

    def load_options(self):
        self.savepath_box.SetValue(self.opt_manager.options['save_path'])

    def save_options(self):
        self.opt_manager.options['save_path'] = fix_path(self.savepath_box.GetValue())


class OtherPanel(wx.Panel):

    def __init__(self, parent, opt_manager):
        wx.Panel.__init__(self, parent)

        self.opt_manager = opt_manager

        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        HelpTextBox = wx.BoxSizer(wx.HORIZONTAL)
        HelpTextBox.Add(wx.StaticText(self, label='Command line arguments (e.g. --help)'), flag=wx.TOP, border=30)
        MainBoxSizer.Add(HelpTextBox, flag=wx.LEFT, border=50)

        CmdInputBox = wx.BoxSizer(wx.HORIZONTAL)
        self.cmd_args_box = wx.TextCtrl(self)
        CmdInputBox.Add(self.cmd_args_box, 1, flag=wx.TOP, border=10)
        MainBoxSizer.Add(CmdInputBox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=50)

        self.SetSizer(MainBoxSizer)

    def load_options(self):
        self.cmd_args_box.SetValue(self.opt_manager.options['cmd_args'])

    def save_options(self):
        self.opt_manager.options['cmd_args'] = self.cmd_args_box.GetValue()


class OptionsFrame(wx.Frame):

    def __init__(self, opt_manager, parent=None, id=-1, logger=None):
        wx.Frame.__init__(self, parent, id, "Options", size=self.get_frame_sizer())

        self.opt_manager = opt_manager

        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)

        # Special Tabs
        self.general_tab = GeneralPanel(notebook, self.opt_manager, self.reset)
        self.log_tab = LogPanel(notebook, self.opt_manager, logger)

        # Notebook, OptManager Tabs
        self.audio_tab = AudioPanel(notebook, self.opt_manager)
        self.video_tab = VideoPanel(notebook, self.opt_manager)
        self.other_tab = OtherPanel(notebook, self.opt_manager)
        self.output_tab = OutputPanel(notebook, self.opt_manager)
        self.playlist_tab = PlaylistPanel(notebook, self.opt_manager)
        self.shutdown_tab = ShutdownPanel(notebook, self.opt_manager)
        self.subtitles_tab = SubtitlesPanel(notebook, self.opt_manager)
        self.auth_tab = AuthenticationPanel(notebook, self.opt_manager)
        self.connection_tab = ConnectionPanel(notebook, self.opt_manager)
        self.filesystem_tab = FilesystemPanel(notebook, self.opt_manager)

        notebook.AddPage(self.general_tab, "General")
        notebook.AddPage(self.video_tab, "Video")
        notebook.AddPage(self.audio_tab, "Audio")
        notebook.AddPage(self.playlist_tab, "Playlist")
        notebook.AddPage(self.output_tab, "Output")
        notebook.AddPage(self.subtitles_tab, "Subtitles")
        notebook.AddPage(self.filesystem_tab, "Filesystem")
        notebook.AddPage(self.shutdown_tab, "Shutdown")
        notebook.AddPage(self.auth_tab, "Authentication")
        notebook.AddPage(self.connection_tab, "Connection")
        notebook.AddPage(self.log_tab, "Log")
        notebook.AddPage(self.other_tab, "Commands")

        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.load_all_options()

    def get_frame_sizer(self):
        if os_type == 'nt':
            return (640, 270)
        else:
            return (640, 250)

    def OnClose(self, event):
        self.save_all_options()
        self.Destroy()

    def reset(self):
        self.opt_manager.load_default()
        self.load_all_options()

    def load_all_options(self):
        self.log_tab.load_options()
        self.auth_tab.load_options()
        self.audio_tab.load_options()
        self.video_tab.load_options()
        self.other_tab.load_options()
        self.output_tab.load_options()
        self.general_tab.load_options()
        self.playlist_tab.load_options()
        self.shutdown_tab.load_options()
        self.subtitles_tab.load_options()
        self.connection_tab.load_options()
        self.filesystem_tab.load_options()

    def save_all_options(self):
        self.log_tab.save_options()
        self.auth_tab.save_options()
        self.audio_tab.save_options()
        self.video_tab.save_options()
        self.other_tab.save_options()
        self.output_tab.save_options()
        self.general_tab.save_options()
        self.playlist_tab.save_options()
        self.shutdown_tab.save_options()
        self.subtitles_tab.save_options()
        self.connection_tab.save_options()
        self.filesystem_tab.save_options()
