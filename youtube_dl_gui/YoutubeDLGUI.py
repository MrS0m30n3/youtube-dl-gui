#! /usr/bin/env python

''' 
This file contains all gui classes
MainFrame
Custom wx.ListCtrl class
OptionsFrame
  ConnectionPanel
  AudioPanel
  videoPanel
  DownloadPanel
  SubtitlesPanel
  GeneralPanel
  OtherPanel
'''

import os
import wx
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .version import __version__
from .UpdateThread import UpdateThread
from .DownloadThread import DownloadManager
from .OptionsHandler import OptionsHandler
from .YoutubeDLInterpreter import YoutubeDLInterpreter

if os.name == 'nt':
  YOUTUBE_DL_FILENAME = 'youtube-dl.exe'
else:
  YOUTUBE_DL_FILENAME = 'youtube-dl'

TITLE = 'Youtube-dlG'
AUDIOFORMATS = ["mp3", "wav", "aac", "m4a"]
VIDEOFORMATS = ["highest available",
		"mp4 [1280x720]",
		"mp4 [640x360]",
		"webm [640x360]",
		"flv [400x240]",
		"3gp [320x240]",
		"mp4 1080p(DASH)",
		"mp4 720p(DASH)",
		"mp4 480p(DASH)",
		"mp4 360p(DASH)"]
LANGUAGES = ["English",
	     "Greek",
	     "Portuguese",
	     "French",
	     "Italian",
	     "Russian",
	     "Spanish",
	     "German"]

