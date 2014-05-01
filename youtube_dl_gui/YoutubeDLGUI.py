#! /usr/bin/env python

import wx
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from .version import __version__
from .UpdateThread import UpdateThread
from .DownloadThread import DownloadManager
from .OptionsHandler import OptionsHandler
from .YoutubeDLInterpreter import YoutubeDLInterpreter
from .OutputHandler import DownloadHandler
from .LogManager import LogManager, LogGUI
from .Utils import (
    video_is_dash,
    have_dash_audio,
    os_type,
    file_exist,
    fix_path,
    abs_path,
    open_dir,
    remove_spaces
)
from .data import (
    __author__,
    __projecturl__,
    __appname__,
    __licensefull__,
    __descriptionfull__
)

if os_type == 'nt':
    YOUTUBE_DL_FILENAME = 'youtube-dl.exe'
else:
    YOUTUBE_DL_FILENAME = 'youtube-dl'

AUDIOFORMATS = ["mp3", "wav", "aac", "m4a"]

VIDEOFORMATS = ["default",
                "mp4 [1280x720]",
                "mp4 [640x360]",
                "webm [640x360]",
                "flv [400x240]",
                "3gp [320x240]",
                "mp4 1080p(DASH)",
                "mp4 720p(DASH)",
                "mp4 480p(DASH)",
                "mp4 360p(DASH)"]

DASH_AUDIO_FORMATS = ["NO SOUND",
                      "DASH m4a audio 128k",
                      "DASH webm audio 48k"]

LANGUAGES = ["English",
             "Greek",
             "Portuguese",
             "French",
             "Italian",
             "Russian",
             "Spanish",
             "German"]

ICON = fix_path(abs_path(__file__))+'icons/youtube-dl-gui.png'

