#!/usr/bin/env python2

''' Contains code for main app frame & custom ListCtrl. '''

import os.path

import wx
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from .LogManager import LogManager
from .OptionsFrame import OptionsFrame
from .UpdateThread import UpdateThread
from .OptionsManager import OptionsManager
from .DownloadThread import DownloadManager, DownloadThread

from .utils import (
    get_youtubedl_filename,
    get_config_path,
    get_icon_path,
    shutdown_sys,
    get_time,
    open_dir
)
from .data import (
    __author__,
    __appname__
)

CONFIG_PATH = os.path.join(get_config_path(), __appname__.lower())


class MainFrame(wx.Frame):

    ''' Youtube-dlG main frame. '''

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, __appname__, size=(650, 440))

        self.init_gui()

        icon = get_icon_path()
        if icon is not None:
            self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_PNG))

        Publisher.subscribe(self.update_handler, "update")
        Publisher.subscribe(self.download_handler, "dlmanager")
        Publisher.subscribe(self.download_handler, "dlthread")

        self.opt_manager = OptionsManager(CONFIG_PATH)
        self.download_manager = None
        self.update_thread = None
        self.log_manager = None

        if self.opt_manager.options['enable_log']:
            self.log_manager = LogManager(
                CONFIG_PATH,
                self.opt_manager.options['log_time']
            )

    def init_gui(self):
        ''' Initialize youtube-dlG GUI components & sizers. '''
        panel = wx.Panel(self)

        # Create components
        self.url_list = wx.TextCtrl(panel,
                                    size=(-1, 120),
                                    style=wx.TE_MULTILINE | wx.TE_DONTWRAP)

        self.download_button = wx.Button(panel, label='Download', size=(90, 30))
        self.update_button = wx.Button(panel, label='Update', size=(90, 30))
        self.options_button = wx.Button(panel, label='Options', size=(90, 30))

        self.status_list = ListCtrl(panel,
                                    style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.status_bar = wx.StaticText(panel, label='Author: ' + __author__)

        # Set sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.AddSpacer(10)

        # URLs label
        main_sizer.Add(wx.StaticText(panel, label='URLs'), flag=wx.LEFT, border=20)

        # URLs list
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_sizer.Add(self.url_list, 1)
        main_sizer.Add(horizontal_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        main_sizer.AddSpacer(10)

        # Buttons
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_sizer.Add(self.download_button)
        horizontal_sizer.Add(self.update_button, flag=wx.LEFT | wx.RIGHT, border=80)
        horizontal_sizer.Add(self.options_button)
        main_sizer.Add(horizontal_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        main_sizer.AddSpacer(10)

        # Status list
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_sizer.Add(self.status_list, 1, flag=wx.EXPAND)
        main_sizer.Add(horizontal_sizer, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        main_sizer.AddSpacer(5)

        # Status bar
        main_sizer.Add(self.status_bar, flag=wx.LEFT, border=20)

        main_sizer.AddSpacer(5)

        panel.SetSizer(main_sizer)

        # Bind events
        self.Bind(wx.EVT_BUTTON, self.OnDownload, self.download_button)
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.update_button)
        self.Bind(wx.EVT_BUTTON, self.OnOptions, self.options_button)
        self.Bind(wx.EVT_TEXT, self.OnListCtrlEdit, self.url_list)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def youtubedl_exist(self):
        ''' Return True if youtube-dl executable exists. '''
        path = os.path.join(self.opt_manager.options['youtubedl_path'],
                            get_youtubedl_filename())

        return os.path.exists(path)

    def update_youtubedl(self, quiet=False):
        ''' Update youtube-dl executable. '''
        if not quiet:
            self.update_button.Disable()
            self.download_button.Disable()

        self.update_thread = UpdateThread(
            self.opt_manager.options['youtubedl_path'],
            quiet
        )

    def status_bar_write(self, msg):
        ''' Write msg to self.status_bar. '''
        self.status_bar.SetLabel(msg)

    def reset(self):
        ''' Reset GUI and variables after download process. '''
        self.download_button.SetLabel('Download')
        self.update_button.Enable()
        self.download_manager.join()
        self.download_manager = None

    def print_stats(self):
        ''' Print stats to self.status_bar after downloading. '''
        successful_downloads = self.download_manager.successful_downloads
        dtime = get_time(self.download_manager.time)

        msg = 'Successfully downloaded %s url(s) in ' % successful_downloads

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

    def fin_tasks(self):
        ''' Run tasks after download process has finished. '''
        if self.opt_manager.options['shutdown']:
            self.opt_manager.save_to_file()
            shutdown_sys(self.opt_manager.options['sudo_password'])
        else:
            self.create_popup('Downloads completed', 'Info', wx.OK | wx.ICON_INFORMATION)
            if self.opt_manager.options['open_dl_dir']:
                open_dir(self.opt_manager.options['save_path'])

    def download_handler(self, msg):
        ''' Handle messages from DownloadManager & DownloadThread. '''
        topic = msg.topic[0]
        data = msg.data

        if topic == 'dlthread':
            self.status_list.write(data)

            msg = 'Downloading %s url(s)' % self.download_manager.not_finished()
            self.status_bar_write(msg)

        if topic == 'dlmanager':
            if data == 'closing':
                self.status_bar_write('Stopping downloads')
            if data == 'closed':
                self.status_bar_write('Downloads stopped')
                self.reset()
            if data == 'finished':
                self.print_stats()
                self.reset()
                self.fin_tasks()

    def update_handler(self, msg):
        ''' Handle messages from UpdateThread. '''
        if msg.data == 'finish':
            self.download_button.Enable()
            self.update_button.Enable()
            self.update_thread.join()
            self.update_thread = None
        else:
            self.status_bar_write(msg.data)

    def load_on_list(self, url):
        ''' Load url on ListCtrl. Return True if url
        loaded successfully, else return False.
        '''
        url = url.replace(' ', '')

        if url != '' and not self.status_list.has_url(url):
            self.status_list.add_url(url)
            return True

        return False

    def start_download(self):
        ''' Handle pre-download tasks & start download process. '''
        self.status_list.clear()

        if not self.youtubedl_exist():
                self.update_youtubedl(True)
        
        for url in self.url_list.GetValue().split('\n'):
            self.load_on_list(url)

        if self.status_list.is_empty():
            self.create_popup(
                'You need to provide at least one url',
                'Error',
                wx.OK | wx.ICON_EXCLAMATION
            )
        else:
            threads_list = []
            for item in self.status_list.get_items():
                threads_list.append(self.create_thread(item))

            self.download_manager = DownloadManager(threads_list, self.update_thread)

            self.status_bar_write('Download started')
            self.download_button.SetLabel('Stop')
            self.update_button.Disable()

    def create_thread(self, item):
        ''' Return DownloadThread created from item. '''
        return DownloadThread(item['url'],
                              item['index'],
                              self.opt_manager,
                              self.log_manager)

    def create_popup(self, text, title, style):
        ''' Create popup message. '''
        wx.MessageBox(text, title, style)

    def OnListCtrlEdit(self, event):
        ''' Dynamically add url for download.'''
        if self.download_manager is not None:
            for url in self.url_list.GetValue().split('\n'):
                # If url successfully loaded on list
                if self.load_on_list(url):
                    thread = self.create_thread(self.status_list.get_last_item())
                    self.download_manager.add_thread(thread)

    def OnDownload(self, event):
        ''' Event handler method for self.download_button. '''
        if self.download_manager is None:
            self.start_download()
        else:
            self.download_manager.close()

    def OnUpdate(self, event):
        ''' Event handler method for self.update_button. '''
        self.update_youtubedl()

    def OnOptions(self, event):
        ''' Event handler method for self.options_button. '''
        options_frame = OptionsFrame(
            self.opt_manager,
            parent=self,
            logger=self.log_manager
        )
        options_frame.Show()

    def OnClose(self, event):
        ''' Event handler method (wx.EVT_CLOSE). '''
        if self.download_manager is not None:
            self.download_manager.close()
            self.download_manager.join()

        if self.update_thread is not None:
            self.update_thread.join()

        self.opt_manager.save_to_file()
        self.Destroy()


class ListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):

    '''
    Custom ListCtrl class.

    Accessible Methods
        write()
            Params: Python dictionary that contains data to write

            Return: None

        has_url()
            Params: Url to search

            Return: True if url in ListCtrl, else False

        add_url()
            Params: Url to add

            Return: None

        clear()
            Params: None

            Return: None

        is_empty()
            Params: None

            Return: True if ListCtrl is empty, else False

        get_items()
            Params: None

            Return: Python list that contains all ListCtrl items

        get_last_item()
            Params: None

            Return: Last item inserted in ListCtrl
    '''

    # Hold column for each data
    DATA_COLUMNS = {
        'filename': 0,
        'filesize': 1,
        'percent': 2,
        'status': 5,
        'speed': 4,
        'eta': 3
    }

    def __init__(self, parent=None, style=0):
        wx.ListCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style)
        ListCtrlAutoWidthMixin.__init__(self)
        self.InsertColumn(0, 'Video', width=150)
        self.InsertColumn(1, 'Size', width=80)
        self.InsertColumn(2, 'Percent', width=65)
        self.InsertColumn(3, 'ETA', width=45)
        self.InsertColumn(4, 'Speed', width=90)
        self.InsertColumn(5, 'Status', width=160)
        self.setResizeColumn(0)
        self._list_index = 0
        self._url_list = []

    def write(self, data):
        ''' Write data on ListCtrl row-column. '''
        for key in data:
            if key in self.DATA_COLUMNS:
                self._write_data(data[key], data['index'], self.DATA_COLUMNS[key])

    def has_url(self, url):
        ''' Return True if url in ListCtrl, else return False. '''
        return url in self._url_list

    def add_url(self, url):
        ''' Add url on ListCtrl. '''
        self.InsertStringItem(self._list_index, url)
        self._url_list.append(url)
        self._list_index += 1

    def clear(self):
        ''' Clear ListCtrl & reset self._list_index. '''
        self.DeleteAllItems()
        self._list_index = 0
        self._url_list = []

    def is_empty(self):
        ''' Return True if list is empty. '''
        return self._list_index == 0

    def get_items(self):
        ''' Return list of items in ListCtrl. '''
        items = []

        for row in range(self._list_index):
            item = self._get_item(row)
            items.append(item)

        return items

    def get_last_item(self):
        ''' Return last item of ListCtrl '''
        return self._get_item(self._list_index - 1)

    def _write_data(self, data, row, column):
        ''' Write data on row, column. '''
        if isinstance(data, basestring):
            self.SetStringItem(row, column, data)

    def _get_item(self, index):
        ''' Return single item base on index. '''
        data = {}
        item = self.GetItem(itemId=index, col=0)
        data['url'] = item.GetText()
        data['index'] = index
        return data