class MainFrame(wx.Frame):
  
  def __init__(self, parent=None, id=-1):
    wx.Frame.__init__(self, parent, id, TITLE+' '+__version__, size=(600, 410), style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
    
    # set sizers for status box (Windows & Linux)
    if os.name == 'nt':
      statusListSizer = (580, 165)
      statusBarSizer = (15, 365)
    else:
      statusListSizer = (580, 195)
      statusBarSizer = (15, 390)
    
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
    icon = wx.Icon('../icons/ytube.png', wx.BITMAP_TYPE_ICO)
    self.SetIcon(icon)
    
    # set publisher for update thread
    Publisher.subscribe(self.update_handler, "update")
    
    # set publisher for download thread
    Publisher.subscribe(self.download_handler, "download")
    
    # init options object
    self.optionsList = OptionsHandler()
    
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
  
  def check_if_youtube_dl_exist(self):
    if not os.path.exists(YOUTUBE_DL_FILENAME):
      self.status_bar_write("Youtube-dl is missing, trying to download it...")
      self.update_youtube_dl()
  
  def update_youtube_dl(self):
    self.downloadButton.Disable()
    self.updateThread = UpdateThread(YOUTUBE_DL_FILENAME)
  
  def status_bar_write(self, msg):
    self.statusBar.SetLabel(msg)
  
  def download_handler(self, msg):
    ''' Handles msg base into signals see SIGNALS.txt for more info'''
    if msg.data[0] == 'finish':
      index = msg.data.pop()
      if index == -1:
	self.status_bar_write('Done')
	self.downloadButton.SetLabel('Download')
	self.updateButton.Enable()
	self.downloadThread = None
	self.urlList = []
      else:
	self.statusList._write_data(index, 4, '')
	self.statusList._write_data(index, 5, 'Finished')
    elif msg.data[0] == 'close':
      index = msg.data.pop()
      if index == -1:
	self.status_bar_write('Stoping downloads')
      else:
	self.statusList._write_data(index, 3, '')
	self.statusList._write_data(index, 4, '')
	self.statusList._write_data(index, 5, 'Stopped')
    elif msg.data[0] == 'error':
      index = msg.data.pop()
      self.statusList._write_data(index, 3, '')
      self.statusList._write_data(index, 4, '')
      self.statusList._write_data(index, 5, 'Error')
    elif msg.data[0] == '[youtube]':
      index = msg.data.pop()
      self.statusList._write_data(index, 5, 'Pre-Processing')
    elif msg.data[0] == '[download]':
      index = msg.data.pop()
      self.statusList._write_data(index, 1, msg.data[3])
      self.statusList._write_data(index, 2, msg.data[1])
      self.statusList._write_data(index, 3, msg.data[7])
      self.statusList._write_data(index, 4, msg.data[5])
      self.statusList._write_data(index, 5, 'Downloading')
    elif msg.data[0] == '[ffmpeg]':
      index = msg.data.pop()
      self.statusList._write_data(index, 4, '')
      self.statusList._write_data(index, 5, 'Converting to Audio')
    else: # ['ignore'] or anything else
      pass # do nothing
	
  def update_handler(self, msg):
    if msg.data == 'finish':
      self.downloadButton.Enable()
      self.updateThread = None
    else:
      self.status_bar_write(msg.data)
  
  def stop_download(self):
    self.downloadThread.close()
    self.downloadThread.join()
    self.downloadThread = None
    self.urlList = []
  
  def start_download(self, trackList):
    self.statusList._clear_list()
    for url in trackList:
      if url != '':
	self.urlList.append(url)
	self.statusList._add_item(url)
    if not self.statusList._is_empty():
      options = YoutubeDLInterpreter(self.optionsList, YOUTUBE_DL_FILENAME).get_options()
      self.status_bar_write('Download started')
      self.downloadThread = DownloadManager(options, self.statusList._get_items())
      self.downloadButton.SetLabel('Stop')
      self.updateButton.Disable()
  
  def save_options(self):
    self.optionsList.save_to_file()
  
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
	  index = self.statusList._add_item(url)
	  ''' Retrieve last item as {url:url, index:indexNo} '''
	  item = self.statusList._get_last_item()
	  ''' Pass that item into downloadThread '''
	  self.downloadThread.add_download_item(item)
  
  def OnDownload(self, event):
    if self.downloadThread != None:
      self.stop_download()
    else:
      self.start_download(self.trackList.GetValue().split('\n'))
      
  def OnUpdate(self, event):
    if (self.downloadThread == None and self.updateThread == None):
      self.status_bar_write("Updating youtube-dl...")
      self.update_youtube_dl()
  
  def OnOptions(self, event):
    optionsFrame = OptionsFrame(self.optionsList)
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
    self.InsertColumn(5, 'Status', width=120)
    self.ListIndex = 0
  
  ''' Add single item on list '''
  def _add_item(self, item):
    self.InsertStringItem(self.ListIndex, item)
    self.ListIndex += 1
    return self.ListIndex
  
  ''' Write data on index, column '''
  def _write_data(self, index, column, data):
    self.SetStringItem(index, column, data)
  
  ''' Clear list and set index to 0'''
  def _clear_list(self):
    self.DeleteAllItems()
    self.ListIndex = 0
  
  ''' Return True if list is empty '''
  def _is_empty(self):
    if self.ListIndex == 0:
      return True
    else:
      return False
  
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
    
class ConnectionPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, 'User Agent', (15, 10))
    self.userAgentBox = wx.TextCtrl(self, -1, pos=(10, 30), size=(230, -1))
    wx.StaticText(self, -1, 'Referer', (270, 10))
    self.refererBox = wx.TextCtrl(self, -1, pos=(265, 30), size=(230, -1))
    wx.StaticText(self, -1, 'Username', (15, 60))
    self.usernameBox = wx.TextCtrl(self, -1, pos=(10, 80), size=(230, -1))
    wx.StaticText(self, -1, 'Password', (270, 60))
    self.passwordBox = wx.TextCtrl(self, -1, pos=(265, 80), size=(230, -1), style = wx.TE_PASSWORD)
    wx.StaticText(self, -1, 'Proxy', (15, 110))
    self.proxyBox = wx.TextCtrl(self, -1, pos=(10, 130), size=(350, -1))
  
  def load_options(self):
    self.userAgentBox.SetValue(self.optList.userAgent)
    self.refererBox.SetValue(self.optList.referer)
    self.usernameBox.SetValue(self.optList.username)
    self.proxyBox.SetValue(self.optList.proxy)
    
  def save_options(self):
    self.optList.userAgent = self.userAgentBox.GetValue()
    self.optList.referer = self.refererBox.GetValue()
    self.optList.username = self.usernameBox.GetValue()
    self.optList.proxy = self.proxyBox.GetValue()
    
class AudioPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    self.toAudioChk = wx.CheckBox(self, -1, 'Convert to Audio', (10, 10))
    self.keepVideoChk = wx.CheckBox(self, -1, 'Keep Video', (30, 40))
    wx.StaticText(self, -1, 'Audio Format', (35, 80))
    self.audioFormatCombo = wx.ComboBox(self, choices=AUDIOFORMATS, pos=(30, 100), size=(95, -1))
    wx.StaticText(self, -1, "Audio Quality 0 (best) 9 (worst)", (35, 130))
    self.audioQualitySpnr = wx.SpinCtrl(self, -1, "", (30, 150))
    self.audioQualitySpnr.SetRange(0, 9)
    
    self.Bind(wx.EVT_CHECKBOX, self.OnAudioCheck, self.toAudioChk)
    
  def OnAudioCheck(self, event):
    if (self.toAudioChk.GetValue()):
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
    if (self.optList.toAudio == False):
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
    wx.StaticText(self, -1, 'Video Format', (15, 10))
    self.videoFormatCombo = wx.ComboBox(self, choices=VIDEOFORMATS, pos=(10, 30), size=(160, 30))
    wx.StaticText(self, -1, 'Playlist  Options', (300, 30))
    wx.StaticText(self, -1, 'Start', (250, 60))
    self.startBox = wx.TextCtrl(self, -1, pos=(320, 55), size=(50, -1))
    wx.StaticText(self, -1, 'Stop', (250, 100))
    self.stopBox = wx.TextCtrl(self, -1, pos=(320, 95), size=(50, -1))
    wx.StaticText(self, -1, 'Max DLs', (250, 140))
    self.maxBox = wx.TextCtrl(self, -1, pos=(320, 135), size=(50, -1))
  
  def load_options(self):
    self.videoFormatCombo.SetValue(self.optList.videoFormat)
    self.startBox.SetValue(self.optList.startTrack)
    self.stopBox.SetValue(self.optList.endTrack)
    self.maxBox.SetValue(self.optList.maxDownloads)
    
  def save_options(self):
    self.optList.videoFormat = self.videoFormatCombo.GetValue()
    self.optList.startTrack = self.startBox.GetValue()
    self.optList.endTrack = self.stopBox.GetValue()
    self.optList.maxDownloads = self.maxBox.GetValue()
    
class DownloadPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, 'Rate Limit (e.g. 50k or 44.6m)', (250, 15))
    self.limitBox = wx.TextCtrl(self, -1, pos=(245, 35), size=(80, -1))
    wx.StaticText(self, -1, 'Retries', (15, 15))
    self.retriesBox = wx.TextCtrl(self, -1, pos=(10, 35), size=(50, -1))
    self.writeDescriptionChk = wx.CheckBox(self, -1, 'Write description to file', (10, 60))
    self.writeInfoChk = wx.CheckBox(self, -1, 'Write info to (.json) file', (10, 85))
    self.writeThumbnailChk = wx.CheckBox(self, -1, 'Write thumbnail to disk', (10, 110))
    self.ignoreErrorsChk = wx.CheckBox(self, -1, 'Ignore Errors', (10, 135))
    wx.StaticText(self, -1, 'Min Filesize (e.g. 50k or 44.6m)', (250, 65))
    self.minFilesizeBox = wx.TextCtrl(self, -1, pos=(245, 85), size=(80, -1))
    wx.StaticText(self, -1, 'Max Filesize (e.g. 50k or 44.6m)', (250, 115))
    self.maxFilesizeBox = wx.TextCtrl(self, -1, pos=(245, 135), size=(80, -1))
    
  def load_options(self):
    self.limitBox.SetValue(self.optList.rateLimit)
    self.retriesBox.SetValue(self.optList.retries)
    self.writeDescriptionChk.SetValue(self.optList.writeDescription)
    self.writeInfoChk.SetValue(self.optList.writeInfo)
    self.writeThumbnailChk.SetValue(self.optList.writeThumbnail)
    self.ignoreErrorsChk.SetValue(self.optList.ignoreErrors)
    self.minFilesizeBox.SetValue(self.optList.minFileSize)
    self.maxFilesizeBox.SetValue(self.optList.maxFileSize)
  
  def save_options(self):
    self.optList.rateLimit = self.limitBox.GetValue()
    self.optList.retries = self.retriesBox.GetValue()
    self.optList.writeDescription = self.writeDescriptionChk.GetValue()
    self.optList.writeInfo = self.writeInfoChk.GetValue()
    self.optList.writeThumbnail = self.writeThumbnailChk.GetValue()
    self.optList.ignoreErrors = self.ignoreErrorsChk.GetValue()
    self.optList.minFileSize = self.minFilesizeBox.GetValue()
    self.optList.maxFileSize = self.maxFilesizeBox.GetValue()
  
class SubtitlesPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    self.writeSubsChk = wx.CheckBox(self, -1, 'Write subtitle file', (10, 10))
    self.writeAllSubsChk = wx.CheckBox(self, -1, 'Download all available subtitles', (10, 40))
    self.writeAutoSubsChk = wx.CheckBox(self, -1, 'Write automatic subtitle file (YOUTUBE ONLY)', (10, 70))
    wx.StaticText(self, -1, 'Subtitles Language', (15, 105))
    self.subsLangCombo = wx.ComboBox(self, choices=LANGUAGES, pos=(10, 125), size=(140, 30))
    
    self.Bind(wx.EVT_CHECKBOX, self.OnWriteSubsChk, self.writeSubsChk)
    self.Bind(wx.EVT_CHECKBOX, self.OnWriteAllSubsChk, self.writeAllSubsChk)
    self.Bind(wx.EVT_CHECKBOX, self.OnWriteAutoSubsChk, self.writeAutoSubsChk)
    
  def OnWriteAutoSubsChk(self, event):
    if (self.writeAutoSubsChk.GetValue()):
      self.writeAllSubsChk.Disable()
      self.writeSubsChk.Disable()
      self.subsLangCombo.Disable()
    else:
      self.writeAllSubsChk.Enable()
      self.writeSubsChk.Enable()
      self.subsLangCombo.Enable()
  
  def OnWriteSubsChk(self, event):
    if (self.writeSubsChk.GetValue()):
      self.writeAllSubsChk.Disable()
      self.writeAutoSubsChk.Disable()
    else:
      self.writeAllSubsChk.Enable()
      self.writeAutoSubsChk.Enable()
  
  def OnWriteAllSubsChk(self, event):
    if (self.writeAllSubsChk.GetValue()):
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
    if (self.writeSubsChk.GetValue()):
      self.writeAllSubsChk.Disable()
      self.writeAllSubsChk.SetValue(False)
      self.writeAutoSubsChk.Disable()
      self.writeAutoSubsChk.SetValue(False)
    if (self.writeAllSubsChk.GetValue()):
      self.writeSubsChk.Disable()
      self.writeSubsChk.SetValue(False)
      self.subsLangCombo.Disable()
      self.writeAutoSubsChk.Disable()
      self.writeAutoSubsChk.SetValue(False)
    if (self.writeAutoSubsChk.GetValue()):
      self.writeAllSubsChk.Disable()
      self.writeAllSubsChk.SetValue(False)
      self.writeSubsChk.Disable()
      self.writeSubsChk.SetValue(False)
      self.subsLangCombo.Disable()
  
  def save_options(self):
    self.optList.writeSubs = self.writeSubsChk.GetValue()
    self.optList.writeAllSubs = self.writeAllSubsChk.GetValue()
    self.optList.subsLang = self.subsLangCombo.GetValue()
    self.optList.writeAutoSubs = self.writeAutoSubsChk.GetValue()
  