class MainFrame(wx.Frame):

    def __init__(self, parent=None, id=-1):
        wx.Frame.__init__(self, parent, id, __appname__+' '+__version__, size=(600, 420))

        # init gui
        self.InitGUI()

        # bind events
        self.Bind(wx.EVT_BUTTON, self.OnDownload, self.downloadButton)
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.updateButton)
        self.Bind(wx.EVT_BUTTON, self.OnOptions, self.optionsButton)
        self.Bind(wx.EVT_TEXT, self.OnTrackListChange, self.trackList)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # set app icon
        icon = wx.Icon(ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # set publisher for update thread
        Publisher.subscribe(self.update_handler, "update")

        # set publisher for download thread
        Publisher.subscribe(self.download_handler, "download")

        # init Options and DownloadHandler objects
        self.optManager = OptionsHandler()
        self.downloadHandler = None

        # init log manager
        self.logManager = None
        if self.optManager.options['enable_log']:
            self.logManager = LogManager(
              self.optManager.get_config_path(),
              self.optManager.options['log_time']
            )

        # init some thread variables
        self.downloadThread = None
        self.updateThread = None

        # init urlList for evt_text on self.trackList
        self.urlList = []

    def InitGUI(self):
        self.panel = wx.Panel(self)
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        urlTextBox = wx.BoxSizer(wx.HORIZONTAL)
        urlTextBox.Add(wx.StaticText(self.panel, label='URLs'), flag = wx.TOP, border=10)
        mainBoxSizer.Add(urlTextBox, flag = wx.LEFT, border=20)

        trckListBox = wx.BoxSizer(wx.HORIZONTAL)
        self.trackList = wx.TextCtrl(self.panel, size=(-1, 120), style = wx.TE_MULTILINE | wx.TE_DONTWRAP)
        trckListBox.Add(self.trackList, 1)
        mainBoxSizer.Add(trckListBox, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.downloadButton = wx.Button(self.panel, label='Download', size=(90, 30))
        buttonsBox.Add(self.downloadButton)
        self.updateButton = wx.Button(self.panel, label='Update', size=(90, 30))
        buttonsBox.Add(self.updateButton, flag = wx.LEFT | wx.RIGHT, border=80)
        self.optionsButton = wx.Button(self.panel, label='Options', size=(90, 30))
        buttonsBox.Add(self.optionsButton)
        mainBoxSizer.Add(buttonsBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM | wx.TOP, border=10)

        stListBox = wx.BoxSizer(wx.HORIZONTAL)
        self.statusList = ListCtrl(self.panel, style = wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        stListBox.Add(self.statusList, 1, flag = wx.EXPAND)
        mainBoxSizer.Add(stListBox, 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        stBarBox = wx.BoxSizer(wx.HORIZONTAL)
        self.statusBar = wx.StaticText(self.panel, label='Author: '+__author__)
        stBarBox.Add(self.statusBar, flag = wx.TOP | wx.BOTTOM, border=5)
        mainBoxSizer.Add(stBarBox, flag = wx.LEFT, border=20)

        self.panel.SetSizer(mainBoxSizer)

    def check_if_youtube_dl_exist(self):
        path = fix_path(self.optManager.options['youtubedl_path'])+YOUTUBE_DL_FILENAME
        if not file_exist(path):
            self.status_bar_write("Youtube-dl is missing, trying to download it...")
            self.update_youtube_dl()

    def update_youtube_dl(self):
        self.downloadButton.Disable()
        self.updateThread = UpdateThread(self.optManager.options['youtubedl_path'], YOUTUBE_DL_FILENAME)

    def status_bar_write(self, msg):
        self.statusBar.SetLabel(msg)

    def fin_task(self, msg):
        self.status_bar_write(msg)
        self.downloadButton.SetLabel('Download')
        self.updateButton.Enable()
        self.downloadThread.join()
        self.downloadThread = None
        self.downloadHandler = None
        self.urlList = []
        self.finished_popup()
        self.open_destination_dir()

    def open_destination_dir(self):
        if self.optManager.options['open_dl_dir']:
            open_dir(self.optManager.options['save_path'])

    def download_handler(self, msg):
        self.downloadHandler.handle(msg)
        if self.downloadHandler._has_closed():
            self.status_bar_write('Stoping downloads')
        if self.downloadHandler._has_finished():
            if self.downloadHandler._has_error():
                if self.logManager != None:
                    msg = 'An error occured while downloading. See Options>Log.'
                else:
                    msg = 'An error occured while downloading'
            else:
                msg = 'Done'
            self.fin_task(msg)

    def update_handler(self, msg):
        if msg.data == 'finish':
            self.downloadButton.Enable()
            self.updateThread.join()
            self.updateThread = None
        else:
            self.status_bar_write(msg.data)

    def stop_download(self):
        self.downloadThread.close()

    def load_tracklist(self, trackList):
        for url in trackList:
            url = remove_spaces(url)
            if url != '':
                self.urlList.append(url)
                self.statusList._add_item(url)

    def start_download(self):
        self.statusList._clear_list()
        self.load_tracklist(self.trackList.GetValue().split('\n'))
        if not self.statusList._is_empty():
            self.check_if_youtube_dl_exist()
            if self.updateThread is not None:
                self.updateThread.join()
            options = YoutubeDLInterpreter(self.optManager, YOUTUBE_DL_FILENAME).get_options()
            self.downloadThread = DownloadManager(
              options,
              self.statusList._get_items(),
              self.optManager.options['clear_dash_files'],
              self.logManager
            )
            self.downloadHandler = DownloadHandler(self.statusList)
            self.status_bar_write('Download started')
            self.downloadButton.SetLabel('Stop')
            self.updateButton.Disable()
        else:
            self.no_url_popup()

    def save_options(self):
        self.optManager.save_to_file()

    def finished_popup(self):
        wx.MessageBox('Downloads completed.', 'Info', wx.OK | wx.ICON_INFORMATION)

    def no_url_popup(self):
        wx.MessageBox('You need to provide at least one url.', 'Error', wx.OK | wx.ICON_EXCLAMATION)

    def OnTrackListChange(self, event):
        if self.downloadThread != None:
            ''' Get current url list from trackList textCtrl '''
            curList = self.trackList.GetValue().split('\n')
            ''' For each url in current url list '''
            for url in curList:
                ''' Remove spaces from url '''
                url = remove_spaces(url)
                ''' If url is not in self.urlList (original downloads list) and url is not empty '''
                if url not in self.urlList and url != '':
                    ''' Add url into original download list '''
                    self.urlList.append(url)
                    ''' Add handler for url '''
                    self.downloadHandler._add_empty_handler()
                    ''' Add url into statusList '''
                    self.statusList._add_item(url)
                    ''' Retrieve last item as {url:url, index:indexNo} '''
                    item = self.statusList._get_last_item()
                    ''' Pass that item into downloadThread '''
                    self.downloadThread._add_download_item(item)

    def OnDownload(self, event):
        if self.downloadThread != None:
            self.stop_download()
        else:
            self.start_download()

    def OnUpdate(self, event):
        if (self.downloadThread == None and self.updateThread == None):
            self.update_youtube_dl()

    def OnOptions(self, event):
        optionsFrame = OptionsFrame(self.optManager, parent=self, logger=self.logManager)
        optionsFrame.Show()

    def OnClose(self, event):
        if self.downloadThread != None:
            self.downloadThread.close(kill=True)
            self.downloadThread.join()
        self.save_options()
        self.Destroy()

class ListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    ''' Custom ListCtrl class '''
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
        self.ListIndex = 0

    ''' Add single item on list '''
    def _add_item(self, item):
        self.InsertStringItem(self.ListIndex, item)
        self.ListIndex += 1

    ''' Write data on index, column '''
    def _write_data(self, index, column, data):
        self.SetStringItem(index, column, data)

    ''' Clear list and set index to 0'''
    def _clear_list(self):
        self.DeleteAllItems()
        self.ListIndex = 0

    ''' Return True if list is empty '''
    def _is_empty(self):
        return self.ListIndex == 0

    ''' Get last item inserted, Returns dictionary '''
    def _get_last_item(self):
        data = {}
        last_item = self.GetItem(itemId=self.ListIndex-1, col=0)
        data['url'] = last_item.GetText()
        data['index'] = self.ListIndex-1
        return data

    ''' Retrieve all items [start, self.ListIndex), Returns list '''
    def _get_items(self, start=0):
        items = []
        for row in range(start, self.ListIndex):
            item = self.GetItem(itemId=row, col=0)
            data = {}
            data['url'] = item.GetText()
            data['index'] = row
            items.append(data)
        return items

class LogPanel(wx.Panel):

    size = ''
    path = ''
    win_box_border = 0

    def __init__(self, parent, optManager, log):
        wx.Panel.__init__(self, parent)

        self.SetBoxBorder()
        self.optManager = optManager
        self.log = log
        self.set_data()
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        enLogBox = wx.BoxSizer(wx.HORIZONTAL)
        self.enableLogChk = wx.CheckBox(self, label='Enable Log')
        enLogBox.Add(self.enableLogChk)
        mainBoxSizer.Add(enLogBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20+self.win_box_border)

        wrTimeBox = wx.BoxSizer(wx.HORIZONTAL)
        self.enableTimeChk = wx.CheckBox(self, label='Write Time')
        wrTimeBox.Add(self.enableTimeChk)
        mainBoxSizer.Add(wrTimeBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5+self.win_box_border)

        butBox = wx.BoxSizer(wx.HORIZONTAL)
        self.clearLogButton = wx.Button(self, label='Clear Log')
        butBox.Add(self.clearLogButton)
        self.viewLogButton = wx.Button(self, label='View Log')
        butBox.Add(self.viewLogButton, flag = wx.LEFT, border=20)
        mainBoxSizer.Add(butBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        if self.optManager.options['enable_log']:
            self.SetDataSizers(mainBoxSizer)

        self.SetSizer(mainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnEnable, self.enableLogChk)
        self.Bind(wx.EVT_CHECKBOX, self.OnTime, self.enableTimeChk)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clearLogButton)
        self.Bind(wx.EVT_BUTTON, self.OnView, self.viewLogButton)

    def SetBoxBorder(self):
        ''' Set border for windows '''
        if os_type == 'nt':
            self.win_box_border = 10

    def SetDataSizers(self, box):
        logPathText = wx.BoxSizer(wx.HORIZONTAL)
        logPathText.Add(wx.StaticText(self, label='Path: ' + self.path))
        box.Add(logPathText, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)
        logSizeText = wx.BoxSizer(wx.HORIZONTAL)
        self.sizeText = wx.StaticText(self, label='Log Size: ' + self.size)
        logSizeText.Add(self.sizeText)
        box.Add(logSizeText, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)

    def set_data(self):
        if self.log != None:
            self.size = str(self.log.size()) + ' Bytes'
            self.path = self.log.path

    def OnTime(self, event):
        if self.log != None:
            self.log.add_time = self.enableTimeChk.GetValue()

    def OnEnable(self, event):
        if self.enableLogChk.GetValue():
            self.enableTimeChk.Enable()
        else:
            self.enableTimeChk.Disable()
        self.restart_popup()

    def OnClear(self, event):
        if self.log != None:
            self.log.clear()
            self.sizeText.SetLabel('Log Size: 0 Bytes')

    def OnView(self, event):
        if self.log != None:
            log_gui = LogGUI(self.path, parent=self)
            log_gui.Show()

    def load_options(self):
        self.enableLogChk.SetValue(self.optManager.options['enable_log'])
        self.enableTimeChk.SetValue(self.optManager.options['log_time'])
        if self.optManager.options['enable_log'] == False:
            self.enableTimeChk.Disable()
        if self.log == None:
            self.clearLogButton.Disable()
            self.viewLogButton.Disable()

    def save_options(self):
        self.optManager.options['enable_log'] = self.enableLogChk.GetValue()
        self.optManager.options['log_time'] = self.enableTimeChk.GetValue()

    def restart_popup(self):
        wx.MessageBox('Please restart ' + __appname__, 'Restart', wx.OK | wx.ICON_INFORMATION)

class PlaylistPanel(wx.Panel):

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self, parent)

        self.optManager = optManager
        mainBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self, label='Playlist Options'), wx.VERTICAL)

        mainBoxSizer.Add((-1, 10))

        startBox = wx.BoxSizer(wx.HORIZONTAL)
        startBox.Add(wx.StaticText(self, label='Start'), flag = wx.RIGHT, border=32)
        self.startSpnr = wx.SpinCtrl(self, size=(60, -1))
        self.startSpnr.SetRange(1, 999)
        startBox.Add(self.startSpnr)
        mainBoxSizer.Add(startBox, flag = wx.TOP | wx.LEFT, border=20)

        stopBox = wx.BoxSizer(wx.HORIZONTAL)
        stopBox.Add(wx.StaticText(self, label='Stop'), flag = wx.RIGHT, border=34)
        self.stopSpnr = wx.SpinCtrl(self, size=(60, -1))
        self.stopSpnr.SetRange(0, 999)
        stopBox.Add(self.stopSpnr)
        mainBoxSizer.Add(stopBox, flag = wx.TOP | wx.LEFT, border=20)

        maxBox = wx.BoxSizer(wx.HORIZONTAL)
        maxBox.Add(wx.StaticText(self, label='Max DLs'), flag = wx.RIGHT, border=self.get_border())
        self.maxSpnr = wx.SpinCtrl(self, size=(60, -1))
        self.maxSpnr.SetRange(0, 999)
        maxBox.Add(self.maxSpnr)
        mainBoxSizer.Add(maxBox, flag = wx.TOP | wx.LEFT, border=20)

        self.SetSizer(mainBoxSizer)

    def get_border(self):
        if os_type == 'nt':
            return 16
        return 10

    def load_options(self):
        self.startSpnr.SetValue(self.optManager.options['playlist_start'])
        self.stopSpnr.SetValue(self.optManager.options['playlist_end'])
        self.maxSpnr.SetValue(self.optManager.options['max_downloads'])

    def save_options(self):
        self.optManager.options['playlist_start'] = self.startSpnr.GetValue()
        self.optManager.options['playlist_end'] = self.stopSpnr.GetValue()
        self.optManager.options['max_downloads'] = self.maxSpnr.GetValue()

class ConnectionPanel(wx.Panel):

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self, parent)

        self.optManager = optManager
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        retBox = wx.BoxSizer(wx.HORIZONTAL)
        retBox.Add(wx.StaticText(self, label='Retries'), flag = wx.RIGHT, border=8)
        self.retriesSpnr = wx.SpinCtrl(self, size=(50, -1))
        self.retriesSpnr.SetRange(1, 99)
        retBox.Add(self.retriesSpnr)
        mainBoxSizer.Add(retBox, flag = wx.LEFT | wx.TOP, border=10)

        uaText = wx.BoxSizer(wx.HORIZONTAL)
        uaText.Add(wx.StaticText(self, label='User Agent'), flag = wx.LEFT, border=15)
        mainBoxSizer.Add(uaText, flag = wx.TOP, border=10)

        mainBoxSizer.Add((-1, 5))

        uaBox = wx.BoxSizer(wx.HORIZONTAL)
        self.userAgentBox = wx.TextCtrl(self)
        uaBox.Add(self.userAgentBox, 1, flag = wx.LEFT, border=10)
        mainBoxSizer.Add(uaBox, flag = wx.EXPAND | wx.RIGHT, border=200)

        refText = wx.BoxSizer(wx.HORIZONTAL)
        refText.Add(wx.StaticText(self, label='Referer'), flag = wx.LEFT, border=15)
        mainBoxSizer.Add(refText, flag = wx.TOP, border=10)

        mainBoxSizer.Add((-1, 5))

        refBox = wx.BoxSizer(wx.HORIZONTAL)
        self.refererBox = wx.TextCtrl(self)
        refBox.Add(self.refererBox, 1, flag = wx.LEFT, border=10)
        mainBoxSizer.Add(refBox, flag = wx.EXPAND | wx.RIGHT, border=200)

        prxyText = wx.BoxSizer(wx.HORIZONTAL)
        prxyText.Add(wx.StaticText(self, label='Proxy'), flag = wx.LEFT, border=15)
        mainBoxSizer.Add(prxyText, flag = wx.TOP, border=10)

        mainBoxSizer.Add((-1, 5))

        prxyBox = wx.BoxSizer(wx.HORIZONTAL)
        self.proxyBox = wx.TextCtrl(self)
        prxyBox.Add(self.proxyBox, 1, flag = wx.LEFT, border=10)
        mainBoxSizer.Add(prxyBox, flag = wx.EXPAND | wx.RIGHT, border=100)

        self.SetSizer(mainBoxSizer)

    def load_options(self):
        self.userAgentBox.SetValue(self.optManager.options['user_agent'])
        self.refererBox.SetValue(self.optManager.options['referer'])
        self.proxyBox.SetValue(self.optManager.options['proxy'])
        self.retriesSpnr.SetValue(self.optManager.options['retries'])

    def save_options(self):
        self.optManager.options['user_agent'] = self.userAgentBox.GetValue()
        self.optManager.options['referer'] = self.refererBox.GetValue()
        self.optManager.options['proxy'] = self.proxyBox.GetValue()
        self.optManager.options['retries'] = self.retriesSpnr.GetValue()

