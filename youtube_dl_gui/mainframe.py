#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg module responsible for the main app window. """

from __future__ import unicode_literals

import os
import gettext

import wx
from wx.lib.pubsub import setuparg1 #NOTE Should remove deprecated
from wx.lib.pubsub import pub as Publisher

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from .parsers import OptionsParser

from .optionsframe import (
    OptionsFrame,
    LogGUI
)

from .updatemanager import (
    UPDATE_PUB_TOPIC,
    UpdateThread
)

from .downloadmanager import (
    MANAGER_PUB_TOPIC,
    WORKER_PUB_TOPIC,
    DownloadManager,
    DownloadList,
    DownloadItem
)

from .utils import (
    get_pixmaps_dir,
    build_command,
    get_icon_file,
    shutdown_sys,
    remove_file,
    open_file,
    get_time
)

from .widgets import CustomComboBox

from .formats import (
    DEFAULT_FORMATS,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    FORMATS
)

from .info import (
    __descriptionfull__,
    __licensefull__,
    __projecturl__,
    __appname__,
    __author__
)

from .version import __version__


class MainFrame(wx.Frame):

    """Main window class.

    This class is responsible for creating the main app window
    and binding the events.

    Attributes:
        FRAMES_MIN_SIZE (tuple): Tuple that contains the minumum width, height of the frame.

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

    FRAMES_MIN_SIZE = (560, 360)

    # Labels area
    URLS_LABEL = _("Enter URLs below")
    UPDATE_LABEL = _("Update")
    OPTIONS_LABEL = _("Options")
    STOP_LABEL = _("Stop")
    INFO_LABEL = _("Info")
    WELCOME_MSG = _("Welcome")
    WARNING_LABEL = _("Warning")

    ADD_LABEL = _("Add")
    DOWNLOAD_LIST_LABEL = _("Download list")
    DELETE_LABEL = _("Delete")
    PLAY_LABEL = _("Play")
    UP_LABEL = _("Up")
    DOWN_LABEL = _("Down")
    RELOAD_LABEL = _("Reload")
    PAUSE_LABEL = _("Pause")
    START_LABEL = _("Start")
    ABOUT_LABEL = _("About")
    VIEWLOG_LABEL = _("View Log")

    SUCC_REPORT_MSG = _("Successfully downloaded {0} URL(s) in {1} "
                       "day(s) {2} hour(s) {3} minute(s) {4} second(s)")
    DL_COMPLETED_MSG = _("Downloads completed")
    URL_REPORT_MSG = _("Total Progress: {0:.1f}% | Queued ({1}) Paused ({2}) Active ({3}) Completed ({4}) Error ({5})")
    CLOSING_MSG = _("Stopping downloads")
    CLOSED_MSG = _("Downloads stopped")
    PROVIDE_URL_MSG = _("You need to provide at least one URL")
    DOWNLOAD_STARTED = _("Downloads started")
    CHOOSE_DIRECTORY = _("Choose Directory")

    DOWNLOAD_ACTIVE = _("Download in progress. Please wait for all downloads to complete")
    UPDATE_ACTIVE = _("Update already in progress")

    UPDATING_MSG = _("Downloading latest youtube-dl. Please wait...")
    UPDATE_ERR_MSG = _("Youtube-dl download failed [{0}]")
    UPDATE_SUCC_MSG = _("Successfully downloaded youtube-dl")

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
        super(MainFrame, self).__init__(parent, wx.ID_ANY, __appname__, size=opt_manager.options["main_win_size"])
        self.opt_manager = opt_manager
        self.log_manager = log_manager
        self.download_manager = None
        self.update_thread = None
        self.app_icon = None  #REFACTOR Get and set on __init__.py

        self._download_list = DownloadList()

        # Set up youtube-dl options parser
        self._options_parser = OptionsParser()

        # Get the pixmaps directory
        self._pixmaps_path = get_pixmaps_dir()

        # Set the Timer
        self._app_timer = wx.Timer(self)

        # Set the app icon
        app_icon_path = get_icon_file()
        if app_icon_path is not None:
            self.app_icon = wx.Icon(app_icon_path, wx.BITMAP_TYPE_PNG)
            self.SetIcon(self.app_icon)

        bitmap_data = (
           ("down", "arrow_down_32px.png"),
           ("up", "arrow_up_32px.png"),
           ("play", "camera_32px.png"),
           ("start", "cloud_download_32px.png"),
           ("delete", "delete_32px.png"),
           ("folder", "folder_32px.png"),
           ("pause", "pause_32px.png"),
           ("resume", "play_arrow_32px.png"),
           ("reload", "reload_32px.png"),
           ("settings", "settings_20px.png"),
           ("stop", "stop_32px.png")
        )

        self._bitmaps = {}

        for item in bitmap_data:
            target, name = item
            self._bitmaps[target] = wx.Bitmap(os.path.join(self._pixmaps_path, name))

        # Set the data for all the wx.Button items
        # name, label, size, event_handler
        buttons_data = (
            ("delete", self.DELETE_LABEL, (-1, -1), self._on_delete, wx.BitmapButton),
            ("play", self.PLAY_LABEL, (-1, -1), self._on_play, wx.BitmapButton),
            ("up", self.UP_LABEL, (-1, -1), self._on_arrow_up, wx.BitmapButton),
            ("down", self.DOWN_LABEL, (-1, -1), self._on_arrow_down, wx.BitmapButton),
            ("reload", self.RELOAD_LABEL, (-1, -1), self._on_reload, wx.BitmapButton),
            ("pause", self.PAUSE_LABEL, (-1, -1), self._on_pause, wx.BitmapButton),
            ("start", self.START_LABEL, (-1, -1), self._on_start, wx.BitmapButton),
            ("savepath", "...", (35, -1), self._on_savepath, wx.Button),
            ("add", self.ADD_LABEL, (-1, -1), self._on_add, wx.Button)
        )

        # Set the data for the settings menu item
        # label, event_handler
        settings_menu_data = (
            (self.OPTIONS_LABEL, self._on_options),
            (self.UPDATE_LABEL, self._on_update),
            (self.VIEWLOG_LABEL, self._on_viewlog),
            (self.ABOUT_LABEL, self._on_about)
        )

        statuslist_menu_data = (
            (_("Get URL"), self._on_geturl),
            (_("Get command"), self._on_getcmd),
            (_("Open destination"), self._on_open_dest),
            (_("Re-enter"), self._on_reenter)
        )

        # Create options frame
        self._options_frame = OptionsFrame(self)

        # Create frame components
        self._panel = wx.Panel(self)

        self._url_text = self._create_statictext(self.URLS_LABEL)

        #REFACTOR Move to buttons_data
        self._settings_button = self._create_bitmap_button(self._bitmaps["settings"], (30, 30), self._on_settings)

        self._url_list = self._create_textctrl(wx.TE_MULTILINE | wx.TE_DONTWRAP, self._on_urllist_edit)

        self._folder_icon = self._create_static_bitmap(self._bitmaps["folder"], self._on_open_path)

        self._path_combobox = ExtComboBox(self._panel, 5, style=wx.CB_READONLY)
        self._videoformat_combobox = CustomComboBox(self._panel, style=wx.CB_READONLY)

        self._download_text = self._create_statictext(self.DOWNLOAD_LIST_LABEL)
        self._status_list = ListCtrl(self.STATUSLIST_COLUMNS,
                                     parent=self._panel,
                                     style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)

        # Dictionary to store all the buttons
        self._buttons = {}

        for item in buttons_data:
            name, label, size, evt_handler, parent = item

            button = parent(self._panel, size=size)

            if parent == wx.Button:
                button.SetLabel(label)
            elif parent == wx.BitmapButton:
                button.SetToolTip(wx.ToolTip(label))

            if name in self._bitmaps:
                button.SetBitmap(self._bitmaps[name], wx.TOP)

            if evt_handler is not None:
                button.Bind(wx.EVT_BUTTON, evt_handler)

            self._buttons[name] = button

        self._status_bar = self.CreateStatusBar()

        # Create extra components
        self._settings_menu = self._create_menu_item(settings_menu_data)
        self._statuslist_menu = self._create_menu_item(statuslist_menu_data)

        # Overwrite the menu hover event to avoid changing the statusbar
        self.Bind(wx.EVT_MENU_HIGHLIGHT, lambda event: None)

        # Bind extra events
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_statuslist_right_click, self._status_list)
        self.Bind(wx.EVT_TEXT, self._update_savepath, self._path_combobox)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._update_pause_button, self._status_list)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._update_pause_button, self._status_list)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(wx.EVT_TIMER, self._on_timer, self._app_timer)

        self._videoformat_combobox.Bind(wx.EVT_COMBOBOX, self._update_videoformat)

        # Set threads wxCallAfter handlers
        self._set_publisher(self._update_handler, UPDATE_PUB_TOPIC)
        self._set_publisher(self._download_worker_handler, WORKER_PUB_TOPIC)
        self._set_publisher(self._download_manager_handler, MANAGER_PUB_TOPIC)

        # Set up extra stuff
        self.Center()
        self.SetMinSize(self.FRAMES_MIN_SIZE)

        self._status_bar_write(self.WELCOME_MSG)

        self._update_videoformat_combobox()
        self._path_combobox.LoadMultiple(self.opt_manager.options["save_path_dirs"])
        self._path_combobox.SetValue(self.opt_manager.options["save_path"])

        self._set_layout()

        self._url_list.SetFocus()

    def _create_menu_item(self, items):
        menu = wx.Menu()

        for item in items:
            label, evt_handler = item
            menu_item = menu.Append(-1, label)

            menu.Bind(wx.EVT_MENU, evt_handler, menu_item)

        return menu

    def _on_statuslist_right_click(self, event):
        selected = event.GetIndex()

        if selected != -1:
            self._status_list.deselect_all()
            self._status_list.Select(selected, on=1)

            self.PopupMenu(self._statuslist_menu)

    def _on_reenter(self, event):
        selected = self._status_list.get_selected()

        if selected != -1:
            object_id = self._status_list.GetItemData(selected)
            download_item = self._download_list.get_item(object_id)

            if download_item.stage != "Active":
                self._status_list.remove_row(selected)
                self._download_list.remove(object_id)

                options = self._options_parser.parse(self.opt_manager.options)

                download_item = DownloadItem(download_item.url, options)
                download_item.path = self.opt_manager.options["save_path"]

                if not self._download_list.has_item(download_item.object_id):
                    self._status_list.bind_item(download_item)
                    self._download_list.insert(download_item)

    def reset(self):
        self._update_videoformat_combobox()
        self._path_combobox.LoadMultiple(self.opt_manager.options["save_path_dirs"])
        self._path_combobox.SetValue(self.opt_manager.options["save_path"])

    def _on_open_dest(self, event):
        selected = self._status_list.get_selected()

        if selected != -1:
            object_id = self._status_list.GetItemData(selected)
            download_item = self._download_list.get_item(object_id)

            if download_item.path:
                open_file(download_item.path)

    def _on_open_path(self, event):
        open_file(self._path_combobox.GetValue())

    def _on_geturl(self, event):
        selected = self._status_list.get_selected()

        if selected != -1:
            object_id = self._status_list.GetItemData(selected)
            download_item = self._download_list.get_item(object_id)

            url = download_item.url

            if not wx.TheClipboard.IsOpened():
                clipdata = wx.TextDataObject()
                clipdata.SetText(url)
                wx.TheClipboard.Open()
                wx.TheClipboard.SetData(clipdata)
                wx.TheClipboard.Close()

    def _on_getcmd(self, event):
        selected = self._status_list.get_selected()

        if selected != -1:
            object_id = self._status_list.GetItemData(selected)
            download_item = self._download_list.get_item(object_id)

            cmd = build_command(download_item.options, download_item.url)

            if not wx.TheClipboard.IsOpened():
                clipdata = wx.TextDataObject()
                clipdata.SetText(cmd)
                wx.TheClipboard.Open()
                wx.TheClipboard.SetData(clipdata)
                wx.TheClipboard.Close()

    def _on_timer(self, event):
        total_percentage = 0.0
        queued = paused = active = completed = error = 0

        for item in self._download_list.get_items():
            if item.stage == "Queued":
                queued += 1
            if item.stage == "Paused":
                paused += 1
            if item.stage == "Active":
                active += 1
                total_percentage += float(item.progress_stats["percent"].split('%')[0])
            if item.stage == "Completed":
                completed += 1
            if item.stage == "Error":
                error += 1

        # REFACTOR Store percentage as float in the DownloadItem?
        # REFACTOR DownloadList keep track for each item stage?

        items_count = active + completed + error + queued
        total_percentage += completed * 100.0 + error * 100.0

        if items_count:
            total_percentage /= items_count

        msg = self.URL_REPORT_MSG.format(total_percentage, queued, paused, active, completed, error)

        if self.update_thread is None:
            # Dont overwrite the update messages
            self._status_bar_write(msg)

    def _update_pause_button(self, event):
        selected_rows = self._status_list.get_all_selected()

        label = _("Pause")
        bitmap = self._bitmaps["pause"]

        for row in selected_rows:
            object_id = self._status_list.GetItemData(row)
            download_item = self._download_list.get_item(object_id)

            if download_item.stage == "Paused":
                # If we find one or more items in Paused
                # state set the button functionality to resume
                label = _("Resume")
                bitmap = self._bitmaps["resume"]
                break

        self._buttons["pause"].SetLabel(label)
        self._buttons["pause"].SetToolTip(wx.ToolTip(label))
        self._buttons["pause"].SetBitmap(bitmap, wx.TOP)

    def _update_videoformat_combobox(self):
        self._videoformat_combobox.Clear()

        self._videoformat_combobox.add_items(list(DEFAULT_FORMATS.values()), False)

        vformats = []
        for vformat in self.opt_manager.options["selected_video_formats"]:
            vformats.append(FORMATS[vformat])

        aformats = []
        for aformat in self.opt_manager.options["selected_audio_formats"]:
            aformats.append(FORMATS[aformat])

        if vformats:
            self._videoformat_combobox.add_header(_("Video"))
            self._videoformat_combobox.add_items(vformats)

        if aformats:
            self._videoformat_combobox.add_header(_("Audio"))
            self._videoformat_combobox.add_items(aformats)

        current_index = self._videoformat_combobox.FindString(FORMATS[self.opt_manager.options["selected_format"]])

        if current_index == wx.NOT_FOUND:
            self._videoformat_combobox.SetSelection(0)
        else:
            self._videoformat_combobox.SetSelection(current_index)

        self._update_videoformat(None)

    def _update_videoformat(self, event):
        self.opt_manager.options["selected_format"] = selected_format = FORMATS[self._videoformat_combobox.GetValue()]

        if selected_format in VIDEO_FORMATS:
            self.opt_manager.options["video_format"] = selected_format
            self.opt_manager.options["audio_format"] = ""  #NOTE Set to default value, check parsers.py
        elif selected_format in AUDIO_FORMATS:
            self.opt_manager.options["video_format"] = DEFAULT_FORMATS[_("default")]
            self.opt_manager.options["audio_format"] = selected_format
        else:
            self.opt_manager.options["video_format"] = DEFAULT_FORMATS[_("default")]
            self.opt_manager.options["audio_format"] = ""

    def _update_savepath(self, event):
        self.opt_manager.options["save_path"] = self._path_combobox.GetValue()

    def _on_delete(self, event):
        index = self._status_list.get_next_selected()

        if index == -1:
            dlg = ButtonsChoiceDialog(self, [_("Remove all"), _("Remove completed")], _("No items selected. Please pick an action"), _("Delete"))
            ret_code = dlg.ShowModal()
            dlg.Destroy()

            #REFACTOR Maybe add this functionality directly to DownloadList?
            if ret_code == 1:
                for ditem in self._download_list.get_items():
                    if ditem.stage != "Active":
                        self._status_list.remove_row(self._download_list.index(ditem.object_id))
                        self._download_list.remove(ditem.object_id)

            if ret_code == 2:
                for ditem in self._download_list.get_items():
                    if ditem.stage == "Completed":
                        self._status_list.remove_row(self._download_list.index(ditem.object_id))
                        self._download_list.remove(ditem.object_id)
        else:
            if self.opt_manager.options["confirm_deletion"]:
                dlg = wx.MessageDialog(self, _("Are you sure you want to remove selected items?"), _("Delete"), wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal() == wx.ID_YES
                dlg.Destroy()
            else:
                result = True

            if result:
                while index >= 0:
                    object_id = self._status_list.GetItemData(index)
                    selected_download_item = self._download_list.get_item(object_id)

                    if selected_download_item.stage == "Active":
                        self._create_popup(_("Item is active, cannot remove"), self.WARNING_LABEL, wx.OK | wx.ICON_EXCLAMATION)
                    else:
                        #if selected_download_item.stage == "Completed":
                            #dlg = wx.MessageDialog(self, "Do you want to remove the files associated with this item?", "Remove files", wx.YES_NO | wx.ICON_QUESTION)

                            #result = dlg.ShowModal() == wx.ID_YES
                            #dlg.Destroy()

                            #if result:
                                #for cur_file in selected_download_item.get_files():
                                    #remove_file(cur_file)

                        self._status_list.remove_row(index)
                        self._download_list.remove(object_id)
                        index -= 1

                    index = self._status_list.get_next_selected(index)

        self._update_pause_button(None)

    def _on_play(self, event):
        selected_rows = self._status_list.get_all_selected()

        if selected_rows:
            for selected_row in selected_rows:
                object_id = self._status_list.GetItemData(selected_row)
                selected_download_item = self._download_list.get_item(object_id)

                if selected_download_item.stage == "Completed":
                    if selected_download_item.filenames:
                        filename = selected_download_item.get_files()[-1]
                        open_file(filename)
                else:
                    self._create_popup(_("Item is not completed"), self.INFO_LABEL, wx.OK | wx.ICON_INFORMATION)

    def _on_arrow_up(self, event):
        index = self._status_list.get_next_selected()

        if index != -1:
            while index >= 0:
                object_id = self._status_list.GetItemData(index)
                download_item = self._download_list.get_item(object_id)

                new_index = index - 1
                if new_index < 0:
                    new_index = 0

                if not self._status_list.IsSelected(new_index):
                    self._download_list.move_up(object_id)
                    self._status_list.move_item_up(index)
                    self._status_list._update_from_item(new_index, download_item)

                index = self._status_list.get_next_selected(index)

    def _on_arrow_down(self, event):
        index = self._status_list.get_next_selected(reverse=True)

        if index != -1:
            while index >= 0:
                object_id = self._status_list.GetItemData(index)
                download_item = self._download_list.get_item(object_id)

                new_index = index + 1
                if new_index >= self._status_list.GetItemCount():
                    new_index = self._status_list.GetItemCount() - 1

                if not self._status_list.IsSelected(new_index):
                    self._download_list.move_down(object_id)
                    self._status_list.move_item_down(index)
                    self._status_list._update_from_item(new_index, download_item)

                index = self._status_list.get_next_selected(index, True)

    def _on_reload(self, event):
        selected_rows = self._status_list.get_all_selected()

        if not selected_rows:
            for index, item in enumerate(self._download_list.get_items()):
                if item.stage in ("Paused", "Completed", "Error"):
                    # Store the old savepath because reset is going to remove it
                    savepath = item.path
                    item.reset()
                    item.path = savepath
                    self._status_list._update_from_item(index, item)
        else:
            for selected_row in selected_rows:
                object_id = self._status_list.GetItemData(selected_row)
                item = self._download_list.get_item(object_id)

                if item.stage in ("Paused", "Completed", "Error"):
                    # Store the old savepath because reset is going to remove it
                    savepath = item.path
                    item.reset()
                    item.path = savepath
                    self._status_list._update_from_item(selected_row, item)

            self._update_pause_button(None)

    def _on_pause(self, event):
        selected_rows = self._status_list.get_all_selected()

        if selected_rows:
            #REFACTOR Use DoubleStageButton for this and check stage
            if self._buttons["pause"].GetLabel() == _("Pause"):
                new_state = "Paused"
            else:
                new_state = "Queued"

            for selected_row in selected_rows:
                object_id = self._status_list.GetItemData(selected_row)
                download_item = self._download_list.get_item(object_id)

                if download_item.stage == "Queued" or download_item.stage == "Paused":
                    self._download_list.change_stage(object_id, new_state)

                self._status_list._update_from_item(selected_row, download_item)

            self._update_pause_button(None)

    def _on_start(self, event):
        if self.download_manager is None:
            if self.update_thread is not None and self.update_thread.is_alive():
                self._create_popup(_("Update in progress. Please wait for the update to complete"),
                                   self.WARNING_LABEL,
                                   wx.OK | wx.ICON_EXCLAMATION)
            else:
                self._start_download()
        else:
            self.download_manager.stop_downloads()

    def _on_savepath(self, event):
        dlg = wx.DirDialog(self, self.CHOOSE_DIRECTORY, self._path_combobox.GetStringSelection())

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

            self._path_combobox.Append(path)
            self._path_combobox.SetValue(path)
            self._update_savepath(None)

        dlg.Destroy()

    def _on_add(self, event):
        urls = self._get_urls()

        if not urls:
            self._create_popup(self.PROVIDE_URL_MSG,
                               self.WARNING_LABEL,
                               wx.OK | wx.ICON_EXCLAMATION)
        else:
            self._url_list.Clear()
            options = self._options_parser.parse(self.opt_manager.options)

            for url in urls:
                download_item = DownloadItem(url, options)
                download_item.path = self.opt_manager.options["save_path"]

                if not self._download_list.has_item(download_item.object_id):
                    self._status_list.bind_item(download_item)
                    self._download_list.insert(download_item)


    def _on_settings(self, event):
        event_object_pos = event.EventObject.GetPosition()
        event_object_height = event.EventObject.GetSize()[1]
        event_object_pos = (event_object_pos[0], event_object_pos[1] + event_object_height)
        self.PopupMenu(self._settings_menu, event_object_pos)

    def _on_viewlog(self, event):
        if self.log_manager is None:
            self._create_popup(_("Logging is disabled"),
                               self.WARNING_LABEL,
                               wx.OK | wx.ICON_EXCLAMATION)
        else:
            log_window = LogGUI(self)
            log_window.load(self.log_manager.log_file)
            log_window.Show()

    def _on_about(self, event):
        info = wx.AboutDialogInfo()

        if self.app_icon is not None:
            info.SetIcon(self.app_icon)

        info.SetName(__appname__)
        info.SetVersion(__version__)
        info.SetDescription(__descriptionfull__)
        info.SetWebSite(__projecturl__)
        info.SetLicense(__licensefull__)
        info.AddDeveloper(__author__)

        wx.AboutBox(info)

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

    def _create_statictext(self, label):
        return wx.StaticText(self._panel, label=label)

    def _create_bitmap_button(self, icon, size=(-1, -1), handler=None):
        button = wx.BitmapButton(self._panel, bitmap=icon, size=size, style=wx.NO_BORDER)

        if handler is not None:
            button.Bind(wx.EVT_BUTTON, handler)

        return button

    def _create_static_bitmap(self, icon, event_handler=None):
        static_bitmap = wx.StaticBitmap(self._panel, bitmap=icon)

        if event_handler is not None:
            static_bitmap.Bind(wx.EVT_LEFT_DCLICK, event_handler)

        return static_bitmap

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

    def _create_popup(self, text, title, style):
        wx.MessageBox(text, title, style)

    def _set_layout(self):
        """Sets the layout of the main window. """
        main_sizer = wx.BoxSizer()
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self._url_text, 0, wx.ALIGN_BOTTOM | wx.BOTTOM, 5)
        top_sizer.AddSpacer((-1, -1), 1)
        top_sizer.Add(self._settings_button)
        panel_sizer.Add(top_sizer, 0, wx.EXPAND)

        panel_sizer.Add(self._url_list, 1, wx.EXPAND)

        mid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mid_sizer.Add(self._folder_icon)
        mid_sizer.AddSpacer((3, -1))
        mid_sizer.Add(self._path_combobox, 2, wx.ALIGN_CENTER_VERTICAL)
        mid_sizer.AddSpacer((5, -1))
        mid_sizer.Add(self._buttons["savepath"], flag=wx.ALIGN_CENTER_VERTICAL)
        mid_sizer.AddSpacer((10, -1), 1)
        mid_sizer.Add(self._videoformat_combobox, 1, wx.ALIGN_CENTER_VERTICAL)
        mid_sizer.AddSpacer((5, -1))
        mid_sizer.Add(self._buttons["add"], flag=wx.ALIGN_CENTER_VERTICAL)
        panel_sizer.Add(mid_sizer, 0, wx.EXPAND | wx.ALL, 10)

        panel_sizer.Add(self._download_text, 0, wx.BOTTOM, 5)
        panel_sizer.Add(self._status_list, 2, wx.EXPAND)

        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_sizer.Add(self._buttons["delete"])
        bottom_sizer.AddSpacer((5, -1))
        bottom_sizer.Add(self._buttons["play"])
        bottom_sizer.AddSpacer((5, -1))
        bottom_sizer.Add(self._buttons["up"])
        bottom_sizer.AddSpacer((5, -1))
        bottom_sizer.Add(self._buttons["down"])
        bottom_sizer.AddSpacer((5, -1))
        bottom_sizer.Add(self._buttons["reload"])
        bottom_sizer.AddSpacer((5, -1))
        bottom_sizer.Add(self._buttons["pause"])
        bottom_sizer.AddSpacer((10, -1), 1)
        bottom_sizer.Add(self._buttons["start"])
        panel_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.TOP, 5)

        main_sizer.Add(panel_sizer, 1, wx.ALL | wx.EXPAND, 10)
        self._panel.SetSizer(main_sizer)

        self._panel.Layout()

    def _update_youtubedl(self):
        """Update youtube-dl binary to the latest version. """
        if self.download_manager is not None and self.download_manager.is_alive():
            self._create_popup(self.DOWNLOAD_ACTIVE,
                               self.WARNING_LABEL,
                               wx.OK | wx.ICON_EXCLAMATION)
        elif self.update_thread is not None and self.update_thread.is_alive():
            self._create_popup(self.UPDATE_ACTIVE,
                               self.INFO_LABEL,
                               wx.OK | wx.ICON_INFORMATION)
        else:
            self.update_thread = UpdateThread(self.opt_manager.options['youtubedl_path'])

    def _status_bar_write(self, msg):
        """Display msg in the status bar. """
        self._status_bar.SetStatusText(msg)

    def _reset_widgets(self):
        """Resets GUI widgets after update or download process. """
        self._buttons["start"].SetLabel(_("Start"))
        self._buttons["start"].SetToolTip(wx.ToolTip(_("Start")))
        self._buttons["start"].SetBitmap(self._bitmaps["start"], wx.TOP)

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
            dlg = ShutdownDialog(self, 60, _("Shutting down in {0} second(s)"), _("Shutdown"))
            result = dlg.ShowModal() == wx.ID_OK
            dlg.Destroy()

            if result:
                self.opt_manager.save_to_file()
                success = shutdown_sys(self.opt_manager.options['sudo_password'])

                if success:
                    self._status_bar_write(self.SHUTDOWN_MSG)
                else:
                    self._status_bar_write(self.SHUTDOWN_ERR)
        else:
            if self.opt_manager.options["show_completion_popup"]:
                self._create_popup(self.DL_COMPLETED_MSG, self.INFO_LABEL, wx.OK | wx.ICON_INFORMATION)

    def _download_worker_handler(self, msg):
        """downloadmanager.Worker thread handler.

        Handles messages from the Worker thread.

        Args:
            See downloadmanager.Worker _talk_to_gui() method.

        """
        signal, data = msg.data

        download_item = self._download_list.get_item(data["index"])
        download_item.update_stats(data)
        row = self._download_list.index(data["index"])

        self._status_list._update_from_item(row, download_item)

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
            self._app_timer.Stop()
            self._after_download()
        elif data == 'closed':
            self._status_bar_write(self.CLOSED_MSG)
            self._reset_widgets()
            self.download_manager = None
            self._app_timer.Stop()
        elif data == 'closing':
            self._status_bar_write(self.CLOSING_MSG)
        elif data == 'report_active':
            pass
            #NOTE Remove from here and downloadmanager
            #since now we have the wx.Timer to check progress

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
        return [line for line in self._url_list.GetValue().split('\n') if line]

    def _start_download(self):
        if self._status_list.is_empty():
            self._create_popup(_("No items to download"),
                               self.WARNING_LABEL,
                               wx.OK | wx.ICON_EXCLAMATION)
        else:
            self._app_timer.Start(100)
            self.download_manager = DownloadManager(self, self._download_list, self.opt_manager, self.log_manager)

            self._status_bar_write(self.DOWNLOAD_STARTED)
            self._buttons["start"].SetLabel(self.STOP_LABEL)
            self._buttons["start"].SetToolTip(wx.ToolTip(self.STOP_LABEL))
            self._buttons["start"].SetBitmap(self._bitmaps["stop"], wx.TOP)

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
        if event.GetEventType() == wx.EVT_TEXT_PASTE.typeId:
            self._paste_from_clipboard()
        else:
            wx.TheClipboard.UsePrimarySelection(True)
            self._paste_from_clipboard()
            wx.TheClipboard.UsePrimarySelection(False)

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
        if self.opt_manager.options["confirm_exit"]:
            dlg = wx.MessageDialog(self, _("Are you sure you want to exit?"), _("Exit"), wx.YES_NO | wx.ICON_QUESTION)

            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()
        else:
            result = True

        if result:
            self.close()

    def close(self):
        if self.download_manager is not None:
            self.download_manager.stop_downloads()
            self.download_manager.join()

        if self.update_thread is not None:
            self.update_thread.join()

        # Store main-options frame size
        self.opt_manager.options['main_win_size'] = self.GetSize()
        self.opt_manager.options['opts_win_size'] = self._options_frame.GetSize()

        self.opt_manager.options["save_path_dirs"] = self._path_combobox.GetStrings()

        self._options_frame.save_all_options()
        self.opt_manager.save_to_file()

        self.Destroy()


class ListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):

    """Custom ListCtrl widget.

    Args:
        columns (dict): See MainFrame class STATUSLIST_COLUMNS attribute.

    """

    def __init__(self, columns, *args, **kwargs):
        super(ListCtrl, self).__init__(*args, **kwargs)
        ListCtrlAutoWidthMixin.__init__(self)
        self.columns = columns
        self._list_index = 0
        self._url_list = set()
        self._set_columns()

    def remove_row(self, row_number):
        self.DeleteItem(row_number)
        self._list_index -= 1

    def move_item_up(self, row_number):
        self._move_item(row_number, row_number - 1)

    def move_item_down(self, row_number):
        self._move_item(row_number, row_number + 1)

    def _move_item(self, cur_row, new_row):
        self.Freeze()
        item = self.GetItem(cur_row)
        self.DeleteItem(cur_row)

        item.SetId(new_row)
        self.InsertItem(item)

        self.Select(new_row)
        self.Thaw()

    def has_url(self, url):
        """Returns True if the url is aleady in the ListCtrl else False.

        Args:
            url (string): URL string.

        """
        return url in self._url_list

    def bind_item(self, download_item):
        self.InsertStringItem(self._list_index, download_item.url)

        self.SetItemData(self._list_index, download_item.object_id)

        self._update_from_item(self._list_index, download_item)

        self._list_index += 1

    def _update_from_item(self, row, download_item):
        progress_stats = download_item.progress_stats

        for key in self.columns:
            column = self.columns[key][0]

            if key == "status" and progress_stats["playlist_index"]:
                # Not the best place but we build the playlist status here
                status = "{0} {1}/{2}".format(progress_stats["status"],
                                              progress_stats["playlist_index"],
                                              progress_stats["playlist_size"])

                self.SetStringItem(row, column, status)
            else:
                self.SetStringItem(row, column, progress_stats[key])

    def clear(self):
        """Clear the ListCtrl widget & reset self._list_index and
        self._url_list. """
        self.DeleteAllItems()
        self._list_index = 0
        self._url_list = set()

    def is_empty(self):
        """Returns True if the list is empty else False. """
        return self._list_index == 0

    def get_selected(self):
        return self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

    def get_all_selected(self):
        return [index for index in xrange(self._list_index) if self.IsSelected(index)]

    def deselect_all(self):
        for index in xrange(self._list_index):
            self.Select(index, on=0)

    def get_next_selected(self, start=-1, reverse=False):
        if start == -1:
            start = self._list_index - 1 if reverse else 0
        else:
            # start from next item
            if reverse:
                start -= 1
            else:
                start += 1

        end = -1 if reverse else self._list_index
        step = -1 if reverse else 1

        for index in xrange(start, end, step):
            if self.IsSelected(index):
                return index

        return -1

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

# REFACTOR Extra widgets below should move to other module with widgets

class ExtComboBox(wx.ComboBox):

    def __init__(self, parent, max_items=-1, *args, **kwargs):
        super(ExtComboBox, self).__init__(parent, *args, **kwargs)

        assert max_items > 0 or max_items == -1
        self.max_items = max_items

    def Append(self, new_value):
        if self.FindString(new_value) == wx.NOT_FOUND:
            super(ExtComboBox, self).Append(new_value)

            if self.max_items != -1 and self.GetCount() > self.max_items:
                self.SetItems(self.GetStrings()[1:])

    def SetValue(self, new_value):
        if self.FindString(new_value) == wx.NOT_FOUND:
            self.Append(new_value)

        self.SetSelection(self.FindString(new_value))

    def LoadMultiple(self, items_list):
        for item in items_list:
            self.Append(item)


class DoubleStageButton(wx.Button):

    def __init__(self, parent, labels, bitmaps, bitmap_pos=wx.TOP, *args, **kwargs):
        super(DoubleStageButton, self).__init__(parent, *args, **kwargs)

        assert isinstance(labels, tuple) and isinstance(bitmaps, tuple)
        assert len(labels) == 2
        assert len(bitmaps) == 0 or len(bitmaps) == 2

        self.labels = labels
        self.bitmaps = bitmaps
        self.bitmap_pos = bitmap_pos

        self._stage = 0
        self._set_layout()

    def _set_layout(self):
        self.SetLabel(self.labels[self._stage])

        if len(self.bitmaps):
            self.SetBitmap(self.bitmaps[self._stage], self.bitmap_pos)

    def change_stage(self):
        self._stage = 0 if self._stage else 1
        self._set_layout()

    def set_stage(self, new_stage):
        assert new_stage == 0 or new_stage == 1

        self._stage = new_stage
        self._set_layout()


class ButtonsChoiceDialog(wx.Dialog):

    if os.name == "nt":
        STYLE = wx.DEFAULT_DIALOG_STYLE
    else:
        STYLE = wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX

    BORDER = 10

    def __init__(self, parent, choices, message, *args, **kwargs):
        super(ButtonsChoiceDialog, self).__init__(parent, wx.ID_ANY, *args, style=self.STYLE, **kwargs)

        buttons = []

        # Create components
        panel = wx.Panel(self)

        info_bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MESSAGE_BOX)

        info_icon = wx.StaticBitmap(panel, wx.ID_ANY, info_bmp)
        msg_text = wx.StaticText(panel, wx.ID_ANY, message)

        buttons.append(wx.Button(panel, wx.ID_CANCEL, _("Cancel")))

        for index, label in enumerate(choices):
            buttons.append(wx.Button(panel, index + 1, label))

        # Get the maximum button width & height
        max_width = max_height = -1

        for button in buttons:
            button_width, button_height = button.GetSize()

            if button_width > max_width:
                max_width = button_width

            if button_height > max_height:
                max_height = button_height

        max_width += 10

        # Set buttons width & bind events
        for button in buttons:
            if button != buttons[0]:
                button.SetMinSize((max_width, max_height))
            else:
                # On Close button change only the height
                button.SetMinSize((-1, max_height))

            button.Bind(wx.EVT_BUTTON, self._on_close)

        # Set sizers
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        message_sizer = wx.BoxSizer(wx.HORIZONTAL)
        message_sizer.Add(info_icon)
        message_sizer.AddSpacer((10, 10))
        message_sizer.Add(msg_text, flag=wx.EXPAND)

        vertical_sizer.Add(message_sizer, 1, wx.ALL, border=self.BORDER)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for button in buttons[1:]:
            buttons_sizer.Add(button)
            buttons_sizer.AddSpacer((5, -1))

        buttons_sizer.AddSpacer((-1, -1), 1)
        buttons_sizer.Add(buttons[0], flag=wx.ALIGN_RIGHT)
        vertical_sizer.Add(buttons_sizer, flag=wx.EXPAND | wx.ALL, border=self.BORDER)

        panel.SetSizer(vertical_sizer)

        width, height = panel.GetBestSize()
        self.SetSize((width, height * 1.3))

        self.Center()

    def _on_close(self, event):
        self.EndModal(event.GetEventObject().GetId())


class ButtonsGroup(object):

    WIDTH = 0
    HEIGHT = 1

    def __init__(self, buttons_list=None, squared=False):
        if buttons_list is None:
            self._buttons_list = []
        else:
            self._buttons_list = buttons_list

        self._squared = squared

    def set_size(self, size):
        assert len(size) == 2

        width, height = size

        if width == -1:
            for button in self._buttons_list:
                cur_width = button.GetSize()[self.WIDTH]

                if cur_width > width:
                    width = cur_width

        if height == -1:
            for button in self._buttons_list:
                cur_height = button.GetSize()[self.HEIGHT]

                if cur_height > height:
                    height = cur_height

        if self._squared:
            width = height = (width if width > height else height)

        for button in self._buttons_list:
            button.SetMinSize((width, height))

    def create_sizer(self, orient=wx.HORIZONTAL, space=-1):
        box_sizer = wx.BoxSizer(orient)

        for button in self._buttons_list:
            box_sizer.Add(button)

            if space != -1:
                box_sizer.AddSpacer((space, space))

        return box_sizer

    def bind_event(self, event, event_handler):
        for button in self._buttons_list:
            button.Bind(event, event_handler)

    def disable_all(self):
        for button in self._buttons_list:
            button.Enable(False)

    def enable_all(self):
        for button in self._buttons_list:
            button.Enable(True)

    def add(self, button):
        self._buttons_list.append(button)


class ShutdownDialog(wx.Dialog):

    if os.name == "nt":
        STYLE = wx.DEFAULT_DIALOG_STYLE
    else:
        STYLE = wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX

    TIMER_INTERVAL = 1000  # milliseconds

    BORDER = 10

    def __init__(self, parent, timeout, message, *args, **kwargs):
        super(ShutdownDialog, self).__init__(parent, wx.ID_ANY, *args, style=self.STYLE, **kwargs)
        assert timeout > 0

        self.timeout = timeout
        self.message = message

        # Create components
        panel = wx.Panel(self)

        info_bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MESSAGE_BOX)
        info_icon = wx.StaticBitmap(panel, wx.ID_ANY, info_bmp)

        self.msg_text = msg_text = wx.StaticText(panel, wx.ID_ANY, self._get_message())
        ok_button = wx.Button(panel, wx.ID_OK, _("OK"))
        cancel_button = wx.Button(panel, wx.ID_CANCEL, _("Cancel"))

        # Set layout
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        message_sizer = wx.BoxSizer(wx.HORIZONTAL)
        message_sizer.Add(info_icon)
        message_sizer.AddSpacer((10, 10))
        message_sizer.Add(msg_text, flag=wx.EXPAND)

        vertical_sizer.Add(message_sizer, 1, wx.ALL, border=self.BORDER)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(ok_button)
        buttons_sizer.AddSpacer((5, -1))
        buttons_sizer.Add(cancel_button)

        vertical_sizer.Add(buttons_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=self.BORDER)

        panel.SetSizer(vertical_sizer)

        width, height = panel.GetBestSize()
        self.SetSize((width * 1.3, height * 1.3))

        self.Center()

        # Set up timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.timer.Start(self.TIMER_INTERVAL)

    def _get_message(self):
        return self.message.format(self.timeout)

    def _on_timer(self, event):
        self.timeout -= 1
        self.msg_text.SetLabel(self._get_message())

        if self.timeout <= 0:
            self.EndModal(wx.ID_OK)

    def Destroy(self):
        self.timer.Stop()
        return super(ShutdownDialog, self).Destroy()
