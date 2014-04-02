#! /usr/bin/env python

''' 
This file contains all gui classes
MainFrame
Custom wx.ListCtrl class
OptionsFrame
  GeneralPanel
  AudioPanel
  ConnectionPanel
  VideoPanel
  FilesystemPanel
  SubtitlesPanel
  OtherPanel
  UpdatePanel
  AuthenticationPanel
  PlaylistPanel
'''

import wx
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .version import __version__
from .UpdateThread import UpdateThread
from .DownloadThread import DownloadManager
from .OptionsHandler import OptionsHandler
from .YoutubeDLInterpreter import YoutubeDLInterpreter
from .SignalHandler import DownloadHandler
from .LogManager import LogManager, LogGUI
from .Utils import (
  video_is_dash,
  have_dash_audio,
  get_os_type,
  file_exist,
  fix_path,
  get_abs_path,
  get_icon_path
)

if get_os_type() == 'nt':
  YOUTUBE_DL_FILENAME = 'youtube-dl.exe'
else:
  YOUTUBE_DL_FILENAME = 'youtube-dl'

TITLE = 'Youtube-dlG'

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
	     
ICON = get_icon_path(['ytube.png', 'icons'], __file__)
  
class MainFrame(wx.Frame):
  
  def __init__(self, parent=None, id=-1):
    wx.Frame.__init__(self, parent, id, TITLE+' '+__version__, size=(600, 410), style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
    
    # set sizers for status box (Windows & Linux)
    statusListSizer, statusBarSizer = self.set_sizers()
    
    # create panel, trackList, statusBox using global statusBoxSizer
    self.panel = wx.Panel(self)
    wx.StaticText(self.panel, -1, "URLs", (15, 10))
    self.trackList = wx.TextCtrl(self.panel, -1, pos=(10, 25), size=(580, 110), style = wx.TE_MULTILINE | wx.TE_DONTWRAP)
    self.statusList = ListCtrl(self.panel, -1, pos=(10, 190), size=statusListSizer, style = wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
    self.statusBar = wx.StaticText(self.panel, -1, 'Author: Sotiris Papadopoulos', pos=statusBarSizer)
    
    # create buttons
    self.downloadButton = wx.Button(self.panel, label="Download", pos=(100, 145), size=(-1, 30))
    self.updateButton = wx.Button(self.panel, label="Update", pos=(250, 145), size=(-1, 30))
    self.optionsButton = wx.Button(self.panel, label="Options", pos=(390, 145), size=(-1, 30))
    
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
    self.optionsList = OptionsHandler(self.status_bar_write)
    self.downloadHandler = None
    
    # init log manager
    self.logManager = None
    if self.optionsList.enableLog:
      self.logManager = LogManager(
	self.optionsList.get_config_path(),
	self.optionsList.writeTimeToLog
      )
    
    # init some thread variables
    self.downloadThread = None
    self.updateThread = None
    
    # init urlList for evt_text on self.trackList
    self.urlList = []
    
    # check & update libraries (youtube-dl)
    self.check_if_youtube_dl_exist()
    if (self.optionsList.autoUpdate):
      self.status_bar_write("Auto update enable")
      self.update_youtube_dl()
  
  def set_sizers(self):
    if get_os_type() == 'nt':
      statusListSizer = (580, 165)
      statusBarSizer = (15, 365)
    else:
      statusListSizer = (580, 195)
      statusBarSizer = (15, 390)
    return statusListSizer, statusBarSizer
  
  def check_if_youtube_dl_exist(self):
    path = fix_path(self.optionsList.updatePath)+YOUTUBE_DL_FILENAME
    if not file_exist(path):
      self.status_bar_write("Youtube-dl is missing, trying to download it...")
      self.update_youtube_dl()
  
  def update_youtube_dl(self):
    self.downloadButton.Disable()
    self.updateThread = UpdateThread(self.optionsList.updatePath, YOUTUBE_DL_FILENAME)
  
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
      if url != '':
	self.urlList.append(url)
	self.statusList._add_item(url)
  
  def start_download(self):
    self.statusList._clear_list()
    self.load_tracklist(self.trackList.GetValue().split('\n'))
    if not self.statusList._is_empty():
      options = YoutubeDLInterpreter(self.optionsList, YOUTUBE_DL_FILENAME).get_options()
      self.downloadThread = DownloadManager(
	options,
	self.statusList._get_items(),
	self.optionsList.clearDashFiles,
	self.logManager
      )
      self.downloadHandler = DownloadHandler(self.statusList)
      self.status_bar_write('Download started')
      self.downloadButton.SetLabel('Stop')
      self.updateButton.Disable()
    else:
      self.no_url_popup()
  
  def save_options(self):
    self.optionsList.save_to_file()
  
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
	''' If url is not in self.urlList (original downloads list) and url is not empty '''
	if url not in self.urlList and url != '':
	  ''' Add url into original download list '''
	  self.urlList.append(url)
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
    optionsFrame = OptionsFrame(self.optionsList, parent=self, logger=self.logManager)
    optionsFrame.Show()
  
  def OnClose(self, event):
    self.save_options()
    self.Destroy()

class ListCtrl(wx.ListCtrl):
  ''' Custom ListCtrl class '''
  def __init__(self, parent, id, pos, size, style):
    wx.ListCtrl.__init__(self, parent, id, pos, size, style)
    self.InsertColumn(0, 'URL', width=150)
    self.InsertColumn(1, 'Size', width=90)
    self.InsertColumn(2, 'Percent', width=80)
    self.InsertColumn(3, 'ETA', width=50)
    self.InsertColumn(4, 'Speed', width=90)
    self.InsertColumn(5, 'Status', width=150)
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
  
  def __init__(self, parent, optList, log):
    self.optList = optList
    self.log = log
    self.set_data()
    
    wx.Panel.__init__(self, parent)
    self.enableLogChk = wx.CheckBox(self, -1, 'Enable log', (240, 20))
    self.enableTimeChk = wx.CheckBox(self, -1, 'Write time', (240, 50))
    self.clearLogButton = wx.Button(self, label="Clear Log", pos=(200, 90))
    self.viewLogButton = wx.Button(self, label="View Log", pos=(300, 90))
    wx.StaticText(self, -1, 'Path: ' + self.path, (180, 140))
    self.sizeText = wx.StaticText(self, -1, 'Log Size: ' + self.size, (240, 170))
    
    self.Bind(wx.EVT_CHECKBOX, self.OnEnable, self.enableLogChk)
    self.Bind(wx.EVT_CHECKBOX, self.OnTime, self.enableTimeChk)
    self.Bind(wx.EVT_BUTTON, self.OnClear, self.clearLogButton)
    self.Bind(wx.EVT_BUTTON, self.OnView, self.viewLogButton)
  
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
    self.enableLogChk.SetValue(self.optList.enableLog)
    self.enableTimeChk.SetValue(self.optList.writeTimeToLog)
    if self.optList.enableLog == False:
      self.enableTimeChk.Disable()
    if self.log == None:
      self.clearLogButton.Disable()
      self.viewLogButton.Disable()
  
  def save_options(self):
    self.optList.enableLog = self.enableLogChk.GetValue()
    self.optList.writeTimeToLog = self.enableTimeChk.GetValue()
    
  def restart_popup(self):
    wx.MessageBox('Please restart ' + TITLE, 'Restart', wx.OK | wx.ICON_INFORMATION)
    
class UpdatePanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    text = '''Enter the path where youtube-dlG should 
download the latest youtube-dl.'''
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, text, (85, 10))
    wx.StaticText(self, -1, 'Path', (95, 60))
    self.updatePathBox = wx.TextCtrl(self, -1, pos=(90, 80), size=(400, -1))
    self.autoUpdateChk = wx.CheckBox(self, -1, 'Auto Update youtube-dl', (100, 130))
    
  def load_options(self):
    self.updatePathBox.SetValue(self.optList.updatePath)
    self.autoUpdateChk.SetValue(self.optList.autoUpdate)
    
  def save_options(self):
    self.optList.updatePath = get_abs_path(self.updatePathBox.GetValue())
    self.optList.autoUpdate = self.autoUpdateChk.GetValue()
    
class PlaylistPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, 'Playlist  Options', (100, 20))
    wx.StaticText(self, -1, 'Start', (90, 53))
    self.startSpnr = wx.SpinCtrl(self, -1, "", (160, 50), size=(60, -1))
    wx.StaticText(self, -1, 'Stop', (90, 83))
    self.stopSpnr = wx.SpinCtrl(self, -1, "", (160, 80), size=(60, -1))
    wx.StaticText(self, -1, 'Max DLs', (90, 113))
    self.maxSpnr = wx.SpinCtrl(self, -1, "", (160, 110), size=(60, -1))
    wx.StaticText(self, -1, 'Filesize (e.g. 50k or 44.6m)', (330, 20))
    wx.StaticText(self, -1, 'Min', (360, 63))
    self.minFilesizeBox = wx.TextCtrl(self, -1, pos=(400, 60), size=(70, -1))
    wx.StaticText(self, -1, 'Max', (360, 93))
    self.maxFilesizeBox = wx.TextCtrl(self, -1, pos=(400, 90), size=(70, -1))
    self.startSpnr.SetRange(1, 999)
    self.stopSpnr.SetRange(0, 999)
    self.maxSpnr.SetRange(0, 999)
    
  def load_options(self):
    self.startSpnr.SetValue(self.optList.startTrack)
    self.stopSpnr.SetValue(self.optList.endTrack)
    self.maxSpnr.SetValue(self.optList.maxDownloads)
    self.minFilesizeBox.SetValue(self.optList.minFileSize)
    self.maxFilesizeBox.SetValue(self.optList.maxFileSize)
    
  def save_options(self):
    self.optList.startTrack = self.startSpnr.GetValue()
    self.optList.endTrack = self.stopSpnr.GetValue()
    self.optList.maxDownloads = self.maxSpnr.GetValue()
    self.optList.minFileSize = self.minFilesizeBox.GetValue()
    self.optList.maxFileSize = self.maxFilesizeBox.GetValue()
    self.check_input()
    
  def check_input(self):
    self.optList.minFileSize.replace('-', '')
    self.optList.maxFileSize.replace('-', '')
    if self.optList.minFileSize == '':
      self.optList.minFileSize = '0'
    if self.optList.maxFileSize == '':
      self.optList.maxFileSize = '0'
    
class ConnectionPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, 'Retries', (15, 12))
    self.retriesSpnr = wx.SpinCtrl(self, -1, "", (65, 10), size=(50, -1))
    self.retriesSpnr.SetRange(1, 99)
    wx.StaticText(self, -1, 'User Agent', (15, 50))
    self.userAgentBox = wx.TextCtrl(self, -1, pos=(10, 70), size=(320, -1))
    wx.StaticText(self, -1, 'Referer', (15, 100))
    self.refererBox = wx.TextCtrl(self, -1, pos=(10, 120), size=(320, -1))
    wx.StaticText(self, -1, 'Proxy', (15, 150))
    self.proxyBox = wx.TextCtrl(self, -1, pos=(10, 170), size=(450, -1))
  
  def load_options(self):
    self.userAgentBox.SetValue(self.optList.userAgent)
    self.refererBox.SetValue(self.optList.referer)
    self.proxyBox.SetValue(self.optList.proxy)
    self.retriesSpnr.SetValue(self.optList.retries)
    
  def save_options(self):
    self.optList.userAgent = self.userAgentBox.GetValue()
    self.optList.referer = self.refererBox.GetValue()
    self.optList.proxy = self.proxyBox.GetValue()
    self.optList.retries = self.retriesSpnr.GetValue()

class AuthenticationPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self,parent)
    wx.StaticText(self, -1, 'Username', (255, 10))
    self.usernameBox = wx.TextCtrl(self, -1, pos=(175, 30), size=(230, 25))
    wx.StaticText(self, -1, 'Password', (260, 70))
    self.passwordBox = wx.TextCtrl(self, -1, pos=(175, 90), size=(230, 25), style = wx.TE_PASSWORD)
    wx.StaticText(self, -1, 'Video Password (vimeo, smotri)', (190, 130))
    self.videopassBox = wx.TextCtrl(self, -1, pos=(175, 150), size=(230, 25), style = wx.TE_PASSWORD)
    
  def load_options(self):
    self.usernameBox.SetValue(self.optList.username)
    self.passwordBox.SetValue(self.optList.password)
    self.videopassBox.SetValue(self.optList.videoPass)
  
  def save_options(self):
    self.optList.username = self.usernameBox.GetValue()
    self.optList.password = self.passwordBox.GetValue()
    self.optList.videoPass = self.videopassBox.GetValue()

class AudioPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    self.toAudioChk = wx.CheckBox(self, -1, 'Convert to Audio', (220, 10))
    self.keepVideoChk = wx.CheckBox(self, -1, 'Keep Video', (240, 40))
    wx.StaticText(self, -1, 'Audio Format', (250, 80))
    self.audioFormatCombo = wx.ComboBox(self, choices=AUDIOFORMATS, pos=(210, 100), size=(160, 30))
    wx.StaticText(self, -1, "Audio Quality 0 (best) 9 (worst)", (200, 140))
    self.audioQualitySpnr = wx.SpinCtrl(self, -1, "", (248, 160), size=(90, 20))
    self.audioQualitySpnr.SetRange(0, 9)
    
    self.Bind(wx.EVT_CHECKBOX, self.OnAudioCheck, self.toAudioChk)
    
  def OnAudioCheck(self, event):
    if self.toAudioChk.GetValue():
      self.keepVideoChk.Enable()
      self.audioFormatCombo.Enable()
      self.audioQualitySpnr.Enable()
    else:
      self.keepVideoChk.Disable()
      self.audioFormatCombo.Disable()
      self.audioQualitySpnr.Disable()
  
  def load_options(self):
    self.toAudioChk.SetValue(self.optList.toAudio)
    self.keepVideoChk.SetValue(self.optList.keepVideo)
    self.audioFormatCombo.SetValue(self.optList.audioFormat)
    self.audioQualitySpnr.SetValue(self.optList.audioQuality)
    if self.optList.toAudio == False:
      self.keepVideoChk.Disable()
      self.audioFormatCombo.Disable()
      self.audioQualitySpnr.Disable()
  
  def save_options(self):
    self.optList.toAudio = self.toAudioChk.GetValue()
    self.optList.keepVideo = self.keepVideoChk.GetValue()
    self.optList.audioFormat = self.audioFormatCombo.GetValue()
    self.optList.audioQuality = self.audioQualitySpnr.GetValue()
  
class VideoPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, 'Video Format', (250, 10))
    self.videoFormatCombo = wx.ComboBox(self, choices=VIDEOFORMATS, pos=(210, 30), size=(160, 30))
    wx.StaticText(self, -1, 'DASH Audio', (250, 80))
    self.dashAudioFormatCombo = wx.ComboBox(self, choices=DASH_AUDIO_FORMATS, pos=(210, 100), size=(160, 30))
    self.clearDashFilesChk = wx.CheckBox(self, -1, 'Clear DASH audio/video files', (180, 150))
    
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
    self.videoFormatCombo.SetValue(self.optList.videoFormat)
    self.dashAudioFormatCombo.SetValue(self.optList.dashAudioFormat)
    self.clearDashFilesChk.SetValue(self.optList.clearDashFiles)
    if not video_is_dash(self.optList.videoFormat):
      self.dashAudioFormatCombo.Disable()
    if not have_dash_audio(self.optList.dashAudioFormat):
      self.clearDashFilesChk.SetValue(False)
      self.clearDashFilesChk.Disable()
    
  def save_options(self):
    self.optList.videoFormat = self.videoFormatCombo.GetValue()
    self.optList.dashAudioFormat = self.dashAudioFormatCombo.GetValue()
    self.optList.clearDashFiles = self.clearDashFilesChk.GetValue()
    
class FilesystemPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    self.idAsNameChk = wx.CheckBox(self, -1, 'ID as Name', (10, 10))
    self.ignoreErrorsChk = wx.CheckBox(self, -1, 'Ignore Errors', (10, 40))
    self.writeDescriptionChk = wx.CheckBox(self, -1, 'Write description to file', (10, 70))
    self.writeInfoChk = wx.CheckBox(self, -1, 'Write info to (.json) file', (10, 100))
    self.writeThumbnailChk = wx.CheckBox(self, -1, 'Write thumbnail to disk', (10, 130))
    
  def load_options(self):
    self.writeDescriptionChk.SetValue(self.optList.writeDescription)
    self.writeInfoChk.SetValue(self.optList.writeInfo)
    self.writeThumbnailChk.SetValue(self.optList.writeThumbnail)
    self.ignoreErrorsChk.SetValue(self.optList.ignoreErrors)
    self.idAsNameChk.SetValue(self.optList.idAsName)
    
  def save_options(self):
    self.optList.writeDescription = self.writeDescriptionChk.GetValue()
    self.optList.writeInfo = self.writeInfoChk.GetValue()
    self.optList.writeThumbnail = self.writeThumbnailChk.GetValue()
    self.optList.ignoreErrors = self.ignoreErrorsChk.GetValue()
    self.optList.idAsName = self.idAsNameChk.GetValue()
  
class SubtitlesPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    self.writeSubsChk = wx.CheckBox(self, -1, 'Download subtitle file by language', (10, 10))
    self.writeAllSubsChk = wx.CheckBox(self, -1, 'Download all available subtitles', (10, 40))
    self.writeAutoSubsChk = wx.CheckBox(self, -1, 'Download automatic subtitle file (YOUTUBE ONLY)', (10, 70))
    self.embedSubsChk = wx.CheckBox(self, -1, 'Embed subtitles in the video (only for mp4 videos)', (10, 100))
    wx.StaticText(self, -1, 'Subtitles Language', (15, 135))
    self.subsLangCombo = wx.ComboBox(self, choices=LANGUAGES, pos=(10, 155), size=(140, 30))
    self.embedSubsChk.Disable()
    
    self.Bind(wx.EVT_CHECKBOX, self.OnWriteSubsChk, self.writeSubsChk)
    self.Bind(wx.EVT_CHECKBOX, self.OnWriteAllSubsChk, self.writeAllSubsChk)
    self.Bind(wx.EVT_CHECKBOX, self.OnWriteAutoSubsChk, self.writeAutoSubsChk)
  
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
    self.writeSubsChk.SetValue(self.optList.writeSubs)
    self.writeAllSubsChk.SetValue(self.optList.writeAllSubs)
    self.subsLangCombo.SetValue(self.optList.subsLang)
    self.writeAutoSubsChk.SetValue(self.optList.writeAutoSubs)
    self.embedSubsChk.SetValue(self.optList.embedSubs)
    if self.optList.writeSubs:
      self.writeAllSubsChk.Disable()
      self.writeAutoSubsChk.Disable()
      self.embedSubsChk.Enable()
    if self.optList.writeAllSubs:
      self.writeSubsChk.Disable()
      self.subsLangCombo.Disable()
      self.writeAutoSubsChk.Disable()
    if self.optList.writeAutoSubs:
      self.writeAllSubsChk.Disable()
      self.writeSubsChk.Disable()
      self.subsLangCombo.Disable()
      self.embedSubsChk.Enable()
    if not self.subs_are_on():
      self.embedSubsChk.Disable()
  
  def save_options(self):
    self.optList.writeSubs = self.writeSubsChk.GetValue()
    self.optList.writeAllSubs = self.writeAllSubsChk.GetValue()
    self.optList.subsLang = self.subsLangCombo.GetValue()
    self.optList.writeAutoSubs = self.writeAutoSubsChk.GetValue()
    self.optList.embedSubs = self.embedSubsChk.GetValue()
  
class GeneralPanel(wx.Panel):
  
  def __init__(self, parent, optList, controlParent):
    self.optList = optList
    self.parent = controlParent
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, "Save Path", (255, 20))
    self.savePathBox = wx.TextCtrl(self, -1, pos=(60, 50), size=(450, -1))
    self.aboutButton = wx.Button(self, label="About", pos=(70, 100), size=(110, 40))
    self.openButton = wx.Button(self, label="Open", pos=(230, 100), size=(110, 40))
    self.resetButton = wx.Button(self, label="Reset Options", pos=(390, 100), size=(110, 40))
    wx.StaticText(self, -1, "Settings: " + self.optList.settings_abs_path, (140, 170))
     
    self.Bind(wx.EVT_BUTTON, self.OnAbout, self.aboutButton)
    self.Bind(wx.EVT_BUTTON, self.OnOpen, self.openButton)
    self.Bind(wx.EVT_BUTTON, self.OnReset, self.resetButton)
    
  def OnReset(self, event):
    self.parent.reset()
    
  def OnOpen(self, event):
    dlg = wx.DirDialog(None, "Choose directory")
    if dlg.ShowModal() == wx.ID_OK:
      self.savePathBox.SetValue(dlg.GetPath())
    dlg.Destroy()
    
  def OnAbout(self, event):
    description = '''A cross platform front-end GUI of 
the popular youtube-dl written in Python.'''
    
    license = '''This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>'''
    
    info = wx.AboutDialogInfo()
    
    info.SetIcon(wx.Icon(ICON, wx.BITMAP_TYPE_ICO))
    info.SetName(TITLE)
    info.SetVersion(__version__)
    info.SetDescription(description)
    info.SetWebSite('http://mrs0m30n3.github.io/youtube-dl-gui/')
    info.SetLicense(license)
    info.AddDeveloper('Sotiris Papadopoulos')
    wx.AboutBox(info)
    
  def load_options(self):
    self.savePathBox.SetValue(self.optList.savePath)
    
  def save_options(self):
    self.optList.savePath = get_abs_path(self.savePathBox.GetValue())
 
class OtherPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, 'Command line arguments (e.g. --help)', (25, 20))
    self.cmdArgsBox = wx.TextCtrl(self, -1, pos=(20, 40), size=(470, -1))
  
  def load_options(self):
    self.cmdArgsBox.SetValue(self.optList.cmdArgs)
  
  def save_options(self):
    self.optList.cmdArgs = self.cmdArgsBox.GetValue()
 
class OptionsFrame(wx.Frame):
  
  def __init__(self, optionsList, parent=None, id=-1, logger=None):
    wx.Frame.__init__(self, parent, id, "Options", size=(580, 250))
    
    self.optionsList = optionsList
    
    panel = wx.Panel(self)
    notebook = wx.Notebook(panel)
    
    self.generalTab = GeneralPanel(notebook, self.optionsList, self)
    self.audioTab = AudioPanel(notebook, self.optionsList)
    self.connectionTab = ConnectionPanel(notebook, self.optionsList)
    self.videoTab = VideoPanel(notebook, self.optionsList)
    self.filesysTab = FilesystemPanel(notebook, self.optionsList)
    self.subtitlesTab = SubtitlesPanel(notebook, self.optionsList)
    self.otherTab = OtherPanel(notebook, self.optionsList)
    self.updateTab = UpdatePanel(notebook, self.optionsList)
    self.authTab = AuthenticationPanel(notebook, self.optionsList)
    self.videoselTab = PlaylistPanel(notebook, self.optionsList)
    self.logTab = LogPanel(notebook, self.optionsList, logger)
    
    notebook.AddPage(self.generalTab, "General")
    notebook.AddPage(self.videoTab, "Video")
    notebook.AddPage(self.audioTab, "Audio")
    notebook.AddPage(self.videoselTab, "Playlist")
    notebook.AddPage(self.subtitlesTab, "Subtitles")
    notebook.AddPage(self.filesysTab, "Filesystem")
    notebook.AddPage(self.connectionTab, "Connection")
    notebook.AddPage(self.authTab, "Authentication")
    notebook.AddPage(self.updateTab, "Update")
    notebook.AddPage(self.logTab, "Log")
    notebook.AddPage(self.otherTab, "Commands")
    
    sizer = wx.BoxSizer()
    sizer.Add(notebook, 1, wx.EXPAND)
    panel.SetSizer(sizer)
    
    self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    self.load_all_options()
    
  def OnClose(self, event):
    self.save_all_options()
    if not file_exist(fix_path(self.optionsList.updatePath)+YOUTUBE_DL_FILENAME):
      self.wrong_youtubedl_path()
    self.Destroy()
  
  def wrong_youtubedl_path(self):
    text = '''The path under Options>Update is invalid
please do one of the following:
  *) restart youtube-dlG
  *) click the update button
  *) change the path to point where youtube-dl is'''
    wx.MessageBox(text, 'Error', wx.OK | wx.ICON_EXCLAMATION)
  
  def reset(self):
    self.optionsList.load_default()
    self.load_all_options()
  
  def load_all_options(self):
    self.generalTab.load_options()
    self.audioTab.load_options()
    self.connectionTab.load_options()
    self.videoTab.load_options()
    self.filesysTab.load_options()
    self.subtitlesTab.load_options()
    self.otherTab.load_options()
    self.updateTab.load_options()
    self.authTab.load_options()
    self.videoselTab.load_options()
    self.logTab.load_options()
    
  def save_all_options(self):
    self.generalTab.save_options()
    self.audioTab.save_options()
    self.connectionTab.save_options()
    self.videoTab.save_options()
    self.filesysTab.save_options()
    self.subtitlesTab.save_options()
    self.otherTab.save_options()
    self.updateTab.save_options()
    self.authTab.save_options()
    self.videoselTab.save_options()
    self.logTab.save_options()
    