class AuthenticationPanel(wx.Panel):

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self,parent)

        self.optManager = optManager
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        usrTextBox = wx.BoxSizer(wx.HORIZONTAL)
        usrTextBox.Add(wx.StaticText(self, label='Username'))
        mainBoxSizer.Add(usrTextBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        usrBox = wx.BoxSizer(wx.HORIZONTAL)
        self.usernameBox = wx.TextCtrl(self, size=(-1, 25))
        usrBox.Add(self.usernameBox, 1, flag = wx.TOP, border=5)
        mainBoxSizer.Add(usrBox, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border=160)

        passTextBox = wx.BoxSizer(wx.HORIZONTAL)
        passTextBox.Add(wx.StaticText(self, label='Password'))
        mainBoxSizer.Add(passTextBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        passBox = wx.BoxSizer(wx.HORIZONTAL)
        self.passwordBox = wx.TextCtrl(self, size=(-1, 25), style = wx.TE_PASSWORD)
        passBox.Add(self.passwordBox, 1, flag = wx.TOP, border=5)
        mainBoxSizer.Add(passBox, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border=160)

        vPassTextBox = wx.BoxSizer(wx.HORIZONTAL)
        vPassTextBox.Add(wx.StaticText(self, label='Video Password (vimeo, smotri)'))
        mainBoxSizer.Add(vPassTextBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15)

        vPassBox = wx.BoxSizer(wx.HORIZONTAL)
        self.videopassBox = wx.TextCtrl(self, size=(-1, 25), style = wx.TE_PASSWORD)
        vPassBox.Add(self.videopassBox, 1, flag = wx.TOP, border=5)
        mainBoxSizer.Add(vPassBox, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border=160)

        self.SetSizer(mainBoxSizer)

    def load_options(self):
        self.usernameBox.SetValue(self.optManager.options['username'])
        self.passwordBox.SetValue(self.optManager.options['password'])
        self.videopassBox.SetValue(self.optManager.options['video_password'])

    def save_options(self):
        self.optManager.options['username'] = self.usernameBox.GetValue()
        self.optManager.options['password'] = self.passwordBox.GetValue()
        self.optManager.options['video_password'] = self.videopassBox.GetValue()

class AudioPanel(wx.Panel):

    win_box_border = 0
    quality = ['high', 'mid', 'low']

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self, parent)

        self.SetBoxBorder()
        self.optManager = optManager
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        toaBox = wx.BoxSizer(wx.HORIZONTAL)
        self.toAudioChk = wx.CheckBox(self, label='Convert to Audio')
        toaBox.Add(self.toAudioChk)
        mainBoxSizer.Add(toaBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=15+self.win_box_border)

        keepVBox = wx.BoxSizer(wx.HORIZONTAL)
        self.keepVideoChk = wx.CheckBox(self, label='Keep Video')
        keepVBox.Add(self.keepVideoChk)
        mainBoxSizer.Add(keepVBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5+self.win_box_border)

        afTextBox = wx.BoxSizer(wx.HORIZONTAL)
        afTextBox.Add(wx.StaticText(self, label='Audio Format'))
        mainBoxSizer.Add(afTextBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)

        afComboBox = wx.BoxSizer(wx.HORIZONTAL)
        self.audioFormatCombo = wx.ComboBox(self, choices=AUDIOFORMATS, size=(160, 30))
        afComboBox.Add(self.audioFormatCombo)
        mainBoxSizer.Add(afComboBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        aqTextBox = wx.BoxSizer(wx.HORIZONTAL)
        aqTextBox.Add(wx.StaticText(self, label='Audio Quality'))
        mainBoxSizer.Add(aqTextBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)

        aqComboBox = wx.BoxSizer(wx.HORIZONTAL)
        self.audioQualityCombo = wx.ComboBox(self, choices=self.quality, size=(80, 25))
        aqComboBox.Add(self.audioQualityCombo)
        mainBoxSizer.Add(aqComboBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        self.SetSizer(mainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnAudioCheck, self.toAudioChk)

    def SetBoxBorder(self):
        ''' Set border for windows '''
        if os_type == 'nt':
            self.win_box_border = 5

    def OnAudioCheck(self, event):
        if self.toAudioChk.GetValue():
            self.keepVideoChk.Enable()
            self.audioFormatCombo.Enable()
            self.audioQualityCombo.Enable()
        else:
            self.keepVideoChk.Disable()
            self.audioFormatCombo.Disable()
            self.audioQualityCombo.Disable()

    def load_options(self):
        self.toAudioChk.SetValue(self.optManager.options['to_audio'])
        self.keepVideoChk.SetValue(self.optManager.options['keep_video'])
        self.audioFormatCombo.SetValue(self.optManager.options['audio_format'])
        self.audioQualityCombo.SetValue(self.optManager.options['audio_quality'])
        if self.optManager.options['to_audio'] == False:
            self.keepVideoChk.Disable()
            self.audioFormatCombo.Disable()
            self.audioQualityCombo.Disable()

    def save_options(self):
        self.optManager.options['to_audio'] = self.toAudioChk.GetValue()
        self.optManager.options['keep_video'] = self.keepVideoChk.GetValue()
        self.optManager.options['audio_format'] = self.audioFormatCombo.GetValue()
        self.optManager.options['audio_quality'] = self.audioQualityCombo.GetValue()

class VideoPanel(wx.Panel):

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self, parent)

        self.optManager = optManager
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        vfTextBox = wx.BoxSizer(wx.HORIZONTAL)
        vfTextBox.Add(wx.StaticText(self, label='Video Format'))
        mainBoxSizer.Add(vfTextBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        vfComboBox = wx.BoxSizer(wx.HORIZONTAL)
        self.videoFormatCombo = wx.ComboBox(self, choices=VIDEOFORMATS, size=(160, 30))
        vfComboBox.Add(self.videoFormatCombo)
        mainBoxSizer.Add(vfComboBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        daTextBox = wx.BoxSizer(wx.HORIZONTAL)
        daTextBox.Add(wx.StaticText(self, label='DASH Audio'))
        mainBoxSizer.Add(daTextBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)

        daComboBox = wx.BoxSizer(wx.HORIZONTAL)
        self.dashAudioFormatCombo = wx.ComboBox(self, choices=DASH_AUDIO_FORMATS, size=(160, 30))
        daComboBox.Add(self.dashAudioFormatCombo)
        mainBoxSizer.Add(daComboBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=5)

        clrDashBox = wx.BoxSizer(wx.HORIZONTAL)
        self.clearDashFilesChk = wx.CheckBox(self, label='Clear DASH audio/video files')
        clrDashBox.Add(self.clearDashFilesChk)
        mainBoxSizer.Add(clrDashBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        self.SetSizer(mainBoxSizer)

        self.Bind(wx.EVT_COMBOBOX, self.OnVideoFormatPick, self.videoFormatCombo)
        self.Bind(wx.EVT_COMBOBOX, self.OnAudioFormatPick, self.dashAudioFormatCombo)

    def OnAudioFormatPick(self, event):
        if have_dash_audio(self.dashAudioFormatCombo.GetValue()):
            self.clearDashFilesChk.Enable()
        else:
            self.clearDashFilesChk.SetValue(False)
            self.clearDashFilesChk.Disable()

    def OnVideoFormatPick(self, event):
        if video_is_dash(self.videoFormatCombo.GetValue()):
            self.dashAudioFormatCombo.Enable()
            if have_dash_audio(self.dashAudioFormatCombo.GetValue()):
                self.clearDashFilesChk.Enable()
        else:
            self.clearDashFilesChk.SetValue(False)
            self.clearDashFilesChk.Disable()
            self.dashAudioFormatCombo.Disable()

    def load_options(self):
        self.videoFormatCombo.SetValue(self.optManager.options['video_format'])
        self.dashAudioFormatCombo.SetValue(self.optManager.options['dash_audio_format'])
        self.clearDashFilesChk.SetValue(self.optManager.options['clear_dash_files'])
        if not video_is_dash(self.optManager.options['video_format']):
            self.dashAudioFormatCombo.Disable()
        if not have_dash_audio(self.optManager.options['dash_audio_format']):
            self.clearDashFilesChk.SetValue(False)
            self.clearDashFilesChk.Disable()

    def save_options(self):
        self.optManager.options['video_format'] = self.videoFormatCombo.GetValue()
        self.optManager.options['dash_audio_format'] = self.dashAudioFormatCombo.GetValue()
        self.optManager.options['clear_dash_files'] = self.clearDashFilesChk.GetValue()

class OutputPanel(wx.Panel):

    win_box_border = 0

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self, parent)

        self.SetBoxBorder()
        self.optManager = optManager
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        idBox = wx.BoxSizer(wx.HORIZONTAL)
        self.idAsNameChk = wx.CheckBox(self, label='ID as Name')
        idBox.Add(self.idAsNameChk, flag = wx.LEFT, border=5)
        mainBoxSizer.Add(idBox, flag = wx.TOP, border=15)

        titleBox = wx.BoxSizer(wx.HORIZONTAL)
        self.titleBoxChk = wx.CheckBox(self, label='Title as Name')
        titleBox.Add(self.titleBoxChk, flag = wx.LEFT, border=5)
        mainBoxSizer.Add(titleBox, flag = wx.TOP, border=5+self.win_box_border)

        customChkBox = wx.BoxSizer(wx.HORIZONTAL)
        self.customTitleChk = wx.CheckBox(self, label='Custom Template (youtube-dl)')
        customChkBox.Add(self.customTitleChk, flag = wx.LEFT, border=5)
        mainBoxSizer.Add(customChkBox, flag = wx.TOP, border=5+self.win_box_border)

        mainBoxSizer.Add((-1, 10))

        customBox = wx.BoxSizer(wx.HORIZONTAL)
        self.customTitleBox = wx.TextCtrl(self)
        customBox.Add(self.customTitleBox, 1, flag = wx.RIGHT, border=300)
        mainBoxSizer.Add(customBox, flag = wx.EXPAND | wx.LEFT, border=5)

        self.SetSizer(mainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnId, self.idAsNameChk)
        self.Bind(wx.EVT_CHECKBOX, self.OnTitle, self.titleBoxChk)
        self.Bind(wx.EVT_CHECKBOX, self.OnCustom, self.customTitleChk)

    def OnId(self, event):
        self.group_load('id')

    def OnTitle(self, event):
        self.group_load('title')

    def OnCustom(self, event):
        self.group_load('custom')

    def SetBoxBorder(self):
        ''' Set border for windows '''
        if os_type == 'nt':
            self.win_box_border = 10

    def group_load(self, oformat):
        if oformat == 'id':
            self.idAsNameChk.SetValue(True)
            self.titleBoxChk.SetValue(False)
            self.customTitleChk.SetValue(False)
            self.customTitleBox.Disable()
        elif oformat == 'title':
            self.idAsNameChk.SetValue(False)
            self.titleBoxChk.SetValue(True)
            self.customTitleChk.SetValue(False)
            self.customTitleBox.Disable()
        elif oformat == 'custom':
            self.idAsNameChk.SetValue(False)
            self.titleBoxChk.SetValue(False)
            self.customTitleChk.SetValue(True)
            self.customTitleBox.Enable()

    def get_output_format(self):
        if self.idAsNameChk.GetValue():
            return 'id'
        elif self.titleBoxChk.GetValue():
            return 'title'
        elif self.customTitleChk.GetValue():
            return 'custom'

    def load_options(self):
        self.group_load(self.optManager.options['output_format'])
        self.customTitleBox.SetValue(self.optManager.options['output_template'])

    def save_options(self):
        self.optManager.options['output_template'] = self.customTitleBox.GetValue()
        self.optManager.options['output_format'] = self.get_output_format()

class FilesystemPanel(wx.Panel):

    win_box_border = 0

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self, parent)

        self.SetBoxBorder()
        self.optManager = optManager
        mainBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftBoxSizer = wx.BoxSizer(wx.VERTICAL)
        rightBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self, label='Filesize (e.g. 50k or 44.6m)'), wx.VERTICAL)

        self.SetLeftBox(leftBoxSizer)
        self.SetRightBox(rightBoxSizer)

        mainBoxSizer.Add(leftBoxSizer, 1, flag = wx.EXPAND | wx.ALL, border=10)
        mainBoxSizer.Add(rightBoxSizer, 1, flag = wx.EXPAND | wx.ALL, border=10)

        self.SetSizer(mainBoxSizer)

    def SetBoxBorder(self):
        ''' Set border for windows '''
        if os_type == 'nt':
            self.win_box_border = 10

    def SetLeftBox(self, box):
        ignrBox = wx.BoxSizer(wx.HORIZONTAL)
        self.ignoreErrorsChk = wx.CheckBox(self, label='Ignore Errors')
        ignrBox.Add(self.ignoreErrorsChk, flag = wx.LEFT, border=5)
        box.Add(ignrBox, flag = wx.TOP, border=15)

        wrtDescBox = wx.BoxSizer(wx.HORIZONTAL)
        self.writeDescriptionChk = wx.CheckBox(self, label='Write description to file')
        wrtDescBox.Add(self.writeDescriptionChk, flag = wx.LEFT, border=5)
        box.Add(wrtDescBox, flag = wx.TOP, border=5+self.win_box_border)

        wrtInfoBox = wx.BoxSizer(wx.HORIZONTAL)
        self.writeInfoChk = wx.CheckBox(self, label='Write info to (.json) file')
        wrtInfoBox.Add(self.writeInfoChk, flag = wx.LEFT, border=5)
        box.Add(wrtInfoBox, flag = wx.TOP, border=5+self.win_box_border)

        wrtThumBox = wx.BoxSizer(wx.HORIZONTAL)
        self.writeThumbnailChk = wx.CheckBox(self, label='Write thumbnail to disk')
        wrtThumBox.Add(self.writeThumbnailChk, flag = wx.LEFT, border=5)
        box.Add(wrtThumBox, flag = wx.TOP, border=5+self.win_box_border)

        openDirBox = wx.BoxSizer(wx.HORIZONTAL)
        self.openDirChk = wx.CheckBox(self, label='Open destination folder when done')
        openDirBox.Add(self.openDirChk, flag = wx.LEFT, border=5)
        box.Add(openDirBox, flag = wx.TOP, border=5+self.win_box_border)

    def SetRightBox(self, box):
        minBox = wx.BoxSizer(wx.HORIZONTAL)
        minBox.Add(wx.StaticText(self, label='Min'), flag = wx.RIGHT, border=12)
        self.minFilesizeBox = wx.TextCtrl(self, size=(80, -1))
        minBox.Add(self.minFilesizeBox)
        box.Add(minBox, flag = wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, border=10)

        maxBox = wx.BoxSizer(wx.HORIZONTAL)
        maxBox.Add(wx.StaticText(self, label='Max'), flag = wx.RIGHT, border=8)
        self.maxFilesizeBox = wx.TextCtrl(self, size=(80, -1))
        maxBox.Add(self.maxFilesizeBox)
        box.Add(maxBox, flag = wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, border=10)

    def load_options(self):
        self.writeDescriptionChk.SetValue(self.optManager.options['write_description'])
        self.writeInfoChk.SetValue(self.optManager.options['write_info'])
        self.writeThumbnailChk.SetValue(self.optManager.options['write_thumbnail'])
        self.ignoreErrorsChk.SetValue(self.optManager.options['ignore_errors'])
        self.openDirChk.SetValue(self.optManager.options['open_dl_dir'])
        self.minFilesizeBox.SetValue(self.optManager.options['min_filesize'])
        self.maxFilesizeBox.SetValue(self.optManager.options['max_filesize'])

    def save_options(self):
        self.optManager.options['write_description'] = self.writeDescriptionChk.GetValue()
        self.optManager.options['write_info'] = self.writeInfoChk.GetValue()
        self.optManager.options['write_thumbnail'] = self.writeThumbnailChk.GetValue()
        self.optManager.options['ignore_errors'] = self.ignoreErrorsChk.GetValue()
        self.optManager.options['open_dl_dir'] = self.openDirChk.GetValue()
        self.optManager.options['min_filesize'] = self.minFilesizeBox.GetValue()
        self.optManager.options['max_filesize'] = self.maxFilesizeBox.GetValue()
        self.check_input()

    def check_input(self):
        self.optManager.options['min_filesize'].replace('-', '')
        self.optManager.options['max_filesize'].replace('-', '')
        if self.optManager.options['min_filesize'] == '':
            self.optManager.options['min_filesize'] = '0'
        if self.optManager.options['max_filesize'] == '':
            self.optManager.options['max_filesize'] = '0'

class SubtitlesPanel(wx.Panel):

    win_box_border = 0

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self, parent)

        self.SetBoxBorder()
        self.optManager = optManager
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        dlSubsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.writeSubsChk = wx.CheckBox(self, label='Download subtitle file by language')
        dlSubsBox.Add(self.writeSubsChk, flag = wx.LEFT, border=10)
        mainBoxSizer.Add(dlSubsBox, flag = wx.TOP, border=15)

        dlAllSubBox = wx.BoxSizer(wx.HORIZONTAL)
        self.writeAllSubsChk = wx.CheckBox(self, label='Download all available subtitles')
        dlAllSubBox.Add(self.writeAllSubsChk, flag = wx.LEFT, border=10)
        mainBoxSizer.Add(dlAllSubBox, flag = wx.TOP, border=5+self.win_box_border)

        dlAutoSubBox = wx.BoxSizer(wx.HORIZONTAL)
        self.writeAutoSubsChk = wx.CheckBox(self, label='Download automatic subtitle file (YOUTUBE ONLY)')
        dlAutoSubBox.Add(self.writeAutoSubsChk, flag = wx.LEFT, border=10)
        mainBoxSizer.Add(dlAutoSubBox, flag = wx.TOP, border=5+self.win_box_border)

        embSubBox = wx.BoxSizer(wx.HORIZONTAL)
        self.embedSubsChk = wx.CheckBox(self, label='Embed subtitles in the video (only for mp4 videos)')
        self.embedSubsChk.Disable()
        embSubBox.Add(self.embedSubsChk, flag = wx.LEFT, border=10)
        mainBoxSizer.Add(embSubBox, flag = wx.TOP, border=5+self.win_box_border)

        slangTextBox = wx.BoxSizer(wx.HORIZONTAL)
        slangTextBox.Add(wx.StaticText(self, label='Subtitles Language'), flag = wx.LEFT, border=15)
        mainBoxSizer.Add(slangTextBox, flag = wx.TOP, border=10+self.win_box_border)

        slangBox = wx.BoxSizer(wx.HORIZONTAL)
        self.subsLangCombo = wx.ComboBox(self, choices=LANGUAGES, size=(140, 30))
        slangBox.Add(self.subsLangCombo, flag = wx.LEFT, border=10)
        mainBoxSizer.Add(slangBox, flag = wx.TOP, border=5)

        self.SetSizer(mainBoxSizer)

        self.Bind(wx.EVT_CHECKBOX, self.OnWriteSubsChk, self.writeSubsChk)
        self.Bind(wx.EVT_CHECKBOX, self.OnWriteAllSubsChk, self.writeAllSubsChk)
        self.Bind(wx.EVT_CHECKBOX, self.OnWriteAutoSubsChk, self.writeAutoSubsChk)

    def SetBoxBorder(self):
        ''' Set border for windows '''
        if os_type == 'nt':
            self.win_box_border = 5

    def subs_are_on(self):
        return self.writeAutoSubsChk.GetValue() or self.writeSubsChk.GetValue()

    def OnWriteAutoSubsChk(self, event):
        if self.writeAutoSubsChk.GetValue():
            self.writeAllSubsChk.Disable()
            self.writeSubsChk.Disable()
            self.subsLangCombo.Disable()
            self.embedSubsChk.Enable()
        else:
            self.writeAllSubsChk.Enable()
            self.writeSubsChk.Enable()
            self.subsLangCombo.Enable()
            self.embedSubsChk.Disable()
            self.embedSubsChk.SetValue(False)

    def OnWriteSubsChk(self, event):
        if self.writeSubsChk.GetValue():
            self.writeAllSubsChk.Disable()
            self.writeAutoSubsChk.Disable()
            self.embedSubsChk.Enable()
        else:
            self.writeAllSubsChk.Enable()
            self.writeAutoSubsChk.Enable()
            self.embedSubsChk.Disable()
            self.embedSubsChk.SetValue(False)

    def OnWriteAllSubsChk(self, event):
        if self.writeAllSubsChk.GetValue():
            self.writeSubsChk.Disable()
            self.subsLangCombo.Disable()
            self.writeAutoSubsChk.Disable()
        else:
            self.writeSubsChk.Enable()
            self.subsLangCombo.Enable()
            self.writeAutoSubsChk.Enable()

    def load_options(self):
        self.writeSubsChk.Enable()
        self.subsLangCombo.Enable()
        self.writeAllSubsChk.Enable()
        self.writeAutoSubsChk.Enable()
        self.writeSubsChk.SetValue(self.optManager.options['write_subs'])
        self.writeAllSubsChk.SetValue(self.optManager.options['write_all_subs'])
        self.subsLangCombo.SetValue(self.optManager.options['subs_lang'])
        self.writeAutoSubsChk.SetValue(self.optManager.options['write_auto_subs'])
        self.embedSubsChk.SetValue(self.optManager.options['embed_subs'])
        if self.optManager.options['write_subs']:
            self.writeAllSubsChk.Disable()
            self.writeAutoSubsChk.Disable()
            self.embedSubsChk.Enable()
        if self.optManager.options['write_all_subs']:
            self.writeSubsChk.Disable()
            self.subsLangCombo.Disable()
            self.writeAutoSubsChk.Disable()
        if self.optManager.options['write_auto_subs']:
            self.writeAllSubsChk.Disable()
            self.writeSubsChk.Disable()
            self.subsLangCombo.Disable()
            self.embedSubsChk.Enable()
        if not self.subs_are_on():
            self.embedSubsChk.Disable()

    def save_options(self):
        self.optManager.options['write_subs'] = self.writeSubsChk.GetValue()
        self.optManager.options['write_all_subs'] = self.writeAllSubsChk.GetValue()
        self.optManager.options['subs_lang'] = self.subsLangCombo.GetValue()
        self.optManager.options['write_auto_subs'] = self.writeAutoSubsChk.GetValue()
        self.optManager.options['embed_subs'] = self.embedSubsChk.GetValue()

