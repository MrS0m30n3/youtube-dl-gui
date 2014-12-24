#!/usr/bin/env python2

''' Contains code for main app frame & custom ListCtrl. '''

import os.path

import wx
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from .optionsframe import OptionsFrame
from .updthread import UpdateThread
from .dlthread import DownloadManager

from .utils import (
    YOUTUBEDL_BIN,
    get_config_path,
    get_icon_file,
    shutdown_sys,
    get_time,
    open_dir
)
from .info import (
    __appname__
)


class MainFrame(wx.Frame):

    ''' Youtube-dlG main frame. '''

    FRAME_SIZE = (700, 490)
    TEXTCTRL_SIZE = (-1, -1)
    BUTTONS_SIZE = (90, 30)
    BUTTONS_SPACE = 80
    SIZE_20 = 20
    SIZE_10 = 10
    SIZE_5 = 5
    
    URLS_LABEL = "URLs"
    DOWNLOAD_LABEL = "Download"
    UPDATE_LABEL = "Update"
    OPTIONS_LABEL = "Options"
    ERROR_LABEL = "Error"
    STOP_LABEL = "Stop"
    INFO_LABEL = "Info"
    WELCOME_MSG = "Welcome"
    SUCC_REPORT_MSG = ("Successfully downloaded {0} url(s) in {1} "
                       "day(s) {2} hour(s) {3} minute(s) {4} second(s)")
    DL_COMPLETED_MSG = "Download completed"
    URL_REPORT_MSG = "Downloading {0} url(s)"
    CLOSING_MSG = "Stopping downloads"
    CLOSED_MSG = "Downloads stopped"
    PROVIDE_URL_MSG = "You need to provide at least one url"
    DOWNLOAD_STARTED = "Download started"
    
    VIDEO_LABEL = "Video"
    SIZE_LABEL = "Size"
    PERCENT_LABEL = "Percent"
    ETA_LABEL = "ETA"
    SPEED_LABEL = "Speed"
    STATUS_LABEL = "Status"
    
    STATUSLIST_COLUMNS = (
        ('filename', 0, VIDEO_LABEL, 150, True),
        ('filesize', 1, SIZE_LABEL, 80, False),
        ('percent', 2, PERCENT_LABEL, 65, False),
        ('eta', 3, ETA_LABEL, 45, False),
        ('speed', 4, SPEED_LABEL, 90, False),
        ('status', 5, STATUS_LABEL, 160, False)
    )
    
    def __init__(self, opt_manager, log_manager, parent=None):
        wx.Frame.__init__(self, parent, title=__appname__, size=self.FRAME_SIZE)
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self.download_manager = None
        self.update_thread = None
        self.app_icon = get_icon_file()
        
        if self.app_icon is not None:
            self.app_icon = wx.Icon(self.app_icon, wx.BITMAP_TYPE_PNG)
            self.SetIcon(self.app_icon)
        
        # Create options frame
        self._options_frame = OptionsFrame(self)
        
        # Create components
        self._panel = wx.Panel(self)

        self._url_text = self._create_statictext(self.URLS_LABEL)
        self._url_list = self._create_textctrl(wx.TE_MULTILINE | wx.TE_DONTWRAP, self._on_urllist_edit)

        self._download_btn = self._create_button(self.DOWNLOAD_LABEL, self._on_download)
        self._update_btn = self._create_button(self.UPDATE_LABEL, self._on_update)
        self._options_btn = self._create_button(self.OPTIONS_LABEL, self._on_options)

        self._status_list = ListCtrl(self.STATUSLIST_COLUMNS,
                                     parent=self._panel,
                                     style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
                                     
        self._status_bar = self._create_statictext(self.WELCOME_MSG)

        # Bind extra events
        self.Bind(wx.EVT_CLOSE, self._on_close)
        
        self._set_sizers()

        # Set threads wx.CallAfter handlers using subscribe
        self._set_publisher(self._update_handler, 'update')
        self._set_publisher(self._status_list_handler, 'dlworker')
        self._set_publisher(self._download_manager_handler, 'dlmanager')

    def _set_publisher(self, handler, topic):
        Publisher.subscribe(handler, topic)
        
    def _create_statictext(self, label):
        statictext = wx.StaticText(self._panel, label=label)
        return statictext
        
    def _create_textctrl(self, style=None, event_handler=None):
        if style is None:
            textctrl = wx.TextCtrl(self._panel, size=self.TEXTCTRL_SIZE)
        else:
            textctrl = wx.TextCtrl(self._panel, size=self.TEXTCTRL_SIZE, style=style)
            
        if event_handler is not None:
            textctrl.Bind(wx.EVT_TEXT, event_handler)
            
        return textctrl
        
    def _create_button(self, label, event_handler=None):
        btn = wx.Button(self._panel, label=label, size=self.BUTTONS_SIZE)
        
        if event_handler is not None:
            btn.Bind(wx.EVT_BUTTON, event_handler)
            
        return btn
        
    def _create_popup(self, text, title, style):
        ''' Create popup message. '''
        wx.MessageBox(text, title, style)
        
    def _set_sizers(self):
        hor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        vertical_sizer.AddSpacer(self.SIZE_10)

        vertical_sizer.Add(self._url_text)
        vertical_sizer.Add(self._url_list, 1, wx.EXPAND)
        
        vertical_sizer.AddSpacer(self.SIZE_10)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self._download_btn)
        buttons_sizer.Add(self._update_btn, flag=wx.LEFT | wx.RIGHT, border=self.BUTTONS_SPACE)
        buttons_sizer.Add(self._options_btn)
        vertical_sizer.Add(buttons_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        vertical_sizer.AddSpacer(self.SIZE_10)

        vertical_sizer.Add(self._status_list, 2, wx.EXPAND)
        
        vertical_sizer.AddSpacer(self.SIZE_5)

        vertical_sizer.Add(self._status_bar)

        vertical_sizer.AddSpacer(self.SIZE_5)
        
        hor_sizer.Add(vertical_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, border=self.SIZE_20)

        self._panel.SetSizer(hor_sizer)

    def _update_youtubedl(self):
        ''' Update youtube-dl executable. '''
        self._update_btn.Disable()
        self._download_btn.Disable()
        self.update_thread = UpdateThread(self.opt_manager.options['youtubedl_path'])

    def _status_bar_write(self, msg):
        ''' Write msg to self._status_bar. '''
        self._status_bar.SetLabel(msg)

    def _reset_buttons(self):
        ''' Reset GUI and variables after download process. '''
        self._download_btn.SetLabel(self.DOWNLOAD_LABEL)
        self._download_btn.Enable()
        self._update_btn.Enable()

    def _print_stats(self):
        ''' Print stats to self._status_bar after downloading. '''
        suc_downloads = self.download_manager.successful
        dtime = get_time(self.download_manager.time_it_took)

        msg = self.SUCC_REPORT_MSG.format(suc_downloads,
                                          dtime['days'],
                                          dtime['hours'],
                                          dtime['minutes'],
                                          dtime['seconds'])

        self._status_bar_write(msg)

    def _after_download(self):
        ''' Run tasks after download process has finished. '''
        if self.opt_manager.options['shutdown']:
            self.opt_manager.save_to_file()
            shutdown_sys(self.opt_manager.options['sudo_password'])
        else:
            self._create_popup(self.DL_COMPLETED_MSG, self.INFO_LABEL, wx.OK | wx.ICON_INFORMATION)
            if self.opt_manager.options['open_dl_dir']:
                open_dir(self.opt_manager.options['save_path'])

    def _status_list_handler(self, msg):
        data = msg.data
        
        self._status_list.write(data)
        
        # Report urls been downloaded
        msg = self.URL_REPORT_MSG.format(self.download_manager.active())
        self._status_bar_write(msg)
                
    def _download_manager_handler(self, msg):
        ''' Handle messages from DownloadManager. '''
        data = msg.data

        if data == 'finished':
            self._print_stats()
            self._reset_buttons()
            self.download_manager = None
            self._after_download()
        elif data == 'closed':
            self._status_bar_write(self.CLOSED_MSG)
            self._reset_buttons()
            self.download_manager = None
        else:
            self._status_bar_write(self.CLOSING_MSG)

    def _update_handler(self, msg):
        ''' Handle messages from UpdateThread. '''
        data = msg.data
        
        if data == 'finish':
            self._reset_buttons()
            self.update_thread = None
        else:
            self._status_bar_write(data)

    def _get_urls(self):
        return self._url_list.GetValue().split('\n')
            
    def _start_download(self):
        ''' Handle pre-download tasks & start download process. '''
        self._status_list.clear()
        self._status_list.load_urls(self._get_urls())

        if self._status_list.is_empty():
            self._create_popup(self.PROVIDE_URL_MSG,
                               self.ERROR_LABEL,
                               wx.OK | wx.ICON_EXCLAMATION)
        else:
            self.download_manager = DownloadManager(self._status_list.get_items(),
                                                    self.opt_manager,
                                                    self.log_manager)

            self._status_bar_write(self.DOWNLOAD_STARTED)
            self._download_btn.SetLabel(self.STOP_LABEL)
            self._update_btn.Disable()
                              
    def _on_urllist_edit(self, event):
        ''' Dynamically add url for download.'''
        if self.download_manager is not None:
            self._status_list.load_urls(self._get_urls(), self.download_manager.add_url)
        
    def _on_download(self, event):
        ''' Event handler method for self._download_btn. '''
        if self.download_manager is None:
            self._start_download()
        else:
            self.download_manager.stop_downloads()

    def _on_update(self, event):
        ''' Event handler method for self._update_btn. '''
        self._update_youtubedl()

    def _on_options(self, event):
        ''' Event handler method for self._options_btn. '''
        self._options_frame.load_all_options()
        self._options_frame.Show()

    def _on_close(self, event):
        ''' Event handler method (wx.EVT_CLOSE). '''
        if self.download_manager is not None:
            self.download_manager.stop_downloads()
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

    def __init__(self, columns, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ListCtrlAutoWidthMixin.__init__(self)
        self.columns = columns
        self._list_index = 0
        self._url_list = set()
        self._set_columns()

    def write(self, data):
        ''' Write data on ListCtrl row-column. '''
        for column in self.columns:
            column_key = column[0]
            self._write_data(data[column_key], data['index'], column[1])

    def load_urls(self, url_list, func=None):
        for url in url_list:
            url = url.replace(' ', '')
            
            if url and not self.has_url(url):
                self.add_url(url)
                
                if func is not None:
                    # Custom hack to add url into download_manager
                    # i am gonna change this
                    item = self._get_item(self._list_index - 1)
                    func(item)
                
    def has_url(self, url):
        ''' Return True if url in ListCtrl, else return False. '''
        return url in self._url_list

    def add_url(self, url):
        ''' Add url on ListCtrl. '''
        self.InsertStringItem(self._list_index, url)
        self._url_list.add(url)
        self._list_index += 1

    def clear(self):
        ''' Clear ListCtrl & reset self._list_index. '''
        self.DeleteAllItems()
        self._list_index = 0
        self._url_list = set()

    def is_empty(self):
        ''' Return True if list is empty. '''
        return self._list_index == 0

    def get_items(self):
        ''' Return list of items in ListCtrl. '''
        items = []

        for row in xrange(self._list_index):
            item = self._get_item(row)
            items.append(item)

        return items

    def _write_data(self, data, row, column):
        ''' Write data on row, column. '''
        if isinstance(data, basestring):
            self.SetStringItem(row, column, data)

    def _get_item(self, index):
        ''' Return single item base on index. '''
        item = self.GetItem(itemId=index, col=0)        
        data = dict(url=item.GetText(), index=index)
        return data
        
    def _set_columns(self):
        for column in self.columns:
            self.InsertColumn(column[1], column[2], width=column[3])
            if column[4]:
                self.setResizeColumn(column[1])
        
