#! /usr/bin/env python

'''
Parse OptionHandler object into list
and call youtube_dl.main(list) using
subprocess (we use this method to let
youtube_dl.main() handle all the hard
work) 
'''

from .Utils import (
  video_is_dash,
  get_os_type,
  fix_path,
  add_PATH
)

LANGUAGES = {"English":"en", 
	    "Greek":"gr",
	    "Portuguese":"pt",
	    "French":"fr",
	    "Italian":"it",
	    "Russian":"ru",
	    "Spanish":"es",
	    "German":"de"}

VIDEOFORMATS = {"default":"0",
		"mp4 [1280x720]":"22",
		"mp4 [640x360]":"18",
		"webm [640x360]":"43",
		"flv [400x240]":"5",
		"3gp [320x240]":"36",
		"mp4 1080p(DASH)":"137",
		"mp4 720p(DASH)":"136",
		"mp4 480p(DASH)":"135",
		"mp4 360p(DASH)":"134"}
		
DASH_AUDIO_FORMATS = {"NO SOUND":"None",
		      "DASH m4a audio 128k":"140",
		      "DASH webm audio 48k":"171"}

class YoutubeDLInterpreter():
  
  def __init__(self, optionsList, youtubeDLFile):
    self.youtubeDLFile = youtubeDLFile
    self.optionsList = optionsList
    self.opts = []
    self.set_os()
    self.set_progress_opts()
    self.set_output_opts()
    self.set_auth_opts()
    self.set_connection_opts()
    self.set_video_opts()
    self.set_playlist_opts()
    self.set_filesystem_opts()
    self.set_subtitles_opts()
    self.set_audio_opts()
    self.set_other_opts()
  
  def get_options(self):
    return self.opts
  
  def set_os(self):
    if get_os_type() == 'nt':
      self.opts = [self.youtubeDLFile]
      add_PATH(self.optionsList.updatePath)
    else:
      path = fix_path(self.optionsList.updatePath)
      self.opts = ['python', path + self.youtubeDLFile]
  
  def set_progress_opts(self):
    ''' Do NOT change this option '''
    self.opts.append('--newline')
  
  def set_playlist_opts(self):
    if self.optionsList.startTrack != 1:
      self.opts.append('--playlist-start')
      self.opts.append(str(self.optionsList.startTrack))
    if self.optionsList.endTrack != 0:
      self.opts.append('--playlist-end')
      self.opts.append(str(self.optionsList.endTrack))
    if self.optionsList.maxDownloads != 0:
      self.opts.append('--max-downloads')
      self.opts.append(str(self.optionsList.maxDownloads))
    if self.optionsList.minFileSize != '0':
      self.opts.append('--min-filesize')
      self.opts.append(self.optionsList.minFileSize)
    if self.optionsList.maxFileSize != '0':
      self.opts.append('--max-filesize')
      self.opts.append(self.optionsList.maxFileSize)
  
  def set_auth_opts(self):
    if self.optionsList.username != '':
      self.opts.append('-u')
      self.opts.append(self.optionsList.username)
    if self.optionsList.password != '':
      self.opts.append('-p')
      self.opts.append(self.optionsList.password)
    if self.optionsList.videoPass != '':
      self.opts.append('--video-password')
      self.opts.append(self.optionsList.videoPass)
  
  def set_connection_opts(self):
    if self.optionsList.retries != 10:
      self.opts.append('-R')
      self.opts.append(str(self.optionsList.retries))
    if self.optionsList.proxy != '':
      self.opts.append('--proxy')
      self.opts.append(self.optionsList.proxy)
    if self.optionsList.userAgent != '':
      self.opts.append('--user-agent')
      self.opts.append(self.optionsList.userAgent)
    if self.optionsList.referer != '':
      self.opts.append('--referer')
      self.opts.append(self.optionsList.referer)
  
  def set_video_opts(self):
    if self.optionsList.videoFormat != 'default':
      self.opts.append('-f')
      if video_is_dash(self.optionsList.videoFormat):
	vf = VIDEOFORMATS[self.optionsList.videoFormat]
	af = DASH_AUDIO_FORMATS[self.optionsList.dashAudioFormat]
	if af != 'None':
	  self.opts.append(vf+'+'+af)
	else:
	  self.opts.append(vf)
      else:
	self.opts.append(VIDEOFORMATS[self.optionsList.videoFormat])
  
  def set_filesystem_opts(self):
    if self.optionsList.ignoreErrors:
      self.opts.append('-i')
    if self.optionsList.writeDescription:
      self.opts.append('--write-description')
    if self.optionsList.writeInfo:
      self.opts.append('--write-info-json')
    if self.optionsList.writeThumbnail:
      self.opts.append('--write-thumbnail')
  
  def set_subtitles_opts(self):
    if self.optionsList.writeAllSubs:
      self.opts.append('--all-subs')
    if (self.optionsList.writeAutoSubs):
      self.opts.append('--write-auto-sub')
    if self.optionsList.writeSubs:
      self.opts.append('--write-sub')
      if self.optionsList.subsLang != 'English':
	self.opts.append('--sub-lang')
	self.opts.append(LANGUAGES[self.optionsList.subsLang])
    if self.optionsList.embedSubs:
      self.opts.append('--embed-subs')
  
  def set_output_opts(self):
    path = fix_path(self.optionsList.savePath)
    self.opts.append('-o')
    if self.optionsList.outputFormat == 'id':
      self.opts.append(path + '%(id)s.%(ext)s')
    elif self.optionsList.outputFormat == 'title':
      self.opts.append(path + '%(title)s.%(ext)s')
    elif self.optionsList.outputFormat == 'custom':
      self.opts.append(path + self.optionsList.outputTemplate)
  
  def set_audio_opts(self):
    if self.optionsList.toAudio:
      self.opts.append('-x')
      self.opts.append('--audio-format')
      self.opts.append(self.optionsList.audioFormat)
      if self.optionsList.audioQuality != 5:
	self.opts.append('--audio-quality')
	self.opts.append(str(self.optionsList.audioQuality))
      if self.optionsList.keepVideo:
	self.opts.append('-k')
  
  def set_other_opts(self):
    if self.optionsList.cmdArgs != '':
      for option in self.optionsList.cmdArgs.split():
	self.opts.append(option)
	
