#! /usr/bin/env python

from .Utils import (
  get_HOME,
  file_exist,
  get_os_type,
  fix_path
)

SETTINGS_FILENAME = 'settings'
LINUX_SAVEPATH = '/.config'

class OptionsHandler():
  
  settings_abs_path = ''
  
  def __init__(self, statusBarWrite):
    self.statusBarWrite = statusBarWrite
    self.load_default()
    self.set_settings_path()
    if file_exist(self.settings_abs_path):
      self.load_from_file()
      
  def load_default(self):
    self.ignoreErrors = True
    self.idAsName = False
    self.toAudio = False
    self.audioFormat = "mp3"
    self.keepVideo = False
    self.audioQuality = 5
    self.proxy = ""
    self.savePath = get_HOME()
    self.autoUpdate = False
    self.videoFormat = "highest available"
    self.userAgent = ""
    self.referer = ""
    self.username = ""
    self.startTrack = "1"
    self.endTrack = "0"
    self.maxDownloads = "0"
    self.rateLimit = "0"
    self.retries = "10"
    self.writeDescription = False
    self.writeInfo = False
    self.writeThumbnail = False
    self.minFileSize = "0"
    self.maxFileSize = "0"
    self.writeSubs = False
    self.writeAllSubs = False
    self.subsLang = "English"
    self.writeAutoSubs = False
    self.cmdArgs = ""
    self.dashAudioFormat = "NO SOUND"
    self.clearDashFiles = False
    self.updatePath = ""
  
  def set_settings_path(self):
    self.settings_abs_path = get_HOME()
    ''' 
    On Linux save settings file under $HOME/LINUX_SAVEPATH/settings.
    On windows save settings file under %UserProfile%/settings
    '''
    if get_os_type() != 'nt': 
      self.settings_abs_path += LINUX_SAVEPATH
    self.settings_abs_path = fix_path(self.settings_abs_path)
    self.settings_abs_path += SETTINGS_FILENAME
  
  def read_from_file(self):
    f = open(self.settings_abs_path, 'r')
    options = f.readlines()
    f.close()
    return options
  
  def extract_options(self):
    opts = []
    for option in self.read_from_file():
      opt = option.split('=')
      if not len(opt) < 2:
	opts.append(opt[1].rstrip('\n'))
    return opts
  
  def load_from_file(self):
    opts = self.extract_options()
    try:
      self.ignoreErrors = opts[0] in ['True']
      self.idAsName = opts[1] in ['True']
      self.toAudio = opts[2] in ['True']
      self.audioFormat = opts[3]
      self.keepVideo = opts[4] in ['True']
      self.audioQuality = int(opts[5])
      self.proxy = opts[6]
      self.savePath = opts[7].decode('utf8')
      self.autoUpdate = opts[8] in ['True']
      self.videoFormat = opts[9]
      self.userAgent = opts[10]
      self.referer = opts[11]
      self.username = opts[12]
      self.startTrack = opts[13]
      self.endTrack = opts[14]
      self.maxDownloads = opts[15]
      self.rateLimit = opts[16]
      self.retries = opts[17]
      self.writeDescription = opts[18] in ['True']
      self.writeInfo = opts[19] in ['True']
      self.writeThumbnail = opts[20] in ['True']
      self.minFileSize = opts[21]
      self.maxFileSize = opts[22]
      self.writeSubs = opts[23] in ['True']
      self.writeAllSubs = opts[24] in ['True']
      self.subsLang = opts[25]
      self.writeAutoSubs = opts[26] in ['True']
      self.cmdArgs = opts[27]
      self.dashAudioFormat = opts[28]
      self.clearDashFiles = opts[29] in ['True']
      self.updatePath = opts[30]
    except:
      self.statusBarWrite('Error while loading settings file')
      self.load_default()
    
  def save_to_file(self):
    f = open(self.settings_abs_path, 'w')
    f.write('IgnoreErrors='+str(self.ignoreErrors)+'\n')
    f.write('IdAsName='+str(self.idAsName)+'\n')
    f.write('ToAudio='+str(self.toAudio)+'\n')
    f.write('AudioFormat='+str(self.audioFormat)+'\n')
    f.write('KeepVideo='+str(self.keepVideo)+'\n')
    f.write('AudioQuality='+str(self.audioQuality)+'\n')
    f.write('Proxy='+str(self.proxy)+'\n')
    f.write('SavePath='+self.savePath.encode('utf-8')+'\n')
    f.write('AutoUpdate='+str(self.autoUpdate)+'\n')
    f.write('VideoFormat='+str(self.videoFormat)+'\n')
    f.write('UserAgent='+str(self.userAgent)+'\n')
    f.write('Referer='+str(self.referer)+'\n')
    f.write('Username='+str(self.username)+'\n')
    f.write('StartTrack='+str(self.startTrack)+'\n')
    f.write('EndTrack='+str(self.endTrack)+'\n')
    f.write('MaxDownloads='+str(self.maxDownloads)+'\n')
    f.write('RateLimit='+str(self.rateLimit)+'\n')
    f.write('Retries='+str(self.retries)+'\n')
    f.write('WriteDescription='+str(self.writeDescription)+'\n')
    f.write('WriteInfo='+str(self.writeInfo)+'\n')
    f.write('WriteThumbnail='+str(self.writeThumbnail)+'\n')
    f.write('MinFileSize='+str(self.minFileSize)+'\n')
    f.write('MaxFileSize='+str(self.maxFileSize)+'\n')
    f.write('WriteSubtitles='+str(self.writeSubs)+'\n')
    f.write('WriteAllSubtitles='+str(self.writeAllSubs)+'\n')
    f.write('SubtitlesLanguage='+str(self.subsLang)+'\n')
    f.write('WriteAutoSubtitles='+str(self.writeAutoSubs)+'\n')
    f.write('CmdArgs='+str(self.cmdArgs)+'\n')
    f.write('DashAudioFormat='+str(self.dashAudioFormat)+'\n')
    f.write('ClearDashFiles='+str(self.clearDashFiles)+'\n')
    f.write('UpdatePath='+str(self.updatePath)+'\n')
    f.close()
    