class GeneralPanel(wx.Panel):
  
  def __init__(self, parent, optList, controlParent):
    self.optList = optList
    self.parent = controlParent
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, "Save Path", (15, 10))
    self.savePathBox = wx.TextCtrl(self, -1, pos=(10, 30), size=(350, -1))
    self.idAsNameChk = wx.CheckBox(self, -1, 'ID as Name', (10, 70))
    self.autoUpdateChk = wx.CheckBox(self, -1, 'Auto Update', (160, 70))
    self.aboutButton = wx.Button(self, label="About", pos=(380, 80), size=(100, 40))
    self.openButton = wx.Button(self, label="Open", pos=(380, 20), size=(100, 40))
    self.resetButton = wx.Button(self, label="Reset", pos=(380, 140), size=(100, 40))
    wx.StaticText(self, -1, "Settings: " + self.optList.settings_abs_path, (20, 155))
     
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
    msg = TITLE + ' (GUI)'+ '\nVersion: ' + __version__ + '\nCreated by: Sotiris Papadopoulos'
    wx.MessageBox(msg, 'About', wx.OK | wx.ICON_INFORMATION)
    
  def load_options(self):
    self.savePathBox.SetValue(self.optList.savePath)
    self.idAsNameChk.SetValue(self.optList.idAsName)
    self.autoUpdateChk.SetValue(self.optList.autoUpdate)
    
  def save_options(self):
    self.optList.savePath = self.savePathBox.GetValue()
    self.optList.idAsName = self.idAsNameChk.GetValue()
    self.optList.autoUpdate = self.autoUpdateChk.GetValue()
 
class OtherPanel(wx.Panel):
  
  def __init__(self, parent, optList):
    self.optList = optList
    
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, 'Command line arguments (e.g. --help)', (25, 20))
    self.cmdArgsBox = wx.TextCtrl(self, -1, pos=(20, 40), size=(450, -1))
  
  def load_options(self):
    self.cmdArgsBox.SetValue(self.optList.cmdArgs)
  
  def save_options(self):
    self.optList.cmdArgs = self.cmdArgsBox.GetValue()
 
class OptionsFrame(wx.Frame):
  
  def __init__(self, optionsList, parent=None, id=-1):
    wx.Frame.__init__(self, parent, id, "Options", size=(540, 250))
    
    self.optionsList = optionsList
    
    panel = wx.Panel(self)
    notebook = wx.Notebook(panel)
    
    self.generalTab = GeneralPanel(notebook, self.optionsList, self)
    self.audioTab = AudioPanel(notebook, self.optionsList)
    self.connectionTab = ConnectionPanel(notebook, self.optionsList)
    self.videoTab = VideoPanel(notebook, self.optionsList)
    self.downloadTab = DownloadPanel(notebook, self.optionsList)
    self.subtitlesTab = SubtitlesPanel(notebook, self.optionsList)
    self.otherTab = OtherPanel(notebook, self.optionsList)
    
    notebook.AddPage(self.generalTab, "General")
    notebook.AddPage(self.audioTab, "Audio")
    notebook.AddPage(self.videoTab, "Video")
    notebook.AddPage(self.subtitlesTab, "Subtitles")
    notebook.AddPage(self.downloadTab, "Download")
    notebook.AddPage(self.connectionTab, "Connection")
    notebook.AddPage(self.otherTab, "Commands")
    
    sizer = wx.BoxSizer()
    sizer.Add(notebook, 1, wx.EXPAND)
    panel.SetSizer(sizer)
    
    self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    self.load_all_options()
    
  def OnClose(self, event):
    self.save_all_options()
    self.Destroy()
  
  def reset(self):
    self.optionsList.load_default()
    self.load_all_options()
  
  def load_all_options(self):
    self.generalTab.load_options()
    self.audioTab.load_options()
    self.connectionTab.load_options()
    self.videoTab.load_options()
    self.downloadTab.load_options()
    self.subtitlesTab.load_options()
    self.otherTab.load_options()
    
  def save_all_options(self):
    self.generalTab.save_options()
    self.audioTab.save_options()
    self.connectionTab.save_options()
    self.videoTab.save_options()
    self.downloadTab.save_options()
    self.subtitlesTab.save_options()
    self.otherTab.save_options()
    