class GeneralPanel(wx.Panel):

    def __init__(self, parent, optManager, resetHandler):
        wx.Panel.__init__(self, parent)

        self.optManager = optManager
        self.resetHandler = resetHandler
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        svTextBox = wx.BoxSizer(wx.HORIZONTAL)
        svTextBox.Add(wx.StaticText(self, label='Save Path'))
        mainBoxSizer.Add(svTextBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        svPathBox = wx.BoxSizer(wx.HORIZONTAL)
        self.savePathBox = wx.TextCtrl(self)
        svPathBox.Add(self.savePathBox, 1, flag = wx.TOP, border=10)
        mainBoxSizer.Add(svPathBox, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border=40)

        buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.aboutButton = wx.Button(self, label='About', size=(110, 40))
        buttonsBox.Add(self.aboutButton)
        self.openButton = wx.Button(self, label='Open', size=(110, 40))
        buttonsBox.Add(self.openButton, flag = wx.LEFT | wx.RIGHT, border=50)
        self.resetButton = wx.Button(self, label='Reset Options', size=(110, 40))
        buttonsBox.Add(self.resetButton)
        mainBoxSizer.Add(buttonsBox, flag = wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=20)

        setngsBox = wx.BoxSizer(wx.HORIZONTAL)
        text = 'Settings: ' + self.optManager.settings_abs_path
        setngsBox.Add(wx.StaticText(self, label=text), flag = wx.TOP, border=30)
        mainBoxSizer.Add(setngsBox, flag = wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(mainBoxSizer)

        self.Bind(wx.EVT_BUTTON, self.OnAbout, self.aboutButton)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.openButton)
        self.Bind(wx.EVT_BUTTON, self.OnReset, self.resetButton)

    def OnReset(self, event):
        self.resetHandler()

    def OnOpen(self, event):
        dlg = wx.DirDialog(None, "Choose directory")
        if dlg.ShowModal() == wx.ID_OK:
            self.savePathBox.SetValue(dlg.GetPath())
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
        self.savePathBox.SetValue(self.optManager.options['save_path'])

    def save_options(self):
        self.optManager.options['save_path'] = fix_path(self.savePathBox.GetValue())

class OtherPanel(wx.Panel):

    def __init__(self, parent, optManager):
        wx.Panel.__init__(self, parent)

        self.optManager = optManager
        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        textBox = wx.BoxSizer(wx.HORIZONTAL)
        textBox.Add(wx.StaticText(self, label='Command line arguments (e.g. --help)'), flag = wx.TOP, border=30)
        mainBoxSizer.Add(textBox, flag = wx.LEFT, border=50)

        inputBox = wx.BoxSizer(wx.HORIZONTAL)
        self.cmdArgsBox = wx.TextCtrl(self)
        inputBox.Add(self.cmdArgsBox, 1, flag = wx.TOP, border=10)
        mainBoxSizer.Add(inputBox, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border=50)

        self.SetSizer(mainBoxSizer)

    def load_options(self):
        self.cmdArgsBox.SetValue(self.optManager.options['cmd_args'])

    def save_options(self):
        self.optManager.options['cmd_args'] = self.cmdArgsBox.GetValue()

class OptionsFrame(wx.Frame):

    def __init__(self, optManager, parent=None, id=-1, logger=None):
        wx.Frame.__init__(self, parent, id, "Options", size=self.SetFrameSizer())

        self.optManager = optManager

        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)

        self.generalTab = GeneralPanel(notebook, self.optManager, self.reset)
        self.audioTab = AudioPanel(notebook, self.optManager)
        self.connectionTab = ConnectionPanel(notebook, self.optManager)
        self.videoTab = VideoPanel(notebook, self.optManager)
        self.filesysTab = FilesystemPanel(notebook, self.optManager)
        self.subtitlesTab = SubtitlesPanel(notebook, self.optManager)
        self.otherTab = OtherPanel(notebook, self.optManager)
        self.authTab = AuthenticationPanel(notebook, self.optManager)
        self.videoselTab = PlaylistPanel(notebook, self.optManager)
        self.logTab = LogPanel(notebook, self.optManager, logger)
        self.outputTab = OutputPanel(notebook, self.optManager)

        notebook.AddPage(self.generalTab, "General")
        notebook.AddPage(self.videoTab, "Video")
        notebook.AddPage(self.audioTab, "Audio")
        notebook.AddPage(self.outputTab, "Output")
        notebook.AddPage(self.videoselTab, "Playlist")
        notebook.AddPage(self.subtitlesTab, "Subtitles")
        notebook.AddPage(self.filesysTab, "Filesystem")
        notebook.AddPage(self.connectionTab, "Connection")
        notebook.AddPage(self.authTab, "Authentication")
        notebook.AddPage(self.logTab, "Log")
        notebook.AddPage(self.otherTab, "Commands")

        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.load_all_options()

    def SetFrameSizer(self):
        if os_type == 'nt':
            return (580, 270)
        else:
            return (580, 250)

    def OnClose(self, event):
        self.save_all_options()
        self.Destroy()

    def reset(self):
        self.optManager.load_default()
        self.load_all_options()

    def load_all_options(self):
        self.generalTab.load_options()
        self.audioTab.load_options()
        self.connectionTab.load_options()
        self.videoTab.load_options()
        self.filesysTab.load_options()
        self.subtitlesTab.load_options()
        self.otherTab.load_options()
        self.authTab.load_options()
        self.videoselTab.load_options()
        self.logTab.load_options()
        self.outputTab.load_options()

    def save_all_options(self):
        self.generalTab.save_options()
        self.audioTab.save_options()
        self.connectionTab.save_options()
        self.videoTab.save_options()
        self.filesysTab.save_options()
        self.subtitlesTab.save_options()
        self.otherTab.save_options()
        self.authTab.save_options()
        self.videoselTab.save_options()
        self.logTab.save_options()
        self.outputTab.save_options()
