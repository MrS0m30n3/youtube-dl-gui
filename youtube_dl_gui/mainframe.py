#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg module responsible for the main app window. """

from __future__ import unicode_literals

import os
import gettext

import wx
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from .optionsframe import OptionsFrame
from .updatemanager import (
    UPDATE_PUB_TOPIC,
    UpdateThread
)
from .downloadmanager import (
    MANAGER_PUB_TOPIC,
    WORKER_PUB_TOPIC,
    DownloadManager
)

from .utils import (
    get_pixmaps_dir,
    get_icon_file,
    shutdown_sys,
    get_time,
    open_dir
)
from .info import (
    __appname__
)


class MainFrame(wx.Frame):

    """Main window class.

    This class is responsible for creating the main app window
    and binding the events.

    Attributes:
        wxEVT_TEXT_PASTE (int): Event type code for the wx.EVT_TEXT_PASTE

        BUTTONS_SIZE (tuple): Buttons size (width, height).
        BUTTONS_SPACE (tuple): Space between buttons (width, height).
        SIZE_20 (int): Constant size number.
        SIZE_10 (int): Constant size number.
        SIZE_5 (int): Constant size number.

        Labels area (strings): Strings for the widgets labels.

        STATUSLIST_COLUMNS (dict): Python dictionary which holds informations
            about the wxListCtrl columns. For more informations read the
            comments above the STATUSLIST_COLUMNS declaration.

    Args:
        opt_manager (optionsmanager.OptionsManager): Object responsible for
            handling the settings.

        log_manager (logmanager.LogManager): Object responsible for handling
            the log stuff.

        parent (wx.Window): Frame parent.

    """
    wxEVT_TEXT_PASTE = 'wxClipboardTextEvent'

    FRAMES_MIN_SIZE = (440, 360)
    BUTTONS_SIZE = (-1, 30)     # TODO remove not used anymore
    BUTTONS_SPACE = (80, -1)    # TODO remove not used anymore
    SIZE_20 = 20                # TODO write directly
    SIZE_10 = 10
    SIZE_5 = 5

    # Labels area
    URLS_LABEL = _("Enter URLs below")
    DOWNLOAD_LABEL = _("Download")  # TODO remove not used anymore
    UPDATE_LABEL = _("Update")
    OPTIONS_LABEL = _("Options")
    ERROR_LABEL = _("Error")
    STOP_LABEL = _("Stop")
    INFO_LABEL = _("Info")
    WELCOME_MSG = _("Welcome")

    ADD_LABEL = _("Add")
    DOWNLOAD_LIST_LABEL = _("Download list")
    DELETE_LABEL = _("Delete")
    PLAY_LABEL = _("Play")
    UP_LABEL = _("Up")
    DOWN_LABEL = _("Down")
    RELOAD_LABEL = _("Reload")
    PAUSE_LABEL = _("Pause")
    START_LABEL = _("Start")

    SUCC_REPORT_MSG = _("Successfully downloaded {0} url(s) in {1} "
                       "day(s) {2} hour(s) {3} minute(s) {4} second(s)")
    DL_COMPLETED_MSG = _("Downloads completed")
    URL_REPORT_MSG = _("Downloading {0} url(s)")
    CLOSING_MSG = _("Stopping downloads")
    CLOSED_MSG = _("Downloads stopped")
    PROVIDE_URL_MSG = _("You need to provide at least one url")
    DOWNLOAD_STARTED = _("Downloads started")

    UPDATING_MSG = _("Downloading latest youtube-dl. Please wait...")
    UPDATE_ERR_MSG = _("Youtube-dl download failed [{0}]")
    UPDATE_SUCC_MSG = _("Youtube-dl downloaded correctly")

    OPEN_DIR_ERR = _("Unable to open directory: '{dir}'. "
                    "The specified path does not exist")
    SHUTDOWN_ERR = _("Error while shutting down. "
                    "Make sure you typed the correct password")
    SHUTDOWN_MSG = _("Shutting down system")

    VIDEO_LABEL = _("Title")
    EXTENSION_LABEL = _("Extension")
    SIZE_LABEL = _("Size")
    PERCENT_LABEL = _("Percent")
    ETA_LABEL = _("ETA")
    SPEED_LABEL = _("Speed")
    STATUS_LABEL = _("Status")
    #################################

    # STATUSLIST_COLUMNS
    #
    # Dictionary which contains the columns for the wxListCtrl widget.
    # Each key represents a column and holds informations about itself.
    # Structure informations:
    #  column_key: (column_number, column_label, minimum_width, is_resizable)
    #
    STATUSLIST_COLUMNS = {
        'filename': (0, VIDEO_LABEL, 150, True),
        'extension': (1, EXTENSION_LABEL, 60, False),
        'filesize': (2, SIZE_LABEL, 80, False),
        'percent': (3, PERCENT_LABEL, 65, False),
        'eta': (4, ETA_LABEL, 45, False),
        'speed': (5, SPEED_LABEL, 90, False),
        'status': (6, STATUS_LABEL, 160, False)
    }

    def __init__(self, opt_manager, log_manager, parent=None):
        wx.Frame.__init__(self, parent, title=__appname__, size=opt_manager.options['main_win_size'])
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self.download_manager = None
        self.update_thread = None

        # Get the pixmaps directory
        self._pixmaps_path = get_pixmaps_dir()

        # Set the app icon
        app_icon_path = get_icon_file()
        if app_icon_path is not None:
            self.SetIcon(wx.Icon(app_icon_path, wx.BITMAP_TYPE_PNG))

        # Create options frame
        self._options_frame = OptionsFrame(self)

        # Set the data for all the wx.Button items
        # name, label, icon, size
        buttons_data = (
            ("delete", self.DELETE_LABEL, "delete_32px.png", (55, 55)),
            ("play", self.PLAY_LABEL, "camera_32px.png", (55, 55)),
            ("up", self.UP_LABEL, "arrow_up_32px.png", (55, 55)),
            ("down", self.DOWN_LABEL, "arrow_down_32px.png", (55, 55)),
            ("reload", self.RELOAD_LABEL, "reload_32px.png", (55, 55)),
            ("pause", self.PAUSE_LABEL, "pause_32px.png", (55, 55)),
            ("start", self.START_LABEL, "cloud_download_32px.png", (55, 55)),
            ("savepath", "...", None, (40, 27)),
            ("add", self.ADD_LABEL, None, (-1, -1))
        )

        # Create frame components
        self._panel = wx.Panel(self)

        self._url_text = self._create_statictext(self.URLS_LABEL)
        self._settings_button = self._create_bitmap_button("settings_20px.png", (30, 30))

        self._url_list = self._create_textctrl(wx.TE_MULTILINE | wx.TE_DONTWRAP, self._on_urllist_edit)

        self._folder_icon = self._create_static_bitmap("folder_32px.png")
        self._path_combobox = wx.ComboBox(self._panel)
        self._videoformat_combobox = wx.ComboBox(self._panel)

        self._download_text = self._create_statictext(self.DOWNLOAD_LIST_LABEL)
        self._status_list = ListCtrl(self.STATUSLIST_COLUMNS,
                                     parent=self._panel,
                                     style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)

        # Dictionary to store all the buttons
        self._buttons = {}

        for item in buttons_data:
            name, label, icon, size = item

            self._buttons[name] = wx.Button(self._panel, label=label, size=size)

            if icon is not None:
                self._buttons[name].SetBitmap(wx.Bitmap(os.path.join(self._pixmaps_path, icon)), wx.TOP)

        self._status_bar = self.CreateStatusBar()

        # Bind extra events
        self.Bind(wx.EVT_CLOSE, self._on_close)

        # Set threads wxCallAfter handlers
        self._set_publisher(self._update_handler, UPDATE_PUB_TOPIC)
        self._set_publisher(self._download_worker_handler, WORKER_PUB_TOPIC)
        self._set_publisher(self._download_manager_handler, MANAGER_PUB_TOPIC)

        # Set up extra stuff
        self.Center()
        self.SetMinSize(self.FRAMES_MIN_SIZE)

        self._set_buttons_width()
        self._status_bar_write(self.WELCOME_MSG)

        self._set_layout()

    def _set_publisher(self, handler, topic):
        """Sets a handler for the given topic.

        Args:
            handler (function): Can be any function with one parameter
                the message that the caller sends.

            topic (string): Can be any string that identifies the caller.
                You can bind multiple handlers on the same topic or
                multiple topics on the same handler.

        """
        Publisher.subscribe(handler, topic)

    def _set_buttons_width(self):
        """Re-adjust buttons size on runtime so that all buttons
        look the same. """
        widths = [
            #self._download_btn.GetSize()[0],
            #self._update_btn.GetSize()[0],
            #self._options_btn.GetSize()[0],
        ]

        max_width = -1

        for item in widths:
            if item > max_width:
                max_width = item

        #self._download_btn.SetMinSize((max_width, self.BUTTONS_SIZE[1]))
        #self._update_btn.SetMinSize((max_width, self.BUTTONS_SIZE[1]))
        #self._options_btn.SetMinSize((max_width, self.BUTTONS_SIZE[1]))

        self._panel.Layout()

    def _create_statictext(self, label):
        return wx.StaticText(self._panel, label=label)

    def _create_bitmap_button(self, icon, size=(-1, -1)):
        bitmap = wx.Bitmap(os.path.join(self._pixmaps_path, icon))
        return wx.BitmapButton(self._panel, bitmap=bitmap, size=size, style=wx.NO_BORDER)

    def _create_static_bitmap(self, icon):
        bitmap = wx.Bitmap(os.path.join(self._pixmaps_path, icon))
        return wx.StaticBitmap(self._panel, bitmap=bitmap)

    def _create_textctrl(self, style=None, event_handler=None):
        if style is None:
            textctrl = wx.TextCtrl(self._panel)
        else:
            textctrl = wx.TextCtrl(self._panel, style=style)

        if event_handler is not None:
            textctrl.Bind(wx.EVT_TEXT_PASTE, event_handler)
            textctrl.Bind(wx.EVT_MIDDLE_DOWN, event_handler)

        if os.name == 'nt':
            # Enable CTRL+A on Windows
            def win_ctrla_eventhandler(event):
                if event.GetKeyCode() == wx.WXK_CONTROL_A:
                    event.GetEventObject().SelectAll()

                event.Skip()

            textctrl.Bind(wx.EVT_CHAR, win_ctrla_eventhandler)

        return textctrl

    def _create_button(self, label, event_handler=None):
        # TODO remove not used anymore
        btn = wx.Button(self._panel, label=label, size=self.BUTTONS_SIZE)

        if event_handler is not None:
            btn.Bind(wx.EVT_BUTTON, event_handler)

        return btn

    def _create_popup(self, text, title, style):
        wx.MessageBox(text, title, style)

    def _set_layout(self):
        """Sets the layout of the main window. """
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self._url_text, 0, wx.ALIGN_BOTTOM | wx.BOTTOM, 5)
        top_sizer.AddSpacer((100, 20), 1)
        top_sizer.Add(self._settings_button, flag=wx.ALIGN_RIGHT)
        panel_sizer.Add(top_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        panel_sizer.Add(self._url_list, 1, wx.EXPAND)

        mid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mid_sizer.Add(self._folder_icon)
        mid_sizer.Add(self._path_combobox, 2, wx.ALIGN_CENTER_VERTICAL)
        mid_sizer.Add(self._buttons["savepath"], flag=wx.ALIGN_CENTER_VERTICAL)
        mid_sizer.AddSpacer((100, 20), 1)
        mid_sizer.Add(self._videoformat_combobox, 1, wx.ALIGN_CENTER_VERTICAL)
        mid_sizer.Add(self._buttons["add"], flag=wx.ALIGN_CENTER_VERTICAL)
        panel_sizer.Add(mid_sizer, 0, wx.EXPAND | wx.ALL, 10)

        panel_sizer.Add(self._download_text, 0, wx.BOTTOM | wx.LEFT, 5)
        panel_sizer.Add(self._status_list, 2, wx.EXPAND)

        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_sizer.Add(self._buttons["delete"])
        bottom_sizer.Add(self._buttons["play"])
        bottom_sizer.Add(self._buttons["up"])
        bottom_sizer.Add(self._buttons["down"])
        bottom_sizer.Add(self._buttons["reload"])
        bottom_sizer.Add(self._buttons["pause"])
        bottom_sizer.AddSpacer((100, 20), 1)
        bottom_sizer.Add(self._buttons["start"])
        panel_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self._panel.SetSizer(panel_sizer)

        main_sizer.Add(self._panel, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(main_sizer)

    def _update_youtubedl(self):
        """Update youtube-dl binary to the latest version. """
        #self._update_btn.Disable()
        #self._download_btn.Disable()
        self.update_thread = UpdateThread(self.opt_manager.options['youtubedl_path'])

    def _status_bar_write(self, msg):
        """Display msg in the status bar. """
        self._status_bar.SetStatusText(msg)

    def _reset_widgets(self):
        """Resets GUI widgets after update or download process. """
        pass
        #self._download_btn.SetLabel(self.DOWNLOAD_LABEL)
        #self._download_btn.Enable()
        #self._update_btn.Enable()

    def _print_stats(self):
        """Display download stats in the status bar. """
        suc_downloads = self.download_manager.successful
        dtime = get_time(self.download_manager.time_it_took)

        msg = self.SUCC_REPORT_MSG.format(suc_downloads,
                                          dtime['days'],
                                          dtime['hours'],
                                          dtime['minutes'],
                                          dtime['seconds'])

        self._status_bar_write(msg)

    def _after_download(self):
        """Run tasks after download process has been completed.

        Note:
            Here you can add any tasks you want to run after the
            download process has been completed.

        """
        if self.opt_manager.options['shutdown']:
            self.opt_manager.save_to_file()
            success = shutdown_sys(self.opt_manager.options['sudo_password'])

            if success:
                self._status_bar_write(self.SHUTDOWN_MSG)
            else:
                self._status_bar_write(self.SHUTDOWN_ERR)
        else:
            self._create_popup(self.DL_COMPLETED_MSG, self.INFO_LABEL, wx.OK | wx.ICON_INFORMATION)
            if self.opt_manager.options['open_dl_dir']:
                success = open_dir(self.opt_manager.options['save_path'])

                if not success:
                    self._status_bar_write(self.OPEN_DIR_ERR.format(dir=self.opt_manager.options['save_path']))

    def _download_worker_handler(self, msg):
        """downloadmanager.Worker thread handler.

        Handles messages from the Worker thread.

        Args:
            See downloadmanager.Worker _talk_to_gui() method.

        """
        signal, data = msg.data

        if signal == 'send':
            self._status_list.write(data)

        if signal == 'receive':
            self.download_manager.send_to_worker(self._status_list.get(data))

    def _download_manager_handler(self, msg):
        """downloadmanager.DownloadManager thread handler.

        Handles messages from the DownloadManager thread.

        Args:
            See downloadmanager.DownloadManager _talk_to_gui() method.

        """
        data = msg.data

        if data == 'finished':
            self._print_stats()
            self._reset_widgets()
            self.download_manager = None
            self._after_download()
        elif data == 'closed':
            self._status_bar_write(self.CLOSED_MSG)
            self._reset_widgets()
            self.download_manager = None
        elif data == 'closing':
            self._status_bar_write(self.CLOSING_MSG)
        elif data == 'report_active':
            # Report number of urls been downloaded
            msg = self.URL_REPORT_MSG.format(self.download_manager.active())
            self._status_bar_write(msg)

    def _update_handler(self, msg):
        """updatemanager.UpdateThread thread handler.

        Handles messages from the UpdateThread thread.

        Args:
            See updatemanager.UpdateThread _talk_to_gui() method.

        """
        data = msg.data

        if data[0] == 'download':
            self._status_bar_write(self.UPDATING_MSG)
        elif data[0] == 'error':
            self._status_bar_write(self.UPDATE_ERR_MSG.format(data[1]))
        elif data[0] == 'correct':
            self._status_bar_write(self.UPDATE_SUCC_MSG)
        else:
            self._reset_widgets()
            self.update_thread = None

    def _get_urls(self):
        """Returns urls list. """
        return self._url_list.GetValue().split('\n')

    def _start_download(self):
        """Handles pre-download tasks & starts the download process. """
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
            #self._download_btn.SetLabel(self.STOP_LABEL)
            #self._update_btn.Disable()

    def _paste_from_clipboard(self):
        """Paste the content of the clipboard to the self._url_list widget.
        It also adds a new line at the end of the data if not exist.

        """
        if not wx.TheClipboard.IsOpened():

            if wx.TheClipboard.Open():
                if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):

                    data = wx.TextDataObject()
                    wx.TheClipboard.GetData(data)

                    data = data.GetText()

                    if data[-1] != '\n':
                        data += '\n'

                    self._url_list.WriteText(data)

                wx.TheClipboard.Close()

    def _on_urllist_edit(self, event):
        """Event handler of the self._url_list widget.

        This method is triggered when the users pastes text into
        the URLs list either by using CTRL+V or by using the middle
        click of the mouse.

        """
        if event.ClassName == self.wxEVT_TEXT_PASTE:
            self._paste_from_clipboard()
        else:
            wx.TheClipboard.UsePrimarySelection(True)
            self._paste_from_clipboard()
            wx.TheClipboard.UsePrimarySelection(False)

        # Dynamically add urls after download process has started
        if self.download_manager is not None:
            self._status_list.load_urls(self._get_urls(), self.download_manager.add_url)

    def _on_download(self, event):
        """Event handler of the self._download_btn widget.

        This method is used when the download-stop button is pressed to
        start or stop the download process.

        """
        if self.download_manager is None:
            self._start_download()
        else:
            self.download_manager.stop_downloads()

    def _on_update(self, event):
        """Event handler of the self._update_btn widget.

        This method is used when the update button is pressed to start
        the update process.

        Note:
            Currently there is not way to stop the update process.

        """
        self._update_youtubedl()

    def _on_options(self, event):
        """Event handler of the self._options_btn widget.

        This method is used when the options button is pressed to show
        the options window.

        """
        self._options_frame.load_all_options()
        self._options_frame.Show()

    def _on_close(self, event):
        """Event handler for the wx.EVT_CLOSE event.

        This method is used when the user tries to close the program
        to save the options and make sure that the download & update
        processes are not running.

        """
        if self.download_manager is not None:
            self.download_manager.stop_downloads()
            self.download_manager.join()

        if self.update_thread is not None:
            self.update_thread.join()

        # Store main-options frame size
        self.opt_manager.options['main_win_size'] = self.GetSize()
        self.opt_manager.options['opts_win_size'] = self._options_frame.GetSize()

        self._options_frame.save_all_options()
        self.opt_manager.save_to_file()
        self.Destroy()


class ListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):

    """Custom ListCtrl widget.

    Args:
        columns (dict): See MainFrame class STATUSLIST_COLUMNS attribute.

    """

    def __init__(self, columns, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ListCtrlAutoWidthMixin.__init__(self)
        self.columns = columns
        self._list_index = 0
        self._url_list = set()
        self._set_columns()

    def get(self, data):
        """Return data from ListCtrl.

        Args:
            data (dict): Dictionary which contains three keys. The 'index'
                that identifies the current row, the 'source' which identifies
                a column in the wxListCtrl and the 'dest' which tells
                wxListCtrl under which key to store the retrieved value. For
                more informations see the _talk_to_gui() method under
                downloadmanager.py Worker class.

        Returns:
            A dictionary which holds the 'index' (row) and the data from the
            given row-column combination.

        Example:
            args: data = {'index': 0, 'source': 'filename', 'dest': 'new_filename'}

            The wxListCtrl will store the value from the 'filename' column
            into a new dictionary with a key value 'new_filename'.

            return: {'index': 0, 'new_filename': 'The filename retrieved'}

        """
        value = None

        # If the source column exists
        if data['source'] in self.columns:
            value = self.GetItemText(data['index'], self.columns[data['source']][0])

        return {'index': data['index'], data['dest']: value}

    def write(self, data):
        """Write data on ListCtrl row-column.

        Args:
            data (dict): Dictionary that contains the data to be
                written on the ListCtrl. In order for this method to
                write the given data there must be an 'index' key that
                identifies the current row. For a valid data dictionary see
                Worker class __init__() method under downloadmanager.py module.

        """
        for key in data:
            if key in self.columns:
                self._write_data(data['index'], self.columns[key][0], data[key])

    def load_urls(self, url_list, func=None):
        """Load URLs from the url_list on the ListCtrl widget.

        Args:
            url_list (list): List of strings that contains the URLs to add.
            func (function): Callback function. It's used to add the URLs
                on the download_manager.

        """
        for url in url_list:
            url = url.replace(' ', '')

            if url and not self.has_url(url):
                self.add_url(url)

                if func is not None:
                    # Custom hack to add url into download_manager
                    item = self._get_item(self._list_index - 1)
                    func(item)

    def has_url(self, url):
        """Returns True if the url is aleady in the ListCtrl else False.

        Args:
            url (string): URL string.

        """
        return url in self._url_list

    def add_url(self, url):
        """Adds the given url in the ListCtrl.

        Args:
            url (string): URL string.

        """
        self.InsertStringItem(self._list_index, url)
        self._url_list.add(url)
        self._list_index += 1

    def clear(self):
        """Clear the ListCtrl widget & reset self._list_index and
        self._url_list. """
        self.DeleteAllItems()
        self._list_index = 0
        self._url_list = set()

    def is_empty(self):
        """Returns True if the list is empty else False. """
        return self._list_index == 0

    def get_items(self):
        """Returns a list of items inside the ListCtrl.

        Returns:
            List of dictionaries that contains the 'url' and the
            'index'(row) for each item of the ListCtrl.

        """
        items = []

        for row in xrange(self._list_index):
            item = self._get_item(row)
            items.append(item)

        return items

    def _write_data(self, row, column, data):
        """Write data on row-column. """
        if isinstance(data, basestring):
            self.SetStringItem(row, column, data)

    def _get_item(self, index):
        """Returns the corresponding ListCtrl item for the given index.

        Args:
            index (int): Index that identifies the row of the item.
                Index must be smaller than the self._list_index.

        Returns:
            Dictionary that contains the URL string of the row and the
            row number(index).

        """
        item = self.GetItem(itemId=index, col=0)
        data = dict(url=item.GetText(), index=index)
        return data

    def _set_columns(self):
        """Initializes ListCtrl columns.
        See MainFrame STATUSLIST_COLUMNS attribute for more info. """
        for column_item in sorted(self.columns.values()):
            self.InsertColumn(column_item[0], column_item[1], width=wx.LIST_AUTOSIZE_USEHEADER)

            # If the column width obtained from wxLIST_AUTOSIZE_USEHEADER
            # is smaller than the minimum allowed column width
            # then set the column width to the minumum allowed size
            if self.GetColumnWidth(column_item[0]) < column_item[2]:
                self.SetColumnWidth(column_item[0], column_item[2])

            # Set auto-resize if enabled
            if column_item[3]:
                self.setResizeColumn(column_item[0])